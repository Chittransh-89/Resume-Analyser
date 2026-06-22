"""Skills data in ChromaDB"""

import chromadb

# ===========================================
# YOUR SKILLS_DATABASE (full dictionary)
# ===========================================
from skills.skills_data import SKILLS_DATABASE

# ===========================================
# BLOCK 1: Setup ChromaDB
# ===========================================
client = chromadb.PersistentClient(path="Career-assistant_v2/backend/databases/skills_db")
collection = client.get_or_create_collection(name="skills")


# ===========================================
# BLOCK 2: Build Database
# ===========================================
if collection.count() == 0:
    print("📚 Building skills database...")
    
    documents = []
    metadatas = []
    ids = []
    
    for skill_id, skill in SKILLS_DATABASE.items():
        
        # Use cases ko text mein convert
        use_cases_text = ', '.join(skill.get('use_cases', []))
        
        # Free resources ko text mein convert
        free_resources_text = ""
        for resource in skill.get('free_resources', []):
            free_resources_text += f"{resource['title']} ({resource['type']}) - {resource['url']}. "
        
        # Paid resources ko text mein convert
        paid_resources_text = ""
        for resource in skill.get('paid_resources', []):
            paid_resources_text += f"{resource['title']} ({resource['type']}) - {resource['url']}. "
        
        # YouTube channels (already a list of strings)
        youtube_text = ', '.join(skill.get('youtube_channels', []))
        
        # Practice platforms
        practice_text = ', '.join(skill.get('practice_platforms', []))
        
        # Related careers
        careers_text = ', '.join(skill.get('related_careers', []))
        
        # Prerequisites (sirf kuch skills mein hai)
        prerequisites_text = ', '.join(skill.get('prerequisites', []))
        
        # ===== 📄 DOCUMENT (Big text for search) =====
        doc = f"""
Skill: {skill['name']}
Category: {skill['category']}
Difficulty: {skill['difficulty']}
Time to Learn: {skill['time_to_learn']}
Description: {skill['description']}

Use Cases: {use_cases_text}

Prerequisites: {prerequisites_text}

Free Resources: {free_resources_text}

Paid Resources: {paid_resources_text}

YouTube Channels: {youtube_text}

Practice Platforms: {practice_text}

Related Careers: {careers_text}
"""
        
        # ===== 🏷️ METADATA (Small tags for filter) =====
        metadata = {
            "name": skill['name'],
            "category": skill['category'],
            "difficulty": skill['difficulty'],
            "time_to_learn": skill['time_to_learn']
        }
        
        documents.append(doc)
        metadatas.append(metadata)
        ids.append(skill_id)
    
    # Bulk add to ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Added {len(documents)} skills!")
else:
    print(f"✅ Database already has {collection.count()} skills")


# ===========================================
# BLOCK 3: Test Searches
# ===========================================
print("\n" + "="*60)

# Test 1: Semantic search
print("\n🔍 Search: 'I want to learn web programming'")
results = collection.query(
    query_texts=["I want to learn web programming"],
    n_results=3
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    distance = results['distances'][0][i]
    print(f"  {i+1}. {name} (distance: {distance:.3f})")


# Test 2: ML/AI related search
print("\n🔍 Search: 'machine learning and AI'")
results = collection.query(
    query_texts=["machine learning and AI"],
    n_results=3
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    distance = results['distances'][0][i]
    print(f"  {i+1}. {name} (distance: {distance:.3f})")


# Test 3: Filter by difficulty
print("\n🔍 Search: 'easy skill' (Beginner only)")
results = collection.query(
    query_texts=["easy skill to start learning"],
    n_results=5,
    where={"difficulty": "Beginner"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Test 4: Filter by category
print("\n🔍 Search: 'programming basics' (only Programming Language)")
results = collection.query(
    query_texts=["programming basics"],
    n_results=5,
    where={"category": "Programming Language"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Test 5: Get specific skill
print("\n📄 Get specific skill: 'python'")
result = collection.get(ids=["python"])
print(f"  Name: {result['metadatas'][0]['name']}")
print(f"  Document preview: {result['documents'][0][:200]}...")