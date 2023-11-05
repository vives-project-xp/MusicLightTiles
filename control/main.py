import paho.mqtt.client as mqtt
from tile import Tile
from pixel import Pixel
import os
import time
#import asyncio
#import websockets
from dotenv import load_dotenv

load_dotenv()

# Constants
HOST: str = os.getenv("MQTT_SERVER")
PORT: int = int(os.getenv("MQTT_PORT"))
#MQTT_USER = os.getenv("MQTT_USERNAME")
#MQTT_PASS = os.getenv("MQTT_PASSWORD")
BASE_TOPIC = "music-light-tiles"

# Variables
tiles: list[Tile] = []

def on_connect(client, userdata, flags, rc):
  """The callback for when the client receives a CONNACK response from the server."""

  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.

  # Subscribe to all devices (only the device name, not the state)
  client.subscribe(BASE_TOPIC+"/+")

def on_message(client, userdata, msg):
  """The callback for when a PUBLISH message is received from the server."""
  #convert topic and payload to string
  topic = msg.topic
  payload = msg.payload.decode("utf-8")

  #print("Recieved message on topic: " + topic)
 
  topic_parts = topic.split("/")
  tile: Tile = None

  # Check if tile with name exists
  tile_name = topic_parts[1]
  for t in tiles:
    if t.device_name == tile_name:
      tile = t
      break
  # Tile doesn't exist yet, create it
  if tile == None:
    tile = Tile(tile_name)
    tiles.append(tile)
    # Subscribe to the tile's state subtopics
    client.subscribe(BASE_TOPIC+"/"+tile_name+"/state/+")

  # Check if topic ends with tile name
  if topic_parts[-1] == tile_name:
    # Check if payload is online or offline
    if payload == "ONLINE":
      tile.online = True
    elif payload == "OFFLINE":
      tile.online = False
    return
  
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

# Main
if __name__== "__main__":
  # Setup MQTT client
  client = mqtt.Client(client_id="controller", clean_session=True)
  client.on_connect = on_connect
  client.on_message = on_message

  # Connect to MQTT server
  client.connect(HOST, PORT, 60)

  # Keep the client connected (start a new thread)
  client.loop_start()

  # Wait until a tile is online
  while len(tiles) == 0:
    time.sleep(1)

  tiles_online = False
  while not tiles_online:
    for tile in tiles:
      if tile.online:
        tiles_online = True
        break
    time.sleep(1)

  print("Found online tiles")
  
  # Make list of online tiles
  online_tiles = []
  for tile in tiles:
    if tile.online:
      online_tiles.append(tile)

  # Set ping of all tiles to off
  for tile in online_tiles:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/command/system", tile.create_system_command(ping=False))
    while tile.pinging:
      time.sleep(1)

  print("All tiles have ping set to off")
    
  # Set all tiles to the same brightness
  for tile in online_tiles:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/command/light", tile.create_light_command(brightness=100))
    while tile.brightness != 100:
      time.sleep(1)

  print("All tiles have the same brightness")
  
  # Set all tiles to the same color (black)
  for tile in online_tiles:
    pixels = [Pixel() for i in range(len(tile.pixels))]
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/command/light", tile.create_light_command(pixels=pixels))
    while tile.pixels[0].red != 0 or tile.pixels[0].green != 0 or tile.pixels[0].blue != 0:
      time.sleep(1)

  print("All tiles have been set to black")

  # Set first pixel of all tiles to red
  for tile in online_tiles:
    pixels = [Pixel() for i in range(len(tile.pixels))]
    pixels[0].red = 255
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/command/light", tile.create_light_command(pixels=pixels))
    while tile.pixels[0].red != 255:
      time.sleep(0.1)

  print("All first pixels have been set to red")
  
  # Shift pixels of all tiles by 1 loop forever
  counter = 0
  while True:
    print("Counter: " + str(counter))
    for tile in online_tiles:
      pixels = tile.pixels[-1:] + tile.pixels[:-1]
      client.publish(BASE_TOPIC+"/"+tile.device_name+"/command/light", tile.create_light_command(pixels=pixels))
      while tile.pixels[counter].red != 255:
        time.sleep(0.0001)

    if counter == len(online_tiles[0].pixels) - 1:
      counter = 0
    else:
      counter += 1
    time.sleep(0.001)
