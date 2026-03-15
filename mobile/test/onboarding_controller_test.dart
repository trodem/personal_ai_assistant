import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/preferred_language.dart';

import 'fakes/fake_device_permissions_gateway.dart';
import 'fakes/fake_language_preferences_repository.dart';

void main() {
  test("onboarding completes only after first memory and first question", () {
    final FakeLanguagePreferencesRepository languageRepository =
        FakeLanguagePreferencesRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: languageRepository,
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
    );

    expect(controller.completed, isFalse);
    expect(controller.welcomeStepDone, isFalse);
    expect(controller.canFinish, isFalse);

    controller.completeWelcomeStep();
    expect(controller.welcomeStepDone, isTrue);

    controller.completeFirstMemory();
    expect(controller.canFinish, isFalse);

    controller.updateFirstQuestionDraft("What did I buy today?");
    controller.prepareFirstQuestionAnswer();
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
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
    );

    controller.selectLanguage(PreferredLanguage.de);
    await controller.persistLanguageStep();

    expect(controller.languageStepDone, isTrue);
    expect(languageRepository.lastSaved, PreferredLanguage.de);
  });

  test("permissions step requires microphone", () async {
    final FakeDevicePermissionsGateway permissionsGateway =
        FakeDevicePermissionsGateway(
          microphoneGranted: false,
          cameraGranted: true,
        );
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: permissionsGateway,
    );

    await controller.requestCameraPermission();
    controller.completePermissionsStep();
    expect(controller.permissionsStepDone, isFalse);

    permissionsGateway.microphoneGranted = true;
    await controller.requestMicrophonePermission();
    controller.completePermissionsStep();
    expect(controller.permissionsStepDone, isTrue);
  });

  test("first memory requires proposal confirmation", () {
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
    );

    controller.prepareFirstMemoryProposal();
    expect(controller.firstMemoryProposalReady, isFalse);
    expect(controller.firstMemoryError, isNotNull);

    controller.updateFirstMemoryDraft("I bought bread for 3 CHF at Coop");
    controller.prepareFirstMemoryProposal();
    expect(controller.firstMemoryProposalReady, isTrue);

    controller.modifyFirstMemoryProposal();
    expect(controller.firstMemoryProposalReady, isFalse);

    controller.prepareFirstMemoryProposal();
    controller.confirmFirstMemory();
    expect(controller.firstMemoryDone, isTrue);
    expect(controller.firstMemoryProposalReady, isFalse);
  });

  test("first question requires guided ask and supports why disclosure", () {
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
    );

    controller.completeFirstQuestion();
    expect(controller.firstQuestionDone, isFalse);
    expect(controller.firstQuestionError, isNotNull);

    controller.updateFirstQuestionDraft("What did I buy today?");
    controller.prepareFirstQuestionAnswer();
    expect(controller.firstQuestionAnswerReady, isTrue);
    expect(controller.firstQuestionAnswer, isNotEmpty);
    expect(controller.firstQuestionSourceIds, isNotEmpty);

    controller.toggleFirstQuestionWhyDisclosure();
    expect(controller.firstQuestionWhyExpanded, isTrue);

    controller.completeFirstQuestion();
    expect(controller.firstQuestionDone, isTrue);
  });
}
