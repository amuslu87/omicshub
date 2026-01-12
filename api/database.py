"""
Database connection utilities for OmicsHub API
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'omicshub',
    'user': 'postgres',
    'password': '7856'
}

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Automatically handles connection closing
    """
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

def get_db_cursor(conn):
    """Get a cursor from connection"""
    return conn.cursor()

# Test connection function
def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM genes")
            result = cursor.fetchone()
            return {"status": "connected", "gene_count": result['count']}
    except Exception as e:
        return {"status": "error", "message": str(e)}
