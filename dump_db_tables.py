#!/usr/bin/env python3

import sqlite3
import pandas as pd
from pathlib import Path
import sys

db = sys.argv[1]

conn = sqlite3.connect(db)

SCRIPT_DIR = Path(__file__).resolve().parent

outdir = SCRIPT_DIR / "exports"
outdir.mkdir(exist_ok=True)

tables = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""")

for (table,) in tables:

    df = pd.read_sql_query(
        f"SELECT * FROM {table}",
        conn
    )

    csv_path = outdir / f"{table}.csv"

    df.to_csv(
        csv_path,
        index=False
    )

    print(csv_path)

conn.close()