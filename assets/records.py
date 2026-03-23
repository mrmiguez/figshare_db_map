import re
import logging
import collections
from selectors import SelectSelector

from lxml.etree import ElementBase

mods = 'http://www.loc.gov/mods/v3'
NS = {"mods": "http://www.loc.gov/mods/v3",}

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Named tuple definitions
Abstract = collections.namedtuple('Abstract', 'text type displayLabel')
Collection = collections.namedtuple('Collection', 'location title url')
Date = collections.namedtuple('Date', 'text type')
Genre = collections.namedtuple('Genre', 'text uri authority authorityURI')
Identifier = collections.namedtuple('Identifier', 'type text')
Language = collections.namedtuple('Language', 'text code authority')
Name = collections.namedtuple('Name', 'text type uri authority authorityURI role')
NamePart = collections.namedtuple('NamePart', 'text type')
Note = collections.namedtuple('Note', 'text type displayLabel')
PublicationPlace = collections.namedtuple('PublicationPlace', 'text type')
Rights = collections.namedtuple('Rights', 'text type uri')
Role = collections.namedtuple('Role', 'text code authority')
Subject = collections.namedtuple('Subject', 'text uri authority authorityURI')
SubjectPart = collections.namedtuple('SubjectPart', 'text type')

class Record(ElementBase):

    def __init__(self):
        super(Record, self).__init__()

    def _clean_text(self, text):
        mark_up_re = re.compile('<.*?>')
        new_line_re = re.compile('\n')
        date_time_code_re = re.compile('T\\d{2}:\\d{2}:\\d{2}Z')

        # remove extraneous leading and trailing characters
        clean_text = text.strip(':').strip(' ')

        # remove markup
        clean_text = re.sub(mark_up_re, '', clean_text)

        # remove newlines
        clean_text = re.sub(new_line_re, ' ', clean_text)

        # remove timecode data trailing a date
        clean_text = re.sub(date_time_code_re, '', clean_text)
        return clean_text


class ObjectRecord(Record):

    def __init__(self, record):
        super(ObjectRecord, self).__init__()
        self.record = record

    ###########################################################################
    # Figshare Metadata Schema Overview:                                      #
    # https://info.figshare.com/user-guide/figshare-metadata-schema-overview/ #
    #   - IID being used as object table DB key                               #
    ###########################################################################

    # IID
    @property
    def iid(self):
        return self.record.find('mods:identifier[@type="IID"]', NS).text

    # Titles
    @property
    def titles(self):
        return [title for title in self._title_part()]

    # Authors/Names
    @property
    def names(self):
        names = []
        for name in self.record.findall('mods:name', NS):
            # todo: make this work rite

            #name_text = ''
            try:
                name_text = ', '.join(name.find('mods:namePart[@type="family"]', NS).text, name.find('mods:namePart[@type="given"]', NS).text, name.find('mods:namePart[@type="dates"]', NS).text)
            except AttributeError:
                name_text = ', '.join([name.text for name in name.findall('mods:namePart', NS)])
            # elif name.find('mods:namePart[@type="family"]', NS) and name.find('mods:namePart[@type="given"]', NS) and not name.find('mods:namePart[@type="date"]', NS):
            #     name_text = ', '.join([name.find('mods:namePart[@type="family"]', NS).text, name.find('mods:namePart[@type="given"]', NS).text])
            # elif not name.find('mods:namePart[@type="family"]', NS) and not name.find('mods:namePart[@type="given"]', NS) and name.find('mods:namePart[@type="date"]', NS):
            #     name_text = ', '.join([name.findall('mods:namePart[not(@type)]', NS).text]) + ', ' + name.find('mods:namePart[@type="date"]', NS).text
            names.append(Name(name_text,
                              name.get('type'),
                              name.get('valueURI'),
                              name.get('authority'),
                              name.get('authorityURI'),
                              ', '.join([name_role.text for name_role in name.iterfind('mods:role/mods:roleTerm', NS)])))

        """
        return [Name(', '.join([name.find('mods:namePart[@type="family"]', NS).text,
                                name.find('mods:namePart[@type="given"]', NS).text,
                                name.find('mods:namePart[@type="date"]', NS).text]),
                     name.get('type'),
                     name.get('valueURI'),
                     name.get('authority'),
                     name.get('authorityURI'),
                     ', '.join([name_role.text for name_role in name.iterfind('mods:role/mods:roleTerm', NS)]),)
                for name in self.record.iterfind('mods:name', NS)]
        """

        return names


    # Categories
    # Constrained value list - https://docs.figshare.com/#categories_list

    # Item type
    # Constrained value list - https://help.figshare.com/article/item-types

    # Keywords

    # Description

    # License
    # Constrained value list

    # Publication/Published Date

    # Identifiers
    @property
    def identifiers(self):
        return [Identifier(identifier.attrib.get('type'), identifier.text) for identifier in self.record.findall('mods:identifier', NS)]

    # Semi-private methods
    def _get_text(self, elem):
        """Wrapping common use of getattr for safe attribute access."""
        return getattr(elem, 'text', None)

    def _name_part(self, elem=None):
        if elem is None:
            elem = self
        return [NamePart(name.text, name.attrib.get('type'), name) for name in
                elem.iterfind('./{0}namePart'.format(mods))]

    def _name_role(self, elem=None):
        if elem is None:
            elem = self
        return Role(elem._name_role_text(), elem._name_role_code(), elem._name_role_authority(), elem)

    def _name_role_authority(self):
        try:
            return self.find('.//{0}roleTerm'.format(mods)).attrib.get('authority')
        except AttributeError:
            return None

    def _name_role_code(self):
        try:
            return self.find('.//{0}roleTerm[@type="code"]'.format(mods)).text
        except AttributeError:
            return None

    def _name_role_text(self):
        try:
            return self.find('.//{0}roleTerm[@type="text"]'.format(mods)).text
        except AttributeError:
            return None

    def _name_text(self, elem=None):
        if elem is None:
            elem = self
        if elem.attrib.get('type') == 'personal':
            family = ', '.join(x.text for x in elem._name_part() if x.type == 'family')
            given = ', '.join(x.text for x in elem._name_part() if x.type == 'given')
            terms_of_address = ', '.join(x.text for x in elem._name_part() if x.type == 'termsOfAddress')
            date = ', '.join(x.text for x in elem._name_part() if x.type == 'date')
            untyped_name = ', '.join(x.text for x in elem._name_part() if x.type is None)
            return '{family}{given}{termsOfAddress}{untyped_name}{date}'.format(
                family=family + ', ' if family else '',
                given=given if given else '',
                termsOfAddress=', ' + terms_of_address if terms_of_address else '',
                untyped_name=untyped_name if untyped_name else '',
                date=', ' + date if date else ''
            )
        else:
            text = ''
            for part in elem.iter(tag='{0}namePart'.format(mods)):
                text = text + '{0}, '.format(part.text)
            return text.strip(', ')

    def _title_part(self, elem=None):
        """
        :param elem: The element containing a mods:titleInfo elements (i.e. mods:mods or mods:relatedItem).
        :return: A list of correctly formatted titles.
        """
        if elem is None:
            elem = self.record
        return [self._title_text(
            self._get_text(title.find('mods:nonSort', NS)),
            self._get_text(title.find('mods:title', NS)),
            self._get_text(title.find('mods:subTitle', NS)))
            for title in elem.iterfind('mods:titleInfo', NS)]

    def _title_text(self, non_sort, title, subtitle):
        """Construct valid title regardless if any constituent part missing."""
        return '{non_sort}{title}{subtitle}'.format(
            non_sort=non_sort + ' ' if non_sort else '',
            title=title if title else '',
            subtitle=': ' + subtitle if subtitle else '')


class AuthorRecord(Record):

    def __init__(self, record):
        Record.__init__(self)
        self.record = record

