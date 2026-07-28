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

## Command-Line Usage

```text
usage: main.py [-h] [-s] [-v] [-b] [-r] [--db DB]
               record_directory

Figshare data-mapping DB utility

positional arguments:
  record_directory     path to XML records

options:
  -h, --help           show this help message and exit
  -r, --run            populate database
  -s, --status         database statistics
  -b, --burndown       destroy and recreate database
  -v, --verbose        verbose logging
  --db DB              SQLite database path
```

---

## Migration Workflow

The preferred method is to run the entire migration pipeline:

```bash
./run_migration.sh /path/to/mods/root
```

This performs:

1. MODS → SQLite transformation
2. Embargo enrichment
3. Spreadsheet-driven metadata corrections
4. Keyword deduplication
5. PDF/OBJ file staging
6. QA CSV exports
7. Database status reporting

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

### flatten_asset_tree.py

Moves files matching:

```text
*_PDF*
*_OBJ*
```

from nested collection directories to the repository root.

This is used to stage files for bulk transfer workflows.

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

### FTP upload utilities

FTP utilities read credentials from environment variables rather than storing secrets in source code.

Example:

```bash
export FIGSHARE_FTP_HOST=ftp.example.org
export FIGSHARE_FTP_USER=myuser
export FIGSHARE_FTP_PASS=secret
```

---

## Database Override SQL Files

Database updates can also be applied as repeatable SQL scripts.

Example:

```bash
sqlite3 figshare.db < sql/010_cetamura_keywords.sql
```

These scripts are intended for QA-approved metadata corrections that should be reproducible across migration runs.

---

## Repository Layout

```text
figshare_db_map/

├── figshare_db_map/
│   ├── main.py
│   └── assets/
│       ├── data_maps.py
│       ├── db.py
│       └── records.py
│
├── update_db_embargoes.py
├── update_DB_by_CSV.py
├── dedupe_keywords.py
├── flatten_asset_tree.py
├── dump_db_tables.py
│
├── run_migration.sh
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

A typical migration run follows this sequence:

```text
MODS XML
    ↓
figshare_db_map
    ↓
SQLite DB
    ↓
Embargo updates
    ↓
QA spreadsheet updates
    ↓
Keyword deduplication
    ↓
File staging (PDF / OBJ)
    ↓
CSV exports
    ↓
Figshare ingest package
```

The SQLite database serves as the authoritative staging layer throughout the migration process.