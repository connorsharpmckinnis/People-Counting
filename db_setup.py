import sqlite3

def create_db():
    conn = sqlite3.connect("people_counts.db")
    cursor = conn.cursor()
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS counts (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       location TEXT NOT NULL,
                       timestamp TEXT NOT NULL,
                       count INTEGER NOT NULL
                   )
                   """
                   )
    conn.commit()
    conn.close()
    
    
