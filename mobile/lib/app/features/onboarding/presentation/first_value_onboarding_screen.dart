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
    required this.firstQuestionDraft,
    required this.firstQuestionAnswer,
    required this.firstQuestionConfidence,
    required this.firstQuestionSourceIds,
    required this.firstQuestionAnswerReady,
    required this.firstQuestionWhyExpanded,
    required this.firstQuestionError,
    required this.onFirstQuestionDraftChanged,
    required this.onPrepareFirstQuestionAnswer,
    required this.onToggleFirstQuestionWhyDisclosure,
    required this.onCompleteFirstQuestion,
    required this.onSkip,
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
  final String firstQuestionDraft;
  final String firstQuestionAnswer;
  final String firstQuestionConfidence;
  final List<String> firstQuestionSourceIds;
  final bool firstQuestionAnswerReady;
  final bool firstQuestionWhyExpanded;
  final String? firstQuestionError;
  final ValueChanged<String> onFirstQuestionDraftChanged;
  final VoidCallback onPrepareFirstQuestionAnswer;
  final VoidCallback onToggleFirstQuestionWhyDisclosure;
  final VoidCallback onCompleteFirstQuestion;
  final VoidCallback onSkip;
  final Future<void> Function() onFinish;

  @override
  Widget build(BuildContext context) {
    final bool canFinish = firstMemoryDone && firstQuestionDone;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Personal AI Assistant"),
        actions: <Widget>[
          TextButton(
            key: const Key("onboarding-skip-button"),
            onPressed: onSkip,
            child: const Text("Skip for now"),
          ),
        ],
      ),
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
                    style: AppTextStyles.error,
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
                  "Example: \"What did I buy today?\" Ask once, then review why the answer was produced.",
                ),
                const SizedBox(height: AppSpacing.md),
                TextField(
                  key: const Key("onboarding-question-input"),
                  decoration: const InputDecoration(
                    hintText: "What did I buy today?",
                  ),
                  onChanged: onFirstQuestionDraftChanged,
                ),
                const SizedBox(height: AppSpacing.sm),
                AppPrimaryButton(
                  key: const Key("onboarding-question-ask-button"),
                  label: firstQuestionDone ? "First question completed" : "Ask first question",
                  onPressed: firstQuestionDone ? null : onPrepareFirstQuestionAnswer,
                ),
                if (firstQuestionError != null) ...<Widget>[
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    firstQuestionError!,
                    style: AppTextStyles.error,
                  ),
                ],
                if (firstQuestionAnswerReady) ...<Widget>[
                  const SizedBox(height: AppSpacing.md),
                  AppSurfaceCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          "Assistant answer",
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: AppSpacing.xs),
                        Text(firstQuestionAnswer),
                        const SizedBox(height: AppSpacing.sm),
                        OutlinedButton(
                          key: const Key("onboarding-question-why-toggle-button"),
                          onPressed: onToggleFirstQuestionWhyDisclosure,
                          child: Text(
                            firstQuestionWhyExpanded
                                ? "Hide why this answer"
                                : "Why this answer",
                          ),
                        ),
                        if (firstQuestionWhyExpanded) ...<Widget>[
                          const SizedBox(height: AppSpacing.sm),
                          Container(
                            key: const Key("onboarding-question-why-panel"),
                            padding: const EdgeInsets.all(AppSpacing.sm),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(AppRadii.md),
                              color: AppColors.surface,
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text("Confidence: $firstQuestionConfidence"),
                                const SizedBox(height: AppSpacing.xs),
                                Text(
                                  "Sources: ${firstQuestionSourceIds.join(", ")}",
                                ),
                              ],
                            ),
                          ),
                        ],
                        const SizedBox(height: AppSpacing.md),
                        AppPrimaryButton(
                          key: const Key("onboarding-question-complete-button"),
                          label: firstQuestionDone
                              ? "First question completed"
                              : "Complete first question step",
                          onPressed: firstQuestionDone
                              ? null
                              : onCompleteFirstQuestion,
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          AppPrimaryButton(
            key: const Key("onboarding-finish-button"),
            label: "Finish onboarding",
            onPressed: canFinish
                ? () async {
                    await onFinish();
                  }
                : null,
          ),
        ],
      ),
    );
  }
}
