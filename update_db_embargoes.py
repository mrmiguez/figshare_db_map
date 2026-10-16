#!/usr/bin/env python3

import argparse
import csv
import io
import sqlite3
import sys
from pathlib import Path

import boto3

from assets.embargoes import (
    classify_embargo,
    is_indefinite,
)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Import repository embargo metadata "
            "into the Figshare migration database."
        )
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    source = parser.add_mutually_exclusive_group(
        required=True
    )

    source.add_argument(
        "--root",
        help="Local repository root",
    )

    source.add_argument(
        "--s3-bucket",
        help="S3 source bucket",
    )

    parser.add_argument(
        "--s3-prefix",
        default="",
        help="Optional S3 key prefix",
    )

    return parser.parse_args()


# ----------------------------------------------------------------------
# Source readers
# ----------------------------------------------------------------------

def local_embargo_rows(root):
    """
    Yield (source, row) pairs from local child-embargoes.csv files.
    """

    file_count = 0

    for path in Path(root).rglob(
        "*child-embargoes.csv"
    ):

        file_count += 1

        with path.open(
            newline="",
            encoding="utf-8",
        ) as fh:

            reader = csv.reader(fh)

            for row in reader:
                yield str(path), row

    if file_count == 0:
        raise RuntimeError(
            "No *child-embargoes.csv files "
            f"found under {root}"
        )


def s3_embargo_rows(
    bucket,
    prefix="",
):
    """
    Yield (source, row) pairs from child-embargoes.csv
    objects stored in S3.
    """

    s3 = boto3.client("s3")

    paginator = s3.get_paginator(
        "list_objects_v2"
    )

    pages = paginator.paginate(
        Bucket=bucket,
        Prefix=prefix,
    )

    file_count = 0

    for page in pages:

        for obj in page.get(
            "Contents",
            []
        ):

            key = obj["Key"]

            if not key.endswith(
                "child-embargoes.csv"
            ):
                continue

            file_count += 1

            response = s3.get_object(
                Bucket=bucket,
                Key=key,
            )

            source = (
                f"s3://{bucket}/{key}"
            )

            with io.TextIOWrapper(
                response["Body"],
                encoding="utf-8",
                newline="",
            ) as fh:

                reader = csv.reader(fh)

                for row in reader:
                    yield source, row

    if file_count == 0:
        source = f"s3://{bucket}"

        if prefix:
            source += f"/{prefix}"

        raise RuntimeError(
            "No *child-embargoes.csv "
            f"objects found under {source}"
        )


# ----------------------------------------------------------------------
# Row parsing
# ----------------------------------------------------------------------

def parse_row(row):

    return (
        row[0].strip(),
        row[1].strip(),
        row[2].strip(),
    )


# ----------------------------------------------------------------------
# Normalized embargo table
# ----------------------------------------------------------------------

def insert_embargo(
    conn,
    pid,
    embargo_target,
    embargo_value,
):

    embargo_class = classify_embargo(
        embargo_target
    )

    cursor = conn.execute(
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
        ),
    )

    inserted = cursor.rowcount == 1

    return embargo_class, inserted


# ----------------------------------------------------------------------
# Legacy objects projection
# ----------------------------------------------------------------------

def project_embargo_to_object(
    conn,
    pid,
    embargo_value,
    embargo_class,
):
    """
    Project normalized source embargo information onto
    objects.embargo_* for Figshare delivery.

    The embargoes table remains authoritative for the
    complete source embargo state.
    """

    indefinite = is_indefinite(
        embargo_value
    )

    # File-level restrictions
    if embargo_class == "file":

        if indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'file',
                    embargo_date = NULL,
                    embargo_reason =
                        'perpetual file embargo'
                WHERE pid = ?
                """,
                (pid,),
            )

        else:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type   = 'file',
                    embargo_date   = ?,
                    embargo_reason = NULL
                WHERE pid = ?
                """,
                (
                    embargo_value,
                    pid,
                ),
            )

        return

    # Whole-record restrictions
    if embargo_class == "article":

        if indefinite:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'article',
                    embargo_date = NULL,
                    embargo_reason =
                        'perpetual article embargo'
                WHERE pid = ?
                """,
                (pid,),
            )

        else:

            conn.execute(
                """
                UPDATE objects
                SET embargo_type = 'article',
                    embargo_date = ?,
                    embargo_reason = NULL
                WHERE pid = ?
                """,
                (
                    embargo_value,
                    pid,
                ),
            )

        return

    # IP restrictions
    if embargo_class == "access":

        conn.execute(
            """
            UPDATE objects
            SET embargo_reason = ?
            WHERE pid = ?
            """,
            (
                (
                    "IP restriction "
                    f"({embargo_value})"
                ),
                pid,
            ),
        )


# ----------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------

def process_rows(
    conn,
    rows,
):

    stats = {
        "source_records": 0,
        "inserted_records": 0,
        "duplicate_records": 0,
        "invalid_records": 0,
    }

    unknown_types = set()

    conn.execute("BEGIN")

    try:

        for source, row in rows:

            if len(row) < 3:

                stats[
                    "invalid_records"
                ] += 1

                print(
                    "INVALID: "
                    f"{source}: {row}",
                    file=sys.stderr,
                )

                continue

            pid, target, value = parse_row(
                row
            )

            if not pid or not target or not value:

                stats[
                    "invalid_records"
                ] += 1

                print(
                    "INVALID: "
                    f"{source}: {row}",
                    file=sys.stderr,
                )

                continue

            stats[
                "source_records"
            ] += 1

            embargo_class, inserted = (
                insert_embargo(
                    conn,
                    pid,
                    target,
                    value,
                )
            )

            if inserted:

                stats[
                    "inserted_records"
                ] += 1

            else:

                stats[
                    "duplicate_records"
                ] += 1

            if embargo_class == "unknown":
                unknown_types.add(target)

            project_embargo_to_object(
                conn,
                pid,
                value,
                embargo_class,
            )

            if (
                stats["source_records"]
                % 1000
                == 0
            ):

                conn.commit()
                conn.execute("BEGIN")

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    stats["unknown_types"] = (
        unknown_types
    )

    return stats


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def report_results(
    conn,
    stats,
    source_description,
):

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

    class_counts = conn.execute(
        """
        SELECT
            embargo_class,
            COUNT(*) AS rows,
            COUNT(DISTINCT object_id)
                AS objects
        FROM embargoes
        GROUP BY embargo_class
        ORDER BY rows DESC
        """
    ).fetchall()

    print()
    print("EMBARGO IMPORT")
    print("--------------")

    print(
        f"Source: "
        f"{source_description}"
    )

    print(
        f"Parsed source assertions: "
        f"{stats['source_records']:,}"
    )

    print(
        f"New assertions stored: "
        f"{stats['inserted_records']:,}"
    )

    print(
        f"Duplicate assertions: "
        f"{stats['duplicate_records']:,}"
    )

    print(
        f"Invalid assertions: "
        f"{stats['invalid_records']:,}"
    )

    print(
        f"Embargo rows stored: "
        f"{embargo_count:,}"
    )

    print(
        f"Embargoed objects: "
        f"{object_count:,}"
    )

    print()
    print("Embargo classes:")

    for (
        embargo_class,
        rows,
        objects,
    ) in class_counts:

        print(
            f"  {embargo_class:<10} "
            f"{rows:>8,} rows  "
            f"{objects:>8,} objects"
        )

    if stats["unknown_types"]:

        print()
        print("Unknown embargo targets:")

        for target in sorted(
            stats["unknown_types"]
        ):
            print(f"  {target}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def update_embargoes(args):

    conn = sqlite3.connect(
        args.database
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    try:

        if args.root:

            rows = local_embargo_rows(
                args.root
            )

            source_description = (
                f"local:{args.root}"
            )

        else:

            rows = s3_embargo_rows(
                args.s3_bucket,
                args.s3_prefix,
            )

            source_description = (
                f"s3://{args.s3_bucket}"
            )

            if args.s3_prefix:

                source_description += (
                    f"/{args.s3_prefix}"
                )

        stats = process_rows(
            conn,
            rows,
        )

        if (
            stats["source_records"]
            == 0
        ):
            raise RuntimeError(
                "No embargo records "
                "were parsed"
            )

        report_results(
            conn,
            stats,
            source_description,
        )

    finally:
        conn.close()


if __name__ == "__main__":

    args = parse_args()

    update_embargoes(args)