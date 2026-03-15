import 'package:flutter/material.dart';

import '../core/state/app_state.dart';
import '../core/state/app_state_controller.dart';
import '../features/auth/application/auth_controller.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/onboarding/application/onboarding_controller.dart';
import '../features/onboarding/presentation/first_value_onboarding_screen.dart';
import '../screens/theme_preview_screen.dart';
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
        return LoginScreen(
          errorMessage: authController.errorMessage,
          onSubmit: (String email, String password) {
            return authController.signIn(email: email, password: password);
          },
        );
      case AuthStatus.authenticated:
        if (!onboardingController.completed) {
          return FirstValueOnboardingScreen(
            firstMemoryDone: onboardingController.firstMemoryDone,
            firstQuestionDone: onboardingController.firstQuestionDone,
            onCompleteFirstMemory: onboardingController.completeFirstMemory,
            onCompleteFirstQuestion: onboardingController.completeFirstQuestion,
            onFinish: onboardingController.finish,
          );
        }
        return _buildScreen(controller.state.screen);
    }
  }

  Widget _buildScreen(AppScreen screen) {
    switch (screen) {
      case AppScreen.themePreview:
        return ThemePreviewScreen(
          userEmail: authController.user?.email,
          onLogout: () async {
            await authController.signOut();
            onboardingController.reset();
          },
        );
    }
  }
}
