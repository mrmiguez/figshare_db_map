#!/usr/bin/env bash

set -euo pipefail

#
# Locate repository regardless of current working directory
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DB="${DB:-$SCRIPT_DIR/figshare.db}"
RUN_DIR="$(dirname "$DB")"
UPDATES_DIR="${UPDATES_DIR:-$SCRIPT_DIR/updates}"

S3_MODE="${S3_MODE:-true}"

SRCBUCK="${SRCBUCK:-}"
TGTBUCK="${TGTBUCK:-}"
PREFIX="${PREFIX:-}"

#
# Validate source configuration
#

if [[ "$S3_MODE" == "true" ]]; then

    if [[ -z "$SRCBUCK" ]]; then
        echo "ERROR: SRCBUCK must be set in S3 mode" >&2
        exit 1
    fi

    #
    # Arguments for embargo ingestion.
    #
    # SRCBUCK is the repository source bucket.
    #

    EMBARGO_SOURCE_ARGS=(
        --s3-bucket "$SRCBUCK"
    )

    if [[ -n "$PREFIX" ]]; then
        EMBARGO_SOURCE_ARGS+=(
            --s3-prefix "$PREFIX"
        )
    fi

else

    ROOT="${ROOT:-${1:-}}"

    if [[ -z "$ROOT" ]]; then
        echo "ERROR: ROOT must be set in local mode" >&2
        echo "Usage: S3_MODE=false $0 REPOSITORY_ROOT" >&2
        exit 1
    fi

    EMBARGO_SOURCE_ARGS=(
        --root "$ROOT"
    )

fi

#
# Workflow summary
#

echo
echo "=========================================================="
echo "FIGSHARE METADATA WORKFLOW"
echo "=========================================================="
echo "Repository      : $SCRIPT_DIR"
echo "Database        : $DB"
echo "Run Dir         : $RUN_DIR"
echo "Updates Dir     : $UPDATES_DIR"
echo "S3 Mode         : $S3_MODE"

if [[ "$S3_MODE" == "true" ]]; then
    echo "Source Bucket   : $SRCBUCK"
    echo "Source Prefix   : ${PREFIX:-<none>}"
else
    echo "Source Root     : $ROOT"
fi

if [[ -n "$TGTBUCK" ]]; then
    echo "Target Bucket   : $TGTBUCK"
else
    echo "Target Bucket   : <none>"
fi

echo "=========================================================="
echo

#
# Rebuild database
#

echo "[1/12] Building migration database..."

if [[ "$S3_MODE" == "true" ]]; then

    python3 "$SCRIPT_DIR/main.py" \
        --db "$DB" \
        --run \
        --s3 \
        --bucket "$SRCBUCK" \
        --prefix "$PREFIX"

else

    python3 "$SCRIPT_DIR/main.py" \
        --db "$DB" \
        --run \
        "$ROOT"

fi

#
# Embargo enrichment
#
# Individual source embargo assertions are preserved in the
# normalized embargoes table.
#
# objects.embargo_* remains the Figshare-facing projection.
#

echo
echo "[2/12] Applying embargo updates..."

python3 "$SCRIPT_DIR/update_db_embargoes.py" \
    "$DB" \
    "${EMBARGO_SOURCE_ARGS[@]}"

#
# Perpetual whole-object embargo audit
#
# This MUST happen before removal. Deleting an object cascades
# to its normalized embargo rows, so this audit preserves the
# evidence supporting the exclusion.
#

echo
echo "[3/12] Auditing perpetual article embargoes..."

python3 "$SCRIPT_DIR/audit_perpetual_embargoes.py" \
    "$DB"

#
# Perpetual whole-object embargo removal
#
# Removal criterion:
#
#     embargo_class = article
#     embargo_value = indefinite
#
# Source representation:
#
#     target = object
#     value  = indefinite
#
# Indefinite IP restrictions and indefinite file embargoes
# are NOT whole-object exclusion conditions.
#

echo
echo "[4/12] Removing perpetual article embargoes..."

python3 "$SCRIPT_DIR/update_db_remove_perpetual_embargoes.py" \
    "$DB"

#
# Repeatable SQL fixes
#

echo
echo "[5/12] Applying SQL corrections..."

if [[ -d "$SCRIPT_DIR/sql" ]]; then

    for SQL in "$SCRIPT_DIR"/sql/*.sql
    do

        [[ -e "$SQL" ]] || continue

        echo "    Applying: $(basename "$SQL")"

        sqlite3 "$DB" < "$SQL"

    done

fi

#
# CSV-driven corrections
#

echo
echo "[6/12] Applying override spreadsheets..."

if [[ -d "$UPDATES_DIR" ]]; then

    for CSV in "$UPDATES_DIR"/*.csv
    do

        [[ -e "$CSV" ]] || continue

        echo "    Applying: $(basename "$CSV")"

        python3 "$SCRIPT_DIR/update_db_by_csv.py" \
            "$DB" \
            "$CSV"

    done

fi

#
# Scholarly feed audit
#

echo
echo "[7/12] Auditing scholarly feed records..."

python3 "$SCRIPT_DIR/audit_feed_records.py" \
    "$DB"

#
# Scholarly feed removal
#

echo
echo "[8/12] Removing Web of Science and PubMed Central records..."

python3 "$SCRIPT_DIR/update_db_remove_scholarly_feed_records.py" \
    "$DB"

#
# Keyword cleanup
#
