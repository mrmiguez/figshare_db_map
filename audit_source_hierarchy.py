#!/usr/bin/env python3

import argparse
import csv
import hashlib
import os
import re
import sqlite3
import sys
from collections import defaultdict
from xml.etree import ElementTree

import boto3


FEDORA_REL_NS = (
    "info:fedora/fedora-system:def/relations-external#"
)

FEDORA_MODEL_NS = (
    "info:fedora/fedora-system:def/model#"
)

RDF_NS = (
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
)

IS_MEMBER_OF_COLLECTION = (
    f"{{{FEDORA_REL_NS}}}isMemberOfCollection"
)

HAS_MODEL = (
    f"{{{FEDORA_MODEL_NS}}}hasModel"
)

RDF_RESOURCE = (
    f"{{{RDF_NS}}}resource"
)

COLLECTION_MODEL = (
    "info:fedora/islandora:collectionCModel"
)

PID_RE = re.compile(
    r"(fsu_.+)_RELS-EXT\.rdf$"
)


def require_env(name):
    value = os.environ.get(name)

    if not value:
        print(
            f"ERROR: environment variable {name} is not set",
            file=sys.stderr,
        )
        sys.exit(1)

    return value


def storage_pid_to_pid(value):
    """
    Convert the storage representation to a Fedora PID.

        fsu_1039415 -> fsu:1039415
        fsu_cetamura -> fsu:cetamura
    """
    if not value.startswith("fsu_"):
        return value

    return "fsu:" + value[4:]


def fedora_resource_to_pid(value):
    """
    Convert:

        info:fedora/fsu:1039415

    to:

        fsu:1039415
    """
    if not value:
        return None

    prefix = "info:fedora/"

    if value.startswith(prefix):
        return value[len(prefix):]

    return value


class SourceHierarchy:
    def __init__(self, bucket, prefix=""):
        self.bucket = bucket
        self.prefix = prefix
        self.s3 = boto3.client("s3")

        # PID -> list of physical RELS-EXT keys
        self.rels_keys = defaultdict(list)

        # PID -> parsed relationship information
        self.relationships = {}

        # PID -> resolved ancestor chain
        self.hierarchy_cache = {}

    def build_index(self):
        """
        List SRCBUCK once and index RELS-EXT objects by Fedora PID.
        """
        paginator = self.s3.get_paginator(
            "list_objects_v2"
        )

        for page in paginator.paginate(
            Bucket=self.bucket,
            Prefix=self.prefix,
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]

                if not key.endswith(
                    "_RELS-EXT.rdf"
                ):
                    continue

                basename = key.rsplit("/", 1)[-1]

                match = PID_RE.match(
                    basename
                )

                if not match:
                    continue

                pid = storage_pid_to_pid(
                    match.group(1)
                )

                self.rels_keys[pid].append(
                    key
                )

    def get_rels_bytes(self, key):
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=key,
        )

        return response["Body"].read()

    def parse_rels(self, pid):
        """
        Parse one canonical RELS-EXT representation for PID.

        Physical duplicates are not interpreted as separate Fedora
        objects.
        """
        if pid in self.relationships:
            return self.relationships[pid]

        keys = self.rels_keys.get(
            pid,
            [],
        )

        if not keys:
            result = {
                "pid": pid,
                "parent": None,
                "is_collection": False,
                "key": None,
                "copies": 0,
            }

            self.relationships[pid] = result
            return result

        key = sorted(keys)[0]
        data = self.get_rels_bytes(key)

        root = ElementTree.fromstring(
            data
        )

        parent = None
        is_collection = False

        for element in root.iter():

            if element.tag == IS_MEMBER_OF_COLLECTION:

                parent = fedora_resource_to_pid(
                    element.get(
                        RDF_RESOURCE
                    )
                )

            elif element.tag == HAS_MODEL:

                model = element.get(
                    RDF_RESOURCE
                )

                if model == COLLECTION_MODEL:
                    is_collection = True

        result = {
            "pid": pid,
            "parent": parent,
            "is_collection": is_collection,
            "key": key,
            "copies": len(keys),
        }

        self.relationships[pid] = result

        return result

    def resolve(self, pid, max_depth=100):
        """
        Resolve collection ancestry from PID upward.

        Returned list is rootward -> leafward, excluding the object
        PID itself unless that PID is a collection.
        """
        if pid in self.hierarchy_cache:
            return list(
                self.hierarchy_cache[pid]
            )

        original_pid = pid
        chain = []
        seen = set()

        current = pid

        for _ in range(max_depth):

            if current in seen:
                raise RuntimeError(
                    "Collection hierarchy cycle detected: "
                    + " -> ".join(
                        [*chain, current]
                    )
                )

            seen.add(current)

            rels = self.parse_rels(
                current
            )

            if (
                current != original_pid
                and rels["is_collection"]
            ):
                chain.append(
                    current
                )

            parent = rels["parent"]

            if not parent:
                break

            current = parent

        else:
            raise RuntimeError(
                f"Maximum hierarchy depth exceeded for {original_pid}"
            )

        chain.reverse()

        self.hierarchy_cache[original_pid] = tuple(
            chain
        )

        return chain

    def verify_duplicate_rels(self, pid):
        """
        SHA-256 all physical RELS-EXT copies for PID.

        Returns:
            hash -> [keys]
        """
        hashes = defaultdict(list)

        for key in self.rels_keys.get(pid, []):

            data = self.get_rels_bytes(
                key
            )

            digest = hashlib.sha256(
                data
            ).hexdigest()

            hashes[digest].append(
                key
            )

        return dict(hashes)


def print_pid(resolver, pid, verify=False):
    rels = resolver.parse_rels(
        pid
    )

    hierarchy = resolver.resolve(
        pid
    )

    print()
    print("=" * 78)
    print(f"PID: {pid}")
    print("=" * 78)

    print(
        f"RELS-EXT copies: {rels['copies']}"
    )

    print(
        "Direct parent: "
        + (
            rels["parent"]
            if rels["parent"]
            else "[none]"
        )
    )

    print(
        "Object is collection: "
        + (
            "YES"
            if rels["is_collection"]
            else "NO"
        )
    )

    print()

    print("COLLECTION HIERARCHY")

    if not hierarchy:
        print("  [none]")
    else:
        for depth, ancestor in enumerate(
            hierarchy
        ):
            print(
                f"  {'  ' * depth}{ancestor}"
            )

    if verify:
        print()
        print("DUPLICATE RELS-EXT CHECK")

        hashes = resolver.verify_duplicate_rels(
            pid
        )

        print(
            f"  Physical copies: {rels['copies']}"
        )

        print(
            f"  Distinct contents: {len(hashes)}"
        )

        for digest, keys in hashes.items():

            print(
                f"  {digest}  ({len(keys)} copies)"
            )

            for key in keys:
                print(
                    f"    s3://{resolver.bucket}/{key}"
                )

def get_object_pids(db_path):
    """
    Return every surviving object PID from the migration database.
    """
    con = sqlite3.connect(db_path)

    try:
        rows = con.execute(
            """
            SELECT pid
            FROM objects
            ORDER BY pid
            """
        ).fetchall()
    finally:
        con.close()

    return [row[0] for row in rows]

def export_hierarchies(resolver, db_path, output_path):
    """
    Resolve Fedora collection ancestry for every surviving objects.pid
    and write one CSV row per object.

    Hierarchy is stored rootward -> leafward using "|" as the
    delimiter.
    """
    pids = get_object_pids(db_path)

    fieldnames = [
        "pid",
        "direct_collection_pid",
        "collection_hierarchy",
        "hierarchy_depth",
        "rels_ext_copies",
        "status",
        "error",
    ]

    resolved_count = 0
    no_parent_count = 0
    error_count = 0

    os.makedirs(
        os.path.dirname(os.path.abspath(output_path)),
        exist_ok=True,
    )

    with open(
            output_path,
            "w",
            encoding="utf-8",
            newline="",
    ) as fh:

        writer = csv.DictWriter(
            fh,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for position, pid in enumerate(
                pids,
                start=1,
        ):

            try:
                rels = resolver.parse_rels(pid)
                hierarchy = resolver.resolve(pid)

                if rels["parent"]:
                    status = "RESOLVED"
                    resolved_count += 1
                else:
                    status = "NO_COLLECTION_PARENT"
                    no_parent_count += 1

                writer.writerow(
                    {
                        "pid": pid,
                        "direct_collection_pid": (
                                rels["parent"] or ""
                        ),
                        "collection_hierarchy": "|".join(
                            hierarchy
                        ),
                        "hierarchy_depth": len(
                            hierarchy
                        ),
                        "rels_ext_copies": rels["copies"],
                        "status": status,
                        "error": "",
                    }
                )

            except Exception as exc:
                error_count += 1

                writer.writerow(
                    {
                        "pid": pid,
                        "direct_collection_pid": "",
                        "collection_hierarchy": "",
                        "hierarchy_depth": "",
                        "rels_ext_copies": len(
                            resolver.rels_keys.get(
                                pid,
                                [],
                            )
                        ),
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

            if (
                    position % 1000 == 0
                    or position == len(pids)
            ):
                print(
                    f"Resolved {position:,}/{len(pids):,} objects",
                    file=sys.stderr,
                )

    print(
        f"Wrote: {output_path}",
        file=sys.stderr,
    )

    print(
        f"Objects: {len(pids):,}",
        file=sys.stderr,
    )

    print(
        f"Resolved: {resolved_count:,}",
        file=sys.stderr,
    )

    print(
        f"No collection parent: {no_parent_count:,}",
        file=sys.stderr,
    )

    print(
        f"Errors: {error_count:,}",
        file=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Resolve Fedora collection hierarchy from "
            "RELS-EXT relationships in SRCBUCK."
        )
    )

    parser.add_argument(
        "pids",
        nargs="*",
        help=(
            "Fedora PID(s), e.g. fsu:1039415"
        ),
    )

    parser.add_argument(
        "--verify-duplicates",
        action="store_true",
        help=(
            "SHA-256 all physical RELS-EXT copies for each PID."
        ),
    )

    parser.add_argument(
        "--prefix",
        default="",
        help=(
            "Optional S3 prefix to restrict indexing."
        ),
    )

    parser.add_argument(
        "--export",
        metavar="CSV",
        help=(
            "Export resolved Fedora collection hierarchy "
            "for every surviving objects.pid in $DB."
        ),
    )

    args = parser.parse_args()

    bucket = require_env(
        "SRCBUCK"
    )

    resolver = SourceHierarchy(
        bucket=bucket,
        prefix=args.prefix,
    )

    print(
        f"Indexing RELS-EXT objects in s3://{bucket}/...",
        file=sys.stderr,
    )

    resolver.build_index()

    print(
        f"Indexed {len(resolver.rels_keys):,} Fedora PIDs",
        file=sys.stderr,
    )

    if args.export:
        db_path = require_env(
            "DB"
        )

        export_hierarchies(
            resolver,
            db_path,
            args.export,
        )

    for pid in args.pids:
        print_pid(
            resolver,
            pid,
            verify=args.verify_duplicates,
        )

    if not args.export and not args.pids:
        parser.error(
            "provide one or more PIDs or use --export CSV"
        )


if __name__ == "__main__":
    main()