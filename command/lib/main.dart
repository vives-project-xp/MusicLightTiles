import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        
      ], 
      child: const MyApp()
    ),
  );
}

final List<Tile> tiles = [
  const Tile('TILE1', false),
  const Tile('TILE2', false),
  const Tile('TILE3', false),
  const Tile('TILE4', false),
];

final GoRouter _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsPage(),
    ),
    // Create a route for each tile in the list (e.g. /tile1 /tile2 /tile3 /tile4)
    for (final tile in tiles)
      GoRoute(
        path: '/${tile.name.toLowerCase()}',
        builder: (context, state) => const TilePage(),
      ),
  ],
);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Go Router',
      routerConfig: _router,
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
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
          tiles.isNotEmpty ?
            ListView.builder(
              itemCount: tiles.length,
              itemBuilder: (context, index) {
                final Tile tile = tiles[index];
                return ListTile(
                  title: Text(tile.name),
                  subtitle: Text(tile.online ? 'Online' : 'Offline'),
                  onTap: () => context.go('/${tile.name.toLowerCase()}'),
                );
              },
            )
          :
            const Center(
              child: Center(
                child: Text('There are no tiles yet.'),
              ),
            )
      );
  }
}

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

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
          title: const Text('Settings'),
          centerTitle: true,
          automaticallyImplyLeading: false,
        ),
        body: const Center(
          child: Center(
            child: Text('Settings'),
          ),
        ));
  }
}

class TilePage extends StatelessWidget {
  const TilePage({super.key});

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
          title: const Text('Tile'),
          centerTitle: true,
          automaticallyImplyLeading: false,
        ),
        body: const Center(
          child: Center(
            child: Text('Tile'),
          ),
        ));
  }
}

class Tile {
  final String name;
  final bool online;
  // Define constructor
  const Tile(this.name, this.online);
}
