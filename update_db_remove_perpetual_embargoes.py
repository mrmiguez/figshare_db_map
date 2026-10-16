#!/usr/bin/env python3

import sqlite3
import sys


def get_perpetual_embargo_pids(conn):

    rows = conn.execute(
        """
        SELECT DISTINCT object_id
        FROM embargoes
        WHERE embargo_class = 'article'
          AND LOWER(embargo_value) = 'indefinite'
        ORDER BY object_id
        """
    ).fetchall()

    return [
        row[0]
        for row in rows
    ]


def remove_perpetual_embargoes(db_path):

    conn = sqlite3.connect(db_path)

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    pids = get_perpetual_embargo_pids(
        conn
    )

    print()
    print("PERPETUAL ARTICLE EMBARGO REMOVAL")
    print("---------------------------------")
    print(
        f"Objects identified: "
        f"{len(pids):,}"
    )

    if not pids:

        conn.close()
        return

    conn.execute("BEGIN")

    try:

        for pid in pids:

            conn.execute(
                """
                DELETE FROM objects
                WHERE pid = ?
                """,
                (pid,)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        conn.close()
        raise

    remaining = conn.execute(
        """
        SELECT COUNT(*)
        FROM objects o
        JOIN embargoes e
            ON e.object_id = o.pid
        WHERE e.embargo_class = 'article'
          AND LOWER(e.embargo_value) = 'indefinite'
        """
    ).fetchone()[0]

    fk_errors = conn.execute(
        """
        PRAGMA foreign_key_check
        """
    ).fetchall()

    conn.close()

    print(
        f"Objects removed: "
        f"{len(pids):,}"
    )

    print(
        f"Perpetual article objects remaining: "
        f"{remaining:,}"
    )

    print(
        f"Foreign key violations: "
        f"{len(fk_errors):,}"
    )

    if remaining:
        raise RuntimeError(
            "Perpetual article embargo "
            "objects remain after removal"
        )

    if fk_errors:
        raise RuntimeError(
            "Foreign key violations detected "
            "after removal"
        )


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            f"Usage: {sys.argv[0]} DATABASE"
        )

        sys.exit(1)

    remove_perpetual_embargoes(
        sys.argv[1]
    )