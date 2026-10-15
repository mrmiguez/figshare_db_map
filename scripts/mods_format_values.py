#!/usr/bin/env python3

from collections import Counter
from pathlib import Path
from lxml import etree

ROOT = Path("/home/mmiguez/Downloads/root/fsu_research_repository")

NS = {
    "mods": "http://www.loc.gov/mods/v3"
}

queries = {
    "physicalDescription/form": ".//mods:physicalDescription/mods:form",
    "genre": ".//mods:genre",
    "typeOfResource": ".//mods:typeOfResource",
}

counts = {
    name: Counter()
    for name in queries
}

files = list(ROOT.rglob("*_MODS.xml"))

for path in files:

    try:
        tree = etree.parse(str(path))

        for name, xpath in queries.items():

            for elem in tree.xpath(xpath, namespaces=NS):

                value = (elem.text or "").strip()

                if value:
                    counts[name][value] += 1

    except Exception as e:
        print(f"ERROR: {path}: {e}")


print(f"\nMODS files scanned: {len(files):,}")

for name, counter in counts.items():

    print()
    print(name)
    print("-" * len(name))

    for value, count in sorted(
        counter.items(),
        key=lambda x: (-x[1], x[0].lower())
    ):
        print(f"{count:8,}  {value}")
