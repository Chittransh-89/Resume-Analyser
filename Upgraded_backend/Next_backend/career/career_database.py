"""Career Database Setup"""
import os
import sqlite3
from contextlib import contextmanager

# Absolute path use karo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "career_database.db")


def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ========================================
    # 1. CAREER TABLE (Main info)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career(
            career_id           TEXT PRIMARY KEY,
            title               TEXT NOT NULL,
            category            TEXT,
            description         TEXT,
            difficulty          TEXT,
            demand              TEXT
        )
    """)

    # ========================================
    # 2. REQUIRED SKILLS (Flexible)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS required_skills(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            skill_category  TEXT,
            skill_name      TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    # ========================================
    # 3. ROADMAP (Phases)
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            phase_order     INTEGER,
            phase_name      TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    # ========================================
    # 4. ROADMAP TASKS
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_tasks(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id      INTEGER,
            task            TEXT,
            FOREIGN KEY (roadmap_id) REFERENCES roadmap(id)
        )
    """)

    # ========================================
    # 5. SALARY RANGE
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_range(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            location        TEXT,
            salary          TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    # ========================================
    # 6. JOB TITLES
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_job_titles(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            job_title       TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    # ========================================
    # 7. COMPANIES HIRING
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_companies(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            company         TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    # ========================================
    # 8. CERTIFICATIONS
    # ========================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_certifications(
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id       TEXT,
            certification   TEXT,
            FOREIGN KEY (career_id) REFERENCES career(career_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Career Database Initialized!")
    print(f"📁 Location: {DB_NAME}")


@contextmanager
def get_careerdb_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


if __name__ == '__main__':
    init_database()