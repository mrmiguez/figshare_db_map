#!/usr/bin/env python3

import os
import re
import argparse
import boto3

SRCBUCK = os.environ["SRCBUCK"]
TGTBUCK = os.environ["TGTBUCK"]

PID_RE = re.compile(
    r"(fsu_\d+)_(?:PDF|OBJ)",
    re.IGNORECASE
)


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform copies"
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

    count = 0

    print(f"SOURCE: s3://{SRCBUCK}")
    print(f"TARGET: s3://{TGTBUCK}")

    if not args.execute:
        print("\n*** DRY RUN ***\n")

    for obj in src_bucket.objects.all():

        key = obj.key
        filename = os.path.basename(key)

        m = PID_RE.search(filename)

        if not m:
            continue

        pid = m.group(1)

        destination_key = (
            f"{pid}/{filename}"
        )

        print(
            f"s3://{SRCBUCK}/{key}"
            f"\n    -> "
            f"s3://{TGTBUCK}/{destination_key}\n"
        )

        if args.execute:

            tgt_bucket.copy(
                {
                    "Bucket": SRCBUCK,
                    "Key": key
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