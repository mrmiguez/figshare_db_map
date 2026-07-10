import os
import sys
import time
import assets
import logging
from pathlib import Path

from assets import write_author_record, link_author_to_object

PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PATH, 'figshare_record_tables.sqlite3')
logger = logging.getLogger('figshare_db_map')
logging.basicConfig(level=logging.INFO)

# TSV logging
from assets.tsv_logger import TSVHandler

tsv_handler = TSVHandler("figshare_db_map.tsv")
tsv_handler.setLevel(logging.DEBUG)

logging.getLogger().addHandler(tsv_handler)

if __name__ == '__main__':
    # Connect DB
    db_conn = assets.connect_db(DB_PATH)
    # Parse args
    args = assets.argument_parser().parse_args()
    logger.debug(f'Args... {args}')

    # CLI run
    if args.run:

        # DB commit batching
        db_conn.execute("BEGIN")
        BATCH_SIZE = 1000
        count = 0
        start = time.perf_counter()

        # iterate over files in dir structure
        for f in Path(args.record_directory).rglob('*MODS.xml'):
            logger.info(f'Reading... {f}')
            pid = f.stem.replace('fsu_', 'fsu:').replace('FSU_', 'fsu:').removesuffix('_MODS')

            # parse records
            for parsed_record in assets.parse_mods_stream(f):
                if args.verbose:
                    print(f'Parsed... {pid}')

                for name in parsed_record.names:

                    if name.role.code not in ('cre', 'aut'):
                        logger.info(f"Skipping non-author role... {name.text}")
                        continue

                    author = assets.AuthorRecord(name)

                    author_data = {
                        "firstname": author.firstname,
                        "surname": author.surname,
                        "email": author.email,
                        "orcid": author.orcid,
                        "identity": author.identity_key,
                    }

                    author_id = write_author_record(db_conn, author_data)
                    if author_id:
                        link_author_to_object(db_conn, pid, author_id)

                logger.info("Writing record",
                            extra={
                                "pid": pid,
                                "collection": str(f.parent)
                            }
                            )

                assets.write_db_record(db_conn, pid, parsed_record, f.parent)

                # batching DB commits
                count += 1

                if count % BATCH_SIZE == 0:
                    elapsed = time.perf_counter() - start
                    db_conn.commit()
                    db_conn.execute("BEGIN")
                    logger.info("Processed %s records in %.1f sec (%.1f rec/sec)",
                                f"{count:,}", elapsed, count / elapsed)

    # CLI status
    if args.status:
        print(assets.get_db_status(db_conn))

    # CLI burndown
    if args.burndown:
        if args.verbose:
            print(f'Removing database... {DB_PATH}')
        logger.info(f'Removing database... {DB_PATH}')
        os.remove(DB_PATH)

    # Close DB connection
    db_conn.close()
    sys.exit(0)
