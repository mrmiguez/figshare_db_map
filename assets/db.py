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
                                 firstname TEXT,
                                 surname TEXT,
                                 email TEXT,
                                 orcid TEXT,
                                 identity TEXT UNIQUE
                             );

                             CREATE TABLE IF NOT EXISTS objects

                             (
                                 pid TEXT PRIMARY KEY,                            
                                 title TEXT NOT NULL,
                                 category TEXT,
                                 item_type TEXT NOT NULL,                            
                                 keywords TEXT,                          
                                 description TEXT,                                 
                                 publication_date TEXT, 
                                 license TEXT,
                                 embargo_date TEXT,
                                 embargo_type TEXT,
                                 embargo_reason TEXT,
                                 identifier TEXT,  -- doi or handle
                                 language TEXT,
                                 publisher TEXT,
                                 journal TEXT,
                                 volume TEXT,
                                 issue TEXT,
                                 physical_location TEXT,
                                 purl TEXT,
                                 notes TEXT,
                                 other_identifiers TEXT,
                                 contributors TEXT,
                                 subjects TEXT,
                                 source_collection TEXT

                             );

                     
                            CREATE TABLE IF NOT EXISTS object_authors
                            (
                                object_id TEXT NOT NULL,
                                author_id INTEGER NOT NULL,
                                PRIMARY KEY (object_id, author_id),
                                FOREIGN KEY (object_id) REFERENCES objects(pid) ON DELETE CASCADE,
                                FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
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



def write_db_record(db_conn, pid, record, coll_path):

    from assets.records import ObjectRecord

    obj = ObjectRecord(pid, record, coll_path)
    cursor = db_conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO objects (
                pid,
                title,
                item_type,
                keywords,
                description,
                license,
                publication_date,
                language,
                publisher,
                journal,
                volume,
                issue,
                physical_location,
                purl,
                notes,
                subjects,
                other_identifiers,
                contributors,
                source_collection
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?
            )
            ''',
            (
                pid,
                obj.title or "[no title]",
                obj.item_type,
                obj.keywords,
                obj.description,
                obj.license,
                obj.publication_date,
                obj.language,
                obj.publisher,
                obj.journal_title,
                obj.volume,
                obj.issue,
                obj.physical_location,
                obj.purl,
                obj.notes,
                obj.subjects,
                obj.other_identifiers,
                obj.contributors,
                str(obj.collection_path)
            )
        )

    except Exception as e:
        logger.exception(f"Failed to insert... {pid}: {e}")

    db_conn.commit()


def write_author_record(db_conn, author):
    cursor = db_conn.cursor()

    identity = author["identity"]

    # Try insert
    cursor.execute(
        """
        INSERT OR IGNORE INTO authors
        (firstname, surname, email, orcid, identity)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            author["firstname"],
            author["surname"],
            author["email"],
            author["orcid"],
            identity
        )
    )

    # Always fetch ID
    cursor.execute(
        "SELECT id FROM authors WHERE identity = ?",
        (identity,)
    )

    row = cursor.fetchone()

    if row is None:
        logger.error(
            f"Failed to insert author: {author}"
        )
        return None

    return row[0]


def link_author_to_object(db_conn, pid, author_id):
    cursor = db_conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO object_authors (object_id, author_id)
        VALUES (?, ?)
        """,
        (pid, author_id)
    )


