#!/usr/bin/env python3

import csv
import sqlite3
import sys
from pathlib import Path

from assets.embargoes import (
    classify_embargo,
    is_indefinite,
)


def embargo_files(record_directory):
    yield from Path(record_directory).rglob(
        "*child-embargoes.csv"
    )


def parse_row(row):
    return (
        row[0].strip(),
        row[1].strip(),
        row[2].strip(),
    )


def insert_embargo(
    conn,
    pid,
    embargo_target,
    embargo_value,
):
    """
    Preserve the source embargo as a row in the embargoes table.
    """

    embargo_class = classify_embargo(
        embargo_target
    )

    conn.execute(
        """
        INSERT OR IGNORE INTO embargoes (
            object_id,
            target,
            embargo_value,
            embargo_class
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            pid,
            embargo_target,
            embargo_value,
            embargo_class,
        )
    )

    return embargo_class


def project_embargo_to_object(
    conn,
    pid,
    embargo_target,
    embargo_value,
    embargo_class,
):
    """
    Project source embargo information onto the existing
    objects embargo fields used by the Figshare migration.

    The normalized embargoes table remains the authoritative
    source for all embargo conditions.
    """

    indefinite = is_indefinite(
        embargo_value
    )

    # -------------------------
    # File-level restrictions
    # -------------------------

    if embargo_class == "file":

        if indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'file',
                    embargo_date = NULL,
                    embargo_reason = 'perpetual file embargo'
                WHERE pid = ?
                """,
                (pid,)
            )

        else:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'file',
                    embargo_date = ?
                WHERE pid = ?
                """,
                (
                    embargo_value,
                    pid,
                )
            )

        return

    # -------------------------
    # Whole-record restrictions
    # -------------------------

    if embargo_class == "article":

        if indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'article',
                    embargo_date = NULL,
                    embargo_reason = 'perpetual article embargo'
                WHERE pid = ?
                """,
                (pid,)
            )

        else:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'article',
                    embargo_date = ?
                WHERE pid = ?
                """,
                (
                    embargo_value,
                    pid,
                )
            )

        return

    # -------------------------
    # IP restrictions
    # -------------------------

    if embargo_class == "access":

        conn.execute(
            """
            UPDATE objects
            SET embargo_reason = ?
            WHERE pid = ?
            """,
            (
                f"IP restriction ({embargo_value})",
                pid,
            )
        )

        return


def update_embargoes(
    db_path,
    record_directory,
):

    conn = sqlite3.connect(db_path)

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.execute("BEGIN")

    source_rows = 0
    inserted_rows = 0
    unknown_types = set()

    for embargo_file in embargo_files(
        record_directory
    ):

        with embargo_file.open(
            newline="",
            encoding="utf-8",
        ) as fh:

            reader = csv.reader(fh)

            for row in reader:

                if len(row) < 3:
                    continue

                pid, target, value = parse_row(
                    row
                )

                if not pid or not target or not value:
                    continue

                source_rows += 1

                before = conn.total_changes

                embargo_class = insert_embargo(
                    conn,
                    pid,
                    target,
                    value,
                )

                if conn.total_changes > before:
                    inserted_rows += 1

                if embargo_class == "unknown":
                    unknown_types.add(target)

                project_embargo_to_object(
                    conn,
                    pid,
                    target,
                    value,
                    embargo_class,
                )

                if source_rows % 1000 == 0:

                    conn.commit()
                    conn.execute("BEGIN")

    conn.commit()

    embargo_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM embargoes
        """
    ).fetchone()[0]

    object_count = conn.execute(
        """
        SELECT COUNT(
            DISTINCT object_id
        )
        FROM embargoes
        """
    ).fetchone()[0]

    conn.close()

    print()
    print(
        f"Processed {source_rows:,} "
        "source embargo rows"
    )

    print(
        f"Inserted {inserted_rows:,} "
        "new embargo rows"
    )

    print(
        f"Embargo table contains "
        f"{embargo_count:,} rows"
    )

    print(
        f"Embargoed objects: "
        f"{object_count:,}"
    )

    if unknown_types:

        print()
        print("Unknown embargo types:")

        for target in sorted(
            unknown_types
        ):
            print(f"  {target}")


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print(
            f"Usage: {sys.argv[0]} "
            "DATABASE REPOSITORY_ROOT"
        )

        sys.exit(1)

    db_path = sys.argv[1]
    repository_root = sys.argv[2]

    update_embargoes(
        db_path,
        repository_root,
    )