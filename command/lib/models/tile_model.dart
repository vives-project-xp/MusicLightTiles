import 'package:flutter/material.dart';

class Pixel {
  int red = 0;
  int green = 0;
  int blue = 0;
  int white = 0;

  // Default constructor
  Pixel();
  // Constructor from RGBW values
  Pixel.fromrgbw(this.red, this.green, this.blue, this.white);
  // Constructor from dictionary (JSON)
  factory Pixel.fromJson(Map<String, dynamic> json) {
    return Pixel()
      ..red = json['r']
      ..green = json['g']
      ..blue = json['b']
      ..white = json['w'];
  }

  // Function to convert Pixel object to dictionary
  Map<String, dynamic> toJson() => {
        'r': red,
        'g': green,
        'b': blue,
        'w': white,
      };
}

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
}

class TileModel extends ChangeNotifier {
  final List<Tile> _tiles = [
    Tile('1'),
    Tile('2'),
    Tile('3'),
    Tile('4'),
    Tile('5'),
    Tile('6'),
    Tile('7'),
    Tile('8'),
  ];
  List<Tile> get tiles => _tiles;

  void addTile(Tile tile) {
    _tiles.add(tile);
    notifyListeners();
  }

  void removeTile(Tile tile) {
    _tiles.remove(tile);
    notifyListeners();
  }
}
