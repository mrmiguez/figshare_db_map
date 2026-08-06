#!/usr/bin/env python3

import os
import re
import argparse
from pathlib import PurePosixPath

import boto3

SRCBUCK = os.environ["SRCBUCK"]
TGTBUCK = os.environ["TGTBUCK"]

PID_RE = re.compile(
    r"(fsu_\d+)_(?:PDF|OBJ)",
    re.IGNORECASE
)

PARENT_PID_RE = re.compile(
    r"^fsu_\d+$",
    re.IGNORECASE
)


def parse_args():

    parser = argparse.ArgumentParser(
        description="Reorganize Islandora assets in S3 for Figshare ingest."
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform S3 copies"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Process at most N matching files"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    s3 = boto3.resource("s3")

    src_bucket = s3.Bucket(SRCBUCK)
    tgt_bucket = s3.Bucket(TGTBUCK)

    print(f"SOURCE: s3://{SRCBUCK}")
    print(f"TARGET: s3://{TGTBUCK}")

    if not args.execute:
        print("\n*** DRY RUN ***\n")

    count = 0

    for obj in src_bucket.objects.all():

        key = obj.key

        filename = os.path.basename(key)

        #
        # Only process PDF and OBJ assets
        #

        m = PID_RE.search(filename)

        if not m:
            continue

        child_pid = m.group(1)

        #
        # Use parent PID directory if this is a page child
        #
        # Example:
        #
        # .../fsu_107473/fsu_107474_OBJ.tiff
        #
        # becomes:
        #
        # fsu_107473/fsu_107474.tiff
        #
        # Otherwise:
        #
        # fsu_1064943_PDF.pdf
        #
        # becomes:
        #
        # fsu_1064943/fsu_1064943.pdf
        #

        parent_name = PurePosixPath(key).parent.name

        if PARENT_PID_RE.fullmatch(parent_name):
            destination_dir = parent_name
        else:
            destination_dir = child_pid

        extension = os.path.splitext(filename)[1]

        destination_filename = (
            f"{child_pid}{extension}"
        )

        destination_key = (
            f"{destination_dir}/{destination_filename}"
        )

        print(
            f"s3://{SRCBUCK}/{key}\n"
            f"    -> s3://{TGTBUCK}/{destination_key}\n"
        )

        if args.execute:

            tgt_bucket.copy(
                {
                    "Bucket": SRCBUCK,
                    "Key": key,
                },
                destination_key
            )

        count += 1

        if count % 1000 == 0:
            print(
                f"Processed {count:,} files..."
            )

        if args.limit and count >= args.limit:
            print(
                f"\nReached limit of {args.limit:,} files."
            )
            break

    print(
        f"\nProcessed {count:,} files"
    )

    if not args.execute:
        print(
            "\nNo files copied (dry run mode)."
        )


if __name__ == "__main__":
    main()