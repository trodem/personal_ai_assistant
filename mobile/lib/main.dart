import 'package:flutter/material.dart';

import 'app/core/state/app_state_controller.dart';
import 'app/core/state/app_state_scope.dart';
import 'app/features/auth/application/auth_controller.dart';
import 'app/features/auth/data/auth_repository_factory.dart';
import 'app/features/onboarding/application/onboarding_controller.dart';
import 'app/features/onboarding/data/device_permissions_gateway_factory.dart';
import 'app/features/onboarding/data/language_preferences_repository_factory.dart';
import 'app/features/onboarding/data/onboarding_completion_repository_factory.dart';
import 'app/presentation/app_root.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final AuthController authController = AuthController(
    repository: await AuthRepositoryFactory.create(),
  );
  await authController.loadSession();
  final OnboardingController onboardingController = OnboardingController(
    languagePreferencesRepository: LanguagePreferencesRepositoryFactory.create(),
    devicePermissionsGateway: DevicePermissionsGatewayFactory.create(),
    onboardingCompletionRepository:
        OnboardingCompletionRepositoryFactory.create(),
  );
  await onboardingController.hydrateCompletionForUser(authController.user?.id);
  runApp(
    PersonalAIAssistantApp(
      controller: AppStateController(),
      authController: authController,
      onboardingController: onboardingController,
    ),
  );
}

class PersonalAIAssistantApp extends StatelessWidget {
  const PersonalAIAssistantApp({
    super.key,
    required this.controller,
    required this.authController,
    required this.onboardingController,
  });

  final AppStateController controller;
  final AuthController authController;
  final OnboardingController onboardingController;

  @override
  Widget build(BuildContext context) {
    return AppStateScope(
      controller: controller,
      child: AppRoot(
        controller: controller,
        authController: authController,
        onboardingController: onboardingController,
      ),
    );
  }
}
