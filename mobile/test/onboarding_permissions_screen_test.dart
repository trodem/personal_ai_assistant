import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/presentation/onboarding_permissions_screen.dart';

void main() {
  testWidgets(
    "permissions screen shows retry/open-settings CTAs when fallback is active",
    (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: OnboardingPermissionsScreen(
            microphoneGranted: false,
            cameraGranted: false,
            onRequestMicrophone: () {},
            onRequestCamera: () {},
            onContinue: () {},
            onOpenSettings: () {},
            showPermissionDeniedFallback: true,
            onSkip: () {},
            errorMessage:
                "Microphone permission is required to continue onboarding.",
          ),
        ),
      );

      expect(
        find.byKey(const Key("permissions-retry-microphone-button")),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key("permissions-open-settings-button")),
        findsOneWidget,
      );
    },
  );
}
