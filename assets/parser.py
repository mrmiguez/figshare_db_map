import logging
import os
from pathlib import Path
from io import BytesIO

import boto3
import pymods


# MODS namespaces
NS = {
    "mods": "http://www.loc.gov/mods/v3",
}

VALID_MODS_NAMESPACE = (
    b"http://www.loc.gov/mods/v3"
)

PROXIED_MODS_NAMESPACE = (
    b"http://www.loc.gov.proxy.lib.fsu.edu/mods/v3"
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_mods_stream(source):
    """
    Parse a MODS document from either a file-like object or local path.

    A small number of legacy FSU records contain a proxy-contaminated
    MODS namespace:

        http://www.loc.gov.proxy.lib.fsu.edu/mods/v3

    Normalize that namespace to the canonical MODS namespace before
    passing the document to pymods.
    """

    if hasattr(source, "read"):
        data = source.read()

    else:
        data = Path(source).read_bytes()

    if PROXIED_MODS_NAMESPACE in data:

        logger.warning(
            "Normalizing proxied MODS namespace"
        )

        data = data.replace(
            PROXIED_MODS_NAMESPACE,
            VALID_MODS_NAMESPACE,
        )

    records = pymods.MODSReader(
        BytesIO(data)
    )

    yield from records


def iter_local_mods(record_directory):

    for f in Path(record_directory).rglob(
        "*MODS.xml"
    ):

        yield {
            "path": f,
            "collection": str(f.parent),
            "stream": f,
        }


def iter_s3_mods(bucket, prefix=""):

    s3 = boto3.client("s3")

    paginator = s3.get_paginator(
        "list_objects_v2"
    )

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=prefix,
    ):

        for obj in page.get(
            "Contents",
            [],
        ):

            key = obj["Key"]

            if not key.endswith(
                "_MODS.xml"
            ):
                continue

            response = s3.get_object(
                Bucket=bucket,
                Key=key,
            )

            yield {
                "path": key,
                "collection": os.path.dirname(
                    key
                ),
                "stream": response["Body"],
            }