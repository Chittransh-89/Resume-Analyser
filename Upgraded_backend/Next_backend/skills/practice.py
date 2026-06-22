import sqlite3

conn = sqlite3.connect("skills_database.db")
cursor = conn.cursor()

# Test 1: fetchone()
cursor.execute("SELECT * FROM skills LIMIT 1")
one = cursor.fetchone()
print("ONE:", one)
print("Type:", type(one))  # tuple

# Test 2: fetchall()
cursor.execute("SELECT * FROM skills")
all_data = cursor.fetchall()
print("\nALL count:", len(all_data))
print("Type:", type(all_data))  # list

# Test 3: fetchmany()
cursor.execute("SELECT * FROM skills")
many = cursor.fetchmany(3)
print("\nMANY count:", len(many))

conn.close()