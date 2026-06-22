"""Resources data in ChromaDB"""

import chromadb

# ===========================================
# YOUR DATA (full dictionaries)
# ===========================================
from resources.resources_data import LEARNING_PLATFORMS,YOUTUBE_CHANNELS,INTERVIEW_RESOURCES,COMMUNITIES
LEARNING_PLATFORMS 


# ===========================================
# BLOCK 1: Setup ChromaDB
# ===========================================
client = chromadb.PersistentClient(path="Career-assistant_v2/backend/databases/resources_db")
collection = client.get_or_create_collection(name="resources")


# ===========================================
# BLOCK 2: Build Database
# ===========================================
if collection.count() == 0:
    print("📚 Building resources database...")
    
    documents = []
    metadatas = []
    ids = []
    
    # ============================================
    # PART 1: LEARNING PLATFORMS (free/paid/practice)
    # ============================================
    for category, platforms_list in LEARNING_PLATFORMS.items():
        # category = "free", "paid", "practice"
        
        for i, platform in enumerate(platforms_list):
            
            # Best for ko text mein convert
            best_for_text = ', '.join(platform.get('best_for', []))
            
            # 📄 DOCUMENT
            doc = f"""
Resource Type: Learning Platform
Name: {platform['name']}
URL: {platform['url']}
Type: {platform['type']}
Category: {category}
Best For: {best_for_text}
Price: {platform.get('price_range', 'Free')}
Description: {platform['description']}
"""
            
            # 🏷️ METADATA
            metadata = {
                "name": platform['name'],
                "source": "platform",
                "category": category,
                "type": platform['type']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
            ids.append(f"platform_{category}_{i}")
    
    
    # ============================================
    # PART 2: YOUTUBE CHANNELS
    # ============================================
    for category, channels_list in YOUTUBE_CHANNELS.items():
        # category = "programming_general", "hindi", etc.
        
        for i, channel in enumerate(channels_list):
            
            # 📄 DOCUMENT
            doc = f"""
Resource Type: YouTube Channel
Name: {channel['name']}
URL: {channel['url']}
Subscribers: {channel['subscribers']}
Language: {channel['language']}
Category: {category}
Best For: {channel['best_for']}
"""
            
            # 🏷️ METADATA
            metadata = {
                "name": channel['name'],
                "source": "youtube",
                "category": category,
                "language": channel['language']
            }
            
            documents.append(doc)
            metadatas.append(metadata)
            ids.append(f"youtube_{category}_{i}")
    
    
    # ============================================
    # PART 3: INTERVIEW RESOURCES
    # ============================================
    for category, resources_list in INTERVIEW_RESOURCES.items():
        # category = "dsa", "system_design", "behavioral"
        
        for i, resource in enumerate(resources_list):
            
            # 📄 DOCUMENT
            doc = f"""
Resource Type: Interview Preparation
Title: {resource['title']}
URL: {resource['url']}
Category: {category}
Description: {resource['description']}
"""
            
            # 🏷️ METADATA
            metadata = {
                "name": resource['title'],
                "source": "interview",
                "category": category
            }
            
            documents.append(doc)
            metadatas.append(metadata)
            ids.append(f"interview_{category}_{i}")
    
    
    # ============================================
    # PART 4: COMMUNITIES
    # ============================================
    for i, community in enumerate(COMMUNITIES):
        
        # 📄 DOCUMENT
        doc = f"""
Resource Type: Community
Name: {community['name']}
URL: {community['url']}
Platform: {community['platform']}
Description: {community['description']}
"""
        
        # 🏷️ METADATA
        metadata = {
            "name": community['name'],
            "source": "community",
            "platform": community['platform']
        }
        
        documents.append(doc)
        metadatas.append(metadata)
        ids.append(f"community_{i}")
    
    
    # ============================================
    # Bulk add to ChromaDB
    # ============================================
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Added {len(documents)} resources!")
else:
    print(f"✅ Database already has {collection.count()} resources")


# ===========================================
# BLOCK 3: Test Searches
# ===========================================
print("\n" + "="*60)

# Test 1: General search
print("\n🔍 Search: 'I want to learn coding for free'")
results = collection.query(
    query_texts=["I want to learn coding for free"],
    n_results=3
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    source = results['metadatas'][0][i]['source']
    distance = results['distances'][0][i]
    print(f"  {i+1}. {name} [{source}] (distance: {distance:.3f})")


# Test 2: Filter by source (only YouTube)
print("\n🔍 Search: 'React tutorials' (only YouTube)")
results = collection.query(
    query_texts=["React tutorials"],
    n_results=3,
    where={"source": "youtube"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Test 3: Filter by language (Hindi YouTube)
print("\n🔍 Search: 'programming' (only Hindi)")
results = collection.query(
    query_texts=["programming tutorials"],
    n_results=5,
    where={"language": "Hindi"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Test 4: Interview prep search
print("\n🔍 Search: 'DSA problems' (only interview prep)")
results = collection.query(
    query_texts=["DSA coding problems"],
    n_results=3,
    where={"source": "interview"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Test 5: Communities for help
print("\n🔍 Search: 'where to ask coding questions'")
results = collection.query(
    query_texts=["where to ask coding questions"],
    n_results=3,
    where={"source": "community"}
)
for i, doc in enumerate(results['documents'][0]):
    name = results['metadatas'][0][i]['name']
    print(f"  {i+1}. {name}")


# Total count
print(f"\n📊 Total resources in database: {collection.count()}")