#!/usr/bin/env python3

import sqlite3
import argparse


def dedupe_keywords(keyword_string):
    """
    Deduplicate a pipe-delimited keyword string.

    Preserves first occurrence capitalization.
    Deduplicates case-insensitively.

    Example:
        Archaeology|archaeology|Italy
    becomes:
        Archaeology|Italy
    """

    if not keyword_string:
        return ""

    seen = set()
    result = []

    for term in keyword_string.split("|"):

        term = term.strip()

        if not term:
            continue

        key = term.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(term)

    return "|".join(result)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "database",
        help="SQLite database"
    )

    args = parser.parse_args()

    conn = sqlite3.connect(args.database)

    cur = conn.cursor()

    cur.execute("""
        SELECT pid, keywords
        FROM objects
        WHERE keywords IS NOT NULL
          AND keywords <> ''
    """)

    updates = []

    for pid, keywords in cur.fetchall():

        new_keywords = dedupe_keywords(keywords)

        if new_keywords != keywords:
            updates.append(
                (new_keywords, pid)
            )

    cur.executemany("""
        UPDATE objects
        SET keywords = ?
        WHERE pid = ?
    """, updates)

    conn.commit()

    print(
        f"Updated {len(updates)} records."
    )

    conn.close()


if __name__ == "__main__":
    main()