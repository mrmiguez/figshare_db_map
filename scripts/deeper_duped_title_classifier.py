#!/usr/bin/env python3

import csv
import sqlite3
from collections import defaultdict

DB = "/data/figshare_migration/figshare.db"

DUPLICATES = "/data/duplicate_titles_2026-10-12.csv"
COMPOUND = "/data/duplicate_title_classification.csv"

OUTPUT = "/data/duplicate_title_review.csv"


def load_compound_groups():

    compound = {}

    with open(COMPOUND, newline="", encoding="utf-8-sig") as fh:

        reader = csv.DictReader(fh)

        for row in reader:
            compound[row["title"]] = row["classification"]

    return compound


def load_duplicate_groups():

    groups = defaultdict(list)

    with open(DUPLICATES, newline="", encoding="utf-8-sig") as fh:

        reader = csv.DictReader(fh)

        for row in reader:
            groups[row["title"]].append(row["pid"])

    return groups


def get_metadata(conn, pids):

    placeholders = ",".join("?" for _ in pids)

    rows = conn.execute(
        f"""
        SELECT
            pid,
            title,
            item_type,
            description,
            source_collection
        FROM objects
        WHERE pid IN ({placeholders})
        """,
        pids,
    ).fetchall()

    result = {}

    for pid, title, item_type, description, source_collection in rows:

        result[pid] = {
            "title": title,
            "item_type": item_type,
            "description": description,
            "source_collection": source_collection,
        }

    return result


def classify_group(title, pids, metadata, compound_lookup):

    compound_class = compound_lookup.get(title)

    if compound_class == "COMPOUND_OBJECT":
        return "COMPOUND_OBJECT"

    if compound_class == "MIXED_COMPOUND_GROUP":
        return "MIXED_COMPOUND_GROUP"

    item_types = {
        metadata[pid]["item_type"]
        for pid in pids
        if pid in metadata
    }

    descriptions = {
        metadata[pid]["description"]
        for pid in pids
        if pid in metadata
    }

    collections = {
        metadata[pid]["source_collection"]
        for pid in pids
        if pid in metadata
    }

    #
    # Patent.
    #

    if "patent" in title.lower():
        return "PATENT_FAMILY"

    #
    # Field note naming pattern.
    #

    if title.lower().startswith(
        (
            "january ",
            "february ",
            "march ",
            "april ",
            "may ",
            "june ",
            "july ",
            "august ",
            "september ",
            "october ",
            "november ",
            "december ",
        )
    ):
        return "FIELD_NOTE"

    #
    # Exact same description
    # across multiple collections.
    #

    if (
        len(descriptions) == 1
        and len(collections) > 1
    ):
        return "CROSS_COLLECTION_DUPLICATE"

    #
    # Same title represented in
    # multiple formats.
    #

    if len(item_types) > 1:
        return "MULTI_FORMAT"

    return "UNKNOWN"


def main():

    conn = sqlite3.connect(DB)

    try:

        compound_lookup = load_compound_groups()
        groups = load_duplicate_groups()

        all_pids = []

        for pids in groups.values():
            all_pids.extend(pids)

        metadata = get_metadata(
            conn,
            sorted(set(all_pids))
        )

    finally:
        conn.close()

    counts = defaultdict(int)

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

        for title, pids in sorted(groups.items()):

            classification = classify_group(
                title,
                pids,
                metadata,
                compound_lookup,
            )

            counts[classification] += 1

            writer.writerow([
                classification,
                title,
                len(pids),
                "|".join(sorted(pids)),
            ])

    print()
    print("DUPLICATE TITLE CLASSIFICATION")
    print("------------------------------")

    for key in sorted(counts):
        print(
            f"{key:25} "
            f"{counts[key]:,}"
        )

    print()
    print(f"Wrote: {OUTPUT}")


if __name__ == "__main__":
    main()