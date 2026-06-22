"""Database queries - replaces old skills_data.py functions."""
"""Database -> Use in Code"""
from database import get_db_connection

def get_skill(skill_id):
    """Ek skill ka poora data nikalo."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Main skill data
        cursor.execute(
            "SELECT * FROM skills WHERE skill_id = ?", 
            (skill_id,)
        )
        skill_row = cursor.fetchone()
        
        if not skill_row:
            return None
        
        # Dictionary mein convert karo
        skill = dict(skill_row)
        
        # 2. Free resources
        cursor.execute(
            "SELECT title, url, resource_type FROM resources WHERE skill_id = ? AND is_free = 1",
            (skill_id,)
        )
        skill['free_resources'] = [
            {"title": r[0], "url": r[1], "type": r[2]}
            for r in cursor.fetchall()
        ]
        
        # 3. Paid resources
        cursor.execute(
            "SELECT title, url, resource_type FROM resources WHERE skill_id = ? AND is_free = 0",
            (skill_id,)
        )
        skill['paid_resources'] = [
            {"title": r[0], "url": r[1], "type": r[2]}
            for r in cursor.fetchall()
        ]
        
        # 4. Use cases
        cursor.execute(
            "SELECT use_case FROM use_cases WHERE skill_id = ?",
            (skill_id,)
        )
        skill['use_cases'] = [r[0] for r in cursor.fetchall()]
        
        # 5. YouTube channels
        cursor.execute(
            "SELECT channel FROM youtube_channels WHERE skill_id = ?",
            (skill_id,)
        )
        skill['youtube_channels'] = [r[0] for r in cursor.fetchall()]
        
        return skill


def search_skills(query):
    """Keyword search karo."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query_pattern = f"%{query.lower()}%"
        
        cursor.execute("""
            SELECT skill_id FROM skills 
            WHERE LOWER(name) LIKE ? 
               OR LOWER(category) LIKE ?
               OR LOWER(description) LIKE ?
        """, (query_pattern, query_pattern, query_pattern))
        
        skill_ids = [row[0] for row in cursor.fetchall()]
        
        # Har skill ka full data nikalo
        return {sid: get_skill(sid) for sid in skill_ids}


def get_skills_for_career(career_id):
    """Career ki saari skills nikalo."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT skill_id FROM career_skills WHERE career_id = ?",
            (career_id,)
        )
        
        skill_ids = [row[0] for row in cursor.fetchall()]
        return {sid: get_skill(sid) for sid in skill_ids}


def get_all_skills():
    """Saari skills nikalo."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT skill_id FROM skills")
        skill_ids = [row[0] for row in cursor.fetchall()]
        return {sid: get_skill(sid) for sid in skill_ids}