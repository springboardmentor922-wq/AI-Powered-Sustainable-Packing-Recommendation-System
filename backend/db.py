"""
Database Module
MySQL connection utilities for EcoPackAI
"""

import pymysql
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def get_db():
    """
    Returns a MySQL connection
    """
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def test_connection():
    """
    Tests MySQL connectivity
    Returns True / False
    """
    try:
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Allow standalone test
if __name__ == "__main__":
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")