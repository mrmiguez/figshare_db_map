#!/usr/bin/env python3

import os
import re
import argparse
from pathlib import PurePosixPath

import boto3

SRCBUCK = os.environ["SRCBUCK"]
TGTBUCK = os.environ.get("TGTBUCK")

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
        description="Reorganize Islandora assets for Figshare ingest."
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform copy/download"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Process at most N matching files"
    )

    parser.add_argument(
        "--local-root",
        help="Write flattened assets to local filesystem"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    s3 = boto3.resource("s3")

    src_bucket = s3.Bucket(SRCBUCK)

    local_mode = bool(args.local_root)

    if local_mode:

        print(f"SOURCE: s3://{SRCBUCK}")
        print(f"TARGET: {args.local_root}")

    else:

        if not TGTBUCK:
            raise RuntimeError(
                "TGTBUCK must be defined "
                "for S3->S3 mode"
            )

        tgt_bucket = s3.Bucket(TGTBUCK)

        print(f"SOURCE: s3://{SRCBUCK}")
        print(f"TARGET: s3://{TGTBUCK}")

    if not args.execute:
        print("\n*** DRY RUN ***\n")

    count = 0

    for obj in src_bucket.objects.all():

        key = obj.key

        filename = os.path.basename(key)

        m = PID_RE.search(filename)

        if not m:
            continue

        child_pid = m.group(1)

        parent_name = PurePosixPath(
            key
        ).parent.name

        if PARENT_PID_RE.fullmatch(
                parent_name):

            destination_dir = parent_name

        else:

            destination_dir = child_pid

        extension = os.path.splitext(
            filename
        )[1]

        destination_filename = (
            f"{child_pid}{extension}"
        )

        if local_mode:

            destination_path = (
                os.path.join(
                    args.local_root,
                    destination_dir,
                    destination_filename
                )
            )

            print(
                f"s3://{SRCBUCK}/{key}\n"
                f"    -> {destination_path}\n"
            )

            if args.execute:

                os.makedirs(
                    os.path.dirname(
                        destination_path
                    ),
                    exist_ok=True
                )

                src_bucket.download_file(
                    key,
                    destination_path
                )

        else:

            destination_key = (
                f"{destination_dir}/"
                f"{destination_filename}"
            )

            print(
                f"s3://{SRCBUCK}/{key}\n"
                f"    -> "
                f"s3://{TGTBUCK}/"
                f"{destination_key}\n"
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
                f"Processed "
                f"{count:,} files..."
            )

        if (
            args.limit
            and count >= args.limit
        ):
            print(
                f"\nReached limit "
                f"of {args.limit:,} files."
            )
            break

    print(
        f"\nProcessed "
        f"{count:,} files"
    )

    if not args.execute:
        print(
            "\nNo assets copied "
            "(dry run mode)."
        )


if __name__ == "__main__":
    main()