#!/usr/bin/env python3

import csv
import os
from pathlib import Path

import assets
from assets.parser import iter_local_mods


OUTPUT_CSV = "scholarly_feed_audit.csv"


def get_identifier(record, ident_type):

    for ident in getattr(record, "identifiers", []):

        if (
            ident.type
            and ident.type.upper() == ident_type.upper()
        ):
            return ident.text

    return None


def detect_feed(record):

    iid = get_identifier(record, "IID")

    if iid:

        iid_lower = iid.lower()

        if "libsubv1_wos" in iid_lower:
            return "Web of Science"

        if iid_lower.startswith("fsu_pmch_"):
            return "PubMed Central"

    if get_identifier(record, "PMCID"):
        return "PubMed Central"

    return None


with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "pid",
            "feed_source",
            "iid",
            "pmcid",
            "doi",
            "purl",
            "title",
            "publication_date",
            "source_collection",
            "mods_file",
        ]
    )

    writer.writeheader()

    for record in iter_local_mods(
            "/home/mmiguez/Downloads/root/fsu_research_repository"):

        source_path = record["path"]
        collection = record["collection"]

        filename = os.path.basename(
            str(source_path)
        )

        pid = (
            Path(filename)
            .stem
            .replace("fsu_", "fsu:")
            .replace("FSU_", "fsu:")
            .removesuffix("_MODS")
        )

        for parsed_record in assets.parse_mods_stream(
                record["stream"]):

            feed_source = detect_feed(
                parsed_record
            )

            if not feed_source:
                continue

            obj = assets.ObjectRecord(
                pid,
                parsed_record,
                collection
            )

            writer.writerow({
                "pid": pid,
                "feed_source": feed_source,
                "iid": get_identifier(
                    parsed_record,
                    "IID"
                ),
                "pmcid": get_identifier(
                    parsed_record,
                    "PMCID"
                ),
                "doi": get_identifier(
                    parsed_record,
                    "DOI"
                ),
                "purl": obj.purl,
                "title": obj.title,
                "publication_date":
                    obj.publication_date,
                "source_collection":
                    collection,
                "mods_file":
                    source_path,
            })

print(
    f"Wrote feed audit to "
    f"{OUTPUT_CSV}"
)