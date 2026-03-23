import logging
import lxml.etree as ET

from assets.records import ObjectRecord, AuthorRecord

# register namespaces
NS = {"mods": "http://www.loc.gov/mods/v3",}
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def parse_mods_stream(path):
    """Stream-parse a MODS XML file and yield dicts per record"""

    context = ET.iterparse(path, events=('end',), tag='{http://www.loc.gov/mods/v3}mods')
    for event, elem in context:

        record = ObjectRecord(elem)
        print(record.names)
        yield record

        # Free memory
        elem.clear()
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)