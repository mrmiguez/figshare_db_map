#!/usr/bin/env bash

set -euo pipefail

#
# Locate repository regardless of current working directory
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DB="${DB:-$SCRIPT_DIR/figshare.db}"
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
echo "Updates Dir     : $UPDATES_DIR"
echo "S3 Mode         : $S3_MODE"
echo "Bucket          : $BUCKET"
echo "=========================================================="
echo

#
# Rebuild database
#

echo "[1/8] Building migration database..."

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
echo "[2/8] Applying embargo updates..."

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
echo "[3/8] Applying SQL corrections..."

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
echo "[4/8] Applying override spreadsheets..."

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
# Keyword cleanup
#

echo
echo "[5/8] Deduplicating keywords..."

python3 "$SCRIPT_DIR/dedupe_keywords.py" "$DB"

#
# Export tables
#

echo
echo "[6/8] Exporting database tables..."

python3 "$SCRIPT_DIR/dump_db_tables.py" "$DB"

#
# Build metadata package
#

echo
echo "[7/8] Creating metadata.zip..."

PACKAGE_DIR="$SCRIPT_DIR/metadata_package"

rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

#
# Include database
#

cp "$DB" "$PACKAGE_DIR/"

#
# Include exported CSVs
#

find "$SCRIPT_DIR" \
    -maxdepth 1 \
    -type f \
    -name "*.csv" \
    -exec cp {} "$PACKAGE_DIR/" \;

#
# Include TSV logs
#

find "$SCRIPT_DIR" \
    -maxdepth 1 \
    -type f \
    -name "*.tsv" \
    -exec cp {} "$PACKAGE_DIR/" \;

#
# Build archive
#

(
    cd "$PACKAGE_DIR"

    zip -rq \
        "$SCRIPT_DIR/metadata.zip" \
        .
)

sha256sum \
    "$SCRIPT_DIR/metadata.zip" \
    > "$SCRIPT_DIR/metadata.zip.sha256"

#
# Status
#

echo
echo "[8/8] Database status..."

python3 "$SCRIPT_DIR/main.py" \
    --db "$DB" \
    --status

echo
echo "=========================================================="
echo "METADATA WORKFLOW COMPLETE"
echo "=========================================================="

echo
echo "Created:"
echo "  $SCRIPT_DIR/metadata.zip"
echo "  $SCRIPT_DIR/metadata.zip.sha256"

ls -lh \
    "$SCRIPT_DIR/metadata.zip" \
    "$SCRIPT_DIR/metadata.zip.sha256"