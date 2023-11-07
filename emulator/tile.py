from pixel import Pixel
from enum import Enum
import multiprocessing
import paho.mqtt.client as mqtt
import dotenv
import os
import time
import json

class AudioAction(Enum):
  IDLE_PLAY = 1
  IDLE_PAUSE = 2
  IDLE_RESUME = 3
  IDLE_STOP = 4
  PLAY_PLAY = 11
  PLAY_PAUSE = 12
  PLAY_RESUME = 13
  PLAY_STOP = 14
  PAUSE_PLAY = 21
  PAUSE_PAUSE = 22
  PAUSE_RESUME = 23
  PAUSE_STOP = 24

class Tile:
  def __init__(self, device_name: str):
    """Initializes the tile. (Constructor)"""
    self._reboot_tile(device_name)

  def _connect_to_mqtt(self):
    """Connects the tile to MQTT."""
    # Configure MQTT
    self._mqtt_client.on_connect = self._on_mqtt_connect
    self._mqtt_client.on_message = self._on_mqtt_message
    if self._MQTT_USER != None and self._MQTT_PASS != None:
      self._mqtt_client.username_pw_set(self._MQTT_USER, self._MQTT_PASS)
    self._mqtt_client.will_set(f"{self._ROOT_TOPIC}/{self._device_name}/self", "OFFLINE", 1, retain=True)
    # Connect to MQTT
    self._mqtt_client.connect(self._MQTT_HOST, self._MQTT_PORT, 60)

  def _on_mqtt_connect(self, client, userdata, flags, rc):
    """Handles the MQTT connection."""
    # Publish online message
    self._mqtt_client.publish(f"{self._ROOT_TOPIC}/{self._device_name}/self", "ONLINE", 1, retain=True)
    # Publish initial state
    self._mqtt_client.publish(self._state_topic + "/system", self._get_system_state())
    self._mqtt_client.publish(self._state_topic + "/audio", self._get_audio_state())
    self._mqtt_client.publish(self._state_topic + "/light", self._get_light_state())
    self._mqtt_client.publish(self._state_topic + "/presence", self._get_presence_state())
    # Subscribe to command topic
    self._mqtt_client.subscribe(self._command_topic + "/#")

  def _on_mqtt_message(self, client, userdata, message):
    """Handles, parses and processes incoming MQTT messages."""
    # Get topic
    topic: str = message.topic
    # Get payload
    payload: str = message.payload.decode("utf-8")

    # Parse payload for each topic
    try:
      if topic == self._command_topic + "/system":
        # Parse payload
        system_command = json.loads(payload)
        # Set variables
        self._reboot = system_command["reboot"]
        self._ping = system_command["ping"]
      elif topic == self._command_topic + "/audio":
        # Parse payload
        audio_command = json.loads(payload)
        # Set variables
        self._audio_mode = audio_command["mode"]
        self._audio_loop = audio_command["loop"]
        self._audio_sound = audio_command["sound"]
        self._volume = int((audio_command["volume"] / 100) * 30)
      elif topic == self._command_topic + "/light":
        # Parse payload
        light_command = json.loads(payload)
        # Set variables
        self._brightness = light_command["brightness"] / 100 * 255
        # Set pixels
        for i in range(0, self._AMOUNT_OF_PIXELS):
          self._pixels[i].from_dict(light_command["pixels"][i])
      else:
        # Not a valid topic
        pass
    except:
      # Invalid payload
      pass

  def _disconnect_from_mqtt(self):
    """Disconnects the tile from MQTT."""
    # Publish offline message
    self._mqtt_client.publish(f"{self._ROOT_TOPIC}/{self._device_name}/self", "OFFLINE", 1, retain=True)
    # Disconnect from MQTT
    self._mqtt_client.disconnect()

  def _update_system(self) -> bool:
    """Updates the necessary system variables. 
    
    Returns true if the system state has changed."""
    if (self._ping):
      return self._update_uptime()
    elif (self._previous_ping != self._ping):
      # Ping changed
      self._update_uptime()
      # Update previous ping
      self._previous_ping = self._ping
      # Return true
      return True
    else:
      # Update uptime
      self._update_uptime()
      # Return false
      return False

  def _update_uptime(self) -> bool:
    """Updates the uptime.
    
    Returns true if the uptime has changed."""
    # Get current time
    current_time: int = time.time()
    # Check if uptime interval has passed
    if current_time - self._last_time >= self._UPTIME_INTERVAL:
      # Update uptime
      self._uptime += 1
      # Update last time
      self._last_time = current_time
      # Return true
      return True
    else:
      return False

  def _get_system_state(self) -> str:
    """Formats the system state to a JSON string and returns it."""
    # Create system state json
    system_state = {
      "firmware_version": self._FIRMWARE_VERSION,
      "hardware_version": self._HARDWARE_VERSION,
      "ping": self._ping,
      "uptime": self._uptime,
      "sound": self._SOUNDS,
    }
    # Convert system state json to string
    system_state_string: str = json.dumps(system_state)
    # Return system state string
    return system_state_string

  def _update_audio(self) -> bool:
    """Updates the necessary audio variables.
    
    Returns true if the audio state has changed."""
    # Check if audio mode, sound, volume or loop have changed
    if (self._audio_mode != self._previous_audio_mode or self._audio_sound != self._previous_audio_sound or self._volume != self._previous_volume or self._audio_loop != self._previous_audio_loop):
      # Create audio action
      audio_action: AudioAction = AudioAction(self._audio_state * 10 + self._audio_mode)
      # Case audio action
      match audio_action:
        case AudioAction.IDLE_PLAY | AudioAction.PLAY_PLAY | AudioAction.PAUSE_PLAY:
          # Set audio state to playing
          self._audio_state = 1
          # Set audio play time to current uptime
          self._audio_play_time = self._uptime
          # Reset audio pause time
          self._audio_pause_time = 0

        case AudioAction.PLAY_PAUSE:
          # Set audio state to paused
          self._audio_state = 2
          # Set audio pause time to current uptime
          if self._audio_pause_time == 0:
            self._audio_pause_time = self._uptime

        case AudioAction.PLAY_STOP | AudioAction.PAUSE_STOP:
          # Set audio state to idle
          self._audio_state = 0
          # Reset audio play time
          self._audio_play_time = 0
          # Reset audio pause time
          self._audio_pause_time = 0

        case AudioAction.PAUSE_RESUME:
          # Set audio state to playing
          self._audio_state = 1
          # Set audio play time to current uptime - (pause time - start time)
          self._audio_play_time = self._uptime - (self._audio_pause_time - self._audio_play_time)
          # Reset audio pause time
          self._audio_pause_time = 0

        case _:
          # No action needed
          pass

      # Update previous variables
      self._previous_audio_mode = self._audio_mode
      self._previous_audio_sound = self._audio_sound
      self._previous_volume = self._volume
      self._previous_audio_loop = self._audio_loop

      # Return true
      return True
    else:
      # Return false
      return False
    
  def _audio_player_state_changed(self) -> bool:
    """Automatically stops the audio player after 10 seconds of playing to simulate the audio player stopping after the sound has finished playing.
    
    Returns true if the audio state has changed."""
    # State is playing, loop is false
    if self._audio_state == 1 and not self._audio_loop:
      # If 10 seconds have passed since playing started
      if self._uptime - self._audio_play_time >= 10:
        # Set audio state to idle
        self._audio_state = 0
        # Set audio mode to stop
        self._audio_mode = 4
        # Reset audio play time
        self._audio_play_time = 0
        # Reset audio pause time
        self._audio_pause_time = 0
        # Return true
        return True
      else:
        # Return false
        return False
    else:
      # Return false
      return False

  def _get_audio_state(self) -> str:
    """Formats the audio state to a JSON string and returns it."""
    # Create audio state json
    audio_state = {
      "state": self._audio_state,
      "looping": self._audio_loop,
      "sound": self._audio_sound,
      "volume": (self._volume / 30) * 100,
    }
    # Convert audio state json to string
    audio_state_string: str = json.dumps(audio_state)
    # Return audio state string
    return audio_state_string

  def _update_light(self) -> bool:
    """Updates the necessary light variables.

    Returns true if the light state has changed."""
    # Check if brightness or pixels changed
    if self._previous_brightness != self._brightness or self._previous_pixels != self._pixels:
      # Update previous brightness
      self._previous_brightness = self._brightness
      # Update previous pixels
      self._previous_pixels = self._pixels
      # Return true
      return True
    else:
      # Return false
      return False

  def _get_light_state(self) -> str:
    """Formats the light state to a JSON string and returns it."""
    # Convert pixels to dicts
    pixels_dict: list[dict] = []
    for pixel in self._pixels:
      pixels_dict.append(pixel.to_dict())
    # Create light state json
    light_state = {
      "brightness": (self._brightness / 255) * 100,
      "pixels": pixels_dict,
    }
    # Convert light state json to string
    light_state_string: str = json.dumps(light_state)
    # Return light state string
    return light_state_string

  def _update_presence(self) -> bool:
    """Checks if the presence has changed.

    Returns true if the presence state has changed."""
    # Check if presence changed
    if self._previous_presence != self._presence:
      # Update previous presence
      self._previous_presence = self._presence
      # Return true
      return True
    else:
      # Return false
      return False

  def _get_presence_state(self) -> str:
    """Formats the presence state to a JSON string and returns it."""
    # Create presence state json
    presence_state = {
      "detected": self._presence,
    }
    # Convert presence state json to string
    presence_state_string: str = json.dumps(presence_state)
    # Return presence state string
    return presence_state_string

  def run(self, stop_event: multiprocessing.Event) -> None:
    """Runs the tile until the stop_event is set."""
    # Setup
    # Connect to MQTT
    self._connect_to_mqtt()

    # Loop
    while not stop_event.is_set():
      # Check if mqtt is connected
      if not self._mqtt_client.is_connected():
        # Connect to MQTT
        self._connect_to_mqtt()

      # Keep connection alive
      self._mqtt_client.loop()

      # Check if reboot is requested
      if self._reboot:
        # Disconnect from MQTT
        self._disconnect_from_mqtt()

        # Reboot
        self._reboot_tile(self._device_name)

      # Update system
      if self._update_system():
        # Publish system state
        self._mqtt_client.publish(self._state_topic + "/system", self._get_system_state())

      # Update audio
      if self._update_audio() or self._audio_player_state_changed():
        # Publish audio state
        self._mqtt_client.publish(self._state_topic + "/audio", self._get_audio_state())

      # Update light
      if self._update_light():
        # Publish light state
        self._mqtt_client.publish(self._state_topic + "/light", self._get_light_state())

      # Update presence
      if self._update_presence():
        # Publish presence state
        self._mqtt_client.publish(self._state_topic + "/presence", self._get_presence_state())

      # Sleep for 0.0000125ms (to simulate the 80MHz clock speed of the ESP32)
      time.sleep(0.0000125)

    # Graceful exit
    # Disconnect from MQTT
    self._disconnect_from_mqtt()

  def set_presence(self, presence: bool) -> None:
    """Sets the presence of the tile. Because this is a simulation, this method is used to simulate the presence sensor.

    Args:
      presence (bool): The presence of the tile. (True = detected, False = not detected)
    """
    self._presence = presence

  def _reboot_tile(self, device_name: str) -> None:
    """Sets all variables to their default values, to simulate a reboot."""
    # Constants
    self._ROOT_TOPIC: str = "PM/MLT"
    self._UPTIME_INTERVAL: int = 1 # 1 second
    self._AMOUNT_OF_PIXELS: int = 12
    self._FIRMWARE_VERSION: str = "0.0.6"
    self._HARDWARE_VERSION: str = "0.0.2"
    self._SOUNDS: list[str] = [
      "A cat meowing",
      "A dog barking",
      "A duck quacking",
      "A frog croaking",
      "A horse neighing",
      "A pig grunt",
      "A rooster crowing",
      "A chicken clucking",
      "A sheep baaing",
      "A wolf howling",
      "Minecraft villager",
      "Minecraft creeper hissing",
      "Minecraft explosion",
      "Mario jump",
      "Mario coin",
      "Mario death",
      "Among Us role reveal",
      "Fortnite death",
      "Roblox oof",
      "CS:GO bomb planted",
      "CS:GO bomb defused",
      "GTA San Andreas - Here we go again",
      "GTA V wasted",
      "GTA V phone ring",
      "Bruh sound effect",
      "Emotional damage",
      "Sad violin",
      "Windows XP error",
      "Windows XP shutdown",
      "Windows XP startup",
      "Piano C note",
      "Piano C# note",
      "Piano D note",
      "Piano D# note",
      "Piano E note",
      "Piano F note",
      "Piano F# note",
      "Piano G note",
      "Piano G# note",
      "Piano A note",
      "Piano A# note",
      "Piano B note",
      "Applause",
      "Kids cheering",
      "Crickets",
      "Wheel spin",
      "Wrong answer",
      "Right answer",
      "Intermission",
      "The Office - That's what she said",
      "The Office - No, God! No, God, please no! No! No! Nooooooo!",
      "Obi-Wan Kenobi - Hello there"
      ]
    self._AMOUNT_OF_SOUNDS: int = len(self._SOUNDS)
    # Environment variables
    dotenv.load_dotenv()
    self._MQTT_HOST: str = os.getenv("MQTT_HOST")
    self._MQTT_PORT: int = int(os.getenv("MQTT_PORT"))
    self._MQTT_USER: str | None = os.getenv("MQTT_USER")
    self._MQTT_PASS: str | None = os.getenv("MQTT_PASS")
    # Variables
    self._device_name: str = device_name
    self._reboot: bool = False
    self._ping: bool = True
    self._previous_ping: bool = self._ping
    self._uptime: int = 0
    self._last_time: int = 0
    self._presence: bool = False
    self._previous_presence: bool = self._presence
    self._audio_mode: int = 4 # 1 = play, 2 = pause, 3 = resume, 4 = stop
    self._previous_audio_mode: int = self._audio_mode
    self._audio_state: int = 0 # 0 = idle, 1 = playing, 2 = paused
    self._audio_loop: bool = False
    self._previous_audio_loop: bool = self._audio_loop
    self._audio_sound: str = self._SOUNDS[0]
    self._previous_audio_sound: str = self._audio_sound
    self._volume: int = 0 # 0 - 30
    self._previous_volume: int = self._volume
    self._brightness: int = 0 # 0 - 255
    self._previous_brightness: int = self._brightness
    self._pixels: list[Pixel] = [Pixel(0, 0, 0, 0) for i in range(0, self._AMOUNT_OF_PIXELS)]
    self._previous_pixels: list[Pixel] = self._pixels
    # MQTT
    self._state_topic: str = f"{self._ROOT_TOPIC}/{self._device_name}/self/state"
    self._command_topic: str = f"{self._ROOT_TOPIC}/{self._device_name}/self/command"
    self._mqtt_client: mqtt.Client = mqtt.Client()
    # Extra variables
    self._audio_play_time: int = 0
    self._audio_pause_time: int = 0
