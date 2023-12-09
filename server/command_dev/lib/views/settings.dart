import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

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