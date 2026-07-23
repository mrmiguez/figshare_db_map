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
}

LICENSE_URL_MAP = {

    # CC BY
    "http://creativecommons.org/licenses/by/4.0/":
        "https://creativecommons.org/licenses/by/4.0/",

    # CC BY-NC
    "http://creativecommons.org/licenses/by-nc/4.0/":
        "https://creativecommons.org/licenses/by-nc/4.0/",

    # CC BY-NC-ND
    "http://creativecommons.org/licenses/by-nc-nd/4.0/":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "https://creativecommons.org/licenses/by-nc-nd/4.0":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    "https://creativecommons.org/licenses/by-nc-nd//4.0/":
        "https://creativecommons.org/licenses/by-nc-nd/4.0/",

    # CC0
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

# Figshare Field of Research (FoR) category map
CATEGORY_MAP = {
    "fsu_etds": ["Multidisciplinary"],
    "fsu_retroetds": ["Multidisciplinary"],

    "fsu_honors_theses": ["Multidisciplinary"],

    "fsu_department_of_anthropology": [
        "Archaeology",
        "Anthropology",
    ],

    "fsu_department_of_classics": [
        "Classical Studies",
    ],

    "fsu_department_of_physics": [
        "Physics",
    ],

    "fsu_department_of_psychology": [
        "Psychology",
    ],

    "fsu_department_of_statistics": [
        "Statistics",
    ],

    "fsu_school_of_information": [
        "Information and Computing Sciences",
    ],
}

COLLECTION_FOR_MAP = {

    # ------------------------------------------------------------------
    # ETDs
    # ------------------------------------------------------------------

    "fsu_etds": {
        "Multidisciplinary"
    },

    "fsu_retroetds": {
        "Multidisciplinary"
    },

    "fsu_honors_theses": {
        "Multidisciplinary"
    },

    "fsu_dnp_project_graduates": {
        "Nursing"
    },

    "fsu_doctor_of_nurse_anesthesia_practice": {
        "Nursing"
    },

    # ------------------------------------------------------------------
    # Anthropology / Archaeology
    # ------------------------------------------------------------------

    "fsu_department_of_anthropology": {
        "Anthropology",
        "Archaeology"
    },

    "fsu_castrocollectionanthro": {
        "Anthropology",
        "Archaeology"
    },

    "fsu_castrophotographs": {
        "Archaeology"
    },

    "fsu_castroposthole": {
        "Archaeology"
    },

    "fsu_castrocontrolledsurfaceforms": {
        "Archaeology"
    },

    "fsu_castroartifactanalysiscoll": {
        "Archaeology"
    },

    "fsu_castrobeadanalysisforms": {
        "Archaeology"
    },

    "fsu_castrofieldnotes": {
        "Archaeology"
    },

    "fsu_castromaps": {
        "Archaeology"
    },

    # ------------------------------------------------------------------
    # Classics / Cetamura
    # ------------------------------------------------------------------

    "fsu_department_of_classics": {
        "Classical Studies"
    },

    "fsu_cetamura": {
        "Classical Studies",
        "Archaeology"
    },

    "fsu_cetamuraphotos": {
        "Archaeology"
    },

    "fsu_cetamuraExcavations_trenchPhotos": {
        "Archaeology"
    },

    "fsu_cetamuraExcavations_maps": {
        "Archaeology"
    },

    # ------------------------------------------------------------------
    # Physical Sciences
    # ------------------------------------------------------------------

    "fsu_department_of_physics": {
        "Physics"
    },

    "fsu_department_of_earth_ocean_and_atmospheric_science": {
        "Atmospheric Sciences",
        "Oceanography"
    },

    "fsu_florida_climate_institute": {
        "Climate Change Science"
    },

    "fsu_center_for_ocean_atmospheric_prediction_studies": {
        "Oceanography",
        "Atmospheric Sciences"
    },

    "fsu_National_High_Magnetic_Field_Laboratory": {
        "Physics"
    },

    # ------------------------------------------------------------------
    # Chemistry / Biology
    # ------------------------------------------------------------------

    "fsu_department_of_chemistry_and_biochemistry": {
        "Chemistry"
    },

    "fsu_department_of_biological_science": {
        "Biological Sciences"
    },

    "fsu_department_of_biomedical_sciences": {
        "Biomedical Sciences"
    },

    "fsu_institute_of_molecular_biophysics": {
        "Molecular Biophysics"
    },

    # ------------------------------------------------------------------
    # Mathematics / Statistics / Computing
    # ------------------------------------------------------------------

    "fsu_department_of_mathematics": {
        "Mathematics"
    },

    "fsu_department_of_statistics": {
        "Statistics"
    },

    "fsu_department_of_computer_science": {
        "Computer Science"
    },

    "fsu_department_of_scientific_computing": {
        "Scientific Computing"
    },

    "fsu_school_of_information": {
        "Information Systems"
    },

    # ------------------------------------------------------------------
    # Social Sciences
    # ------------------------------------------------------------------

    "fsu_department_of_psychology": {
        "Psychology"
    },

    "fsu_department_of_geography": {
        "Geography"
    },

    "fsu_department_of_sociology": {
        "Sociology"
    },

    "fsu_department_of_political_science": {
        "Political Science"
    },

    "fsu_askew_school_of_public_administration_and_policy": {
        "Public Policy"
    },

    "fsu_department_of_urban_and_regional_planning": {
        "Urban and Regional Planning"
    },

    "fsu_college_of_criminology_and_criminal_justice": {
        "Criminology"
    },

    "fsu_college_of_social_work": {
        "Social Work"
    },

    "fsu_department_of_educational_psychology_and_learning_systems": {
        "Education"
    },

    "fsu_florida_learning_disability_research_center": {
        "Psychology"
    },

    "fsu_school_of_teacher_education": {
        "Education"
    },

    # ------------------------------------------------------------------
    # Humanities
    # ------------------------------------------------------------------

    "fsu_department_of_english": {
        "Literary Studies"
    },

    "fsu_department_of_history": {
        "History"
    },

    "fsu_department_of_philosophy": {
        "Philosophy"
    },

    "fsu_department_of_modern_languages_and_linguistics": {
        "Languages and Linguistics"
    },

    # ------------------------------------------------------------------
    # Medicine / Health
    # ------------------------------------------------------------------

    "fsu_college_of_medicine": {
        "Medical Sciences"
    },

    "fsu_department_of_clinical_sciences": {
        "Clinical Sciences"
    },

    "fsu_department_of_family_medicine_and_rural_health": {
        "Clinical Sciences"
    },

    "fsu_department_of_geriatrics": {
        "Geriatrics"
    },

    "fsu_department_of_behavioral_sciences_and_social_medicine": {
        "Behavioural Health"
    },

    # ------------------------------------------------------------------
    # Engineering
    # ------------------------------------------------------------------

    "fsu_department_of_chemical_and_biomedical_engineering": {
        "Chemical Engineering"
    },

    "fsu_department_of_civil_and_environmental_engineering": {
        "Civil Engineering"
    },

    "fsu_department_of_electrical_and_computer_engineering": {
        "Electrical Engineering"
    },

    "fsu_department_of_mechanical_engineering": {
        "Mechanical Engineering"
    },

    "fsu_industrial_and_manufacturing_engineering": {
        "Industrial Engineering"
    },

    "fsu_center_for_advanced_power_systems": {
        "Electrical Engineering"
    },

    # ------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------

    "fsu_florida_state_university_patents": {
        "Technology",
        "Engineering"
    },

    "fsu_university_libraries": {
        "Library and Information Studies"
    },

    "fsu_huadeepcconsortium": {
        "Engineering"
    },

    "fsu_undergraduate_research_symposium": {
        "Multidisciplinary"
    },

    "fsu_nutrition_integrative_physiology": {
        "Nutrition",
        "Medical Sciences"
    },

    "fsu_center_for_tech_in_counseling_and_career_development": {
        "Psychology",
        "Education"
    },

    "fsu_department_of_educational_leadership_and_policy_studies": {
        "Education",
        "Public Policy"
    },

    "fsu_college_of_nursing": {
        "Nursing"
    },

    "fsu_school_of_communication_science_and_disorders": {
        "Communication Disorders"
    },

    "fsu_human_development_and_family_science": {
        "Social Work",
        "Psychology"
    },

    "fsu_learning_systems_institute": {
        "Education"
    },

    "fsu_department_of_sport_management": {
        "Sport and Exercise Sciences"
    },

    "fsu_florida_center_for_reading_research": {
        "Education"
    },

    "fsu_department_of_management": {
        "Business"
    },

    "fsu_department_of_marketing": {
        "Marketing"
    },

    "fsu_fsu_coastal_and_marine_laboratory": {
        "Biological Sciences",
        "Marine Sciences"
    },

    "fsu_program_in_neuroscience": {
        "Biomedical Sciences",
        "Psychology"
    },
}

SUBJECT_FOR_MAP = {

    # Anthropology / Archaeology
    "anthropology": {
        "Anthropology",
    },

    "archaeology": {
        "Archaeology",
    },

    # Psychology
    "psychology": {
        "Psychology",
    },

    "clinical psychology": {
        "Psychology",
    },

    "developmental psychology": {
        "Psychology",
    },

    "cognitive psychology": {
        "Psychology",
    },

    "counseling psychology": {
        "Psychology",
    },

    # Physical sciences
    "physics": {
        "Physics",
    },

    "meteorology": {
        "Atmospheric Sciences",
    },

    "oceanography": {
        "Oceanography",
    },

    "atmospheric sciences": {
        "Atmospheric Sciences",
    },

    # Computing
    "computer science": {
        "Computer Science",
    },

    "information science": {
        "Information Systems",
    },

    "library science": {
        "Library and Information Studies",
    },

    # Mathematics / Statistics
    "statistics": {
        "Statistics",
    },

    "mathematics": {
        "Mathematics",
    },

    # Engineering
    "electrical engineering": {
        "Electrical Engineering",
    },

    "computer engineering": {
        "Electrical Engineering",
    },

    "mechanical engineering": {
        "Mechanical Engineering",
    },

    "civil engineering": {
        "Civil Engineering",
    },

    "chemical engineering": {
        "Chemical Engineering",
    },

    "environmental engineering": {
        "Civil Engineering",
    },

    "aerospace engineering": {
        "Mechanical Engineering",
    },

    "industrial engineering": {
        "Industrial Engineering",
    },

    # Chemistry
    "chemistry": {
        "Chemistry",
    },

    "organic chemistry": {
        "Chemistry",
    },

    "materials science": {
        "Chemistry",
    },

    # Biology / Medicine
    "biology": {
        "Biological Sciences",
    },

    "life sciences": {
        "Biological Sciences",
    },

    "biochemistry": {
        "Biomedical Sciences",
    },

    "biophysics": {
        "Molecular Biophysics",
    },

    "molecular biology": {
        "Biomedical Sciences",
    },

    "medical sciences": {
        "Medical Sciences",
    },

    "nutrition": {
        "Medical Sciences",
    },

    "dietetics": {
        "Medical Sciences",
    },

    "exercise": {
        "Medical Sciences",
    },

    # Education
    "education": {
        "Education",
    },

    "educational psychology": {
        "Education", "Psychology"
    },

    "educational leadership": {
        "Education",
    },

    "educational technology": {
        "Education",
    },

    "teachers--training of": {
        "Education",
    },

    "school management and organization": {
        "Education",
    },

    "teacher education": {
        "Education",
    },

    "curriculum and instruction": {
        "Education",
    },

    "language and literature": {
        "Education",
        "Languages and Linguistics",
    },

    "higher education": {
        "Education",
    },

    "reading": {
        "Education",
    },

    "educational assessment": {
        "Education",
    },

    "educational measurement": {
        "Education",
    },

    "counselor education": {
        "Education",
    },

    "rehabilitation counseling": {
        "Psychology",
        "Social Work",
    },

    "educational evaluation": {
        "Education",
    },

    "education--research": {
        "Education",
    },

    "instructional systems": {
        "Education",
    },

    # Social sciences
    "sociology": {
        "Sociology",
    },

    "public administration": {
        "Public Policy",
    },

    "public policy": {
        "Public Policy",
    },

    "international relations": {
        "Political Science",
    },

    "city planning": {
        "Urban and Regional Planning",
    },

    "social service": {
        "Social Work",
    },

    "social work": {
        "Social Work",
    },

    "child welfare": {
        "Social Work",
    },

    "human services": {
        "Social Work",
    },

    "family studies": {
        "Social Work",
    },

    "family science": {
        "Social Work",
    },

    "foster care": {
        "Social Work",
    },

    "substance abuse": {
        "Social Work",
    },

    "mental illness": {
        "Psychology",
    },

    # Humanities
    "history": {
        "History",
    },

    "religion": {
        "Religious Studies",
    },

    "literature": {
        "Literary Studies",
    },

    "english literature": {
        "Literary Studies",
    },

    "african literature": {
        "Literary Studies",
    },

    "english language": {
        "Languages and Linguistics",
    },

    "languages, modern": {
        "Languages and Linguistics",
    },

    # Arts
    "music": {
        "Music",
    },

    "music therapy": {
        "Music",
    },

    "performing arts": {
        "Performing Arts",
    },

    "dance": {
        "Performing Arts",
    },

    "creative writing": {
        "Creative Writing",
    },

    "theater": {
        "Performing Arts",
    },

    # Sport
    "sports sciences": {
        "Sport and Exercise Sciences",
    },

    # General engineering
    "engineering": {
        "Engineering",
    },

    # Business
    "economics": {
        "Economics",
    },

    "accounting": {
        "Accounting",
    },

    "marketing": {
        "Marketing",
    },

    "business": {
        "Business",
    },

    "management": {
        "Business",
    },

    "finance": {
        "Economics",
    },

    "entrepreneurship": {
        "Business",
    },

    "risk management": {
        "Business",
    },

    "insurance": {
        "Business",
    },

    "real estate": {
        "Business",
    },

    "business analytics": {
        "Information Systems",
    },

    # Geography / Earth
    "geography": {
        "Geography",
    },

    "geology": {
        "Geology",
    },

    "earth sciences": {
        "Geology",
    },

    # Communications
    "communication": {
        "Communication and Media Studies",
    },

    "communicative disorders": {
        "Communication Disorders",
    },

    "speech therapy": {
        "Communication Disorders",
    },

    # Health
    "nursing": {
        "Nursing",
    },

    "food": {
        "Nutrition",
    },

    "public health": {
        "Medical Sciences",
    },

    "pain management": {
        "Medical Sciences",
    },

    "epidemiology": {
        "Medical Sciences",
    },

    "clinical research": {
        "Medical Sciences",
    },

    "health sciences": {
        "Medical Sciences",
    },

    "exercise science": {
        "Sport and Exercise Sciences",
    },

    # Communication
    "speech-language pathology": {
        "Communication Disorders",
    },

    "communication sciences and disorders": {
        "Communication Disorders",
    },

    "audiology": {
        "Communication Disorders",
    },

    # Arts
    "art": {
        "Visual Arts",
    },

    "art education": {
        "Visual Arts",
        "Education",
    },

    "art therapy": {
        "Visual Arts",
        "Psychology",
    },

    "arts administration": {
        "Visual Arts",
    },

    "music education": {
        "Music",
        "Education",
    },

    # Environmental science
    "marine biology": {
        "Biological Sciences",
    },

    "coastal studies": {
        "Environmental Sciences",
    },

    "climate": {
        "Atmospheric Sciences",
    },

    "geoscience": {
        "Geology",
    },

    # Philosophy
    "philosophy": {
        "Philosophy",
    },

    "political ethics": {
        "Philosophy",
    },

    "ethics": {
        "Philosophy",
    },

    # Political science
    "political science": {
        "Political Science",
    },

    # Music education
    "pedagogy (music)": {
        "Music",
        "Education",
    },

    # GIS
    "geographic information systems": {
        "Geography",
        "Information Systems",
    },

    "geomatics": {
        "Geography",
    },


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
