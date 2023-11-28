import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../models/tile_model.dart';

class TilePage extends StatelessWidget {
  const TilePage({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2, 
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          foregroundColor: Theme.of(context).colorScheme.onPrimary,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            tooltip: 'Home',
            onPressed: () => context.go("/"), // Go back to home screen
          ),
          bottom: const TabBar(
              tabs: [
                Tab(text: 'Command'),
                Tab(text: 'State'),
              ],
              labelColor: Colors.white,
              unselectedLabelColor: Colors.white60,
            ),
          title: Text(tile.deviceName),
          centerTitle: true,
        ),
        body: TabBarView(
          children: [
            TileCommand(tile: tile),
            TileState(tile: tile),
          ],
        ),
      ),
    );
  }
}

class TileCommand extends StatelessWidget {
  const TileCommand({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return 
    Column(
      children: [
        Expanded(child: SystemCommand(tile: tile)),
        const Divider(
              indent: 20,
              endIndent: 20,
            ),
        Expanded(child: AudioCommand(tile: tile)),
        const Divider(
              indent: 20,
              endIndent: 20,
            ),
        Expanded(child: LightCommand(tile: tile)),
        // add a send command button
        FloatingActionButton(
          child: const Icon(Icons.send),
          onPressed: () {
            // Add your onPressed code here!
          },
        )
      ],
    );
  }
}

class SystemCommand extends StatelessWidget {
  const SystemCommand({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('System Command')),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Pinging: '),
            Switch(
              value: tile.pinging,
              onChanged: (value) {
                // Add your onChanged code here!
              },
              activeTrackColor: Colors.lightGreenAccent,
              activeColor: Colors.green,
            ),
          ],
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Reboot: '),
            Switch(
              value: tile.pinging, // TODO: Add reboot to model
              onChanged: (value) {
                // Add your onChanged code here!
              },
              activeTrackColor: Colors.lightGreenAccent,
              activeColor: Colors.green,
            ),
          ],
        )
      ],
    );
  }
}

class AudioCommand extends StatelessWidget {
  const AudioCommand({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('Audio Command')),
        Center(child: Text('Mode: None')),
        Center(child: Text('Looping: ${tile.audioLooping}')),
        Center(child: Text('Sound: ${tile.audioSound}')),
        Center(child: Text('Volume: ${tile.audioVolume}')),
      ],
    );
  }
}

class LightCommand extends StatelessWidget {
  const LightCommand({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('Light Command')),
        Center(child: Text('Brightness: ${tile.brightness}')),
        const Center(child: Text('Pixels:')),
        for (var i = 0; i < tile.pixels.length; i++)
          Center(child: Text(tile.pixels[i].toJson().toString())),
      ],
    );
  }
}

class TileState extends StatelessWidget {
  const TileState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return 
    
    Column(
      children: [
        Expanded(child: SystemState(tile: tile)),
        const Divider(
              indent: 20,
              endIndent: 20,
            ),
        Expanded(child: AudioState(tile: tile)),
        const Divider(
              indent: 20,
              endIndent: 20,
            ),
        Expanded(child: LightState(tile: tile)),
        const Divider(
              indent: 20,
              endIndent: 20,
            ),
        Expanded(child: PresenceState(tile: tile)),
      ],
    );
  }
}

class SystemState extends StatelessWidget {
  const SystemState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('System State')),
        Center(child: Text('Online: ${tile.online}')),
        Center(child: Text('Firmware Version: ${tile.firmwareVersion}')),
        Center(child: Text('Hardware Version: ${tile.hardwareVersion}')),
        Center(child: Text('Pinging: ${tile.pinging}')),
        Center(child: Text('Uptime: ${tile.uptime}')),
        Center(child: Text('Sounds: ${tile.sounds}')),
      ],
    );
  }
}

class AudioState extends StatelessWidget {
  const AudioState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('Audio State')),
        Center(child: Text('State: ${tile.audioState}')),
        Center(child: Text('Looping: ${tile.audioLooping}')),
        Center(child: Text('Sound: ${tile.audioSound}')),
        Center(child: Text('Volume: ${tile.audioVolume}')),
      ],
    );
  }
}

class LightState extends StatelessWidget {
  const LightState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('Light State')),
        Center(child: Text('Brightness: ${tile.brightness}')),
        const Center(child: Text('Pixels:')),
        for (var i = 0; i < tile.pixels.length; i++)
          Center(child: Text(tile.pixels[i].toJson().toString())),
      ],
    );
  }
}

class PresenceState extends StatelessWidget {
  const PresenceState({super.key, required this.tile});

  final Tile tile;

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        const Center(child: Text('Presence State')),
        Center(child: Text('Detected: ${tile.detected}')),
      ],
    );
  }
}