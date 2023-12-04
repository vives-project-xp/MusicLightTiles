import os
import json
import paho.mqtt.client as mqtt

# Connection mqtt

def setup_mqtt():
    client = mqtt.client()
    client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")))
    return client

# Send message to tile

def send_message(tile_id, subtopic, message):
    topic = f"PM/MLT/{tile_id}/self/{subtopic}/"
    client = setup_mqtt()
    client.publish(topic, json.dumps(message))
    client.disconnect()

# Confirm test

def ask_confirmation():
    user_input = input("Is the test correct? (yes/no): ").strip().lower()
    return user_input == "yes"

# Test audio

def test_audio(tile_id):
    print(f"Test audioState {tile_id}")

    
    audio_state = {
        "state": 2,
        "looping": False,
        "sound": "Mario coin",
        "volume": 50,
    }

    # Send audio
    send_message(tile_id, "command/audio", audio_state)

    if ask_confirmation():
        return "Test passed"
    else:
        return "Test failed"

# Test Lights
def test_lights(tile_id):
    print(f"Test LightState: {tile_id}")

    light_state = {
        "brightness": 50,
        "pixels": [{"r": 255, "g": 0, "b": 0, "w": 0}]
    }

    updateLights();

    # Send message
    send_message(tile_id, "command/light", light_state)


def test_system(tile_id):
    print(f"Testen SystemState: {tile_id}")

    system_state = {
        "firmware": "1.0.0",
        "hardware": "1.0.0",
        "ping": False,
        "uptime": 1234,
        "sounds": ["Mario coin", "Mario jump"]
    }

    
    send_message(tile_id, "command/system", system_state)

# Main
if __name__ == "__main__":
    
    topic = input("Enter the topic: ")
    selected_tiles = input("Select tile (Seperate by a comma): ").split(",")

    
    mqtt_client = setup_mqtt()

    result_system_state = test_system(selected_tiles)
    result_audio = test_audio(selected_tiles)
    result_lights = test_lights(selected_tiles)

   
    print(result_system_state)
    print(result_audio)
    print(result_lights)

   
    mqtt_client.disconnect()








  