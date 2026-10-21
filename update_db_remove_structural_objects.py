#!/usr/bin/env python3

import argparse
import os
import sqlite3


def parse_args():
    parser = argparse.ArgumentParser(
        description="Remove Fedora collection objects from the Figshare migration database."
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    parser.add_argument(
        "collection_pids",
        help="Text file containing Fedora collectionCModel PIDs, one PID per line",
    )

    return parser.parse_args()


def load_collection_pids(path):
    with open(path, "r", encoding="utf-8") as fh:
        pids = sorted({
            line.strip()
            for line in fh
            if line.strip()
        })

    if not pids:
        raise RuntimeError(f"No Fedora collection PIDs found in {path}")

    return pids


def get_existing_collection_pids(conn, collection_pids):
    placeholders = ",".join("?" for _ in collection_pids)

    rows = conn.execute(
        f"""
        SELECT pid
        FROM objects
        WHERE pid IN ({placeholders})
        ORDER BY pid
        """,
        collection_pids,
    ).fetchall()

    return [row[0] for row in rows]


def remove_structural_objects(conn, collection_pids):
    pids = get_existing_collection_pids(conn, collection_pids)
    identified = len(pids)

    if not pids:
        foreign_key_violations = conn.execute("PRAGMA foreign_key_check").fetchall()

        return {
            "fedora_collections": len(collection_pids),
            "identified": 0,
            "removed": 0,
            "remaining": 0,
            "foreign_key_violations": foreign_key_violations,
        }

    placeholders = ",".join("?" for _ in pids)

    conn.execute("BEGIN IMMEDIATE")

    try:
        cursor = conn.execute(
            f"""
            DELETE FROM objects
            WHERE pid IN ({placeholders})
            """,
            pids,
        )

        removed = cursor.rowcount

        remaining_pids = get_existing_collection_pids(conn, collection_pids)

        foreign_key_violations = conn.execute("PRAGMA foreign_key_check").fetchall()

        if remaining_pids:
            raise RuntimeError(
                f"{len(remaining_pids):,} Fedora collection objects remain after removal"
            )

        if foreign_key_violations:
            raise RuntimeError(
                f"{len(foreign_key_violations):,} foreign key violations remain "
                "after structural-object removal"
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    return {
        "fedora_collections": len(collection_pids),
        "identified": identified,
        "removed": removed,
        "remaining": 0,
        "foreign_key_violations": [],
    }


def report_results(stats):
    print()
    print("STRUCTURAL OBJECT REMOVAL")
    print("-------------------------")
    print(f"Fedora collectionCModel PIDs:       {stats['fedora_collections']:,}")
    print(f"Collection objects identified in DB: {stats['identified']:,}")
    print(f"Collection objects removed:          {stats['removed']:,}")
    print(f"Collection objects remaining:        {stats['remaining']:,}")
    print(f"Foreign key violations:              {len(stats['foreign_key_violations']):,}")


def main():
    args = parse_args()

    db_path = os.path.abspath(args.database)
    collection_pids_path = os.path.abspath(args.collection_pids)

    collection_pids = load_collection_pids(collection_pids_path)

    conn = sqlite3.connect(db_path)

    try:
        #
        # This must be enabled before any transaction begins.
        #
        conn.execute("PRAGMA foreign_keys = ON")

        foreign_keys_enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]

        if foreign_keys_enabled != 1:
            raise RuntimeError("SQLite foreign key enforcement could not be enabled")

        #
        # Refuse to operate on an already-invalid database.
        #
        existing_violations = conn.execute("PRAGMA foreign_key_check").fetchall()

        if existing_violations:
            raise RuntimeError(
                f"Database already contains {len(existing_violations):,} foreign key "
                "violations before structural-object removal"
            )

        stats = remove_structural_objects(conn, collection_pids)

        report_results(stats)

    finally:
        conn.close()


if __name__ == "__main__":
    main()