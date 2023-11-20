import paho.mqtt.client as mqtt
import json
import time

# MQTT Settings
mqtt_broker = "mqtt.devbit.be"
mqtt_port = 1883
mqtt_user = None
mqtt_password = None
mqtt_topic_command = "PM/MLT/TILE1/self/command"

# Function to send a command to the Arduino
def send_command(command, subtopic):
    topic = f"{mqtt_topic_command}/{subtopic}"
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

# Subscribe to command topics
client.subscribe(f"{mqtt_topic_command}/audio")
client.subscribe(f"{mqtt_topic_command}/light")
client.subscribe(f"{mqtt_topic_command}/system")

# Example command for controlling the LED strip
led_command = {
    "brightness": 255,  # Set brightness to maximum
    "pixels": [
        {"r": 255, "g": 0, "b": 0, "w": 0},  # Set the first LED to red
        {"r": 0, "g": 255, "b": 0, "w": 0},  # Set the second LED to green
        # Add more LEDs as needed
    ]
}

# Example command for controlling audio
audio_command = {
    "mode": 1,  # Play
    "loop": True,
    "sound": "Mario jump",
    "volume": 50  # Set volume to 50%
}

# Example command for controlling lights
light_command = {
    "brightness": 150,
    "pixels": [
        {"r": 0, "g": 0, "b": 255, "w": 0},  # Set the first light to blue
        {"r": 255, "g": 255, "b": 0, "w": 0},  # Set the second light to yellow
        # Add more lights as needed
    ]
}

# Send the LED command
send_command(led_command, "light")

# Wait for a while (e.g., simulate a delay in your Python program)
time.sleep(5)

# Send the audio command
send_command(audio_command, "audio")

# Loop to listen for messages
client.loop_forever()
