#!/usr/bin/env python3

import argparse
import csv
import os
import sqlite3


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Audit repository structural objects that should "
            "not be migrated to Figshare as items."
        )
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    return parser.parse_args()


def get_structural_objects(conn):

    return conn.execute(
        """
        SELECT
            o.pid,
            o.title,
            o.source_collection,
            o.group_id,
            o.collection_id,
            COUNT(oa.author_id) AS author_count
        FROM objects o

        LEFT JOIN object_authors oa
            ON oa.object_id = o.pid

        WHERE
            SUBSTR(o.pid, 5) = ''
            OR SUBSTR(o.pid, 5) GLOB '*[^0-9]*'

        GROUP BY
            o.pid,
            o.title,
            o.source_collection,
            o.group_id,
            o.collection_id

        ORDER BY
            o.source_collection,
            o.pid
        """
    ).fetchall()


def write_audit(
    rows,
    output_csv,
):

    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as fh:

        writer = csv.writer(fh)

        writer.writerow([
            "pid",
            "title",
            "source_collection",
            "group_id",
            "collection_id",
            "author_count",
        ])

        writer.writerows(rows)


def main():

    args = parse_args()

    db_path = os.path.abspath(
        args.database
    )

    run_dir = os.path.dirname(
        db_path
    )

    audits_dir = os.path.join(
        run_dir,
        "audits",
    )

    os.makedirs(
        audits_dir,
        exist_ok=True,
    )

    output_csv = os.path.join(
        audits_dir,
        "structural_objects.csv",
    )

    conn = sqlite3.connect(
        db_path
    )

    try:

        rows = get_structural_objects(
            conn
        )

        structural_count = len(rows)

        author_count = sum(
            row[5]
            for row in rows
        )

        structural_with_authors = sum(
            1
            for row in rows
            if row[5] > 0
        )

        write_audit(
            rows,
            output_csv,
        )

        print()
        print("STRUCTURAL OBJECT AUDIT")
        print("-----------------------")

        print(
            f"Structural objects: "
            f"{structural_count:,}"
        )

        print(
            f"Structural objects with authors: "
            f"{structural_with_authors:,}"
        )

        print(
            f"Author links on structural objects: "
            f"{author_count:,}"
        )

        print()
        print(
            f"Audit written to: "
            f"{output_csv}"
        )

    finally:

        conn.close()


if __name__ == "__main__":

    main()