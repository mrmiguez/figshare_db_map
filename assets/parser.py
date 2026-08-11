import logging
import os
from pathlib import Path
from io import BytesIO

import boto3
import pymods


# register namespaces
NS = {"mods": "http://www.loc.gov/mods/v3",}
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_mods_stream(source):

    if hasattr(source, "read"):
        records = pymods.MODSReader(BytesIO(source.read()))

    else:
        records = pymods.MODSReader(source)

    for record in records:
        yield record


def iter_local_mods(record_directory):

    for f in Path(record_directory).rglob('*MODS.xml'):

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
            Prefix=prefix):

        for obj in page.get(
                "Contents",
                []):

            key = obj["Key"]

            if not key.endswith(
                    "_MODS.xml"):
                continue

            response = s3.get_object(
                Bucket=bucket,
                Key=key
            )

            yield {
                "path": key,
                "collection":
                    os.path.dirname(key),
                "stream":
                    response["Body"],
            }
