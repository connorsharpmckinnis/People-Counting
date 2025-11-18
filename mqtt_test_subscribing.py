import ssl
import paho.mqtt.client as mqtt

BROKER = "h114ad14.ala.us-east-1.emqxsl.com"
PORT = 8883
USERNAME = "username"
PASSWORD = "password"

def on_connect(client, userdata, flags, rc):
    print("Connected with result:", rc)
    client.subscribe("sensors/#")  # <— subscribe to whatever your Pis will publish

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received [{msg.topic}] {payload}")

    # ---- Reaction logic ----
    # if msg.topic == "sensors/pi01/temp":
    #     do_something(payload)
    # ------------------------

client = mqtt.Client(client_id="laptop-server")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.connect(BROKER, PORT)
client.on_connect = on_connect
client.on_message = on_message

print("Listening… (Ctrl+C to quit)")
client.loop_forever()
