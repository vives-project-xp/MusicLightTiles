import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/tile_model.dart';

class TilePage extends StatelessWidget {
  const TilePage({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Theme.of(context).colorScheme.onPrimary,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Home',
          onPressed: () => context.go("/"), // Go back to home screen
        ),
        title: Text(tile.deviceName),
        centerTitle: true,
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          Expanded(
            child: SystemState(tile: tile),
          ),
          // Add devider between system state and audio state
          const Divider(
            indent: 20,
            endIndent: 20,
          ),
          Expanded(
            child: AudioState(tile: tile),
          ),
          const Divider(
            indent: 20,
            endIndent: 20,
          ),
          Expanded(
            child: LightState(tile: tile),
          ),
          const Divider(
            indent: 20,
            endIndent: 20,
          ),
          Expanded(
            child: PresenceState(tile: tile),
          ),
        ],
      ),
    );
  }
}

class SystemState extends StatelessWidget {
  const SystemState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Center(child: Text('System State')),
          Center(child: Text('Online: ${tile.online}')),
          Center(child: Text('Firmware Version: ${tile.firmwareVersion}')),
          Center(child: Text('Hardware Version: ${tile.hardwareVersion}')),
          Center(child: Text('Pinging: ${tile.pinging}')),
          Center(child: Text('Uptime: ${tile.uptime}')),
          Center(child: Text('Sounds: ${tile.sounds}')),
        ],
      )
    );
  }
}

class AudioState extends StatelessWidget {
  const AudioState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Center(child: Text('Audio State')),
          Center(child: Text('State: ${tile.audioState}')),
          Center(child: Text('Looping: ${tile.audioLooping}')),
          Center(child: Text('Sound: ${tile.audioSound}')),
          Center(child: Text('Volume: ${tile.audioVolume}')),
        ],
      )
    );
  }
}

class LightState extends StatelessWidget {
  const LightState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Center(child: Text('Light State')),
          Center(child: Text('Brightness: ${tile.brightness}')),
          const Center(child: Text('Pixels:')),
          for (var i = 0; i < tile.pixels.length; i++)
            Center(child: Text(tile.pixels[i].toJson().toString())),
        ],
      )
    );
  }
}

class PresenceState extends StatelessWidget {
  const PresenceState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Center(child: Text('Presence State')),
          Center(child: Text('Detected: ${tile.detected}')),
        ],
      )
    );
  }
}