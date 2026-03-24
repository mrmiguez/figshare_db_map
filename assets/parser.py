import logging
import pymods

from assets.records import ObjectRecord, AuthorRecord

# register namespaces
NS = {"mods": "http://www.loc.gov/mods/v3",}
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def parse_mods_stream(path):
    records = pymods.MODSReader(path)
    for record in records:
        #print(record.iid) # test
        print(record.names) # test
        yield record

