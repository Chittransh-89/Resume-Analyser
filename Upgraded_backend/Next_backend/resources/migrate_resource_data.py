"""Resources data migration to database"""

from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.resources.resources_database import get_resourcesdb_connection
from Upgraded_backend.Next_backend.Careerassistant_v2.backend.database_chromadb.resources.resources_data import (
    LEARNING_PLATFORMS,
    YOUTUBE_CHANNELS,
    INTERVIEW_RESOURCES,
    COMMUNITIES
)


def migrate_resources_to_db():
    with get_resourcesdb_connection() as conn:
        cursor = conn.cursor()
        
        # ========================================
        # 1. LEARNING PLATFORMS
        # ========================================
        print("\n📚 Migrating Learning Platforms...")
        
        for category, platforms_list in LEARNING_PLATFORMS.items():
            # category = "free", "paid", "practice"
            
            for platform in platforms_list:
                # Insert main platform
                cursor.execute("""
                    INSERT INTO platforms
                    (name, url, type, category, price_range, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    platform['name'],
                    platform['url'],
                    platform['type'],
                    category,
                    platform.get('price_range'),    # Free wale mein nahi hota
                    platform['description']
                ))
                
                # Get last inserted ID
                platform_id = cursor.lastrowid
                
                # Insert "best_for" use cases
                for use_case in platform.get('best_for', []):
                    cursor.execute("""
                        INSERT INTO platform_best_for
                        (platform_id, use_case)
                        VALUES (?, ?)
                    """, (platform_id, use_case))
                
                print(f"  ✅ {platform['name']} ({category})")
        
        # ========================================
        # 2. YOUTUBE CHANNELS
        # ========================================
        print("\n📺 Migrating YouTube Channels...")
        
        for category, channels_list in YOUTUBE_CHANNELS.items():
            # category = "programming_general", "hindi", etc.
            
            for channel in channels_list:
                cursor.execute("""
                    INSERT INTO youtube_channels
                    (name, url, subscribers, language, category, best_for)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    channel['name'],
                    channel['url'],
                    channel['subscribers'],
                    channel['language'],
                    category,
                    channel['best_for']
                ))
                
                print(f"  ✅ {channel['name']} ({category})")
        
        # ========================================
        # 3. INTERVIEW RESOURCES
        # ========================================
        print("\n🎯 Migrating Interview Resources...")
        
        for category, resources_list in INTERVIEW_RESOURCES.items():
            # category = "dsa", "system_design", "behavioral"
            
            for resource in resources_list:
                cursor.execute("""
                    INSERT INTO interview_resources
                    (title, url, category, description)
                    VALUES (?, ?, ?, ?)
                """, (
                    resource['title'],
                    resource['url'],
                    category,
                    resource['description']
                ))
                
                print(f"  ✅ {resource['title']} ({category})")
        
        # ========================================
        # 4. COMMUNITIES (Simple list, no category)
        # ========================================
        print("\n👥 Migrating Communities...")
        
        for community in COMMUNITIES:
            cursor.execute("""
                INSERT INTO communities
                (name, url, platform, description)
                VALUES (?, ?, ?, ?)
            """, (
                community['name'],
                community['url'],
                community['platform'],
                community['description']
            ))
            
            print(f"  ✅ {community['name']} ({community['platform']})")
        
        conn.commit()
    
    print("\n🎉 All resources migrated successfully!")


if __name__ == "__main__":
    migrate_resources_to_db()