#!/usr/bin/env python3

import csv
from collections import Counter
from pathlib import Path

from lxml import etree


ROOT = Path("/home/mmiguez/Downloads/root/fsu_research_repository")

NS = {
    "mods": "http://www.loc.gov/mods/v3",
}


def clean(value):
    if not value:
        return None

    return " ".join(value.split())


def first_text(tree, xpath):
    values = tree.xpath(xpath, namespaces=NS)

    if not values:
        return None

    value = values[0]

    if isinstance(value, str):
        return clean(value)

    return clean(value.text)


records = []
errors = []

for path in ROOT.rglob("*_MODS.xml"):

    try:
        tree = etree.parse(str(path))
    except Exception as exc:
        errors.append((path, str(exc)))
        continue

    pid = first_text(
        tree,
        ".//mods:identifier[translate(@type, 'abcdefghijklmnopqrstuvwxyz', "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='FEDORA']/text()"
    )

    if not pid:
        pid = first_text(
            tree,
            ".//mods:identifier[@type='IID']/text()"
        )

    description_standard = first_text(
        tree,
        ".//mods:recordInfo/mods:descriptionStandard/text()"
    )

    hosts = tree.xpath(
        ".//mods:relatedItem[@type='host']",
        namespaces=NS
    )

    for host in hosts:

        titles = host.xpath(
            "./mods:titleInfo/mods:title/text()",
            namespaces=NS
        )

        locations = host.xpath(
            "./mods:location/mods:physicalLocation/text()",
            namespaces=NS
        )

        host_title = clean(titles[0]) if titles else None
        host_location = clean(locations[0]) if locations else None

        records.append({
            "pid": pid,
            "description_standard": description_standard,
            "host_title": host_title,
            "host_location": host_location,
            "path": str(path),
        })


print()
print(f"MODS host records: {len(records):,}")
print(f"Parse errors:      {len(errors):,}")

print()
print("DESCRIPTION STANDARD")
print("--------------------")

counter = Counter(
    record["description_standard"] or "[NULL]"
    for record in records
)

for value, count in counter.most_common():
    print(f"{count:8,}  {value}")


print()
print("DACS HOST TITLES")
print("----------------")

counter = Counter(
    record["host_title"] or "[NO HOST TITLE]"
    for record in records
    if (record["description_standard"] or "").casefold() == "dacs"
)

for value, count in counter.most_common():
    print(f"{count:8,}  {value}")


print()
print("NON-DACS HOST TITLES")
print("--------------------")

counter = Counter(
    record["host_title"] or "[NO HOST TITLE]"
    for record in records
    if (record["description_standard"] or "").casefold() != "dacs"
)

for value, count in counter.most_common(100):
    print(f"{count:8,}  {value}")


print()
print("DACS HOST LOCATIONS")
print("-------------------")

counter = Counter(
    record["host_location"] or "[NO HOST LOCATION]"
    for record in records
    if (record["description_standard"] or "").casefold() == "dacs"
)

for value, count in counter.most_common():
    print(f"{count:8,}  {value}")


output = Path("mods_host_analysis.csv")

with output.open("w", newline="", encoding="utf-8") as fh:

    writer = csv.DictWriter(
        fh,
        fieldnames=[
            "pid",
            "description_standard",
            "host_title",
            "host_location",
            "path",
        ]
    )

    writer.writeheader()
    writer.writerows(records)


print()
print(f"Detailed results written to: {output}")
