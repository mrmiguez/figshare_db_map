#!/usr/bin/env python3

import csv
import os
import sqlite3
import sys
from assets import feed_records as assets

SCRIPT_DIR = os.path.dirname(
    os.path.realpath(__file__)
)

exports_dir = os.path.join(
    SCRIPT_DIR,
    "exports"
)

def main():

    if len(sys.argv) != 2:

        print(
            f"Usage: {sys.argv[0]} <database>"
        )
        sys.exit(1)

    db_path = sys.argv[1]

    os.makedirs(exports_dir, exist_ok=True)

    output_csv = os.path.join(
        exports_dir,
        "scholarly_feed_audit.csv"
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            pid,
            title,
            publication_date,
            purl,
            other_identifiers,
            source_collection
        FROM objects
        ORDER BY pid
        """
    )

    results = []

    wos_count = 0
    pmc_count = 0

    for row in cur:

        iid = assets.extract_iid(
            row["other_identifiers"]
        )

        feed_source = assets.detect_feed(
            iid,
            row["purl"]
        )

        if not feed_source:
            continue

        if feed_source == "Web of Science":
            wos_count += 1

        if feed_source == "PubMed Central":
            pmc_count += 1

        results.append({
            "pid":
                row["pid"],
            "feed_source":
                feed_source,
            "iid":
                iid,
            "doi":
                assets.extract_doi(
                    row["other_identifiers"]
                ),
            "purl":
                row["purl"],
            "title":
                row["title"],
            "publication_date":
                row["publication_date"],
            "source_collection":
                row["source_collection"],
        })

    with open(
        output_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as fh:

        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "pid",
                "feed_source",
                "iid",
                "doi",
                "purl",
                "title",
                "publication_date",
                "source_collection",
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"Wrote {len(results):,} feed records to "
        f"{output_csv}"
    )

    print(
        f"    Web of Science : {wos_count:,}"
    )

    print(
        f"    PubMed Central : {pmc_count:,}"
    )


if __name__ == "__main__":
    main()