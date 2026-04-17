import mysql.connector
from config import get_db_config


def get_connection():
    """Create and return a new MySQL connection."""
    return mysql.connector.connect(**get_db_config())


def query(sql, params=None):
    """
    Execute a SELECT query and return results as a list of dicts.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


def query_one(sql, params=None):
    """
    Execute a SELECT query and return a single row as dict (or None).
    """
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    """
    Execute an INSERT / UPDATE / DELETE query.
    Commits the transaction and returns the lastrowid.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
