import os
import sys
import glob
import pymods
import assets
import logging
import argparse

PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PATH, 'figshare_record_tables.sqlite3')
logger = logging.getLogger('figshare_db_map')
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Connect DB
    db_conn = assets.connect_db(DB_PATH)
    # Parse args
    args = assets.argument_parser().parse_args()
    logger.debug(f'Args... {args}')

    # CLI status
    if args.status:
        print(assets.get_db_status(db_conn))

    # CLI burndown
    if args.burndown:
        if args.verbose:
            print(f'Removing database... {DB_PATH}')
        logger.info(f'Removing database... {DB_PATH}')
        os.remove(DB_PATH)

    # CLI run
    if args.run:
        for f in glob.iglob(os.path.join(args.record_directory, '*.xml')):
            logger.info(f'Reading... {os.path.join(args.record_directory, f)}')
            for parsed_record in assets.parse_mods_stream(f):
                if args.verbose:
                    print(f'Parsed... {parsed_record.iid}')

                # object_record = assets.ObjectRecord(parsed_record)
                # assets.write_db_record(db_conn, object_record)

                logger.info(f'Writing record to DB... {parsed_record.iid}')
                logger.debug(f'Writing record to DB... {parsed_record}')
                assets.write_db_record(db_conn, parsed_record)

    # Close DB connection
    db_conn.close()
    sys.exit(0)
