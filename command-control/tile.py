from pixel import Pixel
import json

class Tile:
  # Constructor
  def __init__(self, device_name: str):
    print("Tile created: " + device_name)
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

  # Properties
  @property
  def online(self) -> bool:
    return self._online
  
  @online.setter
  def online(self, value: bool) -> None:
    print("Tile " + self.device_name + " is now " + ("online" if value else "offline"))
    self._online = value

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
  def update_state(self, state: str) -> None:
    """Set the state of the tile from a JSON string"""

    print("Tile " + self.device_name + " state updated")
    # Convert JSON string to JSON object
    state_json: dict = json.loads(state)

    # TODO: Check if the JSON format is correct

    # System
    system = state_json["system"]
    self._firmware_version = system["firmware"]
    self._hardware_version = system["hardware"]
    self._pinging = system["ping"]
    self._uptime = system["uptime"]
    self._sounds = system["sounds"]

    # Audio
    audio = state_json["audio"]
    self._audio_state = audio["state"]
    self._audio_looping = audio["looping"]
    self._audio_sound = audio["sound"]
    self._audio_volume = audio["volume"]

    # Light
    light = state_json["light"]
    self._brightness = light["brightness"]
    pixels = light["pixels"]
    for i in range(len(pixels)):
      # Add new pixels if needed
      if i >= len(self._pixels):
        self._pixels.append(Pixel())
      # Update pixel
      self._pixels[i].from_dict(pixels[i])
    # Remove extra unused pixels
    if len(self._pixels) > len(pixels):
      self._pixels = self._pixels[:len(pixels)]

    # Detection
    detection = state_json["detect"]
    self._detected = detection["detected"]

  # Create a new command to send to the tile (using the state where no values are provided)
  def create_command(
      self, 
      system_reboot: bool = False, 
      system_ping: bool = None, 
      audio_mode: int = None, 
      audio_looping: bool = None, 
      audio_sound: str = None, 
      audio_volume: int = None, 
      light_brightness: int = None, 
      light_pixels: list[Pixel] = None
    ) -> str:
    """Create a command to send to the tile"""
    # Replace None values with the current state
    if system_ping is None:
      system_ping = self._pinging
    if audio_mode is None:
      # TODO: Get the current audio mode
      audio_mode = 4 # 4 = stop
    if audio_looping is None:
      audio_looping = self._audio_looping
    if audio_sound is None:
      audio_sound = self._audio_sound
    if audio_volume is None:
      audio_volume = self._audio_volume
    if light_brightness is None:
      light_brightness = self._brightness
    if light_pixels is None:
      light_pixels = self._pixels

    # Convert the pixels to a list of dictionaries
    light_pixels_dict: list[dict] = []
    for pixel in light_pixels:
      light_pixels_dict.append(pixel.to_dict())

    # Create a dictionary to hold the command
    command: dict = {
      "system": {
        "reboot": system_reboot,
        "ping": system_ping
      },
      "audio": {
        "mode": audio_mode,
        "loop": audio_looping,
        "sound": audio_sound,
        "volume": audio_volume
      },
      "light": {
        "brightness": light_brightness,
        "pixels": light_pixels_dict
      }
    }

    # Convert the dictionary to a JSON string
    command_json: str = json.dumps(command)
    return command_json