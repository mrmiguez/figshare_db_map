#!/usr/bin/env python3

import csv
from collections import defaultdict

RELATIONSHIPS = "/data/compound_object_relationships.csv"
DUPLICATES = "/data/duplicate_titles_2026-10-12.csv"
OUTPUT = "/data/duplicate_title_classification.csv"


#
# Build parent/child lookup
#

parent_to_children = defaultdict(set)
child_to_parent = {}

with open(RELATIONSHIPS, newline="", encoding="utf-8") as fh:

    for row in csv.DictReader(fh):

        child = row["child_pid"].strip()
        parent = row["parent_pid"].strip()

        child_to_parent[child] = parent
        parent_to_children[parent].add(child)

#
# Group duplicate-title report
#

groups = defaultdict(list)

with open(DUPLICATES, newline="", encoding="utf-8-sig") as fh:

    reader = csv.DictReader(fh)

    #
    # Try to find the title column automatically.
    #

    title_col = None

    for field in reader.fieldnames:
        if field.lower() == "title":
            title_col = field
            break

    if not title_col:
        raise RuntimeError(
            f"Could not find title column in {reader.fieldnames}"
        )

    pid_col = None

    for field in reader.fieldnames:
        if field.lower() == "pid":
            pid_col = field
            break

    if not pid_col:
        raise RuntimeError(
            f"Could not find pid column in {reader.fieldnames}"
        )

    for row in reader:

        title = row[title_col].strip()
        pid = row[pid_col].strip()

        groups[title].append(pid)

#
# Classify
#

with open(
    OUTPUT,
    "w",
    newline="",
    encoding="utf-8"
) as fh:

    writer = csv.writer(fh)

    writer.writerow([
        "title",
        "classification",
        "record_count",
        "parent_count",
        "child_count",
        "pids",
    ])

    compound_groups = 0
    mixed_groups = 0
    non_compound_groups = 0

    for title, pids in sorted(groups.items()):

        pid_set = set(pids)

        parent_hits = set()
        child_hits = set()

        #
        # Detect direct parent/child relationship
        # within this title group.
        #

        for pid in pid_set:

            if pid in child_to_parent:

                parent = child_to_parent[pid]

                if parent in pid_set:
                    parent_hits.add(parent)
                    child_hits.add(pid)

        if parent_hits and len(child_hits) == len(pid_set) - len(parent_hits):

            classification = "COMPOUND_OBJECT"
            compound_groups += 1

        elif parent_hits or child_hits:

            classification = "MIXED_COMPOUND_GROUP"
            mixed_groups += 1

        else:

            classification = "NON_COMPOUND"
            non_compound_groups += 1

        writer.writerow([
            title,
            classification,
            len(pid_set),
            len(parent_hits),
            len(child_hits),
            "|".join(sorted(pid_set)),
        ])

print()
print("DUPLICATE TITLE CLASSIFICATION")
print("------------------------------")
print(f"Total groups:          {len(groups):,}")
print(f"Compound groups:       {compound_groups:,}")
print(f"Mixed compound groups: {mixed_groups:,}")
print(f"Non-compound groups:   {non_compound_groups:,}")
print()
print(f"Wrote: {OUTPUT}")