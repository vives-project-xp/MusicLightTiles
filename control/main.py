import paho.mqtt.client as mqtt
from tile import Tile, CmdType
from pixel import Pixel
import os
import time
#import asyncio
#import websockets
from dotenv import load_dotenv
import threading

load_dotenv()

# Constants
HOST: str = os.getenv("MQTT_SERVER")
PORT: int = int(os.getenv("MQTT_PORT"))
#MQTT_USER = os.getenv("MQTT_USERNAME")
#MQTT_PASS = os.getenv("MQTT_PASSWORD")
BASE_TOPIC = "PM/MLT"

# Variables
tiles: list[Tile] = []

def on_connect(client: mqtt.Client, userdata, flags, rc) -> None:
  """The callback for when the client receives a CONNACK response from the server."""

  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.

  # Subscribe to all the tiles (self topic)
  print("Subscribing to all devices")
  client.subscribe(BASE_TOPIC+"/+/self")

def on_message(client, userdata, msg) -> None:
  """The callback for when a PUBLISH message is received from the server."""
  #convert topic and payload to string
  topic = msg.topic
  payload = msg.payload.decode("utf-8") 

  # Split the topic into parts (for easier processing)
  topic_parts = topic.split("/")

  # Check if tile with name exists
  tile: Tile = None
  tile_name = topic_parts[2]
  tile = get_existing_tile(tile_name)
  # If tile is None, add it to the list of tiles
  if tile == None:
    tile = add_new_tile(client, tile_name)

  # Handle the message
  message_handler(tile, topic, payload)

def add_new_tile(client: mqtt.Client, tile_name: str) -> Tile:
  """Adds a new tile to the list of tiles."""
  print("Creating new tile: " + tile_name)
  # Check if tile with name exists
  for tile in tiles:
    if tile.device_name == tile_name:
      return
  # Tile doesn't exist yet, create it
  tile = Tile(tile_name)
  tiles.append(tile)
  # Subscribe to the tile's state subtopics
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/self/state/+")
  # Subscribe to the project master's command subtopics
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/command")
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/rgb")
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/effect")
  # Set ping state of tile to False (to show that it's connected) 
  # schedule command for later (after 5 seconds, because the tile might not be fully initialized yet)
  threading.Timer(5.0, send_command, [client, tile, CmdType.SYSTEM, tile.create_system_command(False, False)]).start()
  # Return the tile (for further processing)
  return tile

def get_existing_tile(tile_name: str) -> Tile:
  """Returns the tile with the given name, or None if it doesn't exist."""
  for tile in tiles:
    if tile.device_name == tile_name:
      return tile
  return None

def message_handler(tile: Tile, topic: str, payload: str) -> None:
  """Handles messages from the tile."""
  print("Processing message from tile " + tile.device_name)
  # Split the topic into parts (for easier processing)
  topic_parts = topic.split("/")

  """Handles messages from the tile."""
  # Check if topic ends with self
  if topic_parts[-1] == "self":
    # Check if payload is online or offline
    if payload == "ONLINE":
      tile.online = True
    elif payload == "OFFLINE":
      tile.online = False
    return
  
  # Check if topic comes from self
  if topic_parts[-3] == "self" and topic_parts[-2] == "state":
    # Check if topic ends with "system"
    if topic_parts[-1] == "system":
      tile.update_system_state(payload)
      return

    # Check if topic ends with "audio"
    if topic_parts[-1] == "audio":
      tile.update_audio_state(payload)
      return

    # Check if topic ends with "light"
    if topic_parts[-1] == "light":
      tile.update_light_state(payload)
      return

    # Check if topic ends with "presence"
    if topic_parts[-1] == "presence":
      tile.update_presence_state(payload)
      return
    
  # Check if topic comes from project master
  if topic_parts[-1] == "command":
    # TODO: Process command
    return

  if topic_parts[-1] == "rgb":
    # TODO: Process rgb
    return

  if topic_parts[-1] == "effect":
    # TODO: Process effect
    return

def send_command(client: mqtt.Client, tile: Tile, type: CmdType, command: str) -> None:
  """Sends a command to the tile."""
  # Send command to tile
  if type == CmdType.SYSTEM:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/system", command)
  elif type == CmdType.AUDIO:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/audio", command)
  elif type == CmdType.LIGHT:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/light", command)

# Main
if __name__== "__main__":
  # Configure MQTT client
  client = mqtt.Client(client_id="CONTROLLER", clean_session=True)
  client.on_connect = on_connect
  client.on_message = on_message
  #client.username_pw_set(MQTT_USER, MQTT_PASS)

  # Connect to MQTT server
  client.connect(HOST, PORT, 60)

  # Keep the client connected (start a new thread)
  client.loop_start()

  # Keep the program running (TODO: replace thiw with a proper alternative)
  while True:
    time.sleep(1)
