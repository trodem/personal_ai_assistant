import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';

class OnboardingWelcomeScreen extends StatelessWidget {
  const OnboardingWelcomeScreen({
    super.key,
    required this.onContinue,
  });

  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Personal AI Assistant")),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: <Widget>[
          Text("Welcome", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppSpacing.sm),
          const Text(
            "Your assistant helps you remember expenses, inventory, loans, and notes with reliable confirmations.",
          ),
          const SizedBox(height: AppSpacing.md),
          const AppSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  "Privacy short notice",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                SizedBox(height: AppSpacing.sm),
                Text(
                  "Your data stays user-scoped and memory saves always require explicit confirmation.",
                ),
                SizedBox(height: AppSpacing.xs),
                Text(
                  "Do not share sensitive secrets in voice or text unless needed for your own records.",
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          AppPrimaryButton(
            key: const Key("onboarding-welcome-continue-button"),
            label: "Continue onboarding",
            onPressed: onContinue,
          ),
        ],
      ),
    );
  }
}
