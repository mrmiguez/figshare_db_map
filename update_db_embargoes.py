#!/usr/bin/env python3

import os
import csv
import sqlite3
import sys
from pathlib import Path

PATH = os.path.dirname(os.path.abspath(__file__))

FILE_EMBARGO_TYPES = {
    "PDF datastream",
    "OBJ datastream",
    "FULL_TEXT datastream",
    "MP4 datastream",
    "PREVIEW datastream",
}

ARTICLE_EMBARGO_TYPES = {
    "object",
}

ACCESS_RESTRICTION_TYPES = {
    "IP",
}

UNKNOWN_TYPES = set()


def embargo_files(record_directory):
    yield from Path(record_directory).rglob("*child-embargoes.csv")


def parse_row(row):

    return (
        row[0].strip(),
        row[1].strip(),
        row[2].strip(),
    )


def update_embargo(conn, pid, embargo_target, embargo_value):

    is_indefinite = embargo_value.lower() == "indefinite"

    # File-level restrictions
    if embargo_target in FILE_EMBARGO_TYPES:

        if is_indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type   = 'file',
                    embargo_date   = NULL,
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
                (embargo_value, pid)
            )

        return

    # Whole-object restrictions
    if embargo_target in ARTICLE_EMBARGO_TYPES:

        if is_indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type   = 'article',
                    embargo_date   = NULL,
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
                (embargo_value, pid)
            )

        return

    # IP restrictions
    if embargo_target in ACCESS_RESTRICTION_TYPES:

        conn.execute(
            """
            UPDATE objects
            SET embargo_reason = ?
            WHERE pid = ?
            """,
            (f"IP restriction ({embargo_value})", pid)
        )

        return

    # Unknowns
    UNKNOWN_TYPES.add(embargo_target)

    print(
        f"UNKNOWN: {pid} {embargo_target} {embargo_value}"
    )


def update_embargoes(db_path, record_directory):

    conn = sqlite3.connect(db_path)

    conn.execute("BEGIN")

    count = 0

    for embargo_file in embargo_files(record_directory):

        with open(
            embargo_file,
            newline="",
            encoding="utf-8"
        ) as fh:

            reader = csv.reader(fh)

            for row in reader:

                if len(row) < 3:
                    continue

                pid, target, value = parse_row(row)

                update_embargo(
                    conn,
                    pid,
                    target,
                    value
                )

                count += 1

                if count % 1000 == 0:

                    conn.commit()
                    conn.execute("BEGIN")

    conn.commit()
    conn.close()

    print(f"\nUpdated {count:,} embargo rows")

    if UNKNOWN_TYPES:

        print("\nUnknown embargo types:")

        for t in sorted(UNKNOWN_TYPES):
            print(f"  {t}")


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print(
            f"Usage: {sys.argv[0]} DATABASE REPOSITORY_ROOT"
        )

        sys.exit(1)

    db_path = sys.argv[1]
    repository_root = sys.argv[2]

    update_embargoes(
        db_path,
        repository_root
    )