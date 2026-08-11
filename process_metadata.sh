#
# Export tables
#

echo
echo "[6/8] Exporting database tables..."

python3 dump_db_tables.py "$DB"

#
# Package metadata
#

echo
echo "[7/8] Creating metadata.zip..."

mkdir -p metadata_package

cp "$DB" metadata_package/

cp ./*.csv metadata_package/ 2>/dev/null || true
cp ./*.tsv metadata_package/ 2>/dev/null || true

cd metadata_package

zip -rq ../metadata.zip .

cd ..

sha256sum metadata.zip \
    > metadata.zip.sha256

#
# Status summary
#

echo
echo "[8/8] Database status..."

python3 main.py \
    --db "$DB" \
    --status
