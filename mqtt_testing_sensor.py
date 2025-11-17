import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("localhost", 1883, 60)

while True:
    client.publish("test/topic", "Hello from Windows")
    print("Sent message")
    time.sleep(2)
