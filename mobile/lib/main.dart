import 'package:flutter/material.dart';

import 'app/core/state/app_state_controller.dart';
import 'app/core/state/app_state_scope.dart';
import 'app/presentation/app_root.dart';

void main() {
  runApp(
    PersonalAIAssistantApp(
      controller: AppStateController(),
    ),
  );
}

class PersonalAIAssistantApp extends StatelessWidget {
  const PersonalAIAssistantApp({
    super.key,
    required this.controller,
  });

  final AppStateController controller;

  @override
  Widget build(BuildContext context) {
    return AppStateScope(
      controller: controller,
      child: AppRoot(controller: controller),
    );
  }
}
