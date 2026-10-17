from io import BytesIO

from assets.parser import parse_mods_stream
from assets.records import ObjectRecord


def make_object_record(xml):

    records = list(
        parse_mods_stream(
            BytesIO(
                xml.encode("utf-8")
            )
        )
    )

    assert len(records) == 1

    return ObjectRecord(
        "fsu:test",
        records[0],
        "root/test_collection",
    )


def test_doi_promoted_to_identifier():

    obj = make_object_record(
        """<?xml version="1.0" encoding="UTF-8"?>
        <mods:mods
            xmlns:mods="http://www.loc.gov/mods/v3"
            xmlns="http://www.loc.gov/mods/v3">

            <mods:titleInfo>
                <mods:title>DOI promotion test</mods:title>
            </mods:titleInfo>

            <mods:identifier type="doi">
                10.33009/FSU_test-doi
            </mods:identifier>

        </mods:mods>
        """
    )

    assert obj.identifier == (
        "10.33009/FSU_test-doi"
    )


def test_doi_removed_from_other_identifiers():

    obj = make_object_record(
        """<?xml version="1.0" encoding="UTF-8"?>
        <mods:mods
            xmlns:mods="http://www.loc.gov/mods/v3"
            xmlns="http://www.loc.gov/mods/v3">

            <mods:titleInfo>
                <mods:title>DOI promotion test</mods:title>
            </mods:titleInfo>

            <mods:identifier type="doi">
                10.33009/FSU_test-doi
            </mods:identifier>

            <mods:identifier type="oclc">
                123456789
            </mods:identifier>

            <mods:location displayLabel="purl">
                <mods:url>
                    https://purl.lib.fsu.edu/diginole/test
                </mods:url>
            </mods:location>

        </mods:mods>
        """
    )

    assert obj.identifier == (
        "10.33009/FSU_test-doi"
    )

    assert "doi:" not in (
        obj.other_identifiers or ""
    )

    assert "oclc:123456789" in (
        obj.other_identifiers or ""
    )

    assert (
        "https://purl.lib.fsu.edu/diginole/test"
        in (obj.other_identifiers or "")
    )


def test_doi_url_is_normalized():

    obj = make_object_record(
        """<?xml version="1.0" encoding="UTF-8"?>
        <mods:mods
            xmlns:mods="http://www.loc.gov/mods/v3"
            xmlns="http://www.loc.gov/mods/v3">

            <mods:titleInfo>
                <mods:title>DOI URL test</mods:title>
            </mods:titleInfo>

            <mods:identifier type="doi">
                https://doi.org/10.1016/j.example.2026.1
            </mods:identifier>

        </mods:mods>
        """
    )

    assert obj.identifier == (
        "10.1016/j.example.2026.1"
    )


def test_doi_prefix_is_normalized():

    obj = make_object_record(
        """<?xml version="1.0" encoding="UTF-8"?>
        <mods:mods
            xmlns:mods="http://www.loc.gov/mods/v3"
            xmlns="http://www.loc.gov/mods/v3">

            <mods:titleInfo>
                <mods:title>DOI prefix test</mods:title>
            </mods:titleInfo>

            <mods:identifier type="doi">
                doi:10.17125/plaid.2017.96
            </mods:identifier>

        </mods:mods>
        """
    )

    assert obj.identifier == (
        "10.17125/plaid.2017.96"
    )


def test_publisher_doi_is_also_promoted():

    obj = make_object_record(
        """<?xml version="1.0" encoding="UTF-8"?>
        <mods:mods
            xmlns:mods="http://www.loc.gov/mods/v3"
            xmlns="http://www.loc.gov/mods/v3">

            <mods:titleInfo>
                <mods:title>Publisher DOI test</mods:title>
            </mods:titleInfo>

            <mods:identifier type="doi">
                10.1016/j.example.2026.2
            </mods:identifier>

        </mods:mods>
        """
    )

    assert obj.identifier == (
        "10.1016/j.example.2026.2"
    )

    assert obj.other_identifiers is None