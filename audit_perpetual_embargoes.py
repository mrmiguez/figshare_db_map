#!/usr/bin/env python3

import csv
import sqlite3
import sys
from pathlib import Path


def get_perpetual_embargoes(conn):

    return conn.execute(
        """
        SELECT
            e.object_id AS pid,
            o.title,
            o.source_collection,
            e.target,
            e.embargo_value,
            e.embargo_class,
            o.embargo_type,
            o.embargo_date,
            o.embargo_reason
        FROM embargoes e
        JOIN objects o
            ON o.pid = e.object_id
        WHERE e.embargo_class = 'article'
          AND LOWER(e.embargo_value) = 'indefinite'
        ORDER BY e.object_id
        """
    ).fetchall()


def audit_perpetual_embargoes(db_path):

    db_path = Path(db_path)
    run_dir = db_path.parent

    audit_dir = run_dir / "audits"
    audit_dir.mkdir(exist_ok=True)

    output_path = (
        audit_dir /
        "perpetual_article_embargoes.csv"
    )

    conn = sqlite3.connect(
        f"file:{db_path}?mode=ro",
        uri=True,
    )

    conn.row_factory = sqlite3.Row

    rows = get_perpetual_embargoes(conn)

    fieldnames = [
        "pid",
        "title",
        "source_collection",
        "target",
        "embargo_value",
        "embargo_class",
        "embargo_type",
        "embargo_date",
        "embargo_reason",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as fh:

        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(dict(row))

    projection_mismatches = []

    for row in rows:

        if (
            row["embargo_type"] != "article"
            or row["embargo_date"] is not None
            or row["embargo_reason"]
            != "perpetual article embargo"
        ):
            projection_mismatches.append(
                row["pid"]
            )

    conn.close()

    print()
    print("PERPETUAL ARTICLE EMBARGO AUDIT")
    print("--------------------------------")
    print(
        f"Exclusion candidates: "
        f"{len(rows):,}"
    )
    print(
        f"Projection mismatches: "
        f"{len(projection_mismatches):,}"
    )

    if projection_mismatches:

        print()
        print("Projection mismatch PIDs:")

        for pid in projection_mismatches:
            print(f"  {pid}")

    print()
    print(f"Audit written to: {output_path}")


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            f"Usage: {sys.argv[0]} DATABASE"
        )

        sys.exit(1)

    audit_perpetual_embargoes(
        sys.argv[1]
    )