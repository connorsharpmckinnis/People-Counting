import sqlite3

LOCAL_DB = "offline_cache.db"

def init_local_db():
    """Ensure local cache table exists."""
    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS local_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            timestamp TEXT,
            count INTEGER
        )
    """)
    conn.commit()
    conn.close()
    
init_local_db()