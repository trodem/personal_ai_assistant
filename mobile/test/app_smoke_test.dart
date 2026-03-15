import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/application/auth_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/domain/auth_user.dart';
import 'package:personal_ai_assistant_mobile/main.dart';

import 'fakes/fake_auth_repository.dart';

void main() {
  testWidgets("app boots with themed preview screen", (WidgetTester tester) async {
    final AuthController authController = AuthController(
      repository: FakeAuthRepository(
        currentUser: const AuthUser(id: "1", email: "dev@example.com"),
      ),
    );
    await authController.loadSession();

    await tester.pumpWidget(
      PersonalAIAssistantApp(
        controller: AppStateController(),
        authController: authController,
      ),
    );

    expect(find.text("Personal AI Assistant"), findsOneWidget);
    expect(find.text("Design System Baseline"), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);

    final MaterialApp appWidget = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(appWidget.theme?.scaffoldBackgroundColor, isNotNull);
  });
}
