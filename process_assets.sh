#!/usr/bin/env bash

set -euo pipefail

FILES_DIR="${FILES_DIR:-/data/files}"

rm -rf "$FILES_DIR"
mkdir -p "$FILES_DIR"

echo
echo "[1/4] Flattening assets..."

python3 flatten_asset_tree.py \
    --local-root "$FILES_DIR"

echo
echo "[2/4] Creating files.zip..."

cd /data

zip -rq files.zip files

echo
echo "[3/4] Generating checksum..."

sha256sum files.zip \
    > files.zip.sha256

echo
echo "[4/4] Done"

ls -lh \
    files.zip \
    files.zip.sha256