import re
import logging
import unicodedata

from datetime import datetime
from lxml.etree import ElementBase
from .data_maps import *

mods = 'http://www.loc.gov/mods/v3'
NS = {"mods": "http://www.loc.gov/mods/v3", }

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ORCID_RE = re.compile(
    r"^(\d{4}-\d{4}-\d{4}-[\dX]{4})$",
    re.IGNORECASE
)

def _fix_mojibake(value):
    if not value:
        return value

    if not any(
            marker in value
            for marker in MOJIBAKE_MARKERS
    ):
        return value

    try:
        return value.encode("latin1").decode("utf-8")
    except Exception:
        return value


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

    def __init__(self, pid, record, collection_path=None):
        self.record = record
        self.pid = pid
        self.collection_path = collection_path

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
        text = _fix_mojibake(text)

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

        # logger.info(f'Assigning default statement... {self.pid}')
        # return 'http://rightsstatements.org/vocab/CNE/1.0/' # default rights URI
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

    def _normalize_identifier(self, ident_type, value):

        if not value:
            return None

        value = self._clean_text(value)

        ident_type = (
            ident_type.lower().strip()
            if ident_type
            else None
        )

        # DOI cleanup
        if ident_type == "doi":
            value = re.sub(
                r"^https?://(dx\.)?doi\.org/",
                "",
                value,
                flags=re.I
            )

            return f"doi:{value}"

        # Handle cleanup

        if ident_type in ("hdl", "handle"):
            value = re.sub(
                r"^https?://hdl\.handle\.net/",
                "",
                value,
                flags=re.I
            )

            return f"handle:{value}"

        return (
            f"{ident_type}:{value}"
            if ident_type
            else value
        )

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

    # ------------------------------------------------------------------
    # Category helpers
    # ------------------------------------------------------------------

    def _get_collection_categories(self):
        categories = set()

        if not self.collection_path:
            return categories

        path = str(self.collection_path).lower()

        for collection, values in COLLECTION_FOR_MAP.items():

            if collection.lower() in path:
                categories.update(values)

        return categories

    def _get_subject_categories(self):

        categories = set()

        if not self.subjects:
            return categories

        subject_terms = [
            s.strip().lower()
            for s in self.subjects.split("|")
        ]

        for subject in subject_terms:

            subject = SUBJECT_NORMALIZATION.get(
                subject,
                subject
            )

            if subject in SUBJECT_FOR_MAP:
                categories.update(
                    SUBJECT_FOR_MAP[subject]
                )

        return categories

    # -----------------------
    # Metadata properties
    # -----------------------

    # ---- category Figshare Field of Research (FoR)

    @property
    def categories(self):

        categories = set()

        categories.update(
            self._get_collection_categories()
        )

        categories.update(
            self._get_subject_categories()
        )

        return "|".join(str(c) for c in sorted(categories))

    # ---- contributors
    @property
    def contributors(self):
        values = []

        for name in getattr(self.record, "names", []):

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

        candidates = set()

        for genre in getattr(self.record, "genre", []):

            key = self._normalize_genre(genre.text)

            if not key:
                continue

            if key in IGNORED_GENRES:
                continue

            # strongest signal
            if "thesis" in key or "dissertation" in key:
                candidates.add("Thesis")
                continue

            # direct mapping
            if key in TYPE_MAP:
                candidates.add(TYPE_MAP[key])
                continue

            # heuristic mappings
            if "report" in key:
                candidates.add("Report")

            elif "dataset" in key:
                candidates.add("Dataset")

            elif "poster" in key:
                candidates.add("Poster")

            elif "conference" in key:
                candidates.add("Conference contribution")

            elif any(
                    x in key
                    for x in (
                            "video",
                            "sound",
                            "audio",
                            "film"
                    )
            ):
                candidates.add("Media")

            elif any(
                    x in key
                    for x in (
                            "map",
                            "model",
                            "design"
                    )
            ):
                candidates.add("Model")

        # choose the highest-priority mapped type
        if candidates:
            return max(
                candidates,
                key=lambda x:
                TYPE_PRIORITY.get(x, 0)
            )

        path = str(self.collection_path).lower()

        if any(
                x in path
                for x in (
                        "fsu_etds",
                        "fsu_retroetds",
                        "fsu_honors_theses",
                )
        ):
            return "Thesis"

        logger.debug(
            "Unmapped genres: %s",
            [
                g.text
                for g in getattr(self.record, "genre", [])
                if g.text
            ]
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

    # ---- keywords (keywords note + subjects)
    @property
    def keywords(self):

        terms = []

        # Existing keywords
        for note in getattr(self.record, "note", []):

            if self._normalize_label(note.displayLabel) != "keywords":
                continue

            if not note.text:
                continue

            terms.extend(
                kw.strip()
                for kw in note.text.split(",")
                if kw.strip()
            )

        # Add subject terms
        for subject in self.subjects.split("|") if self.subjects else []:

            subject = subject.strip()

            if subject:
                terms.append(subject)

        # Case-insensitive deduplication preserving first occurrence
        seen = set()
        deduped = []

        for term in terms:

            key = term.casefold()

            if key in seen:
                continue

            seen.add(key)
            deduped.append(term)

        return self._join_pipe(sorted(deduped, key=str.casefold))

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

        rights = getattr(self.record, "rights", [])

        if not rights:
            logger.info(
                f"No rights found on record... {self.pid}"
            )
            return 'http://rightsstatements.org/vocab/CNE/1.0/'

        for r in rights:

            raw_values = []

            if r.uri:
                raw_values.append(r.uri)

            if r.text:
                raw_values.append(r.text)

            for raw in raw_values:

                if not raw:
                    continue

                raw = raw.strip()

                # -----------------------------------
                # Direct URI normalization
                # -----------------------------------

                if raw.startswith("http"):
                    return LICENSE_URL_MAP.get(
                        raw,
                        raw
                    )

                # -----------------------------------
                # Text normalization
                # -----------------------------------

                cleaned = self._normalize_license(raw)

                if not cleaned:
                    continue

                mapped = LICENSE_TEXT_MAP.get(
                    cleaned
                )

                if mapped:
                    return mapped

                # fallback pattern matching
                fallback = self._license_fallback(
                    raw.lower()
                )

                if fallback:
                    return fallback

                logger.info(
                    f"Unmatched license value... {self.pid}: {raw[:120]}"
                )

        logger.info(
            f"Assigning default statement... {self.pid}"
        )

        return 'http://rightsstatements.org/vocab/CNE/1.0/'

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

        for ident in getattr(self.record, "identifiers", []):

            if ident.type and ident.type.lower() == "iid":
                continue

            normalized = self._normalize_identifier(
                ident.type,
                ident.text
            )

            if normalized:
                vals.append(normalized)

        # Add PURLs
        for purl in getattr(self.record, "purl", []):
            if not purl:
                continue
            if purl and purl not in vals:
                vals.append(purl)

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

        def normalize(date_str):

            if not date_str:
                return None

            date_str = self._clean_text(date_str).strip()

            # Drop ranges
            if " - " in date_str:
                date_str = date_str.split(" - ")[0]

            # Null-equivalent values
            if date_str.lower() in {
                "n/a",
                "not published",
            }:
                return None

            # Remove circa / trailing punctuation
            date_str = re.sub(r"^c\.\s*", "", date_str)
            date_str = date_str.rstrip(".")

            # YYYY Copyright...
            # YYYY © ...
            # YYYY, Person Name
            match = re.match(r"^((?:19|20)\d{2})", date_str)

            if (
                    match
                    and not re.match(
                r"^\d{4}(-\d{2})?(-\d{2})?$",
                date_str
            )
            ):
                return f"{match.group(1)}-01-01"

            # YYYY
            if re.match(r"^\d{4}$", date_str):
                return f"{date_str}-01-01"

            # YYYY-MM
            if re.match(r"^\d{4}-\d{2}$", date_str):
                return f"{date_str}-01"

            # Month YYYY
            try:

                dt = datetime.strptime(
                    date_str,
                    "%B %Y"
                )

                return dt.strftime(
                    "%Y-%m-01"
                )

            except ValueError:
                pass

            # Flexible formats
            for fmt in (
                    "%Y-%m-%d",
                    "%Y/%m/%d",
                    "%m/%d/%Y",
                    "%m/%d/%y",
                    "%m-%d-%Y",
                    "%m-%d-%y",
            ):

                try:

                    dt = datetime.strptime(
                        date_str,
                        fmt
                    )

                    return dt.strftime(
                        "%Y-%m-%d"
                    )

                except ValueError:
                    continue

            # YYYY-M-D
            match = re.match(
                r"^(\d{4})-(\d{1,2})-(\d{1,2})$",
                date_str
            )

            if match:
                year, month, day = match.groups()

                return (
                    f"{year}-"
                    f"{int(month):02d}-"
                    f"{int(day):02d}"
                )

            # YYYY/M/D
            match = re.match(
                r"^(\d{4})/(\d{1,2})/(\d{1,2})$",
                date_str
            )

            if match:
                year, month, day = match.groups()

                return (
                    f"{year}-"
                    f"{int(month):02d}-"
                    f"{int(day):02d}"
                )

            logger.warning(
                "Unparsed publication date: %s",
                date_str
            )

            return date_str

        dates = getattr(self.record, "dates", None)

        if not dates:
            return None

        for d in dates:

            if d.type.endswith("dateIssued"):
                return normalize(d.text)

        for d in dates:

            if d.type.endswith("dateCreated"):
                return normalize(d.text)

        return normalize(dates[0].text)

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
        purls = []

        for purl in getattr(self.record, "purl", []):
            if purl:
                purls.append(purl)

        return self._join_pipe(purls)

    # ---- subjects
    @property
    def subjects(self):
        values = []

        for subject in getattr(self.record, "subjects", []):

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
        text = _fix_mojibake(text)
        text = text.replace("\xa0", " ")
        for bad, good in CP1252_FIXES.items():
            text = text.replace(bad, good)

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

        node = self._xpath_first(
            "mods:nameIdentifier[@type='orcid']"
        )

        if node is None:
            return None

        # text node takes precedence

        if node.text:
            return self._normalize_orcid(
                self._clean_text(node.text)
            )

        # fallback to valueURI

        uri = node.get("valueURI")

        if uri:
            return self._normalize_orcid(uri)

        return None

    def _normalize_orcid(self, value):

        if not value:
            return None

        value = value.strip()

        # remove common prefixes

        value = re.sub(
            r"^ORCID:\s*",
            "",
            value,
            flags=re.IGNORECASE
        )

        value = value.replace(
            "https://orcid.org/",
            ""
        )

        value = value.replace(
            "http://orcid.org/",
            ""
        )

        value = value.strip()

        # validate format

        if not ORCID_RE.match(value):
            logger.debug(
                "Rejected invalid ORCID: %s",
                value
            )

            return None

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
