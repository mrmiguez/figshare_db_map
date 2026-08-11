#!/usr/bin/env bash

set -euo pipefail

: "${FIGSHARE_FTP_HOST:?}"
: "${FIGSHARE_FTP_USER:?}"
: "${FIGSHARE_FTP_PASS:?}"

echo
echo "=========================================================="
echo "FIGSHARE FTP TRANSFER"
echo "=========================================================="
echo "Host : $FIGSHARE_FTP_HOST"
echo "=========================================================="
echo

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

    put -c metadata.zip;
    put -c metadata.zip.sha256;

    bye
  " | tee metadata_upload.log

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

    put -c files.zip;
    put -c files.zip.sha256;

    bye
  " | tee files_upload.log

echo
echo "=========================================================="
echo "TRANSFER COMPLETE"
echo "=========================================================="