import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../classes/tile.dart';

class WebSocketProvider extends ChangeNotifier {
  WebSocketChannel _channel;
  late List<Tile> tiles = [];

  // Constructor (connect to the WebSocket server and listen for messages)
  WebSocketProvider() : _channel = WebSocketChannel.connect(Uri.parse('ws://localhost:3000')) {
    // Listen for messages
    _channel.stream.listen(_handleMessage);
  }

  void _handleMessage(dynamic message) {
    // Handle incoming messages
    final JSON = json.decode(message);
    // Print the message to the console
    print(JSON);
    // Notify listeners that the data has changed
    notifyListeners();
  }

  void subscribeToTileList() {
    // Subscribe to the tile list
    _channel.sink.add(json.encode({
      {"action": "subscribe", "type": "tiles"}
    }));
  }

  @override
  void dispose() {
    // Close the WebSocket connection
    _channel.sink.close();
    super.dispose();
  }
}
