#!/usr/bin/env python3

import argparse
import csv
import os
import shutil
import sqlite3
import sys
from pathlib import Path


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
    mapping = {}

    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            hierarchy = row["collection_hierarchy"].strip()

            if not hierarchy:
                continue

            leaf_pid = row["leaf_collection_pid"].strip()

            mapping[hierarchy] = {
                "leaf_pid": leaf_pid,
                "group_id": int(row["group_id"]) if row["group_id"].strip() else None,
                "collection_id": int(row["collection_id"]) if row["collection_id"].strip() else None,
                "status": row["status"].strip(),
            }

    return mapping


def read_object_hierarchies(path):
    rows = []

    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            rows.append({
                "pid": row["pid"].strip(),
                "hierarchy": row["collection_hierarchy"].strip(),
            })

    return rows


def is_excluded(hierarchy):
    if not hierarchy:
        return False

    components = hierarchy.split("|")
    return any(pid in EXCLUDED_COLLECTIONS for pid in components)


def backup_database(db_path):
    db_path = Path(db_path)
    backup_path = db_path.with_suffix(db_path.suffix + ".before_group_collection_update")

    if backup_path.exists():
        raise RuntimeError(f"Backup already exists: {backup_path}")

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


def update_database(db_path, mapping_path, hierarchy_path, dry_run=False):
    mapping = read_mapping(mapping_path)
    object_hierarchies = read_object_hierarchies(hierarchy_path)

    con = sqlite3.connect(db_path)

    try:
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

        print()
        print("PREFLIGHT")
        print(f"  assignable objects:  {len(assignments):,}")
        print(f"  excluded objects:    {len(excluded):,}")
        print(f"  review objects:      {len(review):,}")
        print(f"  unmapped objects:    {len(unmapped):,}")

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

        if dry_run:
            print()
            print("DRY RUN: no database changes made.")
            return

        backup_path = backup_database(db_path)

        print()
        print(f"Backup: {backup_path}")

        con.execute("BEGIN IMMEDIATE")

        # These objects are explicitly outside the migration population.
        if excluded:
            con.executemany(
                "DELETE FROM objects WHERE pid = ?",
                [(pid,) for pid in sorted(excluded)],
            )

        # Start from a deterministic state.
        con.execute("""
            UPDATE objects
            SET group_id = NULL,
                collection_id = NULL
        """)

        con.executemany(
            """
            UPDATE objects
            SET group_id = ?,
                collection_id = ?
            WHERE pid = ?
            """,
            [
                (group_id, collection_id, pid)
                for pid, (group_id, collection_id) in assignments.items()
            ],
        )

        remaining_null_groups = con.execute("""
            SELECT COUNT(*)
            FROM objects
            WHERE group_id IS NULL
        """).fetchone()[0]

        if remaining_null_groups:
            raise RuntimeError(
                f"{remaining_null_groups:,} surviving objects still have NULL group_id"
            )

        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]

        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity_check failed: {integrity}")

        con.commit()

        print_db_summary(con, "AFTER")

        print()
        print("QA")
        print(f"  deleted as excluded: {len(excluded):,}")
        print(f"  updated:             {len(assignments):,}")
        print(f"  integrity_check:     {integrity}")

    except Exception:
        if con.in_transaction:
            con.rollback()
        raise

    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description="Populate objects.group_id and objects.collection_id from the resolved Fedora hierarchy mapping."
    )

    parser.add_argument(
        "--mapping",
        required=True,
        help="Final Draft Mapping CSV.",
    )

    parser.add_argument(
        "--hierarchy",
        required=True,
        help="object_collection_hierarchy.csv produced by audit_source_hierarchy.py.",
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