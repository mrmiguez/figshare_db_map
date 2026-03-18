import logging
import lxml.etree as ET

# register namespaces
NS = {"mods": "http://www.loc.gov/mods/v3",}
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def parse_mods_stream(path):
    """Stream-parse a MODS XML file and yield dicts per record"""

    context = ET.iterparse(path, events=('end',), tag='{http://www.loc.gov/mods/v3}mods')
    for event, elem in context:
        record = {}

        # Title
        title_elem = elem.find('mods:titleInfo/mods:title', NS)
        if title_elem is not None:
            record['title'] = title_elem.text

        # Names
        record['names'] = [
            name_elem.text
            for name_elem in elem.findall('mods:name/mods:namePart', NS)
            if name_elem.text
        ]

        # Identifiers
        record['identifiers'] = [
            (id_elem.get('type'), id_elem.text)
            for id_elem in elem.findall('mods:identifier', NS)
            if id_elem.text
        ]

        # IID
        record['iid'] = elem.find('mods:identifier[@type="IID"]', NS).text
        logger.info(f'Parsing... {record["iid"]}')

        # Resource type
        type_elem = elem.find('mods:typeOfResource', NS)
        if type_elem is not None:
            record['resource_type'] = type_elem.text

        yield record

        # Free memory
        elem.clear()
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)