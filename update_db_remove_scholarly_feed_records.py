#!/usr/bin/env python3

import sqlite3
import sys

from assets import feed_records as assets


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <database>")
        sys.exit(1)

    db_path = sys.argv[1]
    conn = sqlite3.connect(db_path)

    try:
        #
        # This must be enabled before any transaction begins so
        # dependent rows such as embargoes are removed by their
        # ON DELETE CASCADE constraints.
        #

        conn.execute("PRAGMA foreign_keys = ON")

        foreign_keys_enabled = conn.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        if foreign_keys_enabled != 1:
            raise RuntimeError(
                "SQLite foreign key enforcement could not be enabled"
            )

        #
        # Refuse to operate on an already-invalid database.
        #

        existing_violations = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if existing_violations:
            raise RuntimeError(
                f"Database already contains {len(existing_violations):,} "
                "foreign key violations before scholarly-feed removal"
            )

        (
            pids,
            wos_count,
            pmc_count,
        ) = assets.get_feed_pids(conn)

        total_feed_records = len(pids)

        print()
        print("SCHOLARLY FEED RECORD REMOVAL")
        print("-----------------------------")
        print(f"Web of Science : {wos_count:,}")
        print(f"PubMed Central : {pmc_count:,}")
        print(f"Total           : {total_feed_records:,}")
        print()

        if not pids:
            print("No scholarly feed records found.")
            return

        placeholders = ",".join("?" for _ in pids)

        object_author_links = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM object_authors
            WHERE object_id IN ({placeholders})
            """,
            pids,
        ).fetchone()[0]

        dependent_embargoes = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM embargoes
            WHERE object_id IN ({placeholders})
            """,
            pids,
        ).fetchone()[0]

        print(f"Object-author links to remove: {object_author_links:,}")
        print(f"Embargo rows to cascade:      {dependent_embargoes:,}")
        print()

        conn.execute("BEGIN IMMEDIATE")

        try:
            #
            # Remove object-author links explicitly. Other dependent
            # tables with ON DELETE CASCADE, including embargoes,
            # are handled automatically when objects are deleted.
            #

            conn.execute(
                f"""
                DELETE FROM object_authors
                WHERE object_id IN ({placeholders})
                """,
                pids,
            )

            cursor = conn.execute(
                f"""
                DELETE FROM objects
                WHERE pid IN ({placeholders})
                """,
                pids,
            )

            removed = cursor.rowcount

            if removed != total_feed_records:
                raise RuntimeError(
                    f"Expected to remove {total_feed_records:,} scholarly-feed "
                    f"objects but removed {removed:,}"
                )

            #
            # Verify feed detection again before committing.
            #

            (
                remaining_feed_pids,
                remaining_wos,
                remaining_pmc,
            ) = assets.get_feed_pids(conn)

            if remaining_feed_pids:
                raise RuntimeError(
                    f"{len(remaining_feed_pids):,} scholarly-feed records remain "
                    f"after removal: Web of Science={remaining_wos:,}, "
                    f"PubMed Central={remaining_pmc:,}"
                )

            #
            # Verify that cascading deletion removed dependent
            # embargo rows for the deleted objects.
            #

            remaining_embargoes = conn.execute(
                f"""
                SELECT COUNT(*)
                FROM embargoes
                WHERE object_id IN ({placeholders})
                """,
                pids,
            ).fetchone()[0]

            if remaining_embargoes:
                raise RuntimeError(
                    f"{remaining_embargoes:,} embargo rows remain for deleted "
                    "scholarly-feed objects"
                )

            #
            # No foreign-key violations are allowed before commit.
            #

            foreign_key_violations = conn.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if foreign_key_violations:
                raise RuntimeError(
                    f"{len(foreign_key_violations):,} foreign key violations "
                    "remain after scholarly-feed removal"
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        remaining = conn.execute(
            "SELECT COUNT(*) FROM objects"
        ).fetchone()[0]

        print("Verified: no scholarly feed records remain")
        print(f"Removed {removed:,} objects")
        print(f"Removed {object_author_links:,} object-author links")
        print(f"Cascaded {dependent_embargoes:,} embargo rows")
        print("Foreign key violations: 0")
        print()
        print(f"Objects remaining: {remaining:,}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()