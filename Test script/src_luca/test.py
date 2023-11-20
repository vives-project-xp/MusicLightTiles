import paho.mqtt.client as mqtt
import json
import time

# MQTT Settings
mqtt_broker = "mqtt.devbit.be"
mqtt_port = 1883
mqtt_user = None
mqtt_password = None
mqtt_topic_command = "PM/MLT/TILE1/self/command"
mqtt_topic_state = "PM/MLT/TILE1/self/state"

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

# Function to publish presence state
def publish_presence_state(detected):
    topic = f"{mqtt_topic_state}/presence"
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

# Function to get available tiles from MQTT
def get_available_tiles():
    # Connect to MQTT broker to get the list of available tiles
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_broker, mqtt_port, 60)

    # Subscribe to the topic that provides the list of available tiles
    available_tiles_topic = "PM/MLT/+/self"
    client.subscribe(available_tiles_topic)

    # Wait for a short time to receive the list of available tiles
    time.sleep(2)

    # Unsubscribe and disconnect
    client.unsubscribe(available_tiles_topic)
    client.disconnect()

    # Placeholder implementation: return a list of tiles
    # return ["ABE64FHF616", "846ZFFG45", "other_tiles"]

# Function to test a specific device
def test_device(tile):
    # Placeholder implementation for testing commands
    commands = ["light", "audio", "system"]
    test_results = []

    for command in commands:
        # Send the command to the device
        send_command({"command": command}, tile)
        # Ask for visual confirmation
        visual_confirm = input(f"Did the device show the expected response for {command}? (yes/no): ")
        test_results.append((command, visual_confirm))

    return test_results

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

# Subscribe to command and state topics
client.subscribe(f"{mqtt_topic_command}/audio")
client.subscribe(f"{mqtt_topic_command}/light")
client.subscribe(f"{mqtt_topic_command}/system")
client.subscribe(f"{mqtt_topic_state}/presence")

# Main Testing Loop
while True:
    # Retrieve available tiles from MQTT
    tiles = get_available_tiles()

    # Display available tiles and ask for user selection
    print("Available Tiles:")
    for i, tile in enumerate(tiles, 1):
        print(f"{i} - {tile}")

    # Ask for user tile selection
    selected_tiles_str = input("Enter the tile number(s) to test (comma-separated): ")
    selected_tiles_indices = [int(index) - 1 for index in selected_tiles_str.split(",")]
    selected_tiles = [tiles[index] for index in selected_tiles_indices]

    # Main loop to listen for messages
    client.loop_start()

    # Test Loop for each selected tile
    for tile in selected_tiles:
        print(f"\nTesting Tile: {tile}")
        test_results = test_device(tile)

        # Display results
        print("Tested Items:")
        for command, visual_confirm in test_results:
            print(f"Command: {command}, Visual Confirm: {visual_confirm}")

    # Stop the loop after testing
    client.loop_stop()

    # Ask user if they want to test another device
    another_device = input("Do you want to test another device? (yes/no): ")
    if another_device.lower() != 'yes':
        break
