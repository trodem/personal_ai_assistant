import 'package:flutter/material.dart';

import '../core/state/app_state.dart';
import '../core/state/app_state_controller.dart';
import '../screens/theme_preview_screen.dart';
import '../theme/app_theme.dart';

class AppRoot extends StatelessWidget {
  const AppRoot({
    super.key,
    required this.controller,
  });

  final AppStateController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (BuildContext context, Widget? child) {
        return MaterialApp(
          title: "Personal AI Assistant",
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(),
          home: _buildScreen(controller.state.screen),
        );
      },
    );
  }

  Widget _buildScreen(AppScreen screen) {
    switch (screen) {
      case AppScreen.themePreview:
        return const ThemePreviewScreen();
    }
  }
}
