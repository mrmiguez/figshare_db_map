#!/usr/bin/env python3

import csv
import os
import re
from pathlib import Path

ROOT = Path("/data/tmp/mods-audit")

PID_DIR_RE = re.compile(r"fsu_(\d+)$")

#
# Build:
#
#   child_pid -> parent_pid
#
# from the directory tree.
#
child_to_parent = {}

for mods_file in ROOT.rglob("*_MODS.xml"):

    filename = mods_file.name

    if not filename.startswith("fsu_"):
        continue

    child_pid = (
        filename
        .replace("_MODS.xml", "")
        .replace("fsu_", "fsu:")
    )

    parent_name = mods_file.parent.name

    match = PID_DIR_RE.fullmatch(parent_name)

    if not match:
        continue

    parent_pid = f"fsu:{match.group(1)}"

    child_to_parent[child_pid] = parent_pid

#
# Write parent/child inventory.
#
with open(
    "compound_object_relationships.csv",
    "w",
    newline="",
    encoding="utf-8"
) as fh:

    writer = csv.writer(fh)

    writer.writerow([
        "child_pid",
        "parent_pid",
    ])

    for child_pid, parent_pid in sorted(
        child_to_parent.items()
    ):
        writer.writerow([
            child_pid,
            parent_pid,
        ])

print(
    f"Identified "
    f"{len(child_to_parent):,} "
    f"compound child objects."
)