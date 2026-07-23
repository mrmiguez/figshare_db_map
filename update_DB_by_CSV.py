#!/usr/bin/env python3

import csv
import sqlite3
import sys
from pathlib import Path


def get_table_columns(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def main():

    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} DATABASE CSV",
            file=sys.stderr
        )
        sys.exit(1)

    db_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])

    conn = sqlite3.connect(db_path)

    try:

        columns = get_table_columns(conn, "objects")

        with csv_path.open(
            newline="",
            encoding="utf-8"
        ) as fh:

            reader = csv.DictReader(fh)

            fieldnames = reader.fieldnames

            if not fieldnames or len(fieldnames) != 2:
                raise ValueError(
                    "CSV must contain exactly two columns "
                    "(pid and update field)"
                )

            pid_column = fieldnames[0]
            update_column = fieldnames[1]

            if pid_column.lower() != "pid":
                raise ValueError(
                    f"First column must be 'pid', "
                    f"found '{pid_column}'"
                )

            if update_column not in columns:
                raise ValueError(
                    f"Field '{update_column}' not found "
                    f"in objects table"
                )

            sql = f"""
                UPDATE objects
                SET {update_column} = ?
                WHERE pid = ?
            """

            updates = 0

            for row in reader:

                pid = row[pid_column].strip()
                value = row[update_column].strip()

                if not pid:
                    continue

                cur = conn.execute(
                    sql,
                    (value, pid)
                )

                updates += cur.rowcount

            conn.commit()

        print(
            f"Updated {updates} object record(s) "
            f"field '{update_column}'."
        )

    finally:
        conn.close()

if __name__ == "__main__":
    main()