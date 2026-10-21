#!/usr/bin/env python3

import argparse
import csv
import os
import shutil
import sqlite3
import sys
from pathlib import Path


DEFAULT_MAPPING = "/data/figshare_db_map/assets/mappings/source_collection_mapping.csv"
DEFAULT_HIERARCHY = "/data/figshare_migration/audits/object_collection_hierarchy.csv"

EXCLUDED_COLLECTIONS = {
    "fsu:honors_ethical_issues_and_life_choices",
}


def require_env(name):
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)

    return value


def read_mapping(path):
    """
    Read hierarchy -> target group/collection assignments.

    A blank collection_hierarchy is valid when the row contains an
    explicit mapping. It provides the fallback for objects whose Fedora
    hierarchy could not be reconstructed.

    Completely empty rows are ignored.
    """
    mapping = {}

    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            hierarchy = row["collection_hierarchy"].strip()
            leaf_pid = row["leaf_collection_pid"].strip()
            group_id = row["group_id"].strip()
            collection_id = row["collection_id"].strip()
            status = row["status"].strip()

            # Ignore completely empty spreadsheet/CSV rows.
            if not any(value.strip() for value in row.values() if value is not None):
                continue

            # A blank hierarchy is valid only when it has an explicit target.
            if not hierarchy and not group_id:
                continue

            if hierarchy in mapping:
                raise RuntimeError(
                    f"Duplicate collection_hierarchy in mapping CSV: {hierarchy or '[blank]'}"
                )

            mapping[hierarchy] = {
                "leaf_pid": leaf_pid,
                "group_id": int(group_id) if group_id else None,
                "collection_id": int(collection_id) if collection_id else None,
                "status": status,
            }

    return mapping


def read_object_hierarchies(path):
    rows = []
    seen = set()

    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            pid = row["pid"].strip()

            if pid in seen:
                raise RuntimeError(f"Duplicate PID in hierarchy CSV: {pid}")

            seen.add(pid)

            rows.append({
                "pid": pid,
                "hierarchy": row["collection_hierarchy"].strip(),
            })

    return rows


def is_excluded(hierarchy):
    if not hierarchy:
        return False

    return any(component in EXCLUDED_COLLECTIONS for component in hierarchy.split("|"))


def backup_database(db_path):
    db_path = Path(db_path)
    backup_path = db_path.with_suffix(db_path.suffix + ".before_group_collection_ids")

    if backup_path.exists():
        raise RuntimeError(
            f"Backup already exists: {backup_path}\n"
            "Move or remove that backup before running the update again."
        )

    shutil.copy2(db_path, backup_path)
    return backup_path


def print_db_summary(con, label):
    total = con.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
    groups = con.execute("SELECT COUNT(*) FROM objects WHERE group_id IS NOT NULL").fetchone()[0]
    collections = con.execute("SELECT COUNT(*) FROM objects WHERE collection_id IS NOT NULL").fetchone()[0]

    print()
    print(label)
    print(f"  objects:             {total:,}")
    print(f"  group_id populated:  {groups:,}")
    print(f"  collection_id set:   {collections:,}")


def build_assignments(db_pids, object_hierarchies, mapping):
    assignments = {}
    excluded = set()
    unmapped = set()
    review = set()

    for row in object_hierarchies:
        pid = row["pid"]
        hierarchy = row["hierarchy"]

        if pid not in db_pids:
            continue

        if is_excluded(hierarchy):
            excluded.add(pid)
            continue

        target = mapping.get(hierarchy)

        if target is None:
            unmapped.add(pid)
            continue

        if target["status"] != "MAPPED":
            review.add(pid)
            continue

        if target["group_id"] is None:
            unmapped.add(pid)
            continue

        assignments[pid] = (
            target["group_id"],
            target["collection_id"],
        )

    return assignments, excluded, review, unmapped


def print_preflight(assignments, excluded, review, unmapped):
    print()
    print("PREFLIGHT")
    print(f"  assignable objects:  {len(assignments):,}")
    print(f"  excluded objects:    {len(excluded):,}")
    print(f"  review objects:      {len(review):,}")
    print(f"  unmapped objects:    {len(unmapped):,}")


def validate_preflight(db_pids, assignments, excluded, review, unmapped):
    accounted_for = set(assignments) | excluded | review | unmapped

    if accounted_for != db_pids:
        missing = db_pids - accounted_for
        raise RuntimeError(f"{len(missing):,} DB objects were not accounted for")

    if review:
        raise RuntimeError(
            f"{len(review):,} objects still belong to REVIEW mappings; refusing to update DB"
        )

    if unmapped:
        raise RuntimeError(
            f"{len(unmapped):,} objects have no mapped group_id; refusing to update DB"
        )

    expected_survivors = len(db_pids) - len(excluded)

    if len(assignments) != expected_survivors:
        raise RuntimeError(
            "Assignment count does not match expected surviving population: "
            f"{len(assignments):,} assignments vs. {expected_survivors:,} expected"
        )


def apply_exclusions(con, excluded):
    deleted = 0

    for pid in sorted(excluded):
        cursor = con.execute("DELETE FROM objects WHERE pid = ?", (pid,))
        deleted += cursor.rowcount

    if deleted != len(excluded):
        raise RuntimeError(
            f"Expected to delete {len(excluded):,} excluded objects but deleted {deleted:,}"
        )

    return deleted


def apply_assignments(con, assignments):
    con.execute("""
        UPDATE objects
        SET group_id = NULL,
            collection_id = NULL
    """)

    updated = 0

    for pid, (group_id, collection_id) in assignments.items():
        cursor = con.execute(
            """
            UPDATE objects
            SET group_id = ?,
                collection_id = ?
            WHERE pid = ?
            """,
            (group_id, collection_id, pid),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                f"Expected exactly one objects row for {pid}; updated {cursor.rowcount}"
            )

        updated += cursor.rowcount

    return updated


def validate_database(con, expected_objects):
    total = con.execute("SELECT COUNT(*) FROM objects").fetchone()[0]

    if total != expected_objects:
        raise RuntimeError(
            f"Expected {expected_objects:,} surviving objects after exclusions; found {total:,}"
        )

    null_groups = con.execute("""
        SELECT COUNT(*)
        FROM objects
        WHERE group_id IS NULL
    """).fetchone()[0]

    if null_groups:
        raise RuntimeError(f"{null_groups:,} surviving objects still have NULL group_id")

    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]

    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {integrity}")

    fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()

    if fk_errors:
        raise RuntimeError(f"SQLite foreign_key_check returned {len(fk_errors):,} errors")

    return integrity


def update_database(db_path, mapping_path, hierarchy_path, dry_run=False):
    mapping = read_mapping(mapping_path)
    object_hierarchies = read_object_hierarchies(hierarchy_path)

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")

    try:
        print(f"DB:        {db_path}")
        print(f"Mapping:   {mapping_path}")
        print(f"Hierarchy: {hierarchy_path}")

        print_db_summary(con, "BEFORE")

        db_pids = {row[0] for row in con.execute("SELECT pid FROM objects")}
        hierarchy_pids = {row["pid"] for row in object_hierarchies}

        missing_from_hierarchy = db_pids - hierarchy_pids
        extra_in_hierarchy = hierarchy_pids - db_pids

        if missing_from_hierarchy:
            raise RuntimeError(
                f"{len(missing_from_hierarchy):,} DB objects are missing from the hierarchy CSV"
            )

        if extra_in_hierarchy:
            print(
                f"WARNING: {len(extra_in_hierarchy):,} hierarchy rows are not present in objects",
                file=sys.stderr,
            )

        assignments, excluded, review, unmapped = build_assignments(
            db_pids,
            object_hierarchies,
            mapping,
        )

        print_preflight(assignments, excluded, review, unmapped)
        validate_preflight(db_pids, assignments, excluded, review, unmapped)

        expected_objects = len(db_pids) - len(excluded)

        print()
        print("EXPECTED")
        print(f"  starting objects:    {len(db_pids):,}")
        print(f"  objects to exclude:  {len(excluded):,}")
        print(f"  surviving objects:   {expected_objects:,}")
        print(f"  objects to update:   {len(assignments):,}")

        if dry_run:
            print()
            print("DRY RUN: all preflight checks passed; no database changes made.")
            return

        backup_path = backup_database(db_path)

        print()
        print(f"Backup: {backup_path}")

        con.execute("BEGIN IMMEDIATE")

        deleted = apply_exclusions(con, excluded)
        updated = apply_assignments(con, assignments)
        integrity = validate_database(con, expected_objects)

        con.commit()

        print_db_summary(con, "AFTER")

        print()
        print("QA")
        print(f"  deleted as excluded: {deleted:,}")
        print(f"  updated:             {updated:,}")
        print(f"  integrity_check:     {integrity}")
        print("  foreign_key_check:   ok")

    except Exception:
        if con.in_transaction:
            con.rollback()

        raise

    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Populate objects.group_id and objects.collection_id from the "
            "resolved Fedora hierarchy mapping."
        )
    )

    parser.add_argument(
        "--mapping",
        default=DEFAULT_MAPPING,
        help=f"Source hierarchy mapping CSV (default: {DEFAULT_MAPPING})",
    )

    parser.add_argument(
        "--hierarchy",
        default=DEFAULT_HIERARCHY,
        help=f"Object hierarchy audit CSV (default: {DEFAULT_HIERARCHY})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all preflight checks without changing the database.",
    )

    args = parser.parse_args()

    db_path = require_env("DB")

    update_database(
        db_path=db_path,
        mapping_path=args.mapping,
        hierarchy_path=args.hierarchy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()