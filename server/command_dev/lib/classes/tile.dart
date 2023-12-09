import 'pixel.dart';

class Tile {
  final String deviceName;
  bool online = false;
  String firmwareVersion = "";
  String hardwareVersion = "";
  bool pinging = false;
  int uptime = 0;
  List<String> sounds = [];
  int audioState = 0;
  bool audioLooping = false;
  String audioSound = "";
  int audioVolume = 0;
  int brightness = 0;
  List<Pixel> pixels = [];
  bool detected = false;

  // Constructor 
  Tile(this.deviceName);

  // TODO: Add functions to convert to/from JSON etc.
}