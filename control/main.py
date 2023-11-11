import paho.mqtt.client as mqtt
from tile import Tile, CmdType
from pixel import Pixel
import json
import os
import time
import asyncio
from websockets.server import serve
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

tile_channels: dict[str, list] = {}

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
  # Add a list for the tile's channels
  tile_channels[tile_name] = []
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
    # send online update to all ws clients
    for ws in tile_channels[tile.device_name]:
      asyncio.run(ws_send_online(ws, tile))
    return
  
  # Check if topic comes from self
  if topic_parts[-3] == "self" and topic_parts[-2] == "state":
    # Check if topic ends with "system"
    if topic_parts[-1] == "system":
      tile.update_system_state(payload)
      # send system update to all ws clients
      for ws in tile_channels[tile.device_name]:
        asyncio.run(ws_send_system(ws, tile))
      return

    # Check if topic ends with "audio"
    if topic_parts[-1] == "audio":
      tile.update_audio_state(payload)
      # send audio update to all ws clients
      for ws in tile_channels[tile.device_name]:
        asyncio.run(ws_send_audio(ws, tile))
      return

    # Check if topic ends with "light"
    if topic_parts[-1] == "light":
      tile.update_light_state(payload)
      # send light update to all ws clients
      for ws in tile_channels[tile.device_name]:
        asyncio.run(ws_send_light(ws, tile))
      return

    # Check if topic ends with "presence"
    if topic_parts[-1] == "presence":
      tile.update_presence_state(payload)
      # send presence update to all ws clients
      for ws in tile_channels[tile.device_name]:
        asyncio.run(ws_send_presence(ws, tile))
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
  # Prevent sending commands to offline tiles
  if tile.online == False:
    print("Tile " + tile.device_name + " is offline, can't send command")
    return

  # Send command to tile
  if type == CmdType.SYSTEM:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/system", command)
  elif type == CmdType.AUDIO:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/audio", command)
  elif type == CmdType.LIGHT:
    client.publish(BASE_TOPIC+"/"+tile.device_name+"/self/command/light", command)

async def api() -> None:
  async with serve(on_ws_message, "localhost", 3000):
    await asyncio.Future()  # run forever

async def on_ws_message(websocket):
  async for message in websocket:
    # Convert message to JSON
    message_json = json.loads(message)

    # Get action from message
    action = message_json["action"]

    # Handle the action
    if action == "subscribe":
      await ws_subscribe(websocket, message_json)
    elif action == "unsubscribe":
      await ws_unsubscribe(websocket, message_json)
    elif action == "command":
      await ws_command(message_json)
    else:
      # Unknown action, do nothing
      print("Unknown action: " + action)

async def ws_subscribe(websocket, message_json: dict) -> None:
  type = str(message_json["type"])

  if type == "tiles":
    # Create formatted list of tiles (json)
    responds = {
      "action": "tiles",
      "type": "list",
      "tiles": [tile.device_name for tile in tiles]
    }

    # Send list of tiles to client
    await websocket.send(json.dumps(responds, indent=4))

    # TODO: subscribe to changes in tile list

  elif type == "state":
    subscribe_tiles = list(map(str, message_json["tiles"]))

    # Create formatted list of tiles (json)
    for tile in subscribe_tiles:
      # get tile from list
      t = get_existing_tile(tile)
      if t is None:
        # Tile doesn't exist, do nothing
        print("Tile " + tile + " doesn't exist")
        continue
      # Send full state of tile to client
      await ws_send_full(websocket, t)
      # Add websocket to list of channels for the tile
      tile_channels[tile].append(websocket)
    print("Subscribed to state of tiles: " + str(subscribe_tiles))

async def ws_unsubscribe(websocket, message_json: dict) -> None:
  type = str(message_json["type"])

  if type == "tiles":
    # TODO: unsubscribe from changes in tile list
    pass
  elif type == "state":
    unsubscribe_tiles = list(map(str, message_json["tiles"]))
    for tile in unsubscribe_tiles:
      # remove websocket from list of channels for the tile
      tile_channels[tile].remove(websocket)
    print("Unsubscribed from state of tiles: " + str(unsubscribe_tiles))

async def ws_command(message_json: dict) -> None:
  type = str(message_json["type"])
  tiles_to_command = list(map(str, message_json["tiles"]))
  args = dict(message_json["args"])

  if type == "system":
    reboot = bool(args["reboot"])
    ping = bool(args["ping"])

    for tile in tiles_to_command:
      # get tile from list
      t = get_existing_tile(tile)
      if t is None:
        # Tile doesn't exist, do nothing
        print("Tile " + tile + " doesn't exist")
        continue
      # Send command to tile
      send_command(client, t, CmdType.SYSTEM, t.create_system_command(reboot, ping))

  elif type == "audio":
    mode = int(args["mode"])
    loop = bool(args["loop"])
    sound = str(args["sound"])
    volume = int(args["volume"])

    for tile in tiles_to_command:
      # get tile from list
      t = get_existing_tile(tile)
      if t is None:
        # Tile doesn't exist, do nothing
        print("Tile " + tile + " doesn't exist")
        continue
      # Send command to tile
      send_command(client, t, CmdType.AUDIO, t.create_audio_command(mode, loop, sound, volume))

  elif type == "light":
    brightness = int(args["brightness"])
    # Create list of pixels
    pixels = [Pixel() for pixel in args["pixels"]]
    # Add values to pixels
    for i in range(len(pixels)):
      pixels[i].from_dict(args["pixels"][i])

    for tile in tiles_to_command:
      # get tile from list
      t = get_existing_tile(tile)
      if t is None:
        # Tile doesn't exist, do nothing
        print("Tile " + tile + " doesn't exist")
        continue
      # Send command to tile
      send_command(client, t, CmdType.LIGHT, t.create_light_command(brightness, pixels))

  else:
    # Unknown command type, do nothing
    print("Unknown command type: " + type)

async def ws_send_online(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "online",
    "tile": tile.device_name,
    "args": {
      "online": tile.online
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_system(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "system",
    "tile": tile.device_name,
    "args": {
      "firmware": tile.firmware_version,
      "hardware": tile.hardware_version,
      "ping": tile.pinging,
      "uptime": tile.uptime,
      "sounds": tile.sounds
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_audio(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "audio",
    "tile": tile.device_name,
    "args": {
      "state": tile.audio_state,
      "looping": tile.audio_looping,
      "sound": tile.audio_sound,
      "volume": tile.audio_volume
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_light(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "light",
    "tile": tile.device_name,
    "args": {
      "brightness": tile.brightness,
      "pixels": [pixel.to_dict() for pixel in tile.pixels]
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_presence(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "presence",
    "tile": tile.device_name,
    "args": {
      "detected": tile.detected
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_full(websocket, tile: Tile) -> None:
  # Create formatted list of tiles (json)
  responds = {
    "action": "state",
    "type": "full",
    "tile": tile.device_name,
    "args": {
      "online": tile.online,
      "system": {
        "firmware": tile.firmware_version,
        "hardware": tile.hardware_version,
        "ping": tile.pinging,
        "uptime": tile.uptime,
        "sounds": tile.sounds
      },
      "audio": {
        "state": tile.audio_state,
        "looping": tile.audio_looping,
        "sound": tile.audio_sound,
        "volume": tile.audio_volume
      },
      "light": {
        "brightness": tile.brightness,
        "pixels": [pixel.to_dict() for pixel in tile.pixels]
      },
      "presence": {
        "detected": tile.detected
      }
    }
  }

  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

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

  # Run the api
  asyncio.run(api())

  # Keep the program running (TODO: replace thiw with a proper alternative)
  while True:
    time.sleep(1)
