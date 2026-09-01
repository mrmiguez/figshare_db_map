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
BUCKET="${BUCKET:-${SRCBUCK:-}}"
PREFIX="${PREFIX:-}"

#
# Validate arguments
#

if [[ "$S3_MODE" == "true" ]]; then

    if [[ -z "$BUCKET" ]]; then
        echo "ERROR: BUCKET (or SRCBUCK) must be set"
        exit 1
    fi

fi

echo
echo "=========================================================="
echo "FIGSHARE METADATA WORKFLOW"
echo "=========================================================="
echo "Repository      : $SCRIPT_DIR"
echo "Database        : $DB"
echo "Run Dir         : $RUN_DIR"
echo "Updates Dir     : $UPDATES_DIR"
echo "S3 Mode         : $S3_MODE"
echo "Bucket          : $BUCKET"
echo "=========================================================="
echo

#
# Rebuild database
#

echo "[1/10] Building migration database..."

if [[ "$S3_MODE" == "true" ]]; then

    python3 "$SCRIPT_DIR/main.py" \
        --db "$DB" \
        --run \
        --s3 \
        --bucket "$BUCKET" \
        --prefix "$PREFIX"

else

    ROOT="${ROOT:-${1:-}}"

    python3 "$SCRIPT_DIR/main.py" \
        --db "$DB" \
        --run \
        "$ROOT"

fi

#
# Embargo enrichment
#

echo
echo "[2/10] Applying embargo updates..."

if [[ "$S3_MODE" != "true" ]]; then

    python3 "$SCRIPT_DIR/update_db_embargoes.py" \
        "$DB" \
        "$ROOT"

else

    echo "Skipping embargo update in S3 mode"

fi

#
# Repeatable SQL fixes
#

echo
echo "[3/10] Applying SQL corrections..."

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
echo "[4/10] Applying override spreadsheets..."

if [[ -d "$UPDATES_DIR" ]]; then

    for CSV in "$UPDATES_DIR"/*.csv
    do

        [[ -e "$CSV" ]] || continue

        echo "    Applying: $(basename "$CSV")"

        python3 "$SCRIPT_DIR/update_DB_by_CSV.py" \
            "$DB" \
            "$CSV"

    done

fi

#
# Feed audit
#

echo
echo "[5/10] Auditing scholarly feed records..."

python3 "$SCRIPT_DIR/audit_feed_records.py" "$DB"

#
# Feed removal
#

echo
echo "[6/10] Removing Web of Science and PubMed Central records..."

python3 "$SCRIPT_DIR/update_db_remove_scholarly_feed_records.py" "$DB"

#
# Keyword cleanup
#

echo
echo "[7/10] Deduplicating keywords..."

python3 "$SCRIPT_DIR/dedupe_keywords.py" "$DB"

#
# Export tables
#

echo
echo "[8/10] Exporting database tables..."

python3 "$SCRIPT_DIR/dump_db_tables.py" "$DB"

#
# Package metadata
#

echo
echo "[9/10] Creating metadata packages..."

ARCHIVE_DIR="$RUN_DIR/metadata_archive"
FIGSHARE_DIR="$RUN_DIR/metadata_figshare"

rm -rf "$ARCHIVE_DIR"
rm -rf "$FIGSHARE_DIR"

mkdir -p "$ARCHIVE_DIR"
mkdir -p "$FIGSHARE_DIR"

#
# Local preservation package
#

echo "    Building metadata_archive.zip..."

cp "$DB" "$ARCHIVE_DIR/"

if [[ -d "$RUN_DIR/exports" ]]; then
    cp -r "$RUN_DIR/exports" "$ARCHIVE_DIR/"
fi

find "$SCRIPT_DIR" \
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
# Preservation copy to S3
#

if [[ -n "${SRCBUCK:-}" ]]; then

    echo
    echo "    Uploading preservation copy to:"
    echo "        s3://$SRCBUCK/archive/"

    aws s3 cp \
        "$RUN_DIR/metadata_archive.zip" \
        "s3://$SRCBUCK/archive/metadata_archive.zip"

    aws s3 cp \
        "$RUN_DIR/metadata_archive.zip.sha256" \
        "s3://$SRCBUCK/archive/metadata_archive.zip.sha256"

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
echo "[10/10] Database status..."

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

ls -lh \
    "$RUN_DIR/metadata_archive.zip" \
    "$RUN_DIR/metadata_archive.zip.sha256" \
    "$RUN_DIR/metadata.zip" \
    "$RUN_DIR/metadata.zip.sha256"