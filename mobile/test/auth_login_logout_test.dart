import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/application/auth_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';
import 'package:personal_ai_assistant_mobile/main.dart';

import 'fakes/fake_auth_repository.dart';

void main() {
  testWidgets("login and logout flow works with auth controller", (
    WidgetTester tester,
  ) async {
    final AuthController authController = AuthController(
      repository: FakeAuthRepository(),
    );
    final OnboardingController onboardingController = OnboardingController();
    await authController.loadSession();

    await tester.pumpWidget(
      PersonalAIAssistantApp(
        controller: AppStateController(),
        authController: authController,
        onboardingController: onboardingController,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key("login-submit-button")), findsOneWidget);
    await tester.enterText(
      find.byKey(const Key("login-email-field")),
      "dev@example.com",
    );
    await tester.enterText(
      find.byKey(const Key("login-password-field")),
      "pass123",
    );
    await tester.tap(find.byKey(const Key("login-submit-button")));
    await tester.pumpAndSettle();

    expect(find.text("Welcome"), findsOneWidget);
    expect(find.text("Privacy short notice"), findsOneWidget);
    await tester.tap(find.byKey(const Key("onboarding-welcome-continue-button")));
    await tester.pumpAndSettle();

    expect(find.text("Get your first value"), findsOneWidget);
    onboardingController.completeFirstMemory();
    onboardingController.completeFirstQuestion();
    onboardingController.finish();
    await tester.pumpAndSettle();

    expect(find.text("Design System Baseline"), findsOneWidget);
    expect(find.byKey(const Key("logout-button")), findsOneWidget);

    await tester.tap(find.byKey(const Key("logout-button")));
    await tester.pumpAndSettle();

    expect(find.text("Sign in"), findsWidgets);
  });
}
