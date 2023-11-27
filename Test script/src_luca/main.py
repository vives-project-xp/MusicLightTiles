import paho.mqtt.client as mqtt
import json
import time

# MQTT Settings
mqtt_broker = "mqtt.devbit.be"
mqtt_port = 1883
mqtt_user = None
mqtt_password = None
topic_prefix = "PM/MLT"

# List of valid tiles
valid_tiles = ["TILE1", "TILE2", "TILE3"]  # Add your valid tiles here

# Function to check if a tile exists
def tile_exists(tile_name):
    return tile_name in valid_tiles

# Function to send a command to the Arduino
def send_command(subtopic, command_type, command):
    topic = f"{topic_prefix}/{subtopic}/self/command/{command_type}"
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_broker, mqtt_port, 60)

    # Prepare the command message
    message = json.dumps(command)

    # Publish the command
    client.publish(topic, message, qos=1)

    # Wait for a short time to ensure the command is processed
    time.sleep(2)

    # Disconnect from the broker
    client.disconnect()

# Function to publish presence state
def publish_presence_state(detected, subtopic):
    topic = f"{topic_prefix}/{subtopic}/self/state/presence"
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_broker, mqtt_port, 60)

    # Prepare the presence message
    presence_state = {"detected": detected}
    message = json.dumps(presence_state)

    # Publish the presence state
    client.publish(topic, message, qos=1)

    # Disconnect from the broker
    client.disconnect()

# MQTT Callbacks
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode("utf-8"))

    print(f"Received message on topic: {topic}")
    print(f"Payload: {payload}")

# Set up MQTT client
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)

# User input to choose multiple tiles
selected_tiles = input("Enter the tile names (comma-separated, e.g., TILE1,TILE2): ").split(',')

# Check if all tiles exist
invalid_tiles = [tile for tile in selected_tiles if not tile_exists(tile)]
if invalid_tiles:
    print(f"Error: Tiles {', '.join(invalid_tiles)} do not exist.")
    exit()

# Subscribe to command topics for the selected tiles
subscribed_topics = [
    f"{topic_prefix}/{tile}/self/command/audio" for tile in selected_tiles
] + [
    f"{topic_prefix}/{tile}/self/command/light" for tile in selected_tiles
] + [
    f"{topic_prefix}/{tile}/self/command/system" for tile in selected_tiles
] + [
    f"{topic_prefix}/{tile}/self/state/presence" for tile in selected_tiles
]


for topic in subscribed_topics:
    client.subscribe(topic)

# Example command for controlling the LED strip
led_command = {
    "brightness": 255,
    "pixels": [{"r": 0, "g": 255, "b": 0, "w": 0}] * 12
}

# Example command for controlling audio
audio_command = {
    "state": 1,
    "looping": True,
    "sound": "Mario jump",
    "volume": 50
}

system_update_command = {
    "reboot": False,
    "ping": True
}

# Send commands and publish presence detection state for each selected tile
for tile in selected_tiles:
    # Send the LED command
    send_command(tile, "light", led_command)

    # Send the audio command
    send_command(tile, "audio", audio_command)

    # Send the system update command
    send_command(tile, "system", system_update_command)

    # Publish presence detection state
    publish_presence_state(detected=True, subtopic=tile)

# Loop to listen for messages
client.loop_forever()
