# License value maps
# values to discard entirely
STRIP_VALUES = {
    "on campus use only.",
    "unrestricted",
    "author",
    "publisher",
}

# normalized direct mappings (lowercased + cleaned)
LICENSE_MAP = {
    "creative commons attribution (cc by 4.0)": "CC-BY",
    "creative commons attribution-noncommercial (cc by-nc 4.0)": "CC BY-NC",
    "creative commons attribution-noncommercial-noderivatives (cc by-nc-nd 4.0)": "CC BY-NC-ND",
    "creative commons attribution-sharealike (cc by-sa 4.0)": "CC BY-SA",
    "creative commons attribution-nonderivatives (cc by-nd 4.0)": "CC BY-ND",
    "creative commons public domain dedication (cc0)": "CC-0",
    "creative commons attribution-public domain (cc0 1.0)": "CC-0",
}

# MODS genre element text to Figshare Item type
TYPE_MAP = {
    "photographs": "Figure",
    "photograph": "Figure",
    "image": "Figure",
    "illustrations": "Figure",
    "slides": "Figure",

    "text": "Journal contribution",
    "journal article": "Journal contribution",
    "book review": "Journal contribution",
    "book reviews": "Journal contribution",
    "review": "Journal contribution",
    "review article": "Journal contribution",
    "editorial": "Journal contribution",
    "periodicals": "Journal contribution",

    "conference paper": "Conference contribution",
    "conference presentation": "Conference contribution",
    "conference object": "Conference contribution",

    "conference poster": "Poster",
    "poster": "Poster",

    "technical report": "Report",
    "technical reports": "Report",
    "research report": "Report",
    "policy report": "Report",
    "annual reports": "Report",
    "records (documents)": "Report",
    "catalogs": "Report",
    "data paper": "Report",

    "dataset": "Dataset",
    "computer dataset": "Dataset",

    "doctoral thesis": "Thesis",
    "doctoral": "Thesis",
    "bachelor thesis": "Thesis",
    "master thesis": "Thesis",
    "master": "Thesis",
    "thesis": "Thesis",
    "theses": "Thesis",
    "academic theses": "Thesis",
    "academic dissertation": "Thesis",
    "dissertation": "Thesis",
    "graduate study for the m.s.w. degree": "Thesis",
    "thèses et écrits académiques": "Thesis",

    "book": "Book",
    "book part": "Chapter",

    "working paper": "Preprint",

    "patent": "Standard",
    "utility": "Standard",
    "technical documentation": "Standard",

    "digital maps": "Model",
    "design": "Model",

    "video": "Media",
    "sound": "Media",
    "songs and music": "Media",
    "short films": "Media",
    "two-dimensional moving image": "Media",

    "scores": "Composition",
    "sheet music": "Composition",
    "notated music": "Composition",
    "legends": "Composition",
    "juvenile literature": "Composition",
    "juvenile fiction": "Composition",
    "fiction": "Composition",
    "adaptations": "Composition",

    "bibliography": "Educational resource",
    "bibliographie": "Educational resource",
    "bio-bibliography": "Educational resource",
    "biography": "Educational resource",
    "textbooks": "Educational resource",
    "studies and exercises": "Educational resource",
    "sources": "Educational resource",
    "examinations, questions, etc": "Educational resource",
    "examinations": "Educational resource",
    "encyclopedia": "Educational resource",

    "three-dimensional form": "Physical object",
}

# Figshare Field of Research (FoR) category map
CATEGORY_MAP = {
    "fsu_department_of_anthropology": [
        "4301",  # Archaeology
        "4401",  # Anthropology
    ],

    "fsu_anthropology_faculty_scholarship": [
        "4401",  # Anthropology
    ],

    "fsu_doctor_of_nurse_anesthesia_practice": [
        "4205",  # Nursing
        "3202",  # Clinical sciences
    ],
}
