"""Career data migration to database"""

from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.career.career_database import get_careerdb_connection
from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.career.career_data import CAREER_PATHS


def migrate_career_to_db():
    with get_careerdb_connection() as conn:
        cursor = conn.cursor()
        
        for career_id, career_path in CAREER_PATHS.items():
            
            # ========================================
            # 1. MAIN CAREER TABLE
            # ========================================
            cursor.execute("""
                INSERT OR REPLACE INTO career
                (career_id, title, category, description, difficulty, demand)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                career_id,
                career_path['title'],
                career_path['category'],
                career_path['description'],
                career_path['difficulty'],
                career_path['demand']
            ))
            
            # ========================================
            # 2. REQUIRED SKILLS (Nested Dictionary!)
            # ========================================
            required_skills = career_path.get('required_skills', {})
            
            # Loop 1: Categories (core, frameworks, tools...)
            for skill_category, skills_list in required_skills.items():
                
                # Loop 2: Skills in each category
                for skill_name in skills_list:
                    cursor.execute("""
                        INSERT INTO required_skills
                        (career_id, skill_category, skill_name)
                        VALUES (?, ?, ?)
                    """, (career_id, skill_category, skill_name))
            
            # ========================================
            # 3. ROADMAP + TASKS (Nested!)
            # ========================================
            for phase_order, phase_data in enumerate(career_path.get('roadmap', []), start=1):
                
                # Insert roadmap phase
                cursor.execute("""
                    INSERT INTO roadmap
                    (career_id, phase_order, phase_name)
                    VALUES (?, ?, ?)
                """, (career_id, phase_order, phase_data['phase']))
                
                # Get the roadmap_id we just inserted
                roadmap_id = cursor.lastrowid
                
                # Insert all tasks for this phase
                for task in phase_data.get('tasks', []):
                    cursor.execute("""
                        INSERT INTO roadmap_tasks
                        (roadmap_id, task)
                        VALUES (?, ?)
                    """, (roadmap_id, task))
            
            # ========================================
            # 4. SALARY RANGE
            # ========================================
            salary_range = career_path.get('salary_range', {})
            for location, salary in salary_range.items():
                cursor.execute("""
                    INSERT INTO salary_range
                    (career_id, location, salary)
                    VALUES (?, ?, ?)
                """, (career_id, location, salary))
            
            # ========================================
            # 5. JOB TITLES
            # ========================================
            for job_title in career_path.get('job_titles', []):
                cursor.execute("""
                    INSERT INTO career_job_titles
                    (career_id, job_title)
                    VALUES (?, ?)
                """, (career_id, job_title))
            
            # ========================================
            # 6. COMPANIES HIRING
            # ========================================
            for company in career_path.get('companies_hiring', []):
                cursor.execute("""
                    INSERT INTO career_companies
                    (career_id, company)
                    VALUES (?, ?)
                """, (career_id, company))
            
            # ========================================
            # 7. CERTIFICATIONS
            # ========================================
            for certification in career_path.get('certifications', []):
                cursor.execute("""
                    INSERT INTO career_certifications
                    (career_id, certification)
                    VALUES (?, ?)
                """, (career_id, certification))
            
            print(f"✅ Migrated: {career_path['title']}")
        
        conn.commit()
    
    print("\n🎉 All careers migrated successfully!")


if __name__ == "__main__":
    migrate_career_to_db()