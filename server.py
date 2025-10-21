from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn

db_file = "people_counts.db"
app = FastAPI()

class CountData(BaseModel):
    location: str
    timestamp: str = None
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
                        """, (data.location, data.timestamp, data.count))
        conn.commit()
        conn.close()
        return {"message": "Count added successfully"} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)