from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn

db_file = "axis_counts.db"
app = FastAPI()



def create_table():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS counts (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       camera_id TEXT NOT NULL,
                       timestamp TEXT NOT NULL,
                       count INTEGER NOT NULL
                   )
                   """
                   )
    conn.commit()
    conn.close()
    
    



class CountData(BaseModel):
    camera_id: str
    timestamp: str
    count: int
    
    
@app.post("/add_count")
def add_count(data: CountData):
    if data.timestamp is None: 
        data.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO counts (location, timestamp, count)
                        VALUES (?, ?, ?)
                        """, (data.camera_id, data.timestamp, data.count))
        conn.commit()
        conn.close()
        return {"message": "Count added successfully"} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"status": "Axis server ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)