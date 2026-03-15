import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/application/auth_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/domain/auth_user.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';
import 'package:personal_ai_assistant_mobile/main.dart';

import 'fakes/fake_auth_repository.dart';
import 'fakes/fake_device_permissions_gateway.dart';
import 'fakes/fake_language_preferences_repository.dart';
import 'fakes/fake_onboarding_completion_repository.dart';

void main() {
  testWidgets("app boots with themed preview screen", (WidgetTester tester) async {
    final AuthController authController = AuthController(
      repository: FakeAuthRepository(
        currentUser: const AuthUser(id: "1", email: "dev@example.com"),
      ),
    );
    await authController.loadSession();

    final FakeOnboardingCompletionRepository completionRepository =
        FakeOnboardingCompletionRepository();
    completionRepository.setCompletedAtForUser("1", DateTime.utc(2026, 3, 15));

    await tester.pumpWidget(
      PersonalAIAssistantApp(
        controller: AppStateController(),
        authController: authController,
        onboardingController: OnboardingController(
          completed: true,
          languagePreferencesRepository: FakeLanguagePreferencesRepository(),
          devicePermissionsGateway: FakeDevicePermissionsGateway(),
          onboardingCompletionRepository: completionRepository,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("Personal AI Assistant"), findsOneWidget);
    expect(find.text("Design System Baseline"), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);

    final MaterialApp appWidget = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(appWidget.theme?.scaffoldBackgroundColor, isNotNull);
  });
}
