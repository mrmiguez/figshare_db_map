# License value maps
# values to discard entirely
STRIP_VALUES = {
    "on campus use only.",
    "unrestricted",
    "author",
    "publisher",
}

# normalized direct mappings (lowercased + cleaned)
LICENSE_TEXT_MAP = {

    "creative commons attribution (cc by 4.0)":
        "https://creativecommons.org/licenses/by/4.0/",

    "creative commons attribution-sharealike (cc by-sa 4.0)":
        "https://creativecommons.org/licenses/by-sa/4.0/",

    "creative commons attribution-nonderivatives (cc by-nd 4.0)":
        "https://creativecommons.org/licenses/by-nd/4.0/",

    "creative commons attribution-noncommercial (cc by-nc 4.0)":
        "https://creativecommons.org/licenses/by-nc/4.0/",

    "creative commons attribution-noncommercial-noderivatives (cc by-nc-nd 4.0)":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "creative commons public domain dedication (cc0)":
        "https://creativecommons.org/publicdomain/zero/1.0/",

    "creative commons attribution-public domain (cc0 1.0)":
        "https://creativecommons.org/publicdomain/zero/1.0/",

    "copyright not evaluated":
        "http://rightsstatements.org/vocab/CNE/1.0/",
}

LICENSE_URL_MAP = {

    # --------------------------------------------------
    # CC BY
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by/3.0/":
        "https://creativecommons.org/licenses/by/4.0/",

    "http://creativecommons.org/licenses/by/4.0/":
        "https://creativecommons.org/licenses/by/4.0/",

    # --------------------------------------------------
    # CC BY-NC
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by-nc/3.0/":
        "https://creativecommons.org/licenses/by-nc/4.0/",

    "http://creativecommons.org/licenses/by-nc/4.0/":
        "https://creativecommons.org/licenses/by-nc/4.0/",

    # --------------------------------------------------
    # CC BY-NC-SA
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by-nc-sa/3.0/":
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",

    "http://creativecommons.org/licenses/by-nc-sa/4.0/":
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",

    # --------------------------------------------------
    # CC BY-NC-ND
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by-nc-nd/3.0/":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "http://creativecommons.org/licenses/by-nc-nd/4.0/":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "https://creativecommons.org/licenses/by-nc-nd/4.0":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "https://creativecommons.org/licenses/by-nc-nd//4.0/":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    # --------------------------------------------------
    # CC BY-ND
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by-nd/3.0/":
        "https://creativecommons.org/licenses/by-nd/4.0/",

    "http://creativecommons.org/licenses/by-nd/4.0/":
        "https://creativecommons.org/licenses/by-nd/4.0/",

    # --------------------------------------------------
    # CC BY-SA
    # --------------------------------------------------

    "http://creativecommons.org/licenses/by-sa/3.0/":
        "https://creativecommons.org/licenses/by-sa/4.0/",

    "http://creativecommons.org/licenses/by-sa/4.0/":
        "https://creativecommons.org/licenses/by-sa/4.0/",

    # --------------------------------------------------
    # CC0
    # --------------------------------------------------

    "https://creativecommons.org/public-domain/cc0/":
        "https://creativecommons.org/publicdomain/zero/1.0/",
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

TYPE_PRIORITY = {
    "Thesis": 100,
    "Dataset": 90,
    "Standard": 80,
    "Conference contribution": 70,
    "Chapter": 65,
    "Book": 60,
    "Report": 55,
    "Poster": 50,
    "Physical object": 45,
    "Model": 40,
    "Figure": 35,
    "Media": 30,
    "Educational resource": 25,
    "Journal contribution": 10,
}

IGNORED_GENRES = {
    "text",
    "unspecified",
}

# ----------------------------------------------------------------------
# COLLECTION -> FoR codes
# ----------------------------------------------------------------------

COLLECTION_FOR_MAP = {

    # ETDs
    "fsu_etds": {3903},
    "fsu_retroetds": {3903},
    "fsu_honors_theses": {3903},

    # Anthropology / Archaeology
    "fsu_department_of_anthropology": {4301, 4401},
    "fsu_castrocollectionanthro": {4301, 4401},
    "fsu_castrophotographs": {4301},
    "fsu_castroposthole": {4301},
    "fsu_castrocontrolledsurfaceforms": {4301},
    "fsu_castroartifactanalysiscoll": {4301},
    "fsu_castrobeadanalysisforms": {4301},
    "fsu_castrofieldnotes": {4301},
    "fsu_castromaps": {4301},

    # Classics
    "fsu_department_of_classics": {4303},
    "fsu_cetamura": {4301, 4303},

    # Physical sciences
    "fsu_department_of_physics": {5105},
    "fsu_department_of_earth_ocean_and_atmospheric_science": {3701, 3708, 3705},
    "fsu_florida_climate_institute": {3702},
    "fsu_center_for_ocean_atmospheric_prediction_studies": {3701, 3708},
    "fsu_National_High_Magnetic_Field_Laboratory": {5105},

    # Biology / Biomedical
    "fsu_department_of_biological_science": {3103},
    "fsu_department_of_biomedical_sciences": {3101},
    "fsu_institute_of_molecular_biophysics": {3101},

    # Computing
    "fsu_department_of_computer_science": {4601},
    "fsu_department_of_scientific_computing": {4601},
    "fsu_school_of_information": {4609, 4610},

    # Social sciences
    "fsu_department_of_psychology": {5203},
    "fsu_department_of_geography": {4406},
    "fsu_department_of_sociology": {4410},
    "fsu_department_of_political_science": {4408},
    "fsu_askew_school_of_public_administration_and_policy": {4407},
    "fsu_department_of_urban_and_regional_planning": {3304},
    "fsu_college_of_criminology_and_criminal_justice": {4402},
    "fsu_college_of_social_work": {4409},

    # Humanities
    "fsu_department_of_history": {4303},
    "fsu_department_of_philosophy": {5003},
    "fsu_department_of_english": {4705},
    "fsu_department_of_modern_languages_and_linguistics": {4704},

    # Education
    "fsu_school_of_teacher_education": {3903},
    "fsu_department_of_educational_psychology_and_learning_systems": {3904},
    "fsu_learning_systems_institute": {3904},
    "fsu_florida_center_for_reading_research": {3901},

    # Health
    "fsu_college_of_medicine": {3202},
    "fsu_department_of_clinical_sciences": {3202},
    "fsu_department_of_family_medicine_and_rural_health": {3202},
    "fsu_department_of_geriatrics": {3202},
    "fsu_department_of_behavioral_sciences_and_social_medicine": {5203},
    "fsu_college_of_nursing": {4205},
    "fsu_school_of_communication_science_and_disorders": {4201},

    # Engineering
    "fsu_department_of_chemical_and_biomedical_engineering": {4004},
    "fsu_department_of_civil_and_environmental_engineering": {4005},
    "fsu_department_of_electrical_and_computer_engineering": {4008},
    "fsu_department_of_mechanical_engineering": {4017},
    "fsu_industrial_and_manufacturing_engineering": {4014},
    "fsu_center_for_advanced_power_systems": {4008},

    # Libraries / repositories
    "fsu_university_libraries": {4610},

    # Business
    "fsu_department_of_management": {3507},
    "fsu_department_of_marketing": {3506},

    # Misc
    "fsu_nutrition_integrative_physiology": {3210},
    "fsu_program_in_neuroscience": {3209, 5203},
    "fsu_department_of_sport_management": {4207},
    "fsu_undergraduate_research_symposium": {3903},
}

SUBJECT_FOR_MAP = {
    "anthropology": {4401},
    "archaeology": {4301},
    "history": {4303},

    "psychology": {5203},
    "clinical psychology": {5203},
    "counseling psychology": {5203},

    "sociology": {4410},
    "social work": {4409},
    "political science": {4408},
    "public policy": {4407},

    "education": {3903},
    "higher education": {3903},
    "curriculum and instruction": {3901},

    "computer science": {4601},
    "information science": {4609},
    "library science": {4610},

    "statistics": {4905},
    "mathematics": {4901},

    "physics": {5105},
    "atmospheric sciences": {3701},
    "oceanography": {3708},
    "climate": {3702},

    "biology": {3103},
    "biochemistry": {3101},
    "molecular biology": {3101},

    "nursing": {4205},
    "public health": {4206},
    "speech-language pathology": {4201},
    "audiology": {4201},
    "communication sciences and disorders": {4201},

    "communication": {4701},
    "literature": {4705},
    "philosophy": {5003},
    "religion": {5004},

    "music": {3603},
    "performing arts": {3604},
    "creative writing": {3602},
    "art": {3606},

    "marketing": {3506},
    "accounting": {3501},
    "business": {3507},
    "management": {3507},
    "economics": {3801},

    "geography": {4406},
    "geology": {3705},
    "urban planning": {3304},
}

SUBJECT_NORMALIZATION = {

    # Education
    "education, higher": "higher education",
    "education, adult and continuing": "education",
    "education, physical": "education",
    "education, teacher training": "education",
    "education, tests and measurements": "education",
    "education, reading": "reading",
    "education, community college": "education",
    "education, social sciences": "education",
    "education, mathematics": "education",
    "education, technology": "education",
    "education, curriculum and instruction": "curriculum and instruction",
    "education, language and literature": "language and literature",
    "education, teacher education": "teacher education",
    "education, educational psychology": "educational psychology",
    "education, guidance and counseling": "counseling psychology",
    "education, administration": "educational leadership",

    # Psychology
    "psychology, clinical": "psychology",
    "psychology, experimental": "psychology",
    "psychology, general": "psychology",
    "psychology, social": "psychology",
    "psychology, psychobiology": "psychology",

    # Chemistry
    "chemistry, organic": "chemistry",
    "chemistry, biochemistry": "chemistry",
    "chemistry, physical": "chemistry",
    "chemistry, inorganic": "chemistry",
    "chemistry, analytical": "chemistry",

    # Physics
    "physics, nuclear": "physics",
    "physics, atmospheric science": "physics",
    "physics, condensed matter": "physics",
    "physics, elementary particles and high energy": "physics",

    # Literature
    "literature, modern": "literary studies",
    "literature, general": "literary studies",
    "literature, american": "literary studies",
    "literature, english": "literary studies",
    "literature, romance": "literary studies",

    # Sociology
    "sociology, general": "sociology",
    "sociology, individual and family studies": "sociology",
    "sociology, criminology and penology": "criminology",
    "sociology, demography": "sociology",

    # Political science
    "political science, general": "political science",
    "political science, public administration": "public policy",
    "political science, international law and relations": "political science",

    # Business
    "business administration, general": "business",
    "business administration, accounting": "accounting",
    "business administration, marketing": "marketing",
    "business administration, management": "management",
    "business administration, finance": "finance",
    "business administration, entrepreneurship": "entrepreneurship",
    "business administration, risk management": "risk management",

    # Biology
    "biology, general": "biology",
    "biology, zoology": "biology",
    "biology, animal physiology": "biology",
    "biology, genetics": "biology",
    "biology, ecology": "biology",
    "biology, oceanography": "marine biology",

    # Social work
    "social work": "social work",
    "social welfare": "social work",
    "child welfare": "child welfare",
    "human services": "human services",

    # Communication
    "communication sciences and disorders": "communication sciences and disorders",
    "speech-language pathology": "speech-language pathology",
    "audiology": "audiology",

    # Arts
    "arts": "art",
    "art education": "art education",
    "art therapy": "art therapy",
    "arts administration": "arts administration",

    # Marine biology
    "marine biology": "marine biology",
    "biology, marine": "marine biology",

    # Religion
    "religion--history": "religion",

    # Other
    "political ethics": "philosophy",
    "education--research": "educational evaluation",
    "instructional systems": "educational evaluation",
    "geomatics": "geographic information systems",
    "pedagogy (music)": "music education",
}

MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "â€",
    "â€™",
    "â€œ",
    "â€",
)

CP1252_FIXES = {
    "â€™": "’",
    "â€˜": "‘",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€“": "–",
    "â€”": "—",
    "â€": "‑",   # often an en-dash/hyphen corruption
}

DATE_FORMATS = (
"%Y-%m-%d",
"%Y/%m/%d",
"%m/%d/%Y",
"%m/%d/%y",
"%m-%d-%Y",
"%m-%d-%y",
)
