#!/usr/bin/env python3

import sqlite3
import pandas as pd

DB = "/home/mmiguez/bin/figshare_migration/figshare_records.sqlite3"
OUTFILE = "authorless_non_archaeology.csv"

conn = sqlite3.connect(DB)

df = pd.read_sql_query(
    """
    SELECT
        o.pid,
        o.title,
        o.source_collection
    FROM objects o
    LEFT JOIN object_authors oa
        ON o.pid = oa.object_id
    WHERE oa.object_id IS NULL
      AND lower(o.source_collection) NOT LIKE '%castro%'
      AND lower(o.source_collection) NOT LIKE '%cetamura%'
      AND o.pid GLOB 'fsu:[0-9]*'
    ORDER BY
        o.source_collection,
        o.pid
    """,
    conn
)

df.to_csv(
    OUTFILE,
    index=False
)

print(
    f"Wrote {len(df):,} records to "
    f"{OUTFILE}"
)

conn.close()
