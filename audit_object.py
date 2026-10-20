#!/usr/bin/env python3

import argparse
import os
import sqlite3
import subprocess
import sys


def require_env(name):
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)

    return value


def search_bucket(bucket, pid):
    """
    Search an S3 bucket recursively for object keys containing PID.

    Returns complete s3:// paths.
    """
    proc = subprocess.run(
        [
            "aws",
            "s3api",
            "list-objects-v2",
            "--bucket",
            bucket,
            "--query",
            "Contents[].Key",
            "--output",
            "text",
        ],
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        return None, proc.stderr.strip()

    keys = []

    for key in proc.stdout.split():
        if pid in key:
            keys.append(key)

    return [f"s3://{bucket}/{key}" for key in keys], None


def search_db(db, pid):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    try:
        row = con.execute(
            """
            SELECT *
            FROM objects
            WHERE pid = ?
            """,
            (pid,),
        ).fetchone()
    finally:
        con.close()

    return row


def print_db_result(row):
    if row is None:
        print("  NOT FOUND")
        return

    print("  FOUND")

    useful_fields = (
        "pid",
        "iid",
        "title",
        "identifier",
        "source_collection",
    )

    for field in useful_fields:
        if field in row.keys():
            value = row[field]
            if value is not None:
                print(f"  {field}: {value}")


def print_s3_result(bucket, paths, error):
    print(f"  Bucket: s3://{bucket}/")

    if error:
        print(f"  ERROR: {error}")
        return

    if not paths:
        print("  NOT FOUND")
        return

    print(f"  FOUND: {len(paths)} object(s)")

    for path in paths:
        print(f"  {path}")


def audit_pid(pid, db, srcbuck, tgtbuck):
    print()
    print("=" * 78)
    print(f"PID: {pid}")
    print("=" * 78)

    print()
    print("DATABASE")
    print(f"  DB: {db}")

    row = search_db(db, pid)
    print_db_result(row)

    print()
    print("SOURCE BUCKET")

    paths, error = search_bucket(srcbuck, pid)
    print_s3_result(srcbuck, paths, error)

    print()
    print("TARGET BUCKET")

    paths, error = search_bucket(tgtbuck, pid)
    print_s3_result(tgtbuck, paths, error)


def main():
    parser = argparse.ArgumentParser(
        description="Audit Fedora/Figshare migration objects across DB, SRCBUCK, and TGTBUCK."
    )

    parser.add_argument(
        "pids",
        nargs="+",
        help="One or more Fedora PIDs, e.g. fsu:596511",
    )

    args = parser.parse_args()

    db = require_env("DB")
    srcbuck = require_env("SRCBUCK")
    tgtbuck = require_env("TGTBUCK")

    for pid in args.pids:
        audit_pid(pid, db, srcbuck, tgtbuck)


if __name__ == "__main__":
    main()