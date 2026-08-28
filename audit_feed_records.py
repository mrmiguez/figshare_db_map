#!/usr/bin/env python3

import sqlite3
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict

NS = {
    "mods": "http://www.loc.gov/mods/v3"
}

DB = "/home/mmiguez/bin/figshare_migration/figshare_records.sqlite3"
ROOT = "/home/mmiguez/Downloads/root/fsu_research_repository/"

#
# Classify feed records
#

feed_pids = defaultdict(set)

for f in Path(ROOT).rglob("*_MODS.xml"):

    try:
        tree = ET.parse(f)
        root = tree.getroot()

        iid = root.find(
            ".//mods:identifier[@type='IID']",
            NS
        )

        if iid is None:
            continue

        iid_text = (iid.text or "").strip()

        pid = (
            f.stem
            .replace("fsu_", "fsu:")
            .removesuffix("_MODS")
        )

        #
        # Web of Science
        #

        if iid_text.startswith(
                "FSU_libsubv1_wos_"):

            feed_pids["WOS"].add(pid)
            continue

        #
        # PubMed Central harvest
        #

        if iid_text.startswith(
                "FSU_pmch_"):

            feed_pids["PMCH"].add(pid)
            continue

    except Exception as e:

        print(
            f"ERROR: {f}: {e}"
        )

#
# Report feed counts
#

print()
print("Feed records identified")
print("----------------------")

for feed, pids in sorted(
        feed_pids.items()):

    print(
        f"{feed:8s}: "
        f"{len(pids):,}"
    )

#
# Query DB
#

conn = sqlite3.connect(DB)

author_counts = {}

for pid, count in conn.execute("""
    SELECT
        o.pid,
        COUNT(oa.author_id)
    FROM objects o
    LEFT JOIN object_authors oa
        ON o.pid = oa.object_id
    GROUP BY o.pid
"""):

    author_counts[pid] = count

#
# Per-feed stats
#

for feed, pids in sorted(
        feed_pids.items()):

    counts = [
        author_counts.get(pid, 0)
        for pid in pids
    ]

    if not counts:
        continue

    print()
    print(
        f"{feed} statistics"
    )
    print(
        "-" * (
            len(feed) + 11
        )
    )

    print(
        f"Records: "
        f"{len(counts):,}"
    )

    print(
        f"Min authors: "
        f"{min(counts):,}"
    )

    print(
        f"Avg authors: "
        f"{sum(counts)/len(counts):.2f}"
    )

    print(
        f"Max authors: "
        f"{max(counts):,}"
    )

    print()
    print(
        f"Top {feed} author counts"
    )
    print(
        "-" * (
            len(feed) + 18
        )
    )

    for pid, count in sorted(
            (
                (
                    pid,
                    author_counts.get(
                        pid,
                        0
                    )
                )
                for pid in pids
            ),
            key=lambda x: x[1],
            reverse=True
    )[:20]:

        print(
            f"{count:4d}  {pid}"
        )

#
# Non-feed records
#

all_feed_pids = set()

for pids in feed_pids.values():
    all_feed_pids.update(pids)

non_feed_counts = [
    count
    for pid, count
    in author_counts.items()
    if pid not in all_feed_pids
]

max_non_feed = max(
    non_feed_counts
)

print()
print(
    "Non-feed statistics"
)
print(
    "-------------------"
)

print(
    f"Records: "
    f"{len(non_feed_counts):,}"
)

print(
    f"Max authors: "
    f"{max_non_feed:,}"
)

print()
print(
    "Largest non-feed records"
)
print(
    "------------------------"
)

for pid, count in author_counts.items():

    if pid in all_feed_pids:
        continue

    if count != max_non_feed:
        continue

    row = conn.execute(
        """
        SELECT
            pid,
            title,
            source_collection
        FROM objects
        WHERE pid = ?
        """,
        (pid,)
    ).fetchone()

    print()
    print(
        f"PID: {row[0]}"
    )

    print(
        f"Authors: {count:,}"
    )

    print(
        f"Title: {row[1]}"
    )

    print(
        f"Collection: {row[2]}"
    )

conn.close()