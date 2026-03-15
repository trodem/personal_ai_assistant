import 'dart:async';

import 'package:flutter/material.dart';

import '../core/state/app_state.dart';
import '../core/state/app_state_controller.dart';
import '../features/auth/application/auth_controller.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/onboarding/application/onboarding_controller.dart';
import '../features/onboarding/presentation/first_value_onboarding_screen.dart';
import '../features/onboarding/presentation/onboarding_language_screen.dart';
import '../features/onboarding/presentation/onboarding_permissions_screen.dart';
import '../features/onboarding/presentation/onboarding_welcome_screen.dart';
import '../screens/memory_capture_chat_screen.dart';
import '../theme/app_theme.dart';

class AppRoot extends StatelessWidget {
  const AppRoot({
    super.key,
    required this.controller,
    required this.authController,
    required this.onboardingController,
  });

  final AppStateController controller;
  final AuthController authController;
  final OnboardingController onboardingController;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge(<Listenable>[
        controller,
        authController,
        onboardingController,
      ]),
      builder: (BuildContext context, Widget? child) {
        return MaterialApp(
          title: "Personal AI Assistant",
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(),
          home: _buildHome(),
        );
      },
    );
  }

  Widget _buildHome() {
    switch (authController.status) {
      case AuthStatus.loading:
        return const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        );
      case AuthStatus.unauthenticated:
        unawaited(onboardingController.hydrateCompletionForUser(null));
        return LoginScreen(
          errorMessage: authController.errorMessage,
          onSubmit: (String email, String password) {
            return authController.signIn(email: email, password: password);
          },
        );
      case AuthStatus.authenticated:
        unawaited(
          onboardingController.hydrateCompletionForUser(authController.user?.id),
        );
        if (onboardingController.isHydratingCompletion) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        if (!onboardingController.completed) {
          if (!onboardingController.welcomeStepDone) {
            return OnboardingWelcomeScreen(
              onContinue: onboardingController.completeWelcomeStep,
              onSkip: () {
                unawaited(onboardingController.skipForNow());
              },
            );
          }
          if (!onboardingController.languageStepDone) {
            return OnboardingLanguageScreen(
              selectedLanguage: onboardingController.selectedLanguage,
              onLanguageChanged: onboardingController.selectLanguage,
              onContinue: () {
                onboardingController.persistLanguageStep();
              },
              onSkip: () {
                unawaited(onboardingController.skipForNow());
              },
              isSaving: onboardingController.isSavingLanguage,
              errorMessage: onboardingController.languageError,
            );
          }
          if (!onboardingController.permissionsStepDone) {
            return OnboardingPermissionsScreen(
              microphoneGranted: onboardingController.microphoneGranted,
              cameraGranted: onboardingController.cameraGranted,
              onRequestMicrophone: () {
                onboardingController.requestMicrophonePermission();
              },
              onRequestCamera: () {
                onboardingController.requestCameraPermission();
              },
              onContinue: onboardingController.completePermissionsStep,
              onOpenSettings: () {
                onboardingController.openPermissionSettings();
              },
              showPermissionDeniedFallback:
                  onboardingController.showPermissionDeniedFallback,
              onSkip: () {
                unawaited(onboardingController.skipForNow());
              },
              errorMessage: onboardingController.permissionsError,
            );
          }
          return FirstValueOnboardingScreen(
            firstMemoryDone: onboardingController.firstMemoryDone,
            firstMemoryDraft: onboardingController.firstMemoryDraft,
            firstMemoryProposalReady:
                onboardingController.firstMemoryProposalReady,
            firstMemoryError: onboardingController.firstMemoryError,
            onFirstMemoryDraftChanged: onboardingController.updateFirstMemoryDraft,
            onPrepareFirstMemoryProposal:
                onboardingController.prepareFirstMemoryProposal,
            onConfirmFirstMemory: onboardingController.confirmFirstMemory,
            onModifyFirstMemory: onboardingController.modifyFirstMemoryProposal,
            onCancelFirstMemory: onboardingController.cancelFirstMemoryProposal,
            firstQuestionDone: onboardingController.firstQuestionDone,
            firstQuestionDraft: onboardingController.firstQuestionDraft,
            firstQuestionAnswer: onboardingController.firstQuestionAnswer,
            firstQuestionConfidence: onboardingController.firstQuestionConfidence,
            firstQuestionSourceIds: onboardingController.firstQuestionSourceIds,
            firstQuestionAnswerReady:
                onboardingController.firstQuestionAnswerReady,
            firstQuestionWhyExpanded:
                onboardingController.firstQuestionWhyExpanded,
            firstQuestionError: onboardingController.firstQuestionError,
            onFirstQuestionDraftChanged:
                onboardingController.updateFirstQuestionDraft,
            onPrepareFirstQuestionAnswer:
                onboardingController.prepareFirstQuestionAnswer,
            onToggleFirstQuestionWhyDisclosure:
                onboardingController.toggleFirstQuestionWhyDisclosure,
            onCompleteFirstQuestion: onboardingController.completeFirstQuestion,
            onSkip: () {
              unawaited(onboardingController.skipForNow());
            },
            onFinish: onboardingController.finish,
          );
        }
        return _buildScreen(controller.state.screen);
    }
  }

  Widget _buildScreen(AppScreen screen) {
    switch (screen) {
      case AppScreen.themePreview:
        return MemoryCaptureChatScreen(
          userEmail: authController.user?.email,
          onResumeOnboarding: onboardingController.hasPendingOnboardingResume
              ? onboardingController.resumeDeferredOnboarding
              : null,
          onLogout: () async {
            await authController.signOut();
            onboardingController.reset();
          },
        );
    }
  }
}
