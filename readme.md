# figshare_db_map

Program to aid in the MODS to Figshare data mapping process. Iterates over a directory of MODS records to populate a SQLite database.

Usage:
```shell
$> python3 figshare_db_map/main.py --help

usage: main.py [-h] [-s] [-v] [-b] [-r] record_directory

Figshare data-mapping DB utility

options:
  -h, --help        show this help message and exit
  -s, --status      get DB status
  -v, --verbose
  -b, --burndown    burndown database

Run data mapping:
  -r, --run
  record_directory  path to XML records
```