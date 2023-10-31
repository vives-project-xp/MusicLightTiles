import paho.mqtt.client as mqtt
from tile import Tile
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
HOST = os.getenv("MQTT_SERVER")
PORT = os.getenv("MQTT_PORT")
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

  print("Recieved message on topic: " + topic)
 
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
    # Subscribe to the tile's state
    client.subscribe(BASE_TOPIC+"/"+tile_name+"/state")

  # Check if topic ends with tile name
  if topic_parts[-1] == tile_name:
    # Check if payload is online or offline
    if payload == "ONLINE":
      tile.online = True
    elif payload == "OFFLINE":
      tile.online = False
    return
  
  # Check if topic is state
  if topic_parts[2] == "state":
    tile.update_state(payload)
    return

client = mqtt.Client(client_id="controller", clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(HOST, PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()