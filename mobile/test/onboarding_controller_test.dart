import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';

void main() {
  test("onboarding completes only after first memory and first question", () {
    final OnboardingController controller = OnboardingController();

    expect(controller.completed, isFalse);
    expect(controller.canFinish, isFalse);

    controller.completeFirstMemory();
    expect(controller.canFinish, isFalse);

    controller.completeFirstQuestion();
    expect(controller.canFinish, isTrue);

    controller.finish();
    expect(controller.completed, isTrue);
  });
}
