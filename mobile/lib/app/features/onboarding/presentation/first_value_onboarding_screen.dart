import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';

class FirstValueOnboardingScreen extends StatelessWidget {
  const FirstValueOnboardingScreen({
    super.key,
    required this.firstMemoryDone,
    required this.firstMemoryDraft,
    required this.firstMemoryProposalReady,
    required this.firstMemoryError,
    required this.onFirstMemoryDraftChanged,
    required this.onPrepareFirstMemoryProposal,
    required this.onConfirmFirstMemory,
    required this.onModifyFirstMemory,
    required this.onCancelFirstMemory,
    required this.firstQuestionDone,
    required this.onCompleteFirstQuestion,
    required this.onFinish,
  });

  final bool firstMemoryDone;
  final String firstMemoryDraft;
  final bool firstMemoryProposalReady;
  final String? firstMemoryError;
  final ValueChanged<String> onFirstMemoryDraftChanged;
  final VoidCallback onPrepareFirstMemoryProposal;
  final VoidCallback onConfirmFirstMemory;
  final VoidCallback onModifyFirstMemory;
  final VoidCallback onCancelFirstMemory;
  final bool firstQuestionDone;
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
                TextField(
                  key: const Key("onboarding-memory-input"),
                  decoration: const InputDecoration(
                    hintText: "I bought bread for 3 CHF at Coop",
                  ),
                  onChanged: onFirstMemoryDraftChanged,
                ),
                const SizedBox(height: AppSpacing.sm),
                AppPrimaryButton(
                  key: const Key("onboarding-memory-extract-button"),
                  label: firstMemoryDone
                      ? "First memory completed"
                      : "Extract memory proposal",
                  onPressed: firstMemoryDone ? null : onPrepareFirstMemoryProposal,
                ),
                if (firstMemoryError != null) ...<Widget>[
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    firstMemoryError!,
                    style: TextStyle(color: Colors.red.shade700),
                  ),
                ],
                if (firstMemoryProposalReady) ...<Widget>[
                  const SizedBox(height: AppSpacing.md),
                  AppSurfaceCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          "Memory proposal",
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: AppSpacing.xs),
                        Text("Text: $firstMemoryDraft"),
                        const SizedBox(height: AppSpacing.xs),
                        const Text("Actions: Confirm / Modify / Cancel"),
                        const SizedBox(height: AppSpacing.md),
                        Wrap(
                          spacing: AppSpacing.sm,
                          runSpacing: AppSpacing.sm,
                          children: <Widget>[
                            SizedBox(
                              width: 120,
                              child: AppPrimaryButton(
                                key: const Key("onboarding-memory-confirm-button"),
                                label: "Confirm",
                                onPressed: onConfirmFirstMemory,
                              ),
                            ),
                            SizedBox(
                              width: 120,
                              child: AppPrimaryButton(
                                key: const Key("onboarding-memory-modify-button"),
                                label: "Modify",
                                onPressed: onModifyFirstMemory,
                              ),
                            ),
                            SizedBox(
                              width: 120,
                              child: AppPrimaryButton(
                                key: const Key("onboarding-memory-cancel-button"),
                                label: "Cancel",
                                onPressed: onCancelFirstMemory,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
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
