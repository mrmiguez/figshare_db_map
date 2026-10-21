def detect_feed(iid, purl):
    """
    Return:
        Web of Science
        PubMed Central
        None
    """

    iid = (iid or "").lower()
    purl = (purl or "").lower()

    wos_markers = (
        "fsu_libsubv1_wos_",
        "fsu_wos_",
    )

    if any(marker in iid for marker in wos_markers):
        return "Web of Science"

    if any(marker in purl for marker in wos_markers):
        return "Web of Science"

    if iid.startswith("fsu_pmch_"):
        return "PubMed Central"

    if "fsu_pmch_" in purl:
        return "PubMed Central"

    return None


def extract_iid(other_identifiers):
    """
    Pull the feed IID from the pipe-delimited other_identifiers field.
    """

    if not other_identifiers:
        return None

    for value in str(other_identifiers).split("|"):
        value = value.strip()
        value_lower = value.lower()

        if value_lower.startswith("fsu_libsubv1_wos_"):
            return value

        if value_lower.startswith("fsu_wos_"):
            return value

        if value_lower.startswith("fsu_pmch_"):
            return value

    return None


def extract_doi(other_identifiers):

    if not other_identifiers:
        return None

    for value in str(other_identifiers).split("|"):

        value = value.strip()

        if value.lower().startswith("10."):
            return value

        if value.lower().startswith("doi:"):
            return value

    return None

def get_feed_pids(conn):

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            pid,
            purl,
            other_identifiers
        FROM objects
        """
    )

    pids = []

    wos_count = 0
    pmc_count = 0

    for pid, purl, other_identifiers in cur.fetchall():

        iid = extract_iid(other_identifiers)

        feed_source = detect_feed(
            iid,
            purl
        )

        if not feed_source:
            continue

        pids.append(pid)

        if feed_source == "Web of Science":
            wos_count += 1

        elif feed_source == "PubMed Central":
            pmc_count += 1

    return (
        pids,
        wos_count,
        pmc_count
    )