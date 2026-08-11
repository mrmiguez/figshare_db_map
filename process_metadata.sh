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

    echo "Skipping