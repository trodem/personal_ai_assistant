import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/preferred_language.dart';

import 'fakes/fake_language_preferences_repository.dart';

void main() {
  test("onboarding completes only after first memory and first question", () {
    final FakeLanguagePreferencesRepository languageRepository =
        FakeLanguagePreferencesRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: languageRepository,
    );

    expect(controller.completed, isFalse);
    expect(controller.welcomeStepDone, isFalse);
    expect(controller.canFinish, isFalse);

    controller.completeWelcomeStep();
    expect(controller.welcomeStepDone, isTrue);

    controller.completeFirstMemory();
    expect(controller.canFinish, isFalse);

    controller.completeFirstQuestion();
    expect(controller.canFinish, isTrue);

    controller.finish();
    expect(controller.completed, isTrue);
  });

  test("language selection persists preferred_language", () async {
    final FakeLanguagePreferencesRepository languageRepository =
        FakeLanguagePreferencesRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: languageRepository,
    );

    controller.selectLanguage(PreferredLanguage.de);
    await controller.persistLanguageStep();

    expect(controller.languageStepDone, isTrue);
    expect(languageRepository.lastSaved, PreferredLanguage.de);
  });
}
