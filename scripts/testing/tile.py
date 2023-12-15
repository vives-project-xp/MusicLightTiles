from pixel import Pixel
from enum import Enum
import json
import logging

class CmdType(Enum):
  SYSTEM = "system"
  AUDIO = "audio"
  LIGHT = "light"

class StateType(Enum):
  ONLINE = "online"
  SYSTEM = "system"
  AUDIO = "audio"
  LIGHT = "light"
  PRESENCE = "presence"

class Tile:
  # Constructor
  def __init__(self, device_name: str):
    self.device_name: str = device_name
    self._online: bool = False
    self._firmware_version: str = ""
    self._hardware_version: str = ""
    self._pinging: bool = False
    self._uptime: int = 0
    self._sounds: list[str] = []
    self._audio_state: int = 0
    self._audio_looping: bool = False
    self._audio_sound: str = ""
    self._audio_volume: int = 0
    self._brightness: int = 0
    self._pixels: list[Pixel] = []
    self._detected: bool = False
    self.invalid_system_state: bool = False
    self.invalid_audio_state: bool = False
    self.invalid_light_state: bool = False
    self.invalid_presence_state: bool = False

  # Properties
  @property
  def online(self) -> bool:
    return self._online
  
  @property
  def firmware_version(self) -> str:
    return self._firmware_version

  @property
  def hardware_version(self) -> str:
    return self._hardware_version

  @property
  def pinging(self) -> bool:
    return self._pinging
  
  @property
  def uptime(self) -> int:
    return self._uptime

  @property
  def sounds(self) -> list[str]:
    return self._sounds
  
  @property
  def audio_state(self) -> int:
    return self._audio_state

  @property
  def audio_looping(self) -> bool:
    return self._audio_looping

  @property
  def audio_sound(self) -> str:
    return self._audio_sound

  @property
  def audio_volume(self) -> int:
    return self._audio_volume

  @property
  def brightness(self) -> int:
    return self._brightness

  @property
  def pixels(self) -> list[Pixel]:
    return self._pixels

  @property
  def detected(self) -> bool:
    return self._detected
  
  # Methods
  def update_state(self, state_type: StateType, state: str) -> None:
    """Set the state of the tile from a JSON string"""
    match state_type:
      case StateType.ONLINE:
        self.update_online_state(state)
      case StateType.SYSTEM:
        self.update_system_state(state)
      case StateType.AUDIO:
        self.update_audio_state(state)
      case StateType.LIGHT:
        self.update_light_state(state)
      case StateType.PRESENCE:
        self.update_presence_state(state)
      case _:
        # Invalid state type, ignore
        return

  def update_online_state(self, state: str) -> None:
    """Set the self state of the tile from a JSON string"""
    if state == "ONLINE":
      self._online = True
    elif state == "OFFLINE":
      self._online = False
    else:
      # Invalid device state, ignore
      return

  def update_system_state(self, state: str) -> None:
    """Set the system state of the tile from a JSON string"""
    try:
      # Convert JSON string to JSON object
      state_json: dict = json.loads(state)
      # System
      self._firmware_version = str(state_json["firmware"])
      self._hardware_version = str(state_json["hardware"])
      self._pinging = bool(state_json["ping"])
      self._uptime = int(state_json["uptime"])
      self._sounds = list(map(str, state_json["sounds"]))
    except:
      # Invalid JSON string (missing keys, wrong types, etc.), set invalid flag
      self.invalid_system_state = True
      return

  def update_audio_state(self, state: str) -> None:
    """Set the audio state of the tile from a JSON string"""
    try:
      # Convert JSON string to JSON object
      state_json: dict = json.loads(state)
      # Audio
      self._audio_state = int(state_json["state"])
      self._audio_looping = bool(state_json["looping"])
      self._audio_sound = str(state_json["sound"])
      self._audio_volume = int(state_json["volume"])
    except:
      # Invalid JSON string (missing keys, wrong types, etc.), set invalid flag
      self.invalid_audio_state = True
      return

  def update_light_state(self, state: str) -> None:
    """Set the light state of the tile from a JSON string"""
    try:
      # Convert JSON string to JSON object
      state_json: dict = json.loads(state)
      # Light
      self._brightness = int(state_json["brightness"])
      pixels = list(map(dict, state_json["pixels"]))
      for i in range(len(pixels)):
        # Add new pixels if needed
        if i >= len(self._pixels):
          self._pixels.append(Pixel())
        # Update pixel
        self._pixels[i].from_dict(pixels[i])
      # Remove extra unused pixels
      if len(self._pixels) > len(pixels):
        self._pixels = self._pixels[:len(pixels)]
    except:
      # Invalid JSON string (missing keys, wrong types, etc.), set invalid flag
      self.invalid_light_state = True
      return

  def update_presence_state(self, state: str) -> None:
    """Set the presence state of the tile from a JSON string"""
    try:
      # Convert JSON string to JSON object
      state_json: dict = json.loads(state)
      # Detection
      self._detected = bool(state_json["detected"])
    except:
      # Invalid JSON string (missing keys, wrong types, etc.), set invalid flag
      self.invalid_presence_state = True
      return

  def create_system_command(self, reboot: bool = False, ping: bool = None):
    """Create a command to send to the tile to change the system state"""
    # Replace None values with the current state
    if ping is None:
      ping = self._pinging

    # Create a dictionary to hold the command
    command: dict = {
      "reboot": reboot,
      "ping": ping
    }

    # Convert the dictionary to a JSON string
    command_json: str = json.dumps(command)
    return command_json
  
  def create_audio_command(self, mode: int = None, looping: bool = None, sound: str = None, volume: int = None):
    """Create a command to send to the tile to change the audio state"""
    # Replace None values with the current state
    if mode is None:
      # TODO: Get the current audio mode
      mode = 4 # 4 = stop
    if looping is None:
      looping = self._audio_looping
    if sound is None:
      sound = self._audio_sound
    if volume is None:
      volume = self._audio_volume
    
    # Create a dictionary to hold the command
    command: dict = {
      "mode": mode,
      "loop": looping,
      "sound": sound,
      "volume": volume
    }

    # Convert the dictionary to a JSON string
    command_json: str = json.dumps(command)
    return command_json

  def create_light_command(self, brightness: int = None, pixels: list[Pixel] = None):
    """Create a command to send to the tile to change the light state"""
    # Replace None values with the current state
    if brightness is None:
      brightness = self._brightness
    if pixels is None:
      pixels = self._pixels

    # Convert the pixels to a list of dictionaries
    pixels_dict: list[dict] = []
    for pixel in pixels:
      pixels_dict.append(pixel.to_dict())

    # Create a dictionary to hold the command
    command: dict = {
      "brightness": brightness,
      "pixels": pixels_dict
    }

    # Convert the dictionary to a JSON string
    command_json: str = json.dumps(command)
    return command_json
