import re
import logging
import unicodedata

from lxml.etree import ElementBase
from .data_maps import STRIP_VALUES, LICENSE_MAP, TYPE_MAP

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


class ObjectRecord:

    def __init__(self, pid, record):
        self.record = record
        self.pid = pid

    # ------------------
    # Helper methods
    # ------------------

    def _clean_text(self, text):
        if not text:
            return None

        text = text.strip(':').strip()
        text = re.sub(r'&lt;.*?&gt;', '', text)
        text = text.replace('\n', ' ')
        text = re.sub(r'T\d{2}:\d{2}:\d{2}Z', '', text)

        return text.strip()

    def _first(self, values):
        return values[0] if values else None

    def _join_pipe(self, values):
        vals = [self._clean_text(v) for v in values if v]
        vals = [v for v in vals if v]
        return "|".join(vals) if vals else None

    def _license_fallback(self, text):
        """
        Catch high-frequency boilerplate patterns
        """

        # ---- InC-EDU cluster (~most of your data)
        if (
                "freely accessible" in text
                or "educational use" in text
                or "research use" in text
        ):
            return "http://rightsstatements.org/vocab/InC-EDU/1.0/"

        # ---- Plain InC
        if (
                "copyright of this work is held" in text
                or "permission from the rights-holder" in text
                or "further use may require permission" in text
        ):
            return "http://rightsstatements.org/vocab/InC/1.0/"

        # ---- Public domain
        if "public domain" in text:
            return "http://rightsstatements.org/vocab/NoC-US/1.0/"

        # ---- NoC-NC edge
        if "non-commercial use" in text and "freely accessible" not in text:
            return "http://rightsstatements.org/vocab/NoC-NC/1.0/"

        #logger.info(f'Assigning default statement... {self.pid}')
        #return 'http://rightsstatements.org/vocab/CNE/1.0/' # default rights URI
        return None

    def _normalize_genre(self, text):
        if not text:
            return None

        text = self._clean_text(text)

        if not text:
            return None

        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = text.rstrip(".:;")

        return text

    def _normalize_label(self, label):
        label = self._clean_text(label)

        if not label:
            return ""

        return label.lower()

    def _normalize_license(self, val):
        if not val:
            return None

        val = self._clean_text(val)
        if not val:
            return None

        val = val.lower()
        val = " ".join(val.split())

        if val in STRIP_VALUES:
            return None

        return val

    # -----------------------
    # Metadata properties
    # -----------------------

    # ---- contributors
    @property
    def contributors(self):
        values = []

        for name in getattr(self.record, "name", []):

            role = getattr(name, "role", None)

            role_text = (
                (role.text or "").strip().lower()
                if role else ""
            )

            role_code = (
                (role.code or "").strip().lower()
                if role else ""
            )

            if role_text in {"creator", "author"}:
                continue

            if role_code in {"cre", "aut"}:
                continue

            if not name.text:
                continue

            if role_text:
                values.append(f"{name.text} ({role_text})")
            elif role_code:
                values.append(f"{name.text} ({role_code})")
            else:
                values.append(name.text)

        return self._join_pipe(values)

    # ---- description (abstract)
    @property
    def description(self):
        texts = [a.text for a in self.record.abstract if a.text]
        return "\n\n".join(self._clean_text(t) for t in texts) if texts else None

    # ---- journal issue
    @property
    def issue(self):
        for rel in getattr(self.record, "related_item", []):

            for detail in getattr(rel, "detail", []):

                if detail.elem.get("type", "").lower() == "issue":

                    number = getattr(detail, "number", None)

                    if number:
                        return self._clean_text(number)

        return None

    # ---- item_type (genre mapping)
    @property
    def item_type(self):

        for genre in getattr(self.record, "genre", []):

            key = self._normalize_genre(genre.text)

            if not key:
                continue

            if key in TYPE_MAP:
                return TYPE_MAP[key]

            if "thesis" in key or "dissertation" in key:
                return "Thesis"

            if "report" in key:
                return "Report"

            if "dataset" in key:
                return "Dataset"

            if "poster" in key:
                return "Poster"

            if "conference" in key:
                return "Conference contribution"

            if any(x in key for x in ("video", "sound", "audio", "film")):
                return "Media"

            if any(x in key for x in ("map", "model", "design")):
                return "Model"

        logger.debug(
            "Unmapped genres: %s",
            [g.text for g in getattr(self.record, "genre", []) if g.text]
        )

        return "Journal contribution"

    # ---- journal title
    @property
    def journal_title(self):
        for rel in getattr(self.record, "related_item", []):

            rel_type = rel.elem.get("type", "").lower()

            if rel_type in ("host", "series"):

                title_info = getattr(rel, "title_info", None)

                if title_info and getattr(title_info, "title", None):
                    return self._clean_text(title_info.title)

        return None

    # ---- keywords (note@displayLabel="keywords")
    @property
    def keywords(self):
        kws = []

        for note in getattr(self.record, "note", []):

            if self._normalize_label(note.displayLabel) != "keywords":
                continue

            if not note.text:
                continue

            kws.extend(
                kw.strip()
                for kw in note.text.split(",")
                if kw.strip()
            )

        return self._join_pipe(kws)

    # ---- language
    @property
    def language(self):
        langs = []

        for l in getattr(self.record, "language", []):
            if l.text:
                langs.append(l.text)

        return self._join_pipe(langs)

    # ---- license (accessCondition)
    @property
    def license(self):
        ac_list = getattr(self.record, "rights", [])

        if not ac_list:
            logger.info(f"No rights found on record... {self.pid}")
            return 'http://rightsstatements.org/vocab/CNE/1.0/' # default rights URI

        for r in ac_list:
            raw_values = []

            if r.uri:
                raw_values.append(r.uri)

            if r.text:
                raw_values.append(r.text)

            for raw in raw_values:
                cleaned = self._normalize_license(raw)
                if not cleaned:
                    continue

                # ---- direct URI pass-through
                if raw.startswith("http"):
                    return raw.strip()

                # ---- normalized URI (in case clean_text changed it)
                if cleaned.startswith("http://rightsstatements.org/"):
                    return cleaned

                # ---- CC URLs
                if "creativecommons.org" in cleaned:
                    return cleaned

                # ---- direct lookup
                if cleaned in LICENSE_MAP:
                    return LICENSE_MAP[cleaned]

                # ---- fallback pattern matching (use RAW, not cleaned)
                fallback = self._license_fallback(raw.lower())
                if fallback:
                    return fallback

                # ---- debug unmatched cases
                logger.info(f"Unmatched license value: {raw[:120]}")

        logger.info(f'Assigning default statement... {self.pid}')
        #return 'http://rightsstatements.org/vocab/CNE/1.0/' # default rights URI
        return None

    # ---- notes
    @property
    def notes(self):
        values = []

        for note in getattr(self.record, "note", []):

            if self._normalize_label(note.displayLabel) == "keywords":
                continue

            if note.text:
                values.append(note.text)

        return self._join_pipe(values)

    # ---- other identifiers (doi &/or handle)
    @property
    def other_identifiers(self):
        vals = []

        for ident in getattr(self.record, "identifier", []):

            if ident.type and ident.type.lower() == "iid":
                continue

            value = self._clean_text(ident.text)

            if value:
                vals.append(
                    f"{ident.type}:{value}"
                    if ident.type else value
                )

        return self._join_pipe(vals)

    # ---- physical location
    @property
    def physical_location(self):
        locs = []

        for loc in getattr(self.record, "location", []):

            physical = getattr(loc, "physical", None)

            if physical:
                locs.append(physical)

        return self._join_pipe(locs)

    # ---- publication date
    @property
    def publication_date(self):
        """Normalized to YYYY-MM-DD for Figshare compatibility"""

        def normalize(date_str):
            if not date_str:
                return None
            date_str = self._clean_text(date_str)

            if len(date_str) == 4:
                return f"{date_str}-01-01"
            if len(date_str) == 7:
                return f"{date_str}-01"
            return date_str

        oi = getattr(self.record, "origin_info", None)
        if not oi:
            return None

        for d in getattr(oi, "date_issued", []):
            if d.elem.get("keyDate") == "yes":
                return normalize(d.text)

        if getattr(oi, "date_issued", []):
            return normalize(oi.date_issued[0].text)

        if getattr(oi, "date_created", []):
            return normalize(oi.date_created[0].text)

        return None



    # ---- publisher
    @property
    def publisher(self):
        oi = getattr(self.record, "origin_info", None)

        if not oi:
            return None

        publishers = [
            self._clean_text(p)
            for p in getattr(oi, "publisher", [])
            if p
        ]

        return self._join_pipe(publishers)

    # ---- purl
    @property
    def purl(self):
        urls = []

        for loc in getattr(self.record, "location", []):

            url = getattr(loc, "url", None)

            if url:
                urls.append(url)

        return self._join_pipe(urls)

    # ---- subjects
    @property
    def subjects(self):
        values = []

        for subject in getattr(self.record, "subject", []):

            if subject.text:
                values.append(subject.text)

        return self._join_pipe(values)

    # ---- title
    @property
    def title(self):
        val = self._first(self.record.titles)
        return self._clean_text(val)

    # ---- journal volume
    @property
    def volume(self):
        for rel in getattr(self.record, "related_item", []):

            for detail in getattr(rel, "detail", []):

                if detail.elem.get("type", "").lower() == "volume":

                    number = getattr(detail, "number", None)

                    if number:
                        return self._clean_text(number)

        return None


class AuthorRecord:

    def __init__(self, name):
        self.name = name
        self.element = name.elem  # real lxml node

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

    # ---------------
    # Identity key
    # ---------------

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
