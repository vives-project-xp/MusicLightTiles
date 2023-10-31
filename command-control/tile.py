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
      self._pixels[i].from_dict(pixels[i])

    # Detection
    detection = state_json["detect"]
    self._detected = detection["detected"]