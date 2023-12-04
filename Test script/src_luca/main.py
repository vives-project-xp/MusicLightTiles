import os
import time
import asyncio
import threading
import paho.mqtt.client as mqtt
from enum import Enum
from dotenv import load_dotenv
from tile import StateType, CmdType
from pixel import Pixel
from tile import Tile, CmdType, StateType

# --- Global constants ---
BASE_TOPIC = "PM/MLT"
load_dotenv()
MQTT_HOST: str = os.getenv("MQTT_SERVER")
MQTT_PORT: int = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

# --- Global variables ---
tiles: list[Tile] = [] # List of tiles
mqtt_client: mqtt.Client = None # The mqtt client
selected_tile_name: str = None # The name of the selected tile

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

  state_type = None
  if selected_tile_name == None:
    # Set state type (if it's a state update)
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

  if selected_tile_name == tile_name:
    # Set state type (if it's a state update)
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
  # Get values from new tile (after 5 seconds, to give the tile time to connect or initialize)
  # This is done so that the controller has accurate values for the tile, even if it was already online before the controller started.
  threading.Timer(5.0, get_values_from_new_tile, [client, tile]).start()
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

def get_values_from_new_tile(client: mqtt.Client, tile: Tile) -> None:
  """Sends commands to the tile to get the current values.

  Used to get missing values if a tile was already online before the controller started."""
  if tile.online == False:
    # Tile is offline, do nothing
    return
  # Get system values
  while tile.firmware_version == "" or tile.hardware_version == "" or tile.sounds == []:
    # Send command to tile to get system state
    mqtt_send_command(mqtt_client, tile, CmdType.SYSTEM, tile.create_system_command(False, True))
    # Wait for 2 second (because ping is every second)
    time.sleep(2)
  # Turn off the ping state of the tile (to show that it's connected)
  mqtt_send_command(mqtt_client, tile, CmdType.SYSTEM, tile.create_system_command(False, False))
  print("Got system values from tile " + tile.device_name)
  # Get audio values
  while tile.audio_sound == "":
    # Send command to tile to get audio state
    mqtt_send_command(mqtt_client, tile, CmdType.AUDIO, tile.create_audio_command(1, False, tile.sounds[0], 0))
    # Wait for 1 second
    time.sleep(1)
  # Set audio mode to 4 (stop audio)
  mqtt_send_command(mqtt_client, tile, CmdType.AUDIO, tile.create_audio_command(4))
  print("Got audio values from tile " + tile.device_name)
  # Get light values
  while tile.pixels == []:
    # Send command to tile to get light state
    mqtt_send_command(mqtt_client, tile, CmdType.LIGHT, tile.create_light_command(brightness=255))
    # Wait for 1 second
    time.sleep(1)
  # Set brightness back to 0 (to turn off the lights)
  mqtt_send_command(mqtt_client, tile, CmdType.LIGHT, tile.create_light_command(brightness=0))
  print("Got light values from tile " + tile.device_name)

# --- Main ---
async def main():
  # Start the mqtt client
  print("Starting MQTT client")
  mqtt_task = asyncio.create_task(mqtt_controller(MQTT_HOST, MQTT_PORT))

  # Wait till the mqtt_client is set
  await mqtt_client_set_event.wait()

  # Wait for MQTT client to connect
  while mqtt_client.is_connected() == False:
    print("Waiting for MQTT client to connect")
    await asyncio.sleep(1)
  
  # Wait for tiles to be discovered
  await asyncio.sleep(15)

  # Check which tile are online
  print("Checking which tiles are online")
  for tile in tiles:
    if tile.online == True:
      print(tile.device_name + " is online")
    else:
      print(tile.device_name + " is offline")
  # Display available tiles that are online
  print("Available tiles:")
  for tile in tiles:
    print(tile.device_name)
  while True: 
    # User can select tile
    selected_tile_name = input("Enter the name of the tile you want to control (or 'exit' to quit): ")
    if selected_tile_name.lower() == 'exit':
            break  # Exit the loop if the user enters 'exit'
    selected_tile = get_existing_tile(selected_tile_name)
    if selected_tile:
      # print the amount of pixels in the tile
      print("Tile " + selected_tile.device_name + " has " + str(len(selected_tile.pixels)) + " pixels")
      # Create a list of pixels
      pixels: list[Pixel] = selected_tile.pixels
      # Set all pixels to red
      for pixel in pixels:
        pixel.from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      # Send commands to the selected tile
      mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels))
      # Check if the pixels_red command has been sent. Ask the user if it was sent successfully.
      pixels_red_command_sent = False
      while pixels_red_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if pixels_red command has been sent
        if selected_tile.pixels == pixels:
          pixels_red_command_sent = True
          print("Was pixels_red command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get light state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels))
      mqtt_send_command(mqtt_client, selected_tile, CmdType.AUDIO, selected_tile.create_audio_command(1, False, selected_tile.sounds[1], 100))
      # Check if audio command has been sent. Ask the user if it was sent successfully
      audio_command_sent = False
      while audio_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if audio command has been sent
        if selected_tile.audio_sound == selected_tile.sounds[1] and selected_tile.audio_volume == 100:
          audio_command_sent = True
          print("Was audio command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get audio state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.AUDIO, selected_tile.create_audio_command(1, False, selected_tile.sounds[1], 100))
      mqtt_send_command(mqtt_client, selected_tile, CmdType.SYSTEM, selected_tile.create_system_command(False, True))
  
  """"
      # Create a list of pixels with the same amount of pixels as the selected tile
      pixels_red: list[Pixel] = selected_tile.pixels
      # Set first pixel to red
      pixels_red[0].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[1].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[2].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[3].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[4].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[5].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[6].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[7].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[8].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[9].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[10].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})
      pixels_red[11].from_dict({"r": 255, "g": 0, "b": 0, "w": 0})

      pixels_green: list[Pixel] = selected_tile.pixels
      pixels_green[0].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[1].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[2].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[3].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[4].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[5].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[6].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[7].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[8].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[9].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[10].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})
      pixels_green[11].from_dict({"r": 0, "g": 255, "b": 0, "w": 0})

      pixels_blue: list[Pixel] = selected_tile.pixels
      pixels_blue[0].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[1].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[2].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[3].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[4].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[5].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[6].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[7].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[8].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[9].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[10].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})
      pixels_blue[11].from_dict({"r": 0, "g": 0, "b": 255, "w": 0})

      pixels_white: list[Pixel] = selected_tile.pixels
      pixels_white[0].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[1].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[2].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[3].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[4].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[5].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[6].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[7].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[8].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[9].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[10].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      pixels_white[11].from_dict({"r": 0, "g": 0, "b": 0, "w": 255})
      
      # Send commands to the selected tile
      mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels_red))
      # Check if the pixels_red command has been sent. Ask the user if it was sent successfully.
      pixels_red_command_sent = False
      while pixels_red_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if pixels_red command has been sent
        if selected_tile.pixels == pixels_red:
          pixels_red_command_sent = True
          print("Was pixels_red command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get light state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels_red))
      # Check if the pixels_green command has been sent. Ask the user if it was sent successfully.
      pixels_green_command_sent = False
      while pixels_green_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if pixels_green command has been sent
        if selected_tile.pixels == pixels_green:
          pixels_green_command_sent = True
          print("Was pixels_green command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get light state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels_green))
      # Check if the pixels_blue command has been sent. Ask the user if it was sent successfully.
      pixels_blue_command_sent = False
      while pixels_blue_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if pixels_blue command has been sent
        if selected_tile.pixels == pixels_blue:
          pixels_blue_command_sent = True
          print("Was pixels_blue command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get light state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels_blue))
      # Check if the pixels_white command has been sent. Ask the user if it was sent successfully.
      pixels_white_command_sent = False
      while pixels_white_command_sent == False:
        # Wait for 1 second
        time.sleep(1)
        # Check if pixels_white command has been sent
        if selected_tile.pixels == pixels_white:
          pixels_white_command_sent = True
          print("Was pixels_white command sent successfully? (y/n)")
          answer = input()
          if answer == "n":
            break
          else:
            # Send command to tile to get light state
            mqtt_send_command(mqtt_client, selected_tile, CmdType.LIGHT, selected_tile.create_light_command(brightness=255, pixels=pixels_white))
"""
     

  # Wait for mqtt client and websocket server to finish (never)
  await mqtt_task

# Run the main function
if __name__== "__main__":
  # Run the main function
  asyncio.run(main())
