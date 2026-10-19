#!/usr/bin/env python3

import argparse
import sqlite3


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Remove repository structural objects from the "
            "Figshare migration database."
        )
    )

    parser.add_argument(
        "database",
        help="SQLite migration database",
    )

    return parser.parse_args()


# ----------------------------------------------------------------------
# Structural-object predicate
# ----------------------------------------------------------------------

STRUCTURAL_WHERE = """
    SUBSTR(pid, 5) = ''
    OR SUBSTR(pid, 5) GLOB '*[^0-9]*'
"""


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------

def remove_structural_objects(conn):

    pids = [
        row[0]
        for row in conn.execute(
            f"""
            SELECT pid
            FROM objects
            WHERE {STRUCTURAL_WHERE}
            ORDER BY pid
            """
        )
    ]

    identified = len(pids)

    if not pids:

        return {
            "identified": 0,
            "removed": 0,
            "remaining": 0,
            "foreign_key_violations": [],
        }

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.execute("BEGIN")

    try:

        placeholders = ",".join(
            ["?"] * len(pids)
        )

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

    remaining = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM objects
        WHERE {STRUCTURAL_WHERE}
        """
    ).fetchone()[0]

    foreign_key_violations = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    return {
        "identified": identified,
        "removed": removed,
        "remaining": remaining,
        "foreign_key_violations":
            foreign_key_violations,
    }


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def report_results(stats):

    print()
    print("STRUCTURAL OBJECT REMOVAL")
    print("-------------------------")

    print(
        f"Objects identified: "
        f"{stats['identified']:,}"
    )

    print(
        f"Objects removed: "
        f"{stats['removed']:,}"
    )

    print(
        f"Structural objects remaining: "
        f"{stats['remaining']:,}"
    )

    print(
        f"Foreign key violations: "
        f"{len(stats['foreign_key_violations']):,}"
    )

    if stats["foreign_key_violations"]:

        print()
        print("Foreign key violations:")

        for violation in stats[
            "foreign_key_violations"
        ]:
            print(
                f"  {violation}"
            )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():

    args = parse_args()

    conn = sqlite3.connect(
        args.database
    )

    try:

        stats = remove_structural_objects(
            conn
        )

        report_results(
            stats
        )

        if stats["remaining"]:

            raise RuntimeError(
                f"{stats['remaining']:,} structural "
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