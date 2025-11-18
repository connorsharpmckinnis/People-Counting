import time
import paho.mqtt.client as mqtt

BROKER = "h114ad14.ala.us-east-1.emqxsl.com"
PORT = 8883
USERNAME = "username"
PASSWORD = "password"
TOPIC = "sensors/node1"

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()  # Keep TLS; required by your broker
client.connect(BROKER, PORT)

counter = 0
while True:
    client.publish(TOPIC, f"py says {counter}")
    counter += 1
    time.sleep(2)