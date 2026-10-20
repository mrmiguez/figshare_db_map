#!/usr/bin/env python3

import argparse
import os
import sqlite3
import subprocess
import sys


def require_env(name):
    value = os.environ.get(name)

    if not value:
        print(
            f"ERROR: environment variable {name} is not set",
            file=sys.stderr,
        )
        sys.exit(1)

    return value


def storage_pid(pid):
    """
    Convert Fedora PID notation to the form used in S3 keys.

    Example:
        fsu:1001394 -> fsu_1001394
    """
    return pid.replace(":", "_")


def run_aws(args):
    proc = subprocess.run(
        ["aws", *args],
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        return None, proc.stderr.strip()

    return proc.stdout, None


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


def search_src_bucket(bucket, pid, row):
    """
    Find source Fedora datastreams belonging directly to PID.

    When source_collection is available from the DB, use it as
    the S3 prefix rather than listing the entire source bucket.

    Files belonging to descendant Fedora objects are excluded by
    requiring the basename to begin with the requested storage PID.
    """
    spid = storage_pid(pid)

    if row is not None and "source_collection" in row.keys():
        source_collection = row["source_collection"]
    else:
        source_collection = None

    if source_collection:
        prefix = source_collection.strip("/") + "/"
    else:
        prefix = ""

    args = [
        "s3api",
        "list-objects-v2",
        "--bucket",
        bucket,
    ]

    if prefix:
        args.extend([
            "--prefix",
            prefix,
        ])

    args.extend([
        "--query",
        "Contents[].{Key:Key,Size:Size}",
        "--output",
        "json",
    ])

    output, error = run_aws(args)

    if error:
        return None, error, prefix

    import json

    try:
        objects = json.loads(output)
    except json.JSONDecodeError as exc:
        return None, f"Unable to parse AWS output: {exc}", prefix

    if not objects:
        return [], None, prefix

    matches = []

    for obj in objects:
        key = obj["Key"]
        basename = key.rsplit("/", 1)[-1]

        #
        # Direct Fedora representation:
        #
        #     fsu_1001394_DC.xml
        #     fsu_1001394_MODS.xml
        #     fsu_1001394_PDF.pdf
        #     fsu_1001394_POLICY.xml
        #     fsu_1001394_RELS-EXT.rdf
        #     fsu_596511.child-noncollections.pids
        #
        # Do not match child objects merely because they occur
        # beneath an fsu_<pid>/ directory.
        #

        if (
            basename.startswith(spid + "_")
            or basename.startswith(spid + ".")
        ):
            matches.append(
                {
                    "key": key,
                    "size": obj["Size"],
                }
            )

    return matches, None, prefix


def search_tgt_bucket(bucket, pid):
    """
    Search the Figshare asset staging bucket.

    Target assets are stored beneath a top-level PID prefix:

        fsu_1001394/fsu_1001394.pdf
    """
    spid = storage_pid(pid)
    prefix = f"{spid}/"

    args = [
        "s3api",
        "list-objects-v2",
        "--bucket",
        bucket,
        "--prefix",
        prefix,
        "--query",
        "Contents[].{Key:Key,Size:Size}",
        "--output",
        "json",
    ]

    output, error = run_aws(args)

    if error:
        return None, error, prefix

    import json

    try:
        objects = json.loads(output)
    except json.JSONDecodeError as exc:
        return None, f"Unable to parse AWS output: {exc}", prefix

    if not objects:
        return [], None, prefix

    return objects, None, prefix


def format_size(size):
    size = int(size)

    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            if unit == "B":
                return f"{size} {unit}"

            return f"{size:.1f} {unit}"

        size /= 1024

    return str(size)


def print_db_result(db, row):
    print("DATABASE")
    print(f"  DB: {db}")

    if row is None:
        print("  Status: NOT FOUND")
        return

    print("  Status: FOUND")

    useful_fields = (
        "pid",
        "iid",
        "title",
        "identifier",
        "source_collection",
    )

    for field in useful_fields:
        if field not in row.keys():
            continue

        value = row[field]

        if value is not None and str(value).strip():
            print(f"  {field}: {value}")


def print_s3_result(label, bucket, prefix, objects, error):
    print(label)
    print(f"  Prefix: s3://{bucket}/{prefix}")

    if error:
        print(f"  Status: ERROR")
        print(f"  {error}")
        return

    if not objects:
        print("  Status: NOT FOUND")
        return

    print("  Status: FOUND")
    print(f"  Files: {len(objects)}")

    total_size = sum(int(obj["size"] if "size" in obj else obj["Size"]) for obj in objects)

    print(f"  Total size: {format_size(total_size)}")

    for obj in objects:
        key = obj["key"] if "key" in obj else obj["Key"]
        size = obj["size"] if "size" in obj else obj["Size"]

        print(
            f"  {format_size(size):>10}  "
            f"s3://{bucket}/{key}"
        )


def audit_pid(pid, db, srcbuck, tgtbuck):
    spid = storage_pid(pid)

    print()
    print("=" * 90)
    print(f"PID:         {pid}")
    print(f"Storage PID: {spid}")
    print("=" * 90)
    print()

    row = search_db(db, pid)

    print_db_result(db, row)

    print()

    src_objects, src_error, src_prefix = search_src_bucket(
        srcbuck,
        pid,
        row,
    )

    print_s3_result(
        "SOURCE BUCKET",
        srcbuck,
        src_prefix,
        src_objects,
        src_error,
    )

    print()

    tgt_objects, tgt_error, tgt_prefix = search_tgt_bucket(
        tgtbuck,
        pid,
    )

    print_s3_result(
        "TARGET BUCKET",
        tgtbuck,
        tgt_prefix,
        tgt_objects,
        tgt_error,
    )

    print()
    print("SUMMARY")

    print(
        "  DB:       "
        + ("FOUND" if row is not None else "NOT FOUND")
    )

    if src_error:
        print("  SRCBUCK:  ERROR")
    else:
        print(
            "  SRCBUCK:  "
            + ("FOUND" if src_objects else "NOT FOUND")
        )

    if tgt_error:
        print("  TGTBUCK:  ERROR")
    else:
        print(
            "  TGTBUCK:  "
            + ("FOUND" if tgt_objects else "NOT FOUND")
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Audit Fedora/Figshare migration objects across "
            "figshare.db, SRCBUCK, and TGTBUCK."
        )
    )

    parser.add_argument(
        "pids",
        nargs="+",
        help="One or more Fedora PIDs, e.g. fsu:1001394",
    )

    args = parser.parse_args()

    db = require_env("DB")
    srcbuck = require_env("SRCBUCK")
    tgtbuck = require_env("TGTBUCK")

    for pid in args.pids:
        audit_pid(
            pid,
            db,
            srcbuck,
            tgtbuck,
        )


if __name__ == "__main__":
    main()