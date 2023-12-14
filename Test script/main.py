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
  elif topic_parts[-1] == "system":
    state_type = StateType.SYSTEM
  elif topic_parts[-1] == "audio":
    state_type = StateType.AUDIO
  elif topic_parts[-1] == "light":
    state_type = StateType.LIGHT
  elif topic_parts[-1] == "presence":
    state_type = StateType.PRESENCE
  # Update tile state
  if state_type == StateType.ONLINE:
    tile.update_state(state_type, payload)
  elif state_type != None and tile == selected_tile:
    tile.update_state(state_type, payload)

# --- Main ---
def main():
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
  
  # Subscribe to all available tiles (done in on_connect)
  print("Looking for available tiles...")
  time.sleep(15)
  available_tiles = get_online_tiles()
  if available_tiles == []:
    print("No tiles found. Exiting...")
    exit()
      
  # List all available tiles
  print("Available tiles:")
  for i in range(len(available_tiles)):
    print(f"{i+1}: {available_tiles[i].device_name}")
    
  # Ask user to select a tile
  valid_selection = False
  while not valid_selection:
    tile_num = int(input("Select a tile: "))
    if tile_num < 1 or tile_num > len(available_tiles):
      print("Invalid tile number. Try again.")
    else:
      valid_selection = True
  selected_tile = available_tiles[tile_num-1]
  
  # Test tile
  print(f"Testing tile {selected_tile.device_name} ...")

  # Test tile system values
  # Turn off ping
  send_command(mqtt_client, selected_tile, CmdType.SYSTEM, selected_tile.create_system_command("ping", False))
  # Turn on ping
  send_command(mqtt_client, selected_tile, CmdType.SYSTEM, selected_tile.create_system_command("ping", True))
    
  # Test tile audio values
  # Send audio command with volume, sound and looping
  send_command(mqtt_client, selected_tile, CmdType.AUDIO, selected_tile.create_audio_command(1, False, selected_tile.sounds[0], 50))
    
  # Test tile light values
  pixels: list[Pixel] = selected_tile.pixels
  # Test color red
  for pixel in pixels:
    pixel.from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
  send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(150, pixels))
  # Test color green
  for pixel in pixels:
    pixel.from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
  send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(150, pixels))
    
  # Test color blue
  for pixel in pixels:
    pixel.from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
  send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(150, pixels))
    
  # Test color white
  for pixel in pixels:
    pixel.from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
  send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(150, pixels))
      
  # Test tile pressence values
    
  # Display test results
  
  # Ask user to continue testing or exit

  
# --- Run Main ---
if __name__ == "__main__":
  main()