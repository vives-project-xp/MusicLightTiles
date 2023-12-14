import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../classes/tile.dart';

class WebSocketProvider extends ChangeNotifier {
  WebSocketChannel _channel;
  late List<Tile> tiles = [];

  // Constructor (connect to the WebSocket server and listen for messages)
  WebSocketProvider()
      : _channel = WebSocketChannel.connect(Uri.parse('ws://localhost:3000')) {
    // Listen for messages
    _channel.stream.listen(_handleMessage);
  }

  void _handleMessage(dynamic message) {
    // Handle incoming messages
    final JSON = json.decode(message);
    // Print the message to the console
    print(JSON);
    // If the incoming action is "welcome", subscribe to the tile list
    if (JSON['action'] == 'welcome') {
      subscribeToTileList();
    }
    // If the incoming action is "tiles", update the tile list
    if (JSON['action'] == 'tiles') {
      // If the type is "list"
      if (JSON['type'] == 'list') {
        // Convert the tiles list to a list of strings
        final List<String> deviceNames = [];
        for (var name in JSON['tiles']) {
          // convert the name to a string and add it to the list
          print('Adding tile: $name');
          deviceNames.add(name);
        }
        print('Adding tile: $deviceNames');
        // Reset the tiles list
        tiles = [];
        // Add the new tiles (device names) to the tiles list
        for (final deviceName in deviceNames) {
          tiles.add(Tile(deviceName));
        }
        // Subscribe to the tiles
        subscribeToTiles(deviceNames);
      }
      // If the type is "add"
      if (JSON['type'] == 'add') {
        print('Adding tiles to tile list');
        // Add the new tiles to the tiles list
        for (final deviceName in JSON['tiles'] as List<String>) {
          print('Adding tile: $deviceName');
          tiles.add(Tile(deviceName));
        }
        // Subscribe to the new tiles
        subscribeToTiles(JSON['tiles'] as List<String>);
      }
    }
    // If the incoming action is "state", update the state of the tile
    // TODO: process the state

    // Notify listeners that the data has changed
    notifyListeners();
  }

  void subscribeToTileList() {
    // Subscribe to the tile list
    _channel.sink.add('{"action": "subscribe", "type": "tiles"}');
  }

  void subscribeToTiles(List<String> deviceNames) {
    // Subscribe to a tile
    _channel.sink
        .add('{"action": "subscribe", "type": "tiles", "tiles": $deviceNames}');
  }

  @override
  void dispose() {
    // Close the WebSocket connection
    _channel.sink.close();
    super.dispose();
  }
}
