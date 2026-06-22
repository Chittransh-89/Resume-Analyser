"""SQLite database setup and connection."""

# Step 1: Database File banao            (Restaurant kholo)
#    ↓
# Step 2: Tables banao (Schema)          (Furniture lagao)
#    ↓
# Step 3: Data daalo (Migration)         (Khana stock karo)
#    ↓
# Step 4: Data nikalo (Query)            (Customer ko serve karo)
#    ↓
# Step 5: Connection close karo          (Restaurant band karo)

import sqlite3
import os
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "skills_database.db")

def init_database():
    """Database aur tables create karo (sirf pehli baar)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table 1: Skills
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id        TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            category        TEXT,
            difficulty      TEXT,
            time_to_learn   TEXT,
            description     TEXT
        )
    """)
    
    # Table 2: Resources
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id        TEXT,
            title           TEXT,
            url             TEXT,
            resource_type   TEXT,
            is_free         BOOLEAN DEFAULT 1,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)
    
    # Table 3: Use Cases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS use_cases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id    TEXT,
            use_case    TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)
    
    # Table 4: YouTube Channels
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_channels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id    TEXT,
            channel     TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id  TEXT,
            platform TEXT, 
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)
    
    # Table 5: Career-Skill Mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_skills (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id   TEXT,
            skill_id    TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


@contextmanager
def get_db_connection():
    """Safe connection - auto close hota hai."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Dictionary-like access
    try:
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()