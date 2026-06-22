"""Old dictionary data ko database mein migrate karo."""
"""Dictionary -> Database"""
from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.skills.skills_database import get_db_connection
from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.skills.skills_data import SKILLS_DATABASE

def migrate_skills_to_db(): 
    """SKILLS_DATABASE dictionary se SQLite mein data daalo."""
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for skill_id, skill in SKILLS_DATABASE.items():
            
            # 1. Main skill insert karo
            cursor.execute("""
                INSERT OR REPLACE INTO skills 
                (skill_id, name, category, difficulty, time_to_learn, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                skill_id,
                skill['name'],
                skill['category'],
                skill['difficulty'],
                skill['time_to_learn'],
                skill['description']
            ))
            
            # 2. Free resources insert karo
            for resource in skill.get('free_resources', []):
                cursor.execute("""
                    INSERT INTO resources 
                    (skill_id, title, url, resource_type, is_free)
                    VALUES (?, ?, ?, ?, 1)
                """, (
                    skill_id,
                    resource['title'],
                    resource['url'],
                    resource['type']
                ))
            
            # 3. Paid resources insert karo
            for resource in skill.get('paid_resources', []):
                cursor.execute("""
                    INSERT INTO resources 
                    (skill_id, title, url, resource_type, is_free)
                    VALUES (?, ?, ?, ?, 0)
                """, (
                    skill_id,
                    resource['title'],
                    resource['url'],
                    resource['type']
                ))
            
            # 4. Use cases insert karo
            for use_case in skill.get('use_cases', []):
                cursor.execute("""
                    INSERT INTO use_cases (skill_id, use_case)
                    VALUES (?, ?)
                """, (skill_id, use_case))
            
            # 5. YouTube channels insert karo
            for channel in skill.get('youtube_channels', []):
                cursor.execute("""
                    INSERT INTO youtube_channels (skill_id, channel)
                    VALUES (?, ?)
                """, (skill_id, channel))

            for practice in skill.get('practice_platforms',[]):
                cursor.execute(""" 
                    INSERT INTO practice_platforms (skill_id, platform)
                    VALUES(? ,?) 
                """,(skill_id,practice))
            
            # 6. Career mapping insert karo
            for career_id in skill.get('related_careers', []):
                cursor.execute("""
                    INSERT INTO career_skills (career_id, skill_id)
                    VALUES (?, ?)
                """, (career_id, skill_id))
            
            print(f"✅ Migrated: {skill['name']}")
        
        conn.commit()
    
    print("\n🎉 All skills migrated to database!")


if __name__ == "__main__":
    migrate_skills_to_db()