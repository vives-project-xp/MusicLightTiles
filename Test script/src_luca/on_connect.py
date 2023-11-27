import paho.mqtt.client as mqtt

# MQTT broker details
broker_address = "mqtt.devbit.be"
port = 1883
topic_prefix = "PM/MLT"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe to the topics of interest
    client.subscribe(topic_prefix + "/+/self")

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    # Extract the tile information from the topic
    tile = msg.topic.split("/")[-2]
    print(f"Tile: {tile} - Value: {msg.payload.decode()}")

# Create an MQTT client
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, port, 60)

# Loop to maintain the connection and process incoming messages
client.loop_forever()
