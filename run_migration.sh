#!/usr/bin/env bash

set -euo pipefail

DB="${DB:-figshare.db}"
ROOT="${ROOT:-$1}"
UPDATES_DIR="${UPDATES_DIR:-updates}"

if [[ -z "${ROOT}" ]]; then
    echo "Usage:"
    echo "  ROOT=/path/to/repository ./run_migration.sh"
    echo ""
    echo "or"
    echo ""
    echo "  ./run_migration.sh /path/to/repository"
    exit 1
fi

echo
echo "=========================================================="
echo "FIGSHARE MIGRATION WORKFLOW"
echo "=========================================================="
echo "Repository Root : $ROOT"
echo "Database        : $DB"
echo "Updates Dir     : $UPDATES_DIR"
echo "=========================================================="
echo

#
# Rebuild database
#

echo "[1/8] Building migration database..."

python3 main.py \
    --db "$DB" \
    --run \
    "$ROOT"

#
# Embargo enrichment
#

echo
echo "[2/8] Applying embargo updates..."

python3 update_db_embargoes.py \
    "$DB" \
    "$ROOT"

#
# Repeatable SQL fixes
#

echo
echo "[3/8] Applying SQL corrections..."

if [[ -d "sql" ]]; then

    for SQL in sql/*.sql
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

        python3 update_DB_by_CSV.py \
            "$DB" \
            "$CSV"
    done
fi

#
# Keyword cleanup
#

echo
echo "[5/8] Deduplicating keywords..."

python3 dedupe_keywords.py "$DB"

#
# File flattening
#

echo
echo "[6/8] Moving *_PDF* and *_OBJ* files to repository root..."

python3 flatten_asset_tree.py "$ROOT"

#
# Export tables for QA
#

echo
echo "[7/8] Exporting database tables..."

python3 dump_db_tables.py "$DB"

#
# Status summary
#

echo
echo "[8/8] Database status..."

python3 main.py \
    --db "$DB" \
    --status

echo
echo "=========================================================="
echo "Migration workflow complete."
echo "=========================================================="