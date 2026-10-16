#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict
from pathlib import Path


FILE_EMBARGO_TYPES = {
    "PDF datastream",
    "OBJ datastream",
    "FULL_TEXT datastream",
    "MP4 datastream",
    "PREVIEW datastream",
}

ARTICLE_EMBARGO_TYPES = {
    "object",
}

ACCESS_RESTRICTION_TYPES = {
    "IP",
}


def embargo_files(root):
    yield from Path(root).rglob("*child-embargoes.csv")


def main(root):

    records = defaultdict(list)

    for path in embargo_files(root):

        with path.open(newline="", encoding="utf-8") as fh:

            for row in csv.reader(fh):

                if len(row) < 3:
                    continue

                pid = row[0].strip()
                target = row[1].strip()
                value = row[2].strip()

                records[pid].append((target, value))

    combinations = defaultdict(list)

    for pid, embargoes in records.items():

        perpetual_file = any(
            target in FILE_EMBARGO_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        perpetual_article = any(
            target in ARTICLE_EMBARGO_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        perpetual_ip = any(
            target in ACCESS_RESTRICTION_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        key = (
            perpetual_article,
            perpetual_file,
            perpetual_ip,
        )

        combinations[key].append(pid)

    print()
    print("PERPETUAL EMBARGO COMBINATIONS")
    print("------------------------------")

    for key, pids in sorted(
        combinations.items(),
        key=lambda x: len(x[1]),
        reverse=True
    ):

        article, file_, ip = key

        print(
            f"{len(pids):6,}  "
            f"object={str(article):5}  "
            f"file={str(file_):5}  "
            f"IP={str(ip):5}"
        )

    print()
    print("INDEFINITE OBJECT + FILE")
    print("------------------------")

    matches = []

    for pid, embargoes in records.items():

        article = any(
            target in ARTICLE_EMBARGO_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        file_ = any(
            target in FILE_EMBARGO_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        if article and file_:
            matches.append((pid, embargoes))

    print(f"Records: {len(matches):,}")
    print()

    for pid, embargoes in matches[:100]:

        print(pid)

        for target, value in embargoes:
            print(f"    {target}: {value}")

    print()
    print("INDEFINITE IP + FILE")
    print("--------------------")

    matches = []

    for pid, embargoes in records.items():

        ip = any(
            target in ACCESS_RESTRICTION_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        file_ = any(
            target in FILE_EMBARGO_TYPES
            and value.casefold() == "indefinite"
            for target, value in embargoes
        )

        if ip and file_:
            matches.append((pid, embargoes))

    print(f"Records: {len(matches):,}")
    print()

    for pid, embargoes in matches[:100]:

        print(pid)

        for target, value in embargoes:
            print(f"    {target}: {value}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} REPOSITORY_ROOT")
        sys.exit(1)

    main(sys.argv[1])
