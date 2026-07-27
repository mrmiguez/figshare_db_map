#!/usr/bin/env python3

from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).resolve()

count = 0

for path in root.rglob("*"):

    if not path.is_file():
        continue

    name = path.name.upper()

    if "_PDF" not in name and "_OBJ" not in name:
        continue

    target = root / path.name

    if target == path:
        continue

    print(f"{path} -> {target}")

    shutil.move(
        str(path),
        str(target)
    )

    count += 1

print(f"\nMoved {count} files")