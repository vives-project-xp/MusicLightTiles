import 'package:command/providers/websocket_provider.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../classes/tile.dart';
import '../classes/pixel.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<WebSocketProvider>(
      builder: (context, tileModel, child) {
        return Scaffold(
          appBar: AppBar(
            backgroundColor: Theme.of(context).colorScheme.primary,
            foregroundColor: Theme.of(context).colorScheme.onPrimary,
            title: const Text('Tiles'),
            centerTitle: true,
            actions: [
              IconButton(
                icon: const Icon(Icons.menu),
                tooltip: 'Settings',
                onPressed: () => context.go("/settings"), // Go to settings screen
              )
            ],
            automaticallyImplyLeading: false,
          ),
          body:
            // Create a list of tiles
            tileModel.tiles.isNotEmpty
              ? ListView.builder(
                itemCount: tileModel.tiles.length,
                itemBuilder: (context, index) {
                  final Tile tile = tileModel.tiles[index];
                  return ListTile(
                    title: Text(tile.deviceName),
                    subtitle: Text(tile.online ? 'Online' : 'Offline'),
                    onTap: () => context.go('/tile/${tile.deviceName.toLowerCase()}'),
                  );
                },
              )
              : const Center(
                child: Center(
                  child: Text('There are no tiles yet.'),
                ),
              ),
        );
      }
    );
  }
}