FILE_EMBARGO_TYPES = {
    "PDF datastream",
    "OBJ datastream",
    "FULL_TEXT datastream",
    "MP4 datastream",
    "PREVIEW datastream",
}

ARTICLE_EMBARGO_TYPES = {
    "object",
}

ACCESS_RESTRICTION_TYPES = {
    "IP",
}


def classify_embargo(target):

    if target in FILE_EMBARGO_TYPES:
        return "file"

    if target in ARTICLE_EMBARGO_TYPES:
        return "article"

    if target in ACCESS_RESTRICTION_TYPES:
        return "access"

    return "unknown"


def is_indefinite(value):
    return bool(
        value
        and value.strip().casefold() == "indefinite"
    )


def is_perpetual_article_embargo(target, value):
    return (
        classify_embargo(target) == "article"
        and is_indefinite(value)
    )