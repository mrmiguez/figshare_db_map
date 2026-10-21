#!/usr/bin/env bash

set -euo pipefail

#
# Locate repository regardless of current working directory
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DB="${DB:-$SCRIPT_DIR/figshare.db}"
RUN_DIR="$(dirname "$DB")"

UPDATES_DIR="${UPDATES_DIR:-$SCRIPT_DIR/updates}"
MAPPINGS_DIR="${MAPPINGS_DIR:-$SCRIPT_DIR/assets/mappings}"

S3_MODE="${S3_MODE:-true}"

SRCBUCK="${SRCBUCK:-}"
TGTBUCK="${TGTBUCK:-}"
PREFIX="${PREFIX:-}"

AUDITS_DIR="$RUN_DIR/audits"

FEDORA_COLLECTION_PIDS="$AUDITS_DIR/fedora_collection_pids.txt"
OBJECT_COLLECTION_HIERARCHY="$AUDITS_DIR/object_collection_hierarchy.csv"
SOURCE_COLLECTION_MAPPING="${SOURCE_COLLECTION_MAPPING:-$MAPPINGS_DIR/source_collection_mapping.csv}"

#
# Ensure run directories exist
#

mkdir -p "$RUN_DIR"
mkdir -p "$AUDITS_DIR"

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
# Validate required mapping files before beginning expensive work.
#

for MAPPING in groups.csv collections.csv source_collection_mapping.csv
do
    if [[ ! -f "$MAPPINGS_DIR/$MAPPING" ]]; then
        echo "ERROR: Missing required mapping file: $MAPPINGS_DIR/$MAPPING" >&2
        exit 1
    fi
done

#
# Validate required scripts before beginning expensive work.
#

REQUIRED_SCRIPTS=(
    main.py
    update_db_embargoes.py
    audit_perpetual_embargoes.py
    update_db_remove_perpetual_embargoes.py
    update_db_by_csv.py
    audit_feed_records.py
    update_db_remove_scholarly_feed_records.py
    audit_structural_objects.py
    update_db_remove_structural_objects.py
    audit_source_hierarchy.py
    update_db_add_group_collection_ids.py
    dump_db_tables.py
)

for SCRIPT in "${REQUIRED_SCRIPTS[@]}"
do
    if [[ ! -f "$SCRIPT_DIR/$SCRIPT" ]]; then
        echo "ERROR: Missing required script: $SCRIPT_DIR/$SCRIPT" >&2
        exit 1
    fi
done

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
echo "Mappings Dir    : $MAPPINGS_DIR"
echo "Mapping         : $SOURCE_COLLECTION_MAPPING"
echo "Audits Dir      : $AUDITS_DIR"
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

echo "[1/16] Building migration database..."

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
echo "[2/16] Applying embargo updates..."

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
echo "[3/16] Auditing perpetual article embargoes..."

python3 "$SCRIPT_DIR/audit_perpetual_embargoes.py" \
    "$DB"

#
# Perpetual whole-object embargo removal
#

echo
echo "[4/16] Removing perpetual article embargoes..."

python3 "$SCRIPT_DIR/update_db_remove_perpetual_embargoes.py" \
    "$DB"

#
# Repeatable SQL fixes
#

echo
echo "[5/16] Applying SQL corrections..."

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
echo "[6/16] Applying override spreadsheets..."

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
echo "[7/16] Auditing scholarly feed records..."

python3 "$SCRIPT_DIR/audit_feed_records.py" \
    "$DB"

#
# Scholarly feed removal
#

echo
echo "[8/16] Removing Web of Science and PubMed Central records..."

python3 "$SCRIPT_DIR/update_db_remove_scholarly_feed_records.py" \
    "$DB"

#
# Derive authoritative Fedora collection inventory.
#
# Collectionhood is determined ONLY from Fedora RELS-EXT RDF:
#
#     fedora-model:hasModel
#         rdf:resource="info:fedora/islandora:collectionCModel"
#
# PID syntax is deliberately NOT used as a fallback.
#
# The resulting inventory is retained in audits/ so the exact
# classification input used for this migration run is preserved.
#

echo
echo "[9/16] Deriving Fedora collection PID inventory..."

rm -f "$FEDORA_COLLECTION_PIDS"

if [[ "$S3_MODE" == "true" ]]; then
    RELS_EXT_TMP="$(mktemp -d)"
    trap 'rm -rf "$RELS_EXT_TMP"' EXIT

    S3_SOURCE="s3://$SRCBUCK"

    if [[ -n "$PREFIX" ]]; then
        S3_SOURCE="$S3_SOURCE/$PREFIX"
    fi

    echo "    Source: $S3_SOURCE"
    echo "    Downloading RELS-EXT RDF..."

    aws s3 cp \
        "$S3_SOURCE" \
        "$RELS_EXT_TMP" \
        --recursive \
        --exclude "*" \
        --include "*RELS-EXT*"

    RELS_EXT_ROOT="$RELS_EXT_TMP"
else
    RELS_EXT_ROOT="$ROOT"
fi

#
# Parse only RELS-EXT files that explicitly declare
# islandora:collectionCModel.
#
# Fedora RDF uses the subject URI to identify the object:
#
#     rdf:about="info:fedora/fsu:405773"
#
# We extract the PID from that declaration rather than inferring it
# from directory names or PID syntax.
#

python3 - "$RELS_EXT_ROOT" "$FEDORA_COLLECTION_PIDS" <<'PY'
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(sys.argv[1])
output = Path(sys.argv[2])

RDF_ABOUT = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
RDF_RESOURCE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"

FEDORA_PREFIX = "info:fedora/"
COLLECTION_MODEL = "info:fedora/islandora:collectionCModel"

collection_pids = set()
rels_ext_files = 0
parse_errors = []

for path in root.rglob("*"):
    if not path.is_file():
        continue

    if "RELS-EXT" not in path.name:
        continue

    rels_ext_files += 1

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        parse_errors.append((path, str(exc)))
        continue

    for description in tree.getroot().iter():
        about = description.attrib.get(RDF_ABOUT)

        if not about or not about.startswith(FEDORA_PREFIX):
            continue

        is_collection = any(
            element.attrib.get(RDF_RESOURCE) == COLLECTION_MODEL
            for element in description
        )

        if is_collection:
            collection_pids.add(about[len(FEDORA_PREFIX):])

if parse_errors:
    print(
        f"ERROR: {len(parse_errors)} RELS-EXT file(s) could not be parsed.",
        file=sys.stderr,
    )

    for path, error in parse_errors[:20]:
        print(f"    {path}: {error}", file=sys.stderr)

    if len(parse_errors) > 20:
        print(
            f"    ... plus {len(parse_errors) - 20} additional parse errors",
            file=sys.stderr,
        )

    sys.exit(1)

if rels_ext_files == 0:
    print(
        "ERROR: No RELS-EXT files were found in the Fedora source.",
        file=sys.stderr,
    )
    sys.exit(1)

if not collection_pids:
    print(
        "ERROR: RELS-EXT files were found but none declared "
        "islandora:collectionCModel.",
        file=sys.stderr,
    )
    sys.exit(1)

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8") as fh:
    for pid in sorted(collection_pids):
        fh.write(pid + "\n")

print(f"    RELS-EXT files examined: {rels_ext_files:,}")
print(f"    Fedora collectionCModel PIDs: {len(collection_pids):,}")
print(f"    Inventory: {output}")
PY

#
# Clean temporary S3 download now rather than waiting for shell exit.
#

if [[ "$S3_MODE" == "true" ]]; then
    rm -rf "$RELS_EXT_TMP"
    trap - EXIT
fi

#
# Repository structural-object audit.
#
# The Fedora collectionCModel inventory is authoritative.
# No numeric/nonnumeric PID heuristic is used.
#

echo
echo "[10/16] Auditing Fedora collection objects..."

python3 "$SCRIPT_DIR/audit_structural_objects.py" \
    "$DB" \
    "$FEDORA_COLLECTION_PIDS"

#
# Repository structural-object removal
#

echo
echo "[11/16] Removing Fedora collection objects..."

python3 "$SCRIPT_DIR/update_db_remove_structural_objects.py" \
    "$DB" \
    "$FEDORA_COLLECTION_PIDS"

#
# Resolve authoritative source hierarchy for the surviving
# migration population.
#
# audit_source_hierarchy.py follows both:
#
#     fedora:isMemberOfCollection
#     fedora:isConstituentOf
#
# Compound-object parents are traversed, but only collectionCModel
# nodes are retained in collection_hierarchy.
#

echo
echo "[12/16] Resolving Fedora source hierarchy..."

rm -f "$OBJECT_COLLECTION_HIERARCHY"

python3 "$SCRIPT_DIR/audit_source_hierarchy.py" \
    --export "$OBJECT_COLLECTION_HIERARCHY"

if [[ ! -s "$OBJECT_COLLECTION_HIERARCHY" ]]; then
    echo "ERROR: Source hierarchy audit was not created: $OBJECT_COLLECTION_HIERARCHY" >&2
    exit 1
fi

#
# Apply Figshare group and collection mappings.
#
# source_collection_mapping.csv maps each resolved Fedora hierarchy
# to the target Figshare group and optional collection.
#
# The blank hierarchy mapping is intentional. It assigns the known
# source-hierarchy-gap objects to the configured fallback group.
#
# fsu:honors_ethical_issues_and_life_choices is explicitly excluded
# by update_db_add_group_collection_ids.py.
#

echo
echo "[13/16] Applying Figshare group and collection IDs..."

python3 "$SCRIPT_DIR/update_db_add_group_collection_ids.py" \
    --mapping "$SOURCE_COLLECTION_MAPPING" \
    --hierarchy "$OBJECT_COLLECTION_HIERARCHY"

#
# Export tables
#

echo
echo "[14/16] Exporting database tables..."

python3 "$SCRIPT_DIR/dump_db_tables.py" \
    "$DB"

#
# Add Figshare group / collection maps to exports.
#
# Mapping sources remain versioned under assets/mappings,
# but delivery copies are placed alongside the other CSVs.
#

echo "    Adding mapping CSVs..."

for MAPPING in groups.csv collections.csv source_collection_mapping.csv
do
    cp \
        "$MAPPINGS_DIR/$MAPPING" \
        "$RUN_DIR/exports/$MAPPING"
done

#
# Package metadata
#

echo
echo "[15/16] Creating metadata packages..."

ARCHIVE_DIR="$RUN_DIR/metadata_archive"
FIGSHARE_DIR="$RUN_DIR/metadata_figshare"

rm -rf "$ARCHIVE_DIR"
rm -rf "$FIGSHARE_DIR"

mkdir -p "$ARCHIVE_DIR"
mkdir -p "$FIGSHARE_DIR"

#
# Remove stale packages before rebuilding.
#

rm -f \
    "$RUN_DIR/metadata_archive.zip" \
    "$RUN_DIR/metadata_archive.zip.sha256" \
    "$RUN_DIR/metadata.zip" \
    "$RUN_DIR/metadata.zip.sha256"

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
# Final status
#

echo
echo "[16/16] Database status..."

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

echo
echo "Packages:"

ls -lh \
    "$RUN_DIR/metadata_archive.zip" \
    "$RUN_DIR/metadata_archive.zip.sha256" \
    "$RUN_DIR/metadata.zip" \
    "$RUN_DIR/metadata.zip.sha256"