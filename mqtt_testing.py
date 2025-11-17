import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Received on {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.subscribe("test/topic")

print("Subscribed and listening...")
client.loop_forever()