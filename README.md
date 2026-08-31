# figshare_db_map

Utilities supporting the Florida State University Research Repository migration from Islandora/MODS to Figshare.

The project transforms MODS records into a structured SQLite staging database, applies migration-specific enrichments and QA corrections, and prepares content for Figshare bulk ingest.

## Features

- Parse MODS XML records into a SQLite database
- Generate Figshare-compatible metadata
- Map item types
- Map Fields of Research (FoR) category codes
- Normalize licenses
- Normalize and deduplicate keywords
- Apply embargo updates
- Apply QA spreadsheet corrections
- Audit scholarly feed records (Web of Science and PubMed Central)
- Exclude scholarly feed records from production migration datasets
- Export database tables to CSV for review
- Flatten PDF and OBJ files for bulk transfer workflows

---

## Installation

```bash
git clone git@github.com:<ORG>/figshare_db_map.git

cd figshare_db_map

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## Building the Database

Create or rebuild the migration database:

```bash
python3 figshare_db_map/main.py \
    --run \
    --db figshare.db \
    /path/to/mods/root
```

---

### S3 Mode (EC2 Migration Environment)

In the EC2 migration environment, MODS metadata can be read directly from an S3 bucket.

Example:

```bash
python3 figshare_db_map/main.py \
    --db figshare.db \
    --run \
    --s3 \
    --bucket migration-ir-1014030
```

Optionally limit processing to a specific prefix:

```bash
python3 figshare_db_map/main.py \
    --db figshare.db \
    --run \
    --s3 \
    --bucket migration-ir-1014030 \
    --prefix root/fsu_research_repository
```

This mode uses the instance IAM role and reads MODS XML directly from S3 without requiring a local repository checkout.

The traditional filesystem mode remains supported.

---

## Command-Line Usage

### Filesystem Mode

```bash
python3 main.py \
    --run \
    --db figshare.db \
    /path/to/mods/root
```

### S3 Mode

```bash
python3 main.py \
    --run \
    --db figshare.db \
    --s3 \
    --bucket migration-ir-1014030
```

### Status

```bash
python3 main.py \
    --db figshare.db \
    --status
```

### Burndown

```bash
python3 main.py \
    --db figshare.db \
    --burndown
```

---

## Migration Workflow

The migration process is divided into three independent workflows:

1. Metadata Processing
2. Asset Packaging
3. Figshare Delivery

Separating these stages allows metadata generation, asset packaging, and delivery to be rerun independently.

### Metadata Processing

```bash
./process_metadata.sh
```

Builds the migration database and creates:

```text
figshare.db
metadata.zip
metadata.zip.sha256
```

Metadata processing includes:

1. MODS → SQLite transformation
2. Embargo enrichment
3. SQL-based corrections
4. Spreadsheet-driven metadata corrections
5. Scholarly feed audit generation
6. Scholarly feed record removal
7. Keyword deduplication
8. CSV exports
9. Metadata package creation
10. Migration QA reporting

The feed audit report is preserved in the metadata archive package for QA documentation purposes.

### Asset Packaging

```bash
./process_assets.sh
```

Builds a flattened asset structure from S3 and creates:

```text
files.zip
files.zip.sha256
```

This workflow:

1. Reads source assets from S3
2. Reorganizes PDF and OBJ datastreams into Figshare ingest structure
3. Builds a local packaging directory
4. Creates a ZIP package
5. Generates SHA256 checksums

### Figshare Delivery

```bash
./transfer_to_figshare.sh
```

Uploads migration packages to Figshare FTPS.

Uploaded destinations:

```text
data/files/files.zip
data/files/files.zip.sha256

data/metadata/metadata.zip
data/metadata/metadata.zip.sha256
```

FTP credentials are read from:

```bash
FIGSHARE_FTP_HOST
FIGSHARE_FTP_USER
FIGSHARE_FTP_PASS
```

---

## QA Corrections

Override spreadsheets are loaded from:

```text
updates/
```

Each CSV must contain exactly two columns:

```text
pid,<database_field>
```

Example:

```csv
pid,item_type
fsu:862008,Thesis
fsu:912587,Model
```

Applied using:

```bash
python3 update_DB_by_CSV.py \
    figshare.db \
    updates/item_type_updates.csv
```

The column header of the second column determines which field in the `objects` table will be updated.

---

## Utility Scripts

### update_db_embargoes.py

Applies embargo metadata from migration spreadsheets.

### update_DB_by_CSV.py

Updates object records using QA-maintained CSV files.

Example:

```csv
pid,item_type
fsu:862008,Thesis
fsu:912587,Model
```

### audit_feed_records.py

Generates an audit report of scholarly feed records identified in the migration dataset.

Currently supported feed sources:

```text
Web of Science
PubMed Central
```

Output:

```text
exports/scholarly_feed_audit.csv
```

The audit report includes identifiers and provenance information needed to review records excluded from the production migration.

### stats_on_feed_records.py

Generates summary statistics and reporting for scholarly feed records.

Typical reporting includes:

```text
Record counts by feed source
Collection distribution
Identifier analysis
Quality assurance metrics
```

This utility is used for migration QA and feed inventory analysis.

### update_db_remove_scholarly_feed_records.py

Removes scholarly feed records from the SQLite migration database after audit generation and before export.

Currently removed feed sources:

```text
Web of Science
PubMed Central
```

The script removes matching records from:

```text
objects
object_authors
```

This utility is executed as part of the metadata processing workflow and ensures excluded feed records are not included in final Figshare export packages.

### dedupe_keywords.py

Removes duplicate pipe-delimited keywords.

Example:

```text
Archaeology|archaeology|Italy excavations|Archaeology
```

becomes:

```text
Archaeology|Italy excavations
```

Deduplication is case-insensitive while preserving the first occurrence.

### dump_db_tables.py

Exports all SQLite tables to CSV.

Example output:

```text
exports/
├── objects.csv
├── contributors.csv
├── files.csv
└── subjects.csv
```

### flatten_asset_tree.py

Reorganizes Islandora assets into a Figshare-friendly layout.

Assets matching:

```text
*_PDF*
*_OBJ*
```

are transformed into a flattened object-centric structure.

Example:

```text
root/.../fsu_1064943_PDF.pdf
```

becomes:

```text
fsu_1064943/
    fsu_1064943.pdf
```

Compound object example:

```text
root/.../fsu_107473/fsu_107474_OBJ.tiff
```

becomes:

```text
fsu_107473/
    fsu_107474.tiff
```

This utility is primarily used by `process_assets.sh` when building the Figshare asset package.

### transfer_to_figshare.sh

Uploads migration packages directly to the Figshare FTPS endpoint using `lftp`.

Required environment variables:

```bash
export FIGSHARE_FTP_HOST=ftps.example.org
export FIGSHARE_FTP_USER=myuser
export FIGSHARE_FTP_PASS=secret
```

The script uploads:

```text
metadata.zip
metadata.zip.sha256

files.zip
files.zip.sha256
```

Transfer logging is enabled through verbose `lftp` settings and upload logs are written locally during execution.

---

## Database Override SQL Files

Database updates can also be applied as repeatable SQL scripts.

Example:

```bash
sqlite3 figshare.db < sql/010_cetamura_keywords.sql
```

These scripts are intended for QA-approved metadata corrections that should be reproducible across migration runs.

---

## Scholarly Feed Records 

The production migration excludes records harvested from external scholarly feeds. 

Currently excluded feed sources: 

- Web of Science 
- PubMed Central 
 
These records are first ingested into the SQLite staging database to support QA review and auditing. 

### Feed Audit 

Feed records are identified using source-system identifiers stored in MODS metadata. 

Examples: 

    FSU_libsubv1_wos_000440090400002 
    FSU_pmch_26855607 

An audit report is generated using: 

```bash
python3 audit_feed_records.py figshare.db
```

Output: 

    exports/scholarly_feed_audit.csv 

The audit CSV includes: 

    pid 
    feed_source 
    iid 
    doi 
    pmcid 
    purl 
    title 
    publication_date 
    journal 
    source_collection 

Feed inventory identified during migration QA: 

    Web of Science : 1,718 records 
    PubMed Central : 1,443 records 
    Total : 3,161 records 

### Feed Record Removal 

After audit generation, scholarly feed records are removed from the migration database: 

```bash
python3 update_db_remove_scholarly_feed_records.py figshare.db 
```

This removal occurs before CSV exports and Figshare delivery package generation. The audit CSV remains available for QA review and is included in metadata archive packages. 

### Related Utilities 

audit_feed_records.py 
    
    Generates exports/scholarly_feed_audit.csv. 

stats_on_feed_records.py 

    Generates summary statistics and reporting on scholarly feed content. 

update_db_remove_scholarly_feed_records.py 

    Removes approved scholarly feed records from the migration database.

---

## Repository Layout

```text
figshare_db_map/

├── figshare_db_map/
│   ├── main.py
│   └── assets/
│       ├── cli.py
│       ├── parser.py
│       ├── data_maps.py
│       ├── db.py
│       └── records.py
│
├── process_metadata.sh
├── process_assets.sh
├── transfer_to_figshare.sh
│
├── update_db_embargoes.py
├── update_DB_by_CSV.py
├── audit_feed_records.py
├── stats_on_feed_records.py
├── update_db_remove_scholarly_feed_records.py
├── dedupe_keywords.py
├── flatten_asset_tree.py
├── dump_db_tables.py
│
├── sql/
├── updates/
├── exports/
│
├── README.md
└── requirements.txt
```

---

## End-to-End Workflow

### Metadata Pipeline

```text
MODS XML
        ↓
figshare_db_map
        ↓
SQLite DB
        ↓
Embargo updates
        ↓
QA updates
        ↓
Feed audit
        ↓
Feed removal
        ↓
Keyword cleanup
        ↓
CSV exports
        ↓
metadata.zip
```

### Asset Pipeline

```text
S3 Asset Repository
        ↓
flatten_asset_tree.py
        ↓
Local packaging directory
        ↓
files.zip
```

### Delivery Pipeline

```text
metadata.zip
files.zip
        ↓
FTPS Upload
        ↓
Figshare STAGE / PROD Ingest
```

The SQLite database remains the authoritative metadata staging layer throughout the migration process. The production migration excludes records harvested from Web of Science and PubMed Central. These records are audited, documented, and removed from the staging database prior to metadata export.