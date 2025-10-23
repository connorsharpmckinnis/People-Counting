import sqlite3

command = """ 
    DELETE FROM counts 
    WHERE timestamp <= ?
    """

cutoff = "2025-10-22 16:45:48"

conn = sqlite3.connect("people_counts.db")
cursor = conn.cursor()

cursor.execute(command, (cutoff,))

print(f"Deleted {cursor.rowcount} rows")

conn.commit()
conn.close()