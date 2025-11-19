from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import datetime
import uvicorn
import ssl
import paho.mqtt.client as mqtt
import json
import threading


db_file = "people_counts.db"

class CountData(BaseModel):
    location: str
    timestamp: str
    count: int





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
    print("Connected with result:", rc)
    client.subscribe("sensors/#")  # <— subscribe to whatever your Pis will publish

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received [{msg.topic}] {payload}")
    insert_count(msg.topic, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), payload)

def main():
    BROKER = "h114ad14.ala.us-east-1.emqxsl.com"
    PORT = 8883
    USERNAME = "username"
    PASSWORD = "password"


    client = mqtt.Client(client_id="laptop-server")
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.connect(BROKER, PORT)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Listening… (Ctrl+C to quit)")
    client.loop_forever()

if __name__ == "__main__":

    main()
    
    
    
    
    
    



