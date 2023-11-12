import os
import json
import asyncio
import threading
import paho.mqtt.client as mqtt
from enum import Enum
from pixel import Pixel
from dotenv import load_dotenv
from tile import StateType, CmdType
from tile import Tile, CmdType, StateType
from websockets.server import serve, WebSocketServerProtocol

# --- Global constants ---
BASE_TOPIC = "PM/MLT"
load_dotenv()
MQTT_HOST: str = os.getenv("MQTT_SERVER")
MQTT_PORT: int = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

# --- Global variables ---
tiles: list[Tile] = [] # List of tiles
channel_tiles: list[WebSocketServerProtocol] = [] # List of websockets that are subscribed to changes in the tile list
channel_states: dict[str, list[WebSocketServerProtocol]] = {} # List of websockets that are subscribed to changes in the state of a specific tile
mqtt_client: mqtt.Client = None # The mqtt client

# --- Global Enums ---
class TileListChange(Enum):
  LIST = "list"
  ADD = "add"
  REMOVE = "remove"

# --- Global functions ---
def get_existing_tile(tile_name: str) -> Tile:
  """Returns the tile with the given name, or None if it doesn't exist."""
  # Check if tile with name exists
  for tile in tiles:
    if tile.device_name == tile_name:
      return tile
  # Tile doesn't exist yet, return None
  return None

# --- Events ---
mqtt_client_set_event = asyncio.Event()

# --- MQTT ---
async def mqtt_controller(HOST: str, PORT: int, USER: str = None, PASS: str = None) -> None:
  # Configure MQTT client
  client = mqtt.Client(client_id="CONTROLLER", clean_session=True)
  client = mqtt.Client(client_id="CONTROLLER", clean_session=True)
  client.on_connect = mqtt_on_connect
  client.on_message = mqtt_on_message
  if USER != None and PASS != None:
    client.username_pw_set(USER, PASS)

  # Connect to MQTT server
  client.connect(HOST, PORT, 60)

  # Start the MQTT client loop
  client.loop_start()

  # Set global mqtt_client variable
  global mqtt_client
  mqtt_client = client
  mqtt_client_set_event.set()

  # Wait for the mqtt client to finish
  await asyncio.Future()  # run forever

def mqtt_on_connect(client: mqtt.Client, userdata, flags, rc: mqtt.ReasonCodes) -> None:
  """The callback for when the client receives a CONNACK response from the server."""

  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.

  # Subscribe to all the tiles (self topic)
  print("Subscribing to all available tiles")
  client.subscribe(BASE_TOPIC+"/+/self")

def mqtt_on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
  """The callback for when a PUBLISH message is received from the server."""
  #convert topic and payload to string
  topic = msg.topic
  payload = msg.payload.decode("utf-8")

  # Split the topic into parts (for easier processing)
  topic_parts = topic.split("/")

  # Check if tile with name exists
  tile_name = topic_parts[2]
  tile = get_tile(client, tile_name)

  # Set project master command type (if it's a pm command)
  pm_command_type = None
  if topic_parts[-1] == "command":
    pm_command_type = PMCmdType.COMMAND
  elif topic_parts[-1] == "rgb":
    pm_command_type = PMCmdType.RGB
  elif topic_parts[-1] == "effect":
    pm_command_type = PMCmdType.EFFECT
  
  # Process project master command (if pm_command_type has been set)
  if pm_command_type != None:
    process_pm_command(pm_command_type, payload)
    return
  
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

  # Process state update (if state_type has been set)
  if state_type != None:
    # Pass the message to the tile
    tile.update_state(state_type, payload)
    # Send state update to all ws clients
    loop = get_event_loop()
    for ws in channel_states[tile.device_name]:
      loop.run_until_complete(ws_send_tile_state(ws, tile, state_type))

def mqtt_send_command(client: mqtt.Client, tile: Tile, type: CmdType, command: str) -> None:
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

def get_tile(client: mqtt.Client, tile_name: str) -> Tile:
  """Returns the tile with the given name, or creates a new one if it doesn't exist."""
  # Check if tile with name exists
  tile = get_existing_tile(tile_name)
  if tile != None:
    # Tile exists, return it
    return tile
  else:
    # Tile doesn't exist yet, create new one
    return create_new_tile(client, tile_name)

def create_new_tile(client: mqtt.Client, tile_name: str) -> Tile:
  """Creates a new tile with the given name."""
  # Create new tile
  tile = Tile(tile_name)
  tiles.append(tile)
  # Subscribe to the tile's state subtopics
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/self/state/+")
  # Subscribe to the project master's command subtopics
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/command")
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/rgb")
  client.subscribe(BASE_TOPIC+"/"+tile_name+"/effect")
  # Set ping state of tile to False (to show that it's connected) 
  # Schedule the command for later (after 5 seconds, because the tile might not be fully initialized yet)
  threading.Timer(5.0, mqtt_send_command, [client, tile, CmdType.SYSTEM, tile.create_system_command(False, False)]).start()
  
  # Add tile to the channel_states dict with an empty list (to put the subscribed websockets in)
  channel_states[tile_name] = []
  # Send tile list changes to all ws clients
  loop = get_event_loop()
  for ws in channel_tiles:
    # Run the task in the event loop
    loop.run_until_complete(ws_send_tile_list_changes(ws, [tile], TileListChange.ADD))
  # Return the new tile
  return tile

def get_event_loop() -> asyncio.AbstractEventLoop:
  """Returns the event loop for the current thread."""
  try:
    loop = asyncio.get_event_loop()
  except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
  return loop

# --- Websocket ---
async def ws_server(HOST: str = "localhost", PORT: int = 3000) -> None:
  """Starts the websocket server."""
  # Start the websocket server
  async with serve(ws_handler, HOST, PORT):
    await asyncio.Future()  # run forever

async def ws_handler(websocket: WebSocketServerProtocol, path: str):
  """Handles incoming websocket connections."""
  try:
    # Handle incoming messages
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
        await ws_command(websocket, message_json)
      else:
        # Unknown action, do nothing
        print("Unknown action: " + action)
  except Exception as e:
    # Print error
    print(e)
  finally:
    # Client disconnected, remove websocket from all channels
    print("Websocket: " + str(websocket) + " disconnected")
    if websocket in channel_tiles:
      channel_tiles.remove(websocket)
    for tile_name in channel_states:
      if websocket in channel_states[tile_name]:
        channel_states[tile_name].remove(websocket)

async def ws_subscribe(websocket: WebSocketServerProtocol, message_json: dict) -> None:
  """Subscribes the websocket to the given channels."""
  type = str(message_json["type"])

  if type == "tiles":
    # Check if websocket is not already in list
    if websocket not in channel_tiles:
      # Send full list of tiles to client
      await ws_send_tile_list_changes(websocket, tiles, TileListChange.LIST)
      # Add websocket to 'tiles' channel
      channel_tiles.append(websocket)
      print("Websocket: " + str(websocket) + " subscribed to tile list")
    else:
      # Websocket is already in list, do nothing
      print("Websocket: " + str(websocket) + " tried to subscribe to tile list, but it was already subscribed")

  elif type == "state":
    subscribe_tiles = list(map(str, message_json["tiles"]))
    # Create formatted list of tiles (json)
    for tile_name in subscribe_tiles:
      # get tile from list
      tile = get_existing_tile(tile_name)
      if tile is None:
        # Tile doesn't exist, do nothing
        print("Websocket: " + str(websocket) + " tried to subscribe to state of tile " + tile_name + ", but it doesn't exist")
        continue
      # Check if websocket is not already in list
      if websocket not in channel_states[tile_name]:
        # Send full state of tile to client
        await ws_send_tile_state(websocket, tile, StateType.FULL)
        # Add websocket to tile_name's state channel
        channel_states[tile_name].append(websocket)
        print("Websocket: " + str(websocket) + " subscribed to state of tile " + tile_name)
      else:
        # Websocket is already in list, do nothing
        print("Websocket: " + str(websocket) + " tried to subscribe to state of tile " + tile_name + ", but it was already subscribed")

async def ws_unsubscribe(websocket: WebSocketServerProtocol, message_json: dict) -> None:
  """Unsubscribes the websocket from the given channels."""
  type = str(message_json["type"])

  if type == "tiles":
    # Check if websocket is in list
    if websocket in channel_tiles:
      # remove websocket from 'tiles' channel
      channel_tiles.remove(websocket)
      print("Websocket: " + str(websocket) + " unsubscribed from tile list")
    else:
      # Websocket is not in list, do nothing
      print("Websocket: " + str(websocket) + " tried to unsubscribe from tile list, but it wasn't subscribed")
  
  elif type == "state":
    unsubscribe_tiles = list(map(str, message_json["tiles"]))
    for tile_name in unsubscribe_tiles:
      try:
        # Check if websocket is in list
        if websocket in channel_states[tile_name]:
          # remove websocket from tile_name's state channel
          channel_states[tile_name].remove(websocket)
          print("Websocket: " + str(websocket) + " unsubscribed from state of tile " + tile_name)
        else:
          # Websocket is not in list, do nothing
          print("Websocket: " + str(websocket) + " tried to unsubscribe from state of tile " + tile_name + ", but it wasn't subscribed")
      except:
        # Tile doesn't exist, do nothing
        print("Websocket: " + str(websocket) + " tried to unsubscribe from state of tile " + tile_name + ", but it doesn't exist")
        continue

async def ws_command(websocket: WebSocketServerProtocol, message_json: dict) -> None:
  """Sends the given command to the given tiles."""
  type = str(message_json["type"])
  tiles_to_command = list(map(str, message_json["tiles"]))
  args = dict(message_json["args"])

  match type:
    case CmdType.SYSTEM.value:
      reboot = bool(args["reboot"])
      ping = bool(args["ping"])

      for tile_name in tiles_to_command:
        # get tile from list
        tile = get_existing_tile(tile_name)
        if tile is None:
          # Tile doesn't exist, do nothing
          print("Tile " + tile_name + " doesn't exist")
          continue
        # Send command to tile
        mqtt_send_command(mqtt_client, tile, CmdType.SYSTEM, tile.create_system_command(reboot, ping))

    case CmdType.AUDIO.value:
      mode = int(args["mode"])
      loop = bool(args["loop"])
      sound = str(args["sound"])
      volume = int(args["volume"])

      for tile_name in tiles_to_command:
        # get tile from list
        tile = get_existing_tile(tile_name)
        if tile is None:
          # Tile doesn't exist, do nothing
          print("Tile " + tile_name + " doesn't exist")
          continue
        # Send command to tile
        mqtt_send_command(mqtt_client, tile, CmdType.AUDIO, tile.create_audio_command(mode, loop, sound, volume))

    case CmdType.LIGHT.value:
      brightness = int(args["brightness"])
      # Create list of pixels
      pixels = [Pixel() for pixel in args["pixels"]]
      # Add values to pixels
      for i in range(len(pixels)):
        pixels[i].from_dict(args["pixels"][i])
      
      for tile_name in tiles_to_command:
        # get tile from list
        tile = get_existing_tile(tile_name)
        if tile is None:
          # Tile doesn't exist, do nothing
          print("Tile " + tile_name + " doesn't exist")
          continue
        # Send command to tile
        mqtt_send_command(mqtt_client, tile, CmdType.LIGHT, tile.create_light_command(brightness, pixels))

    case _:
      # Unknown command type, do nothing
      print("Websocket: " + str(websocket) + " tried to send unknown command type: " + type + " to tiles: " + str(tiles_to_command))

async def ws_send_tile_state(websocket: WebSocketServerProtocol, tile: Tile, type: StateType) -> None:
  """Sends the state of the given tile to the websocket."""
  # Create formatted responds
  responds = {
    "action": "state",
    "type": type.value,
    "tile": tile.device_name,
    "args": tile.get_state(type)
  }
  # Send responds to client
  await websocket.send(json.dumps(responds, indent=4))

async def ws_send_tile_list_changes(websocket: WebSocketServerProtocol, tiles: list[Tile], change: TileListChange) -> None:
  """Sends a list of tiles to the websocket, with the given change type."""
  # Check if tiles is not empty
  if len(tiles) == 0:
    print("Tried to send empty list of tiles to websocket: " + str(websocket))
    return
  # Create formatted list of tiles (json)
  responds = {
    "action": "tiles",
    "type": change.value,
    "tiles": [tile.device_name for tile in tiles]
  }
  # Send list of tiles to client
  await websocket.send(json.dumps(responds, indent=4))

# --- Project master ---
class PMCmdType(Enum):
  COMMAND = 1
  RGB = 2
  EFFECT = 3

def process_pm_command(pm_command_type, payload):
  """Process a command from the project master"""
  if pm_command_type == PMCmdType.COMMAND:
    process_pm_command_command(payload)
  elif pm_command_type == PMCmdType.RGB:
    process_pm_rgb_command(payload)
  elif pm_command_type == PMCmdType.EFFECT:
    process_pm_effect_command(payload)
  else:
    # Unknown command type, do nothing
    print("Unknown project master command type: " + pm_command_type)

def process_pm_command_command(payload):
  # TODO: Implement function
  pass

def process_pm_rgb_command(payload):
  # TODO: Implement function
  pass

def process_pm_effect_command(payload):
  # This project does not have any effects at this time.
  pass

# --- Main ---
async def main():
  # Start the mqtt client
  print("Starting MQTT client")
  mqtt_task = asyncio.create_task(mqtt_controller(MQTT_HOST, MQTT_PORT))

  # Wait till the mqtt_client is set
  await mqtt_client_set_event.wait()

  # Start the websocket server 
  print("Starting websocket server")
  ws_task = asyncio.create_task(ws_server())

  # Wait for mqtt client and websocket server to finish (never)
  await mqtt_task
  await ws_task

# Run the main function
if __name__== "__main__":
  # Run the main function
  asyncio.run(main())