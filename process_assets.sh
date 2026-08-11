#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FILES_DIR="${FILES_DIR:-/data/files}"
FILES_ZIP="${FILES_ZIP:-$SCRIPT_DIR/files.zip}"
FILES_SHA="${FILES_SHA:-$SCRIPT_DIR/files.zip.sha256}"

: "${SRCBUCK:?}"

echo
echo "=========================================================="
echo "FIGSHARE ASSET PACKAGING"
echo "=========================================================="
echo "Repository : $SCRIPT_DIR"
echo "Source     : $SRCBUCK"
echo "Files Dir  : $FILES_DIR"
echo "Output ZIP : $FILES_ZIP"
echo "=========================================================="
echo

echo "[1/4] Preparing local asset directory..."

rm -rf "$FILES_DIR"
mkdir -p "$FILES_DIR"

echo
echo "[2/4] Building flattened asset tree..."

python3 "$SCRIPT_DIR/flatten_asset_tree.py" \
    --execute \
    --local-root "$FILES_DIR"

echo
echo "[3/4] Creating files.zip..."

(
    cd "$(dirname "$FILES_DIR")"

    zip -rq \
        "$FILES_ZIP" \
        "$(basename "$FILES_DIR")"
)

echo
echo "[4/4] Generating checksum..."

sha256sum "$FILES_ZIP" \
    > "$FILES_SHA"

echo
echo "=========================================================="
echo "ASSET PACKAGING COMPLETE"
echo "=========================================================="

ls -lh \
    "$FILES_ZIP" \
    "$FILES_SHA"