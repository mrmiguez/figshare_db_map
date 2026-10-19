#!/usr/bin/env python3

import argparse
import csv
import os
import sqlite3


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Audit Fedora collection objects that should "
            "not be migrated to Figshare as items."
        )
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    parser.add_argument(
        "collection_pids",
        help=(
            "Text file containing Fedora collectionCModel "
            "PIDs, one PID per line"
        ),
    )

    return parser.parse_args()


def load_collection_pids(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as fh:
        pids = sorted({
            line.strip()
            for line in fh
            if line.strip()
        })

    if not pids:
        raise RuntimeError(
            f"No Fedora collection PIDs found in {path}"
        )

    return pids


def get_structural_objects(conn, collection_pids):
    placeholders = ",".join(
        "?" for _ in collection_pids
    )

    return conn.execute(
        f"""
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

        WHERE o.pid IN ({placeholders})

        GROUP BY
            o.pid,
            o.title,
            o.source_collection,
            o.group_id,
            o.collection_id

        ORDER BY
            o.source_collection,
            o.pid
        """,
        collection_pids,
    ).fetchall()


def write_audit(rows, output_csv):
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

    collection_pids_path = os.path.abspath(
        args.collection_pids
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

    collection_pids = load_collection_pids(
        collection_pids_path
    )

    conn = sqlite3.connect(
        db_path
    )

    try:
        rows = get_structural_objects(
            conn,
            collection_pids,
        )

        structural_count = len(rows)

        author_links = sum(
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
            f"Fedora collectionCModel PIDs: "
            f"{len(collection_pids):,}"
        )

        print(
            f"Collection objects present in DB: "
            f"{structural_count:,}"
        )

        print(
            f"Collection objects with authors: "
            f"{structural_with_authors:,}"
        )

        print(
            f"Author links on collection objects: "
            f"{author_links:,}"
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