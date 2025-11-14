from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn
import paho.mqtt.client as mqtt
import json
import threading


db_file = "people_counts.db"
app = FastAPI()

class CountData(BaseModel):
    location: str
    timestamp: str
    count: int
    
    
@app.post("/add_count")
def add_count(data: CountData):
    print(f"{data.location}: {data.count}")
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

@app.get("/ping")
def ping():
    return {"status": "ok"}





# ---------------------
# MQTT HANDLING
# ---------------------

MQTT_BROKER = "10.9.81.105"   # or your laptop IP
MQTT_TOPIC = "apex/sensors/people_count"


def insert_count(location, timestamp, count):
    """Shared insert helper so MQTT and FastAPI use the same DB logic."""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO counts (location, timestamp, count)
            VALUES (?, ?, ?)
        """, (location, timestamp, count))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB insert error:", e)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code", rc)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        # Expecting: { "location": "...", "timestamp": "...", "count": int }
        location = payload["location"]
        timestamp = payload.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count = payload["count"]

        insert_count(location, timestamp, count)

        print(f"MQTT Insert OK: {location} @ {timestamp} = {count}")

    except Exception as e:
        print("MQTT message error:", e)


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()  # blocking; that's why this runs in a thread



if __name__ == "__main__":
    
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)