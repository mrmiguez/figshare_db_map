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
    "Report": 70,
    "Physical object": 60,
    "Model": 50,
    "Figure": 40,
    "Media": 30,
    "Educational resource": 20,
    "Journal contribution": 10,
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