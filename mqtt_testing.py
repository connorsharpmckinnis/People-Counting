import time
import json
import random
import paho.mqtt.client as mqtt

BROKER_HOST = "10.9.81.105"
BROKER_PORT = 1883
TOPIC = "apex/sensors/people_count"
SENSOR_NAME = "sensor_001"
INTERVAL = 5

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with code: {rc}")
    
client.on_connect = on_connect

client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
client.loop_start()   # handles background network traffic

while True:
    timestamp = int(time.time())
    count = random.randint(0, 10)  # simulating your people-counting algo

    payload = {
        "location": SENSOR_NAME,
        "timestamp": timestamp,
        "count": count
    }

    client.publish(TOPIC, json.dumps(payload))
    print("Published:", payload)

    time.sleep(INTERVAL)