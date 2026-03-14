import 'package:flutter/material.dart';

import 'app/screens/theme_preview_screen.dart';
import 'app/theme/app_theme.dart';

void main() {
  runApp(const PersonalAIAssistantApp());
}

class PersonalAIAssistantApp extends StatelessWidget {
  const PersonalAIAssistantApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Personal AI Assistant",
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: const ThemePreviewScreen(),
    );
  }
}
