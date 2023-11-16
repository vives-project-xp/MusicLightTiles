import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'models/tile_model.dart';
import 'views/home.dart';
import 'views/notfound.dart';
import 'views/settings.dart';
import 'views/tile.dart';

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/settings',
      name: 'settings',
      builder: (context, state) => const SettingsPage(),
    ),
    GoRoute(
      path: '/tile/:name',
      name: 'tile',
      builder: (context, state) {
        final String? name = state.pathParameters['name'];
        // Look if the tile exists in the model
        final TileModel tileModel = Provider.of<TileModel>(context, listen: false);
        final bool tileExists = tileModel.tiles.any((tile) => tile.deviceName == name?.toUpperCase());
        // If the tile exists, return the tile page, otherwise return the not found page
        if (name != null && tileExists) {
          return TilePage(tile: tileModel.tiles.firstWhere((tile) => tile.deviceName == name.toUpperCase()));
        } else {
          return const NotFoundPage();
        }
      },
    )
  ],
  // TODO: Add error page
);

void main() {
  runApp(
    MultiProvider(providers: [
      ChangeNotifierProvider(create: (_) => TileModel()),
    ], child: const MyApp()),
  );
}

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