#!/usr/bin/env python3

import sqlite3
import sys
from assets import feed_records as assets


def main():

    if len(sys.argv) != 2:

        print(
            f"Usage: {sys.argv[0]} <database>"
        )

        sys.exit(1)

    db_path = sys.argv[1]

    conn = sqlite3.connect(db_path)

    (
        pids,
        wos_count,
        pmc_count
    ) = assets.get_feed_pids(conn)

    total_feed_records = len(pids)

    print()
    print("Scholarly Feed Record Removal")
    print("-----------------------------")
    print(
        f"Web of Science : {wos_count:,}"
    )
    print(
        f"PubMed Central : {pmc_count:,}"
    )
    print(
        f"Total           : {total_feed_records:,}"
    )
    print()

    if not pids:

        print(
            "No scholarly feed records found."
        )

        conn.close()
        return

    cur = conn.cursor()

    placeholders = ",".join(
        ["?"] * len(pids)
    )

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM object_authors
        WHERE object_id IN ({placeholders})
        """,
        pids
    )

    object_author_links = cur.fetchone()[0]

    cur.execute(
        f"""
        DELETE FROM object_authors
        WHERE object_id IN ({placeholders})
        """,
        pids
    )

    cur.execute(
        f"""
        DELETE FROM objects
        WHERE pid IN ({placeholders})
        """,
        pids
    )

    conn.commit()

    (
        remaining_feed_pids,
        remaining_wos,
        remaining_pmc
    ) = assets.get_feed_pids(conn)

    print()

    if remaining_feed_pids:

        print(
            f"WARNING: {len(remaining_feed_pids):,} "
            f"feed records remain"
        )

    else:

        print(
            "Verified: no scholarly feed records remain"
        )

    print(
        f"Removed {total_feed_records:,} objects"
    )

    print(
        f"Removed {object_author_links:,} "
        f"object_author links"
    )

    print()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM objects
        """
    )

    remaining = cur.fetchone()[0]

    print(
        f"Objects remaining: {remaining:,}"
    )

    conn.close()


if __name__ == "__main__":
    main()