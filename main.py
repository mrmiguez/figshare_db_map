import os
import sys
import time
import assets
import logging
from pathlib import Path

from assets import write_author_record, link_author_to_object, iter_local_mods, iter_s3_mods

PATH = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('figshare_db_map')
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':

    # Parse args
    args = assets.argument_parser().parse_args()

    DB_PATH = os.path.abspath(args.db)

    db_dir = os.path.dirname(DB_PATH)
    db_stem = Path(DB_PATH).stem

    # create parent directory if needed
    os.makedirs(db_dir, exist_ok=True)

    TSV_LOG_PATH = os.path.join(
        db_dir,
        f"{db_stem}.tsv"
    )

    # TSV logging
    from assets.tsv_logger import TSVHandler

    tsv_handler = TSVHandler(TSV_LOG_PATH)
    tsv_handler.setLevel(logging.DEBUG)

    logging.getLogger().addHandler(tsv_handler)

    # Connect DB
    db_conn = assets.connect_db(DB_PATH)

    logger.debug(f'Args... {args}')

    # CLI run
    if args.run:

        # Select record source
        if getattr(args, "s3", False):
            logger.info(
                f"Running in S3 mode "
                f"(bucket={args.bucket}, prefix={args.prefix})"
            )

            mods_records = iter_s3_mods(
                args.bucket,
                args.prefix
            )

        else:
            logger.info(
                f"Running in filesystem mode "
                f"(record_directory={args.record_directory})"
            )

            mods_records = iter_local_mods(
                args.record_directory
            )

        # DB commit batching
        db_conn.execute("BEGIN")
        BATCH_SIZE = 1000
        count = 0
        start = time.perf_counter()

        # gathering author stats for log
        fallback_primary_count = 0
        fallback_personal_count = 0

        for record in mods_records:

            source_path = record["path"]
            collection = record["collection"]
            stream = record["stream"]

            logger.info(
                f"Reading... {source_path}"
            )

            filename = os.path.basename(
                str(source_path)
            )

            pid = (
                Path(filename)
                .stem
                .replace("fsu_", "fsu:")
                .replace("FSU_", "fsu:")
                .removesuffix("_MODS")
            )

            # parse records
            for parsed_record in assets.parse_mods_stream(
                    stream):

                if args.verbose:
                    print(
                        f"Parsed... {pid}"
                    )

                author_names = []

                # Pass 1 - explicit creators/authors
                for name in parsed_record.names:

                    role = getattr(
                        name,
                        "role",
                        None
                    )

                    if not role:
                        continue

                    role_code = (
                            getattr(
                                role,
                                "code",
                                None
                            ) or ""
                    ).lower()

                    if role_code in (
                            "aut",
                            "cre"):
                        author_names.append(
                            name
                        )

                # Pass 2 - primary personal name
                if not author_names:

                    primary_names = [
                        n
                        for n in parsed_record.names
                        if getattr(
                            n,
                            "type",
                            None
                        ) == "personal"
                           and n.elem.get(
                            "usage"
                        ) == "primary"
                    ]

                    if primary_names:
                        author_names.append(
                            primary_names[0]
                        )

                        fallback_primary_count += 1

                        logger.debug(
                            f"{pid}... "
                            f"Using primary personal "
                            f"name as author: "
                            f"{primary_names[0].text}"
                        )

                # Pass 3 - first personal name
                if not author_names:

                    personal_names = [
                        n
                        for n in parsed_record.names
                        if getattr(
                            n,
                            "type",
                            None
                        ) == "personal"
                    ]

                    if personal_names:
                        author_names.append(
                            personal_names[0]
                        )

                        fallback_personal_count += 1

                        logger.debug(
                            f"{pid}... "
                            f"Using first personal "
                            f"name as author: "
                            f"{personal_names[0].text}"
                        )

                # write authors
                for name in author_names:

                    author = assets.AuthorRecord(
                        name
                    )

                    author_data = {
                        "firstname":
                            author.firstname,
                        "surname":
                            author.surname,
                        "email":
                            author.email,
                        "orcid":
                            author.orcid,
                        "identity":
                            author.identity_key,
                    }

                    author_id = (
                        write_author_record(
                            db_conn,
                            author_data
                        )
                    )

                    if author_id:
                        link_author_to_object(
                            db_conn,
                            pid,
                            author_id
                        )

                logger.info(
                    "Writing record",
                    extra={
                        "pid": pid,
                        "collection":
                            collection,
                    }
                )

                assets.write_db_record(
                    db_conn,
                    pid,
                    parsed_record,
                    collection
                )

                count += 1

                if count % BATCH_SIZE == 0:
                    elapsed = (
                            time.perf_counter()
                            - start
                    )

                    db_conn.commit()
                    db_conn.execute(
                        "BEGIN"
                    )

                    logger.info(
                        "Processed %s records "
                        "in %.1f sec "
                        "(%.1f rec/sec)",
                        f"{count:,}",
                        elapsed,
                        count / elapsed,
                    )

        db_conn.commit()

        logger.info(
            f"Primary-name fallback authors: "
            f"{fallback_primary_count:,}"
        )

        logger.info(
            f"First-personal fallback authors: "
            f"{fallback_personal_count:,}"
        )

    # CLI status
    if args.status:
        print(assets.get_db_status(db_conn))

    # CLI burndown
    if args.burndown:

        for fpath in (
                DB_PATH,
                TSV_LOG_PATH,
        ):

            try:
                os.remove(fpath)
                logger.info(f"Removed... {fpath}")

            except FileNotFoundError:
                logger.info(
                    f"Already absent... {fpath}"
                )

    # Close DB connection
    db_conn.close()
    sys.exit(0)
