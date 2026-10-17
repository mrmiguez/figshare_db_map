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

echo
echo "[9/12] Deduplicating keywords..."

python3 "$SCRIPT_DIR/update_db_dedupe_keywords.py" \
    "$DB"

#
# Export tables
#

echo
echo "[10/12] Exporting database tables..."

python3 "$SCRIPT_DIR/dump_db_tables.py" \
    "$DB"

#
# Package metadata
#

echo
echo "[11/12] Creating metadata packages..."

ARCHIVE_DIR="$RUN_DIR/metadata_archive"
FIGSHARE_DIR="$RUN_DIR/metadata_figshare"

rm -rf "$ARCHIVE_DIR"
rm -rf "$FIGSHARE_DIR"

mkdir -p "$ARCHIVE_DIR"
mkdir -p "$FIGSHARE_DIR"

#
# Preservation package
#

echo "    Building metadata_archive.zip..."

cp "$DB" "$ARCHIVE_DIR/"

if [[ -d "$RUN_DIR/exports" ]]; then
    cp -r "$RUN_DIR/exports" "$ARCHIVE_DIR/"
fi

if [[ -d "$RUN_DIR/audits" ]]; then
    cp -r "$RUN_DIR/audits" "$ARCHIVE_DIR/"
fi

find "$RUN_DIR" \
    -maxdepth 1 \
    -type f \
    -name "*.tsv" \
    -exec cp {} "$ARCHIVE_DIR/" \;

if [[ -f "$SCRIPT_DIR/README.md" ]]; then
    cp "$SCRIPT_DIR/README.md" "$ARCHIVE_DIR/"
fi

(
    cd "$ARCHIVE_DIR"

    zip -rq \
        "$RUN_DIR/metadata_archive.zip" \
        .
)

sha256sum \
    "$RUN_DIR/metadata_archive.zip" \
    > "$RUN_DIR/metadata_archive.zip.sha256"

#
# Upload preservation copy
#

if [[ -n "$TGTBUCK" ]]; then

    echo
    echo "    Uploading preservation copy to:"
    echo "        s3://$TGTBUCK/archive/"

    aws s3 cp \
        "$RUN_DIR/metadata_archive.zip" \
        "s3://$TGTBUCK/archive/metadata_archive.zip"

    aws s3 cp \
        "$RUN_DIR/metadata_archive.zip.sha256" \
        "s3://$TGTBUCK/archive/metadata_archive.zip.sha256"

else

    echo
    echo "    TGTBUCK not set; skipping preservation upload."

fi

#
# Figshare delivery package
#

echo
echo "    Building metadata.zip..."

if [[ -d "$RUN_DIR/exports" ]]; then
    cp -r "$RUN_DIR/exports" "$FIGSHARE_DIR/"
fi

(
    cd "$FIGSHARE_DIR"

    zip -rq \
        "$RUN_DIR/metadata.zip" \
        .
)

sha256sum \
    "$RUN_DIR/metadata.zip" \
    > "$RUN_DIR/metadata.zip.sha256"

#
# Status
#

echo
echo "[12/12] Database status..."

python3 "$SCRIPT_DIR/main.py" \
    --db "$DB" \
    --status

echo
echo "=========================================================="
echo "METADATA WORKFLOW COMPLETE"
echo "=========================================================="

echo
echo "Created:"
echo "  $RUN_DIR/metadata_archive.zip"
echo "  $RUN_DIR/metadata_archive.zip.sha256"
echo "  $RUN_DIR/metadata.zip"
echo "  $RUN_DIR/metadata.zip.sha256"

if [[ -d "$RUN_DIR/audits" ]]; then
    echo "  $RUN_DIR/audits/"
fi

ls -lh \
    "$RUN_DIR/metadata_archive.zip" \
    "$RUN_DIR/metadata_archive.zip.sha256" \
    "$RUN_DIR/metadata.zip" \
    "$RUN_DIR/metadata.zip.sha256"