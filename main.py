import os
import sys
import glob
import assets
import logging
from pathlib import Path

from assets import write_author_record, link_author_to_object

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

    # CLI run
    if args.run:

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
                        logger.warning(f"Skipping non-author role... {name.text}")
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
                    link_author_to_object(db_conn, pid, author_id)

                logger.info(f'Writing record to DB... {pid}')
                #print("...write to DB...") # test
                assets.write_db_record(db_conn, pid, parsed_record)

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
