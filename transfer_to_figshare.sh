#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${FIGSHARE_FTP_HOST:?}"
: "${FIGSHARE_FTP_USER:?}"
: "${FIGSHARE_FTP_PASS:?}"

METADATA_ZIP="${METADATA_ZIP:-$SCRIPT_DIR/metadata.zip}"
METADATA_SHA="${METADATA_SHA:-$SCRIPT_DIR/metadata.zip.sha256}"

FILES_ZIP="${FILES_ZIP:-$SCRIPT_DIR/files.zip}"
FILES_SHA="${FILES_SHA:-$SCRIPT_DIR/files.zip.sha256}"

echo
echo "=========================================================="
echo "FIGSHARE FTP TRANSFER"
echo "=========================================================="
echo "Host : $FIGSHARE_FTP_HOST"
echo
echo "Metadata:"
echo "  $METADATA_ZIP"
echo "  $METADATA_SHA"
echo
echo "Assets:"
echo "  $FILES_ZIP"
echo "  $FILES_SHA"
echo "=========================================================="
echo

#
# Validate files
#

for f in \
    "$METADATA_ZIP" \
    "$METADATA_SHA" \
    "$FILES_ZIP" \
    "$FILES_SHA"
do

    if [[ ! -f "$f" ]]; then
        echo "ERROR: Missing file $f"
        exit 1
    fi

done

echo "[1/2] Uploading metadata package..."

lftp \
  -u "$FIGSHARE_FTP_USER","$FIGSHARE_FTP_PASS" \
  "$FIGSHARE_FTP_HOST" \
  -e "
    set cmd:trace yes;
    set ftp:ssl-force true;
    set ftp:ssl-protect-data true;
    set net:max-retries 100;
    set net:timeout 30;
    set xfer:clobber on;

    debug 3;

    pwd;
    cls -l;

    cd data/metadata;

    pwd;

    put -c "$METADATA_ZIP";
    put -c "$METADATA_SHA";

    bye
  " | tee "$SCRIPT_DIR/metadata_upload.log"

echo
echo "[2/2] Uploading asset package..."

lftp \
  -u "$FIGSHARE_FTP_USER","$FIGSHARE_FTP_PASS" \
  "$FIGSHARE_FTP_HOST" \
  -e "
    set cmd:trace yes;
    set ftp:ssl-force true;
    set ftp:ssl-protect-data true;
    set net:max-retries 100;
    set net:timeout 30;
    set xfer:clobber on;

    debug 3;

    pwd;
    cls -l;

    cd data/files;

    pwd;

    put -c "$FILES_ZIP";
    put -c "$FILES_SHA";

    bye
  " | tee "$SCRIPT_DIR/files_upload.log"

echo
echo "=========================================================="
echo "TRANSFER COMPLETE"
echo "=========================================================="