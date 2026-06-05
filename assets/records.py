import re
import logging
import unicodedata
import collections
from selectors import SelectSelector

from lxml.etree import ElementBase

mods = 'http://www.loc.gov/mods/v3'
NS = {"mods": "http://www.loc.gov/mods/v3",}

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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


class AuthorRecord:

    def __init__(self, name):
        self.name = name
        self.element = name.elem  # 🔥 real lxml node

    # -------------------------
    # Normalization helpers
    # -------------------------

    def _clean_text(self, text):
        if not text:
            return None

        # strip leading/trailing punctuation/space
        text = text.strip(':').strip()

        # remove basic XML-ish markup artifacts
        text = re.sub(r'<.*?>', '', text)

        # remove newlines
        text = text.replace('\n', ' ')

        # remove ISO datetime fragments
        text = re.sub(r'T\d{2}:\d{2}:\d{2}Z', '', text)

        return text.strip()

    def _normalize_str(self, value):
        if not value:
            return None

        value = self._clean_text(value)

        value = unicodedata.normalize("NFKD", value)
        value = value.lower()
        value = " ".join(value.split())

        return value

    def _xpath_first(self, path):
        nodes = self.element.xpath(path, namespaces=NS)
        return nodes[0] if nodes else None

    # -------------------------
    # Name extraction
    # -------------------------

    @property
    def firstname(self):
        node = self._xpath_first("mods:namePart[@type='given']")
        if node is not None and node.text:
            return self._clean_text(node.text)

        # fallback to flat text
        if self.name.text:
            return self._split_name(self.name.text)[0]

        return None

    @property
    def surname(self):
        node = self._xpath_first("mods:namePart[@type='family']")
        if node is not None and node.text:
            return self._clean_text(node.text)

        if self.name.text:
            return self._split_name(self.name.text)[1]

        return None

    def _split_name(self, text):
        text = self._clean_text(text)
        if not text:
            return (None, None)

        # Handle "Last, First"
        if "," in text:
            last, first = [p.strip() for p in text.split(",", 1)]
            return first, last

        parts = text.split()
        if len(parts) == 1:
            return (parts[0], None)

        return (parts[0], parts[-1])

    # -------------------------
    # Identifier extraction
    # -------------------------

    @property
    def orcid(self):
        node = self._xpath_first("mods:nameIdentifier[@type='orcid']")

        # Case 1: text node
        if node is not None:
            if node.text:
                val = self._clean_text(node.text)
                return self._normalize_orcid(val)

            # Case 2: valueURI
            uri = node.get("valueURI")
            if uri:
                return self._normalize_orcid(uri)

        return None

    def _normalize_orcid(self, value):
        if not value:
            return None

        value = value.strip()

        # strip URI prefix if present
        value = value.replace("https://orcid.org/", "")
        value = value.replace("http://orcid.org/", "")

        return value

    @property
    def email(self):
        node = self._xpath_first("mods:nameIdentifier[@type='email']")
        if node is not None and node.text:
            return self._clean_text(node.text)

        return None

    # -------------------------
    # Identity key (🔥 important)
    # -------------------------

    @property
    def identity_key(self):
        """
        Priority order:
        1. ORCID (best)
        2. URI (less common but useful)
        3. Normalized nameParts
        4. Fallback to flattened name text
        """

        # 1. ORCID
        if self.orcid:
            return f"orcid:{self._normalize_str(self.orcid)}"

        # 2. valueURI on <name>
        if self.name.uri:
            return f"uri:{self._normalize_str(self.name.uri)}"

        # 3. structured name parts
        first = self._normalize_str(self.firstname)
        last = self._normalize_str(self.surname)

        if first or last:
            return f"name:{first}|{last}"

        # 4. fallback raw text
        if self.name.text:
            return f"text:{self._normalize_str(self.name.text)}"

        return None