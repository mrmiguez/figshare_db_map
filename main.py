import os
import glob
import pymods
import assets
import logging
import argparse

PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PATH, 'figshare_record_tables.sqlite3')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    db_conn = assets.connect_db(DB_PATH)
    args = assets.argument_parser().parse_args()
    print(args)  #test

    if args.status:
        print(assets.get_db_status(db_conn))

    if args.burndown:
        os.remove(DB_PATH)

    if args.run:
        for f in glob.iglob(os.path.join(args.records, '*.xml')):
            for rec in assets.parse_mods_stream(f):
                print(rec)


