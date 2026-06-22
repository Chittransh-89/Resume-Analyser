"""Resources Database Setup"""

import sqlite3
import os
from contextlib import contextmanager

# Absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "resources_database.db")


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ========================================
    # 1. LEARNING PLATFORMS (free/paid/practice)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platforms(
            platform_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            url             TEXT,
            type            TEXT,
            category        TEXT,
            price_range     TEXT,
            description     TEXT
        )
    """)
    
    # ========================================
    # 2. PLATFORM BEST FOR (use cases)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_best_for(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_id     INTEGER,
            use_case        TEXT,
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id)
        )
    """)
    
    # ========================================
    # 3. YOUTUBE CHANNELS
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_channels(
            channel_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            url             TEXT,
            subscribers     TEXT,
            language        TEXT,
            category        TEXT,
            best_for        TEXT
        )
    """)
    
    # ========================================
    # 4. INTERVIEW RESOURCES
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_resources(
            resource_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            url             TEXT,
            category        TEXT,
            description     TEXT
        )
    """)
    
    # ========================================
    # 5. COMMUNITIES
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communities(
            community_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            url             TEXT,
            platform        TEXT,
            description     TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Resources Database Initialized!")
    print(f"📁 Location: {DB_NAME}")


@contextmanager
def get_resourcesdb_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


if __name__ == '__main__':
    init_database()