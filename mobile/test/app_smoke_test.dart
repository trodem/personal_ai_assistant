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
import 'fakes/fake_onboarding_resume_repository.dart';

void main() {
  testWidgets("app boots with memory capture chat screen", (WidgetTester tester) async {
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
          onboardingResumeRepository: FakeOnboardingResumeRepository(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("Personal AI Assistant"), findsOneWidget);
    expect(find.byKey(const Key("memory-capture-title")), findsOneWidget);
    expect(find.byKey(const Key("memory-chat-list")), findsOneWidget);
    expect(find.byKey(const Key("memory-composer-text-field")), findsOneWidget);
    expect(find.byKey(const Key("memory-composer-attachment-button")), findsOneWidget);
    expect(find.byKey(const Key("memory-composer-microphone-button")), findsOneWidget);
    expect(find.byKey(const Key("memory-composer-send-button")), findsOneWidget);

    final MaterialApp appWidget = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(appWidget.theme?.scaffoldBackgroundColor, isNotNull);
  });
}
