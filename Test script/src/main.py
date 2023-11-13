
import os
import json
import paho.mqtt.client as mqtt



# Make connection with mqtt

def setup_mqtt():
    client = mqtt.client()
    client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")))
    return client



# Function to send message to tile

def send_message(tile_id,subtopic, message):
    topic = f"PM/MLT/{tile_id}/self/{subtopic}/"
    client = setup_mqtt()
    client.publish(topic, json.dumps(message))
    client.disconnect()


 # Function to ask the user for visual confirmation

def ask_confirmation():
    user_input = input("Is the test correct? (yes/no): ").strip().lower()
    return user_input =="yes"

    

# test audio

def test_audio(tile_id):
    
    print(f"Testing audio state for tile {tile_id}")
      
      # Simulate system

    audio_state = {

        "state": 2,
        "looping": False,
        "sound" : "Mario coin",
        "volume": 50,
    }
    
    # send audio message
    send_message("PM/MLT/" ,tile_id, "self/command/audio", audio_state)

    if ask_confirmation():
        return "Test passed"
    else:
        return "Test failed"
    


# Test light
def test_lights(tile_id):
        print(f"Testing light state: {tile_id} ")

        light_state = {
            "brightness": 50,
            "pixels": [{"r": 255, "g": 0, "b": 0, "w": 0}]
        }

        # message
        send_message("PM/MLT/",tile_id, "self/command/light",test_lights)


def test_system(tile_id):
    print(f"Testing system state: {tile_id}")

    system_state = {
        "firmware": "1.0.0",
        "hardware": "1.0.0",
        "ping": False,
        "uptime":1234,
        "sounds": ["Mario coin", "Mario jump"]
    }



# main function
if __name__=="__main__":

    #ask user for topic
     topic = input("Enter the topic please: ")
     selected_tiles = input("Select the tiles (seperate by a comma)").split(",")


 
import os
import json
import paho.mqtt.client as mqtt



# Make connection with mqtt

def setup_mqtt():
    client = mqtt.client()
    client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")))
    return client



# Function to send message to tile

def send_message(tile_id,subtopic, message):
    topic = f"PM/MLT/{tile_id}/self/{subtopic}/"
    client = setup_mqtt()
    client.publish(topic, json.dumps(message))
    client.disconnect()


 # Function to ask the user for visual confirmation

def ask_confirmation():
    user_input = input("Is the test correct? (yes/no): ").strip().lower()
    return user_input =="yes"

    

# test audio

def test_audio(tile_id):
    
    print(f"Testing audio state for tile {tile_id}")
      
      # Simulate system

    audio_state = {

        "state": 2,
        "looping": False,
        "sound" : "Mario coin",
        "volume": 50,
    }
    
    # send audio message
    send_message("PM/MLT/" ,tile_id, "self/command/audio", audio_state)

    if ask_confirmation():
        return "Test passed"
    else:
        return "Test failed"
    


# Test light
def test_lights(tile_id):
        print(f"Testing light state: {tile_id} ")

        light_state = {
            "brightness": 50,
            "pixels": [{"r": 255, "g": 0, "b": 0, "w": 0}]
        }

        # message
        send_message("PM/MLT/",tile_id, "self/command/light",test_lights)


def test_system(tile_id):
    print(f"Testing system state: {tile_id}")

    system_state = {
        "firmware": "1.0.0",
        "hardware": "1.0.0",
        "ping": False,
        "uptime":1234,
        "sounds": ["Mario coin", "Mario jump"]
    }



# main function
if __name__=="__main__":

    #ask user for topic
     topic = input("Enter the topic please: ")
     selected_tiles = input("Select the tiles (seperate by a comma)").split(",")


    # Set mqtt-connection
mqtt_client = setup_mqtt()

    # Run tests
result_system_state = test_system(selected_tiles)
result_audio = test_audio(selected_tiles)
result_lights = test_lights(selected_tiles)

    

#  print results
print(result_system_state)
print(result_audio)
print(result_lights)


# Disconnect mqtt
mqtt_client.disconnect()








  