import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';

class FirstValueOnboardingScreen extends StatelessWidget {
  const FirstValueOnboardingScreen({
    super.key,
    required this.firstMemoryDone,
    required this.firstQuestionDone,
    required this.onCompleteFirstMemory,
    required this.onCompleteFirstQuestion,
    required this.onFinish,
  });

  final bool firstMemoryDone;
  final bool firstQuestionDone;
  final VoidCallback onCompleteFirstMemory;
  final VoidCallback onCompleteFirstQuestion;
  final VoidCallback onFinish;

  @override
  Widget build(BuildContext context) {
    final bool canFinish = firstMemoryDone && firstQuestionDone;

    return Scaffold(
      appBar: AppBar(title: const Text("Personal AI Assistant")),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: <Widget>[
          Text("Get your first value", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppSpacing.sm),
          Text(
            "Complete one memory and one question to finish first-run onboarding.",
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: AppSpacing.lg),
          AppSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text("Step 1: Save your first memory", style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.sm),
                const Text(
                  "Example: \"I bought bread for 3 CHF at Coop\". Confirm the extracted memory.",
                ),
                const SizedBox(height: AppSpacing.md),
                AppPrimaryButton(
                  key: const Key("onboarding-first-memory-button"),
                  label: firstMemoryDone ? "First memory completed" : "Mark first memory as done",
                  onPressed: firstMemoryDone ? null : onCompleteFirstMemory,
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          AppSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text("Step 2: Ask your first question", style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.sm),
                const Text(
                  "Example: \"What did I buy today?\" and verify the answer with sources.",
                ),
                const SizedBox(height: AppSpacing.md),
                AppPrimaryButton(
                  key: const Key("onboarding-first-question-button"),
                  label: firstQuestionDone ? "First question completed" : "Mark first question as done",
                  onPressed: firstQuestionDone ? null : onCompleteFirstQuestion,
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          AppPrimaryButton(
            key: const Key("onboarding-finish-button"),
            label: "Finish onboarding",
            onPressed: canFinish ? onFinish : null,
          ),
        ],
      ),
    );
  }
}
