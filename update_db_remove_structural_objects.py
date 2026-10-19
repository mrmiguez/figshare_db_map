#!/usr/bin/env python3

import argparse
import os
import sqlite3


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Remove Fedora collection objects from the "
            "Figshare migration database."
        )
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    parser.add_argument(
        "collection_pids",
        help=(
            "Text file containing Fedora collectionCModel "
            "PIDs, one PID per line"
        ),
    )

    return parser.parse_args()


def load_collection_pids(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as fh:
        pids = sorted({
            line.strip()
            for line in fh
            if line.strip()
        })

    if not pids:
        raise RuntimeError(
            f"No Fedora collection PIDs found in {path}"
        )

    return pids


def get_existing_collection_pids(
    conn,
    collection_pids,
):
    placeholders = ",".join(
        "?" for _ in collection_pids
    )

    rows = conn.execute(
        f"""
        SELECT pid
        FROM objects
        WHERE pid IN ({placeholders})
        ORDER BY pid
        """,
        collection_pids,
    ).fetchall()

    return [
        row[0]
        for row in rows
    ]


def remove_structural_objects(
    conn,
    collection_pids,
):
    pids = get_existing_collection_pids(
        conn,
        collection_pids,
    )

    identified = len(pids)

    if not pids:
        foreign_key_violations = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        return {
            "fedora_collections": len(collection_pids),
            "identified": 0,
            "removed": 0,
            "remaining": 0,
            "foreign_key_violations": foreign_key_violations,
        }

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    placeholders = ",".join(
        "?" for _ in pids
    )

    conn.execute(
        "BEGIN"
    )

    try:
        cursor = conn.execute(
            f"""
            DELETE FROM objects
            WHERE pid IN ({placeholders})
            """,
            pids,
        )

        removed = cursor.rowcount

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    remaining_pids = get_existing_collection_pids(
        conn,
        collection_pids,
    )

    foreign_key_violations = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    return {
        "fedora_collections": len(collection_pids),
        "identified": identified,
        "removed": removed,
        "remaining": len(remaining_pids),
        "foreign_key_violations": foreign_key_violations,
    }


def report_results(stats):
    print()
    print("STRUCTURAL OBJECT REMOVAL")
    print("-------------------------")

    print(
        f"Fedora collectionCModel PIDs: "
        f"{stats['fedora_collections']:,}"
    )

    print(
        f"Collection objects identified in DB: "
        f"{stats['identified']:,}"
    )

    print(
        f"Collection objects removed: "
        f"{stats['removed']:,}"
    )

    print(
        f"Collection objects remaining: "
        f"{stats['remaining']:,}"
    )

    print(
        f"Foreign key violations: "
        f"{len(stats['foreign_key_violations']):,}"
    )

    if stats["foreign_key_violations"]:
        print()
        print("Foreign key violations:")

        for violation in stats["foreign_key_violations"]:
            print(
                f"  {violation}"
            )


def main():
    args = parse_args()

    db_path = os.path.abspath(
        args.database
    )

    collection_pids_path = os.path.abspath(
        args.collection_pids
    )

    collection_pids = load_collection_pids(
        collection_pids_path
    )

    conn = sqlite3.connect(
        db_path
    )

    try:
        stats = remove_structural_objects(
            conn,
            collection_pids,
        )

        report_results(
            stats
        )

        if stats["remaining"]:
            raise RuntimeError(
                f"{stats['remaining']:,} Fedora collection "
                "objects remain after removal"
            )

        if stats["foreign_key_violations"]:
            raise RuntimeError(
                "Foreign key violations remain "
                "after structural-object removal"
            )

    finally:
        conn.close()


if __name__ == "__main__":
    main()