import paho.mqtt.client as mqtt
import dotenv
import time
import os
from tile import Tile, StateType, CmdType
from pixel import Pixel

# Load environment variables
dotenv.load_dotenv()
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")
BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC")

# --- Global Variables ---
tiles: list[Tile] = []
available_tiles: list[Tile] = []
selected_tile: Tile = None
test_results: list[list[str]] = []
testing_system: bool = False
testing_audio: bool = False
testing_light: bool = False
testing_presence: bool = False

# --- Functions ---
def get_tile_by_name(client, name: str) -> Tile:
  for tile in tiles:
    # If tile exists, return it
    if tile.device_name == name:
      return tile
  # Create new tile
  new_tile = Tile(name)
  # Add tile to tiles
  tiles.append(new_tile)
  # Subscribe to the tile's state subtopics
  client.subscribe(BASE_TOPIC+"/"+name+"/self/state/+")
  # Return new tile
  return new_tile

def get_online_tiles() -> list[Tile]:
  available_tiles = []
  # Loop through tiles
  for tile in tiles:
    # If state is online
    if tile.online == True:
      # Add tile to available tiles
      available_tiles.append(tile)
  return available_tiles

def send_command(client: mqtt.Client, tile: Tile, type: CmdType, command: str) -> None:
  """Sends a command to the tile."""
  # Prevent sending commands to offline tiles
  if tile.online == False:
    return

  # Send command to tile
  if type == CmdType.SYSTEM:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/system", command)
  elif type == CmdType.AUDIO:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/audio", command)
  elif type == CmdType.LIGHT:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/light", command)

def print_title(title: str) -> None:
  """Prints a title to the console."""
  print(f"\n--- {title} ---\n")

def get_user_confirmation(question: str) -> bool:
  """Asks the user to confirm a message visually."""
  print(f"{question} (y/n)")
  valid_input = False
  while not valid_input:
    selection = input()
    if selection == "y":
      return True
    elif selection == "n":
      return False
    else:
      print("Invalid input. Try again.")

def calculate_result(result: list[str]) -> None:
  # Calculate result
  if result[1] == "Ok" and result[2] == "Ok":
    result[3] = "Passed"
  elif result[1] == "Ok" and result[2] == "N/A":
    result[3] = "Passed"
  else:
    result[3] = "Failed"

def print_results() -> None:
  """Prints the test results to the console."""
  # Calculate overall result
  overall_result = "Passed"
  for result in test_results:
    if result[3] == "Failed":
      overall_result = "Failed"
      break
  # Print test results
  print_title("Test Results")
  print("  Test   | Response |  User  | Result")
  print("-------------------------------------")
  for i in range(len(test_results)):
    print(f"{test_results[i][0].ljust(8)} | {test_results[i][1].ljust(8)} | {test_results[i][2].ljust(6)} | {test_results[i][3].ljust(6)}")
  print("-------------------------------------")
  # Print overall result
  print(f"Overall Result: {overall_result}")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
  # Subscribe to all available tiles
  client.subscribe(BASE_TOPIC+"/+/self")
  
def on_message(client, userdata, msg):
  #convert topic and payload to string
  topic = msg.topic
  payload = msg.payload.decode("utf-8")  
  # Remove base topic from topic
  topic = topic.replace(BASE_TOPIC+"/", "")
  # Split the topic into parts (for easier processing)
  topic_parts = topic.split("/")
  # Check if tile already exists
  tile = get_tile_by_name(client, topic_parts[0])
    
  # Set state type (if it's a state update)
  state_type = None
  if topic_parts[-1] == "self":
    state_type = StateType.ONLINE
  elif topic_parts[-1] == "system" and testing_system:
    state_type = StateType.SYSTEM
  elif topic_parts[-1] == "audio" and testing_audio:
    state_type = StateType.AUDIO
  elif topic_parts[-1] == "light" and testing_light:
    state_type = StateType.LIGHT
  elif topic_parts[-1] == "presence" and testing_presence:
    state_type = StateType.PRESENCE

  # Update tile state
  if state_type == StateType.ONLINE:
    tile.update_state(state_type, payload)
  elif state_type != None and selected_tile != None and tile.device_name == selected_tile.device_name:
    tile.update_state(state_type, payload)

# --- Main ---
def main():
  # Get global variables
  global tiles
  global available_tiles
  global selected_tile
  global test_results
  global testing_system
  global testing_audio
  global testing_light
  global testing_presence
    
  # Wait for broker to send all retained state messages
  available_tiles = get_online_tiles()
  if available_tiles == []:
    print("No tiles found.")
    # Ask user to try again or exit
    if get_user_confirmation("Try again?"):
      main()
    else:
      exit()

  # Sort tiles by name
  available_tiles.sort(key=lambda x: x.device_name)

  # List all available tiles
  print_title("Available Tiles")
  for i in range(len(available_tiles)):
    print(f"{i+1}: {available_tiles[i].device_name}")
    
  # Ask user to select a tile
  valid_selection = False
  while not valid_selection:
    tile_num = int(input("\nSelect a tile: "))
    if tile_num < 1 or tile_num > len(available_tiles):
      print("Invalid tile number. Try again.")
    else:
      valid_selection = True
  selected_tile = available_tiles[tile_num-1]
  
  # Test tile system values
  print_title("Testing Tile System")
  system_result = ["System", "", "N/A", ""]
  # Set testing flag
  testing_system = True
  # Turn off ping
  send_command(mqtt_client, selected_tile, CmdType.SYSTEM, selected_tile.create_system_command(reboot=False, ping=False))
  # Wait for response or timeout
  print("Turning off ping (5s)...")
  time.sleep(5)
  # Check if invalid state
  if selected_tile.invalid_system_state:
    system_result[1] = "Not Ok"
    # Reset invalid state flag
    selected_tile.invalid_system_state = False
  else:
    # Check if ping is off
    if selected_tile.pinging == False:
      system_result[1] = "Ok"
    else:
      system_result[1] = "Not Ok"
  # Reset invalid state flag
  selected_tile.invalid_system_state = False
  # Turn on ping
  send_command(mqtt_client, selected_tile, CmdType.SYSTEM, selected_tile.create_system_command(reboot=False, ping=True))
  # Wait for response or timeout
  print("Turning on ping (5s)...")
  time.sleep(5)
  # Check if invalid state
  if selected_tile.invalid_system_state:
    system_result[2] = "Not Ok"
    # Reset invalid state flag
    selected_tile.invalid_system_state = False
  else:
    # Check previous result
    if system_result[1] == "Ok":
      # Check if ping is on and sounds is not empty
      if selected_tile.pinging == True and selected_tile.sounds != []:
        system_result[1] = "Ok"
      else:
        system_result[1] = "Not Ok"
  # Reset testing flag
  testing_system = False
  # Calculate result
  calculate_result(system_result)
  # Save results
  test_results.append(system_result)
    
  # Test tile audio values
  print_title("Testing Tile Audio")
  audio_result = ["Audio", "", "", ""]
  # Set testing flag
  testing_audio = True
  # Send audio command with volume, sound and looping
  send_command(mqtt_client, selected_tile, CmdType.AUDIO, selected_tile.create_audio_command(1, True, selected_tile.sounds[0], 50))
  # Wait for response or timeout
  print("Playing sound (5s)...")
  time.sleep(5)
  # Check if invalid state
  if selected_tile.invalid_audio_state:
    audio_result[1] = "Not Ok"
    # Reset invalid state flag
    selected_tile.invalid_audio_state = False
  else:
    # Check if audio state is as expected
    if selected_tile.audio_state == 1 and selected_tile.audio_looping == True and selected_tile.audio_sound == selected_tile.sounds[0] and selected_tile.audio_volume == 50:
      audio_result[1] = "Ok"
    else:
      audio_result[1] = "Not Ok"
  # Ask user to confirm audio
  if get_user_confirmation("Do you hear the sound?"):
    audio_result[2] = "Ok"
  else:
    audio_result[2] = "Not Ok"
  # Stop audio
  send_command(mqtt_client, selected_tile, CmdType.AUDIO, selected_tile.create_audio_command(4, False, selected_tile.sounds[0], 0))
  # Wait for response or timeout
  print("Stopping sound (5s)...")
  time.sleep(5)
  # Check if invalid state
  if selected_tile.invalid_audio_state:
    audio_result[1] = "Not Ok"
    # Reset invalid state flag
    selected_tile.invalid_audio_state = False
  else:
    # Check previous result
    if audio_result[1] == "Ok":
      # Check if audio state is as expected
      if selected_tile.audio_state == 0 and selected_tile.audio_looping == False and selected_tile.audio_sound == selected_tile.sounds[0] and selected_tile.audio_volume == 0:
        audio_result[1] = "Ok"
      else:
        audio_result[1] = "Not Ok"
  # Ask user to confirm audio and previous result was ok
  if get_user_confirmation("Did the sound stop?") and audio_result[2] == "Ok":
    audio_result[3] = "Ok"
  else:
    audio_result[3] = "Not Ok"
  # Reset testing flag
  testing_audio = False
  # Calculate result
  calculate_result(audio_result)
  # Save results
  test_results.append(audio_result)
    
  # Test tile light values
  print_title("Testing Tile Light")
  # Set testing flag
  testing_light = True
  # Send empty light command to get current light state
  send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(255, []))
  # Wait for response or timeout
  print("Getting current light state (5s)...")
  time.sleep(5)
  # Check if invalid state or no pixels
  if not selected_tile.invalid_light_state and not selected_tile.pixels == []:
    # Get pixels
    pixels: list[Pixel] = selected_tile.pixels

    # Test color red
    print("\nTesting color red...")
    red_result = ["Red", "", "", ""]
    # Set pixels to red
    for pixel in pixels:
      pixel.from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
    # Send light command
    send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(100, pixels))
    # Wait for response or timeout
    print("Turning LEDs to red (5s)...")
    time.sleep(5)
    # Check if invalid state
    if selected_tile.invalid_light_state:
      red_result[1] = "Not Ok"
      # Reset invalid state flag
      selected_tile.invalid_light_state = False
    else:
      # Check if light state is as expected
      if selected_tile.brightness == 100 and selected_tile.pixels == pixels:
        red_result[1] = "Ok"
      else:
        red_result[1] = "Not Ok"
    # Ask user to confirm color
    if get_user_confirmation("Did all the LEDs turn red?"):
      red_result[2] = "Ok"
    else:
      red_result[2] = "Not Ok"
    # Calculate result
    calculate_result(red_result)
    # Save results
    test_results.append(red_result)

    # Test color green
    print("\nTesting color green...")
    green_result = ["Green", "", "", ""]
    # Set pixels to green
    for pixel in pixels:
      pixel.from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
    # Send light command
    send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(100, pixels))
    # Wait for response or timeout
    print("Turning LEDs to green (5s)...")
    time.sleep(5)
    # Check if invalid state
    if selected_tile.invalid_light_state:
      green_result[1] = "Not Ok"
      # Reset invalid state flag
      selected_tile.invalid_light_state = False
    else:
      # Check if light state is as expected
      if selected_tile.brightness == 100 and selected_tile.pixels == pixels:
        green_result[1] = "Ok"
      else:
        green_result[1] = "Not Ok"
    # Ask user to confirm color
    if get_user_confirmation("Did all the LEDs turn green?"):
      green_result[2] = "Ok"
    else:
      green_result[2] = "Not Ok"
    # Calculate result
    calculate_result(green_result)
    # Save results
    test_results.append(green_result)

    # Test color blue
    print("\nTesting color blue...")
    blue_result = ["Blue", "", "", ""]
    # Set pixels to blue
    for pixel in pixels:
      pixel.from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
    # Send light command
    send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(100, pixels))
    # Wait for response or timeout
    print("Turning LEDs to blue (5s)...")
    time.sleep(5)
    # Check if invalid state
    if selected_tile.invalid_light_state:
      blue_result[1] = "Not Ok"
      # Reset invalid state flag
      selected_tile.invalid_light_state = False
    else:
      # Check if light state is as expected
      if selected_tile.brightness == 100 and selected_tile.pixels == pixels:
        blue_result[1] = "Ok"
      else:
        blue_result[1] = "Not Ok"
    # Ask user to confirm color
    if get_user_confirmation("Did all the LEDs turn blue?"):
      blue_result[2] = "Ok"
    else:
      blue_result[2] = "Not Ok"
    # Calculate result
    calculate_result(blue_result)
    # Save results
    test_results.append(blue_result)

    # Test color white
    print("\nTesting color white...")
    white_result = ["White", "", "", ""]
    # Set pixels to white
    for pixel in pixels:
      pixel.from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
    # Send light command
    send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(100, pixels))
    # Wait for response or timeout
    print("Turning LEDs to white (5s)...")
    time.sleep(5)
    # Check if invalid state
    if selected_tile.invalid_light_state:
      white_result[1] = "Not Ok"
      # Reset invalid state flag
      selected_tile.invalid_light_state = False
    else:
      # Check if light state is as expected
      if selected_tile.brightness == 100 and selected_tile.pixels == pixels:
        white_result[1] = "Ok"
      else:
        white_result[1] = "Not Ok"
    # Ask user to confirm color
    if get_user_confirmation("Did all the LEDs turn white?"):
      white_result[2] = "Ok"
    else:
      white_result[2] = "Not Ok"
    # Calculate result
    calculate_result(white_result)
    # Save results
    test_results.append(white_result)
  else:
    # No pixels
    print("No pixels found.")
    # Create failed light result
    failed_light_result = ["Light", "Not Ok", "N/A", "Failed"]
    # Save results
    test_results.append(failed_light_result)
  # Reset testing flag
  testing_light = False
      
  # Test tile pressence values
  print_title("Testing Tile Presence")
  presence_result = ["Presence", "", "Ok", ""]
  # Set testing flag
  testing_presence = True
  # Ask user to stand on the tile
  print("Please stand on the tile.")
  user_on_tile = False
  while not user_on_tile:
    if get_user_confirmation("Are you standing on the tile?"):
      # Wait for response or timeout
      print("Getting presence state (5s)...")
      time.sleep(5)
      # Check if invalid state
      if selected_tile.invalid_presence_state:
        presence_result[1] = "Not Ok"
        # Reset invalid state flag
        selected_tile.invalid_presence_state = False
      else:
        # Check if presence state is as expected
        if selected_tile.detected == True:
          presence_result[1] = "Ok"
        else:
          presence_result[1] = "Not Ok"
      # Set user on tile flag
      user_on_tile = True
  # Ask user to step off the tile
  print("\nPlease step off the tile.")
  user_off_tile = False
  while not user_off_tile:
    if get_user_confirmation("Are you off the tile?"):
      # Wait for response or timeout
      print("Getting presence state (5s)...")
      time.sleep(5)
      # Check if invalid state
      if selected_tile.invalid_presence_state:
        presence_result[1] = "Not Ok"
        # Reset invalid state flag
        selected_tile.invalid_presence_state = False
      else:
        # Check previous result
        if presence_result[1] == "Ok":
          # Check if presence state is as expected
          if selected_tile.detected == False:
            presence_result[1] = "Ok"
          else:
            presence_result[1] = "Not Ok"
      # Set user off tile flag
      user_off_tile = True
  # Reset testing flag
  testing_presence = False
  # Calculate result
  calculate_result(presence_result)
  # Save results
  test_results.append(presence_result)
  
  # Display test results
  print_results()

# --- Run Main ---
if __name__ == "__main__":
  # Connect to mqtt broker
  print("Connecting to MQTT broker...")
  # Configure MQTT client
  mqtt_client = mqtt.Client(client_id="TESTER", clean_session=True)
  mqtt_client.on_connect = on_connect
  mqtt_client.on_message = on_message
  if MQTT_USER != None and MQTT_PASS != None:
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  # Connect to MQTT server
  mqtt_client.connect(MQTT_HOST, MQTT_PORT)
  # Start the MQTT client loop
  mqtt_client.loop_start()
  # Wait for broker to send all retained state messages
  print("Waiting for broker to send all retained state messages (5s)...")
  time.sleep(5)
  # Loop until user exits
  while True:
    main()
    # Ask user to restart
    if not get_user_confirmation("\nContinue testing?"):
      break
    # Restart
    print("\nRestarting...")
    # Reset global variables
    available_tiles: list[Tile] = []
    selected_tile: Tile = None
    test_results: list[list[str]] = []
    testing_system: bool = False
    testing_audio: bool = False
    testing_light: bool = False
    testing_presence: bool = False
  # Stop the MQTT client loop
  mqtt_client.loop_stop()
  # Disconnect from MQTT server
  mqtt_client.disconnect()