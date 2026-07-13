#!/usr/bin/env python3

import csv
import sqlite3
from pathlib import Path

DB_PATH = "figshare_record_tables.sqlite3"

DATE_EMBARGO_TYPES = {
    "PDF datastream",
    "OBJ datastream",
    "FULL_TEXT datastream",
}

IP_TYPES = {
    "IP",
}

def embargo_files(root):
    yield from Path(root).rglob(
        "*child-embargoes.csv"
    )

def parse_row(row):
    pid = row[0].strip()
    embargo_target = row[1].strip()
    embargo_value = row[2].strip()

    return(
        pid,
        embargo_target,
        embargo_value
    )

def update_embargo(conn, pid, embargo_target, embargo_value):

    # date-based embargoes
    if embargo_target in DATE_EMBARGO_TYPES:
        conn.execute(
            """
            UPDATE objects
            SET
                embargo_date = ?,
                embargo_type = 'file'
            WHERE pid = ?
            """,
            (embargo_value, pid)
        )

        return

    # IP restrictions

    if embargo_target == "IP":
        conn.execute(
            """
            UPDATE objects
            SET
                embargo_reason = ?
            WHERE pid = ?
            """,
            (f"IP restriction ({embargo_value})", pid)
        )

        return

    # everything else

    print(
        "UNKNOWN:",
        pid,
        embargo_target,
        embargo_value
    )

def main(root):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("BEGIN")
    count = 0

    for f in embargo_files(root):
        with open(f, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)

            for row in reader:
                if len(row) < 3:
                    continue
                pid, target, value = parse_row(row)

                update_embargo(conn, pid, target, value)
                count += 1

                if count % 1000 == 0:
                    conn.commit()
                    conn.execute("BEGIN")

    conn.commit()
    conn.close()

    print(f"Updated {count:,} embargo rows")
