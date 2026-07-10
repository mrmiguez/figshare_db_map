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
}

SUBJECT_NORMALIZATION = {

    # Education
    "education, higher": "education",
    "education, administration": "education",
    "education, educational psychology": "education",
    "education, adult and continuing": "education",
    "education, guidance and counseling": "education",
    "education, physical": "education",
    "education, curriculum and instruction": "education",
    "education, teacher training": "education",
    "education, tests and measurements": "education",
    "education, reading": "education",
    "education, community college": "education",
    "education, social sciences": "education",
    "education, mathematics": "education",
    "education, technology": "education",

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
    "business administration, management": "business",
    "business administration, marketing": "marketing",

    # Biology
    "biology, general": "biology",
    "biology, zoology": "biology",
    "biology, animal physiology": "biology",
    "biology, genetics": "biology",
    "biology, ecology": "biology",
    "biology, oceanography": "marine biology",
}

LICENSE_MAP = {

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