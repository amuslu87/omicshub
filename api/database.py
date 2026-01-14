"""
Database connection utilities for OmicsHub API
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Database configuration - uses environment variables with fallback to localhost
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'database': os.getenv('DATABASE_NAME', 'omicshub'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '7856'),
    'port': int(os.getenv('DATABASE_PORT', '5432'))
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
