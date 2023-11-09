
import os
import paho.mqtt.client as mqtt



# Make connection with mqtt

def setup_mqtt():
    client = mqtt.client()
    client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD") )
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")))
    return client



# Function to send message to tile

def send_message(tile_id, message):
    client = setup_mqtt()
    client.publish(f"tile/{tile_id}/text", message)
    client.disconnect()


 # Function to ask the user for visual confirmation

def ask_confirmation():
    user_input = input("Is the test correct? (y/n): ").strip().lower()
    return user_input =="y"

    

#Function to test the tile

def test_tile(tile_id, message):
    
    print(f"Testing tile {tile_id}: {message}")
    send_message(tile_id, message)

    if ask_confirmation():
        return "Test passed"
    else:
        return "Test failed"

# Function to run the test for tiles that are selected

def run_test(selected_tiles, message):
    
    test_results = {}

    for tile_id in selected_tiles:
        test_results[tile_id] = {}

        for command in message:
            result =  test_tile(tile_id, message)
            test_results[tile_id][command] = result

    return test_results



# main function
if __name__=="__main__":

    #ask user for topic
     topic = input("Enter the topic please:")
     selected_tiles = input("Select the tiles (seperate by a comma)").split(",")

     # Define list of commands
commands = ["change pixelcolor", "Play audio", "set volume", "set brightness", "reboot"]


    # Set mqtt-connection
mqtt_client = setup_mqtt()

    # Run tests
test_results = run_test(selected_tiles, commands)

#  print results

print("Results: ")

for tile_id, results in test_results.items():
    print(f"Tile {tile_id}:")
    for command, result in results.items():
        print(f"  {command}: {result}")


# Disconnect mqtt
mqtt_client.disconnect()




  