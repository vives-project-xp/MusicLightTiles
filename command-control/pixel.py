from dataclasses import dataclass

@dataclass
class Pixel:
  _red: int = 0
  _green: int = 0
  _blue: int = 0
  _white: int = 0

  # Properties
  @property
  def red(self) -> int:
    return self._red
  
  @red.setter
  def red(self, value: int):
    if value < 0 or value > 255:
      raise ValueError("The value of red must be between 0 and 255")
    self._red = value

  @property
  def green(self) -> int:
    return self._green
  
  @green.setter
  def green(self, value: int):
    if value < 0 or value > 255:
      raise ValueError("The value of green must be between 0 and 255")
    self._green = value

  @property
  def blue(self) -> int:
    return self._blue
  
  @blue.setter
  def blue(self, value: int):
    if value < 0 or value > 255:
      raise ValueError("The value of blue must be between 0 and 255")
    self._blue = value

  @property
  def white(self) -> int:
    return self._white
  
  @white.setter
  def white(self, value: int):
    if value < 0 or value > 255:
      raise ValueError("The value of white must be between 0 and 255")
    self._white = value

  # Methods
  # Dict to Pixel
  def from_dict(self, data: dict) -> None:
    if "r" in data:
      self._red = data["r"]
    if "g" in data:
      self._green = data["g"]
    if "b" in data:
      self._blue = data["b"]
    if "w" in data:
      self._white = data["w"]
  
  # Pixel to Dict
  def to_dict(self) -> dict:
    return {
      "r": self._red,
      "g": self._green,
      "b": self._blue,
      "w": self._white
    }
  
