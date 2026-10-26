#!/usr/bin/env python3

import csv
import sqlite3
from collections import defaultdict

DB = "/data/figshare_migration/figshare.db"

CLASSIFICATION_CSV = "/data/duplicate_title_classification.csv"
DUPLICATES_CSV = "/data/duplicate_titles_2026-10-12.csv"

OUTPUT = "/data/duplicate_title_review_v2.csv"


def load_unknown_titles():

    titles = set()

    with open(CLASSIFICATION_CSV, newline="", encoding="utf-8-sig") as fh:

        for row in csv.DictReader(fh):

            if row["classification"] == "UNKNOWN":
                titles.add(row["title"])

    return titles


def load_duplicate_groups(unknown_titles):

    groups = defaultdict(list)

    with open(DUPLICATES_CSV, newline="", encoding="utf-8-sig") as fh:

        reader = csv.DictReader(fh)

        for row in reader:

            title = row["title"].strip()

            if title not in unknown_titles:
                continue

            groups[title].append(
                row["pid"].strip()
            )

    return groups


def fetch_metadata(conn, pids):

    placeholders = ",".join(
        "?" for _ in pids
    )

    rows = conn.execute(
        f"""
        SELECT
            pid,
            item_type,
            title,
            description,
            identifier,
            purl,
            publication_date,
            source_collection
        FROM objects
        WHERE pid IN ({placeholders})
        """,
        pids,
    ).fetchall()

    result = {}

    for row in rows:

        result[row[0]] = {
            "item_type": row[1],
            "title": row[2],
            "description": row[3] or "",
            "identifier": row[4] or "",
            "purl": row[5] or "",
            "publication_date": row[6] or "",
            "source_collection": row[7] or "",
        }

    return result


def classify_group(title, pids, metadata):

    descriptions = set()
    identifiers = set()
    purls = set()
    collections = set()
    item_types = set()

    for pid in pids:

        if pid not in metadata:
            continue

        row = metadata[pid]

        descriptions.add(
            row["description"].strip()
        )

        item_types.add(
            row["item_type"]
        )

        collections.add(
            row["source_collection"]
        )

        if row["identifier"]:
            identifiers.add(
                row["identifier"]
            )

        if row["purl"]:
            purls.add(
                row["purl"]
            )

    #
    # Same DOI / identifier.
    #

    if len(identifiers) == 1 and identifiers:
        return "SAME_IDENTIFIER"

    #
    # Same PURL.
    #

    if len(purls) == 1 and purls:
        return "SAME_PURL"

    #
    # Same description,
    # different collections.
    #

    if (
        len(descriptions) == 1
        and descriptions != {""}
        and len(collections) > 1
    ):
        return "SAME_DESCRIPTION_CROSS_COLLECTION"

    #
    # Same description.
    #

    if (
        len(descriptions) == 1
        and descriptions != {""}
    ):
        return "SAME_DESCRIPTION"

    #
    # Different item types.
    #

    if len(item_types) > 1:
        return "MULTI_ITEM_TYPE"

    #
    # Patent-style naming.
    #

    patent_words = (
        "patent",
        "method",
        "composition",
        "apparatus",
        "system",
    )

    lowered = title.lower()

    if any(word in lowered for word in patent_words):
        return "PATENT_FAMILY"

    #
    # Same title but different source collections.
    #

    if len(collections) > 1:
        return "LIKELY_CROSS_COLLECTION_DUPLICATE"

    return "UNKNOWN"


def main():

    unknown_titles = load_unknown_titles()

    groups = load_duplicate_groups(
        unknown_titles
    )

    all_pids = sorted(
        {
            pid
            for pids in groups.values()
            for pid in pids
        }
    )

    conn = sqlite3.connect(DB)

    try:

        metadata = fetch_metadata(
            conn,
            all_pids,
        )

    finally:

        conn.close()

    stats = defaultdict(int)

    with open(
        OUTPUT,
        "w",
        newline="",
        encoding="utf-8",
    ) as fh:

        writer = csv.writer(fh)

        writer.writerow([
            "classification",
            "title",
            "record_count",
            "pids",
        ])

        for title, pids in sorted(
            groups.items()
        ):

            classification = classify_group(
                title,
                pids,
                metadata,
            )

            stats[classification] += 1

            writer.writerow([
                classification,
                title,
                len(pids),
                "|".join(sorted(pids)),
            ])

    print()
    print("UNKNOWN DUPLICATE TITLE RECLASSIFICATION")
    print("----------------------------------------")

    for key in sorted(stats):
        print(
            f"{key:35} "
            f"{stats,}"
        )

    print()
    print(f"Wrote: {OUTPUT}")


if __name__ == "__main__":
    main()