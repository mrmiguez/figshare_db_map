import os
import logging
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db.sqlite3')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def connect_db(DB_PATH):
    """init sqlite3 database and return connection"""
    db_exists = os.path.exists(DB_PATH)
    logger.info(f'DB path... {DB_PATH}')

    # Connect creates the database if it doesn't exist
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not (db_exists):
        logger.info(f'Initializing database... {DB_PATH}')
        cursor.executescript("""
                             CREATE TABLE IF NOT EXISTS authors
                             (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 firstname TEXT NOT NULL,
                                 surname TEXT NOT NULL,
                                 email TEXT,
                                 orcid TEXT
                             );

                             CREATE TABLE IF NOT EXISTS objects
                             (
                                 iid TEXT PRIMARY KEY,
                                 title TEXT NOT NULL,
                                 item_type TEXT NOT NULL,
                                 keywords TEXT,
                                 description TEXT,
                                 license TEXT
                             );

                             CREATE TABLE IF NOT EXISTS object_authors
                             (
                                 object_id INTEGER NOT NULL,
                                 author_id INTEGER NOT NULL,
                                 PRIMARY KEY
                                     ( object_id, author_id ),
                                 FOREIGN KEY
                                     ( object_id ) REFERENCES object ( id ) ON DELETE CASCADE,
                                 FOREIGN KEY
                                     ( author_id ) REFERENCES author ( id ) ON DELETE CASCADE
                             );
                             """)

    return conn


def get_db_status(db_conn):
    """
    Return a dict mapping table_name -> row_count
    for all non-internal SQLite tables.
    """

    # Get all user-defined tables (skip sqlite_* internals)
    cursor = db_conn.cursor()
    cursor.execute("""
                   SELECT name
                   FROM sqlite_master
                   WHERE type = 'table'
                     AND name NOT LIKE 'sqlite_%';
                   """)
    tables = [row[0] for row in cursor.fetchall()]

    status = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        (count,) = cursor.fetchone()
        status[table] = count

    return status


def write_db_record(db_conn, record):
    """"""
    cursor = db_conn.cursor()
    cursor.execute('INSERT INTO objects VALUES (?, ?, ?, ?, ?, ?)',
                   (record.iid, # iid
                    'bar', # test
                    #record.titles, # title
                    'spam', # item_type
                    'eggs', # keywords
                    'boo', # description
                    'bork')) # license
    db_conn.commit()
