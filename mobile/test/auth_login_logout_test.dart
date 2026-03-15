import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/application/auth_controller.dart';
import 'package:personal_ai_assistant_mobile/main.dart';

import 'fakes/fake_auth_repository.dart';

void main() {
  testWidgets("login and logout flow works with auth controller", (
    WidgetTester tester,
  ) async {
    final AuthController authController = AuthController(
      repository: FakeAuthRepository(),
    );
    await authController.loadSession();

    await tester.pumpWidget(
      PersonalAIAssistantApp(
        controller: AppStateController(),
        authController: authController,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("Sign in"), findsWidgets);
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

    expect(find.text("Design System Baseline"), findsOneWidget);
    expect(find.byKey(const Key("logout-button")), findsOneWidget);

    await tester.tap(find.byKey(const Key("logout-button")));
    await tester.pumpAndSettle();

    expect(find.text("Sign in"), findsWidgets);
  });
}
