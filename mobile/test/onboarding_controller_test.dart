import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/application/onboarding_controller.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/onboarding_resume_point.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/preferred_language.dart';

import 'fakes/fake_device_permissions_gateway.dart';
import 'fakes/fake_language_preferences_repository.dart';
import 'fakes/fake_onboarding_completion_repository.dart';
import 'fakes/fake_onboarding_resume_repository.dart';

void main() {
  test("onboarding completes only after first memory and first question", () {
    final FakeLanguagePreferencesRepository languageRepository =
        FakeLanguagePreferencesRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: languageRepository,
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
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
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
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
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
    );

    await controller.requestCameraPermission();
    controller.completePermissionsStep();
    expect(controller.permissionsStepDone, isFalse);

    permissionsGateway.microphoneGranted = true;
    await controller.requestMicrophonePermission();
    controller.completePermissionsStep();
    expect(controller.permissionsStepDone, isTrue);
  });

  test("permission denied fallback exposes retry and open settings path", () async {
    final FakeDevicePermissionsGateway permissionsGateway =
        FakeDevicePermissionsGateway(
          microphoneGranted: false,
          cameraGranted: true,
          openSettingsResult: true,
        );
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: permissionsGateway,
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
    );

    await controller.requestMicrophonePermission();
    expect(controller.showPermissionDeniedFallback, isTrue);

    await controller.openPermissionSettings();
    expect(permissionsGateway.openSettingsCalled, isTrue);
    expect(controller.permissionsError, contains("System settings opened"));
  });

  test("first memory requires proposal confirmation", () {
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
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
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
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

  test("finish persists onboarding_completed_at and hydrates completion state", () async {
    final FakeOnboardingCompletionRepository completionRepository =
        FakeOnboardingCompletionRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: completionRepository,
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
    );

    await controller.hydrateCompletionForUser("user-1");
    expect(controller.completed, isFalse);

    controller.completeFirstMemory();
    controller.updateFirstQuestionDraft("What did I buy today?");
    controller.prepareFirstQuestionAnswer();
    controller.completeFirstQuestion();
    await controller.finish();

    expect(controller.completed, isTrue);
    expect(completionRepository.completedAtForUser("user-1"), isNotNull);

    final OnboardingController hydratedController = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: completionRepository,
      onboardingResumeRepository: FakeOnboardingResumeRepository(),
    );
    await hydratedController.hydrateCompletionForUser("user-1");
    expect(hydratedController.completed, isTrue);
  });

  test("skip persists deterministic resume point and hydrates same step", () async {
    final FakeOnboardingResumeRepository resumeRepository =
        FakeOnboardingResumeRepository();
    final OnboardingController controller = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: resumeRepository,
    );

    await controller.hydrateCompletionForUser("user-2");
    controller.completeWelcomeStep();
    controller.selectLanguage(PreferredLanguage.it);
    await controller.persistLanguageStep();
    await controller.skipForNow();

    expect(controller.completed, isTrue);
    expect(
      resumeRepository.resumePointForUser("user-2"),
      OnboardingResumePoint.permissions,
    );

    final OnboardingController resumedController = OnboardingController(
      languagePreferencesRepository: FakeLanguagePreferencesRepository(),
      devicePermissionsGateway: FakeDevicePermissionsGateway(),
      onboardingCompletionRepository: FakeOnboardingCompletionRepository(),
      onboardingResumeRepository: resumeRepository,
    );
    await resumedController.hydrateCompletionForUser("user-2");
    expect(resumedController.completed, isFalse);
    expect(resumedController.welcomeStepDone, isTrue);
    expect(resumedController.languageStepDone, isTrue);
    expect(resumedController.permissionsStepDone, isFalse);
  });
}
