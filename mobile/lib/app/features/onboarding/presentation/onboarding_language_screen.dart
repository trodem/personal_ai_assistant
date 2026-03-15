import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';
import '../domain/preferred_language.dart';

class OnboardingLanguageScreen extends StatelessWidget {
  const OnboardingLanguageScreen({
    super.key,
    required this.selectedLanguage,
    required this.onLanguageChanged,
    required this.onContinue,
    required this.isSaving,
    this.errorMessage,
  });

  final PreferredLanguage selectedLanguage;
  final ValueChanged<PreferredLanguage> onLanguageChanged;
  final VoidCallback onContinue;
  final bool isSaving;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Personal AI Assistant")),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: <Widget>[
          Text("Choose your language", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: AppSpacing.sm),
          const Text(
            "This sets your preferred language (`preferred_language`) for app responses.",
          ),
          const SizedBox(height: AppSpacing.md),
          AppSurfaceCard(
            child: RadioGroup<PreferredLanguage>(
              groupValue: selectedLanguage,
              onChanged: (PreferredLanguage? language) {
                if (language != null) {
                  onLanguageChanged(language);
                }
              },
              child: const Column(
                children: <Widget>[
                  RadioListTile<PreferredLanguage>(
                    key: Key("language-en"),
                    title: Text("English"),
                    value: PreferredLanguage.en,
                  ),
                  RadioListTile<PreferredLanguage>(
                    key: Key("language-it"),
                    title: Text("Italiano"),
                    value: PreferredLanguage.it,
                  ),
                  RadioListTile<PreferredLanguage>(
                    key: Key("language-de"),
                    title: Text("Deutsch"),
                    value: PreferredLanguage.de,
                  ),
                ],
              ),
            ),
          ),
          if (errorMessage != null) ...<Widget>[
            const SizedBox(height: AppSpacing.sm),
            Text(
              errorMessage!,
              style: TextStyle(color: Colors.red.shade700),
            ),
          ],
          const SizedBox(height: AppSpacing.lg),
          if (isSaving)
            const Center(child: CircularProgressIndicator())
          else
            AppPrimaryButton(
              key: const Key("onboarding-language-continue-button"),
              label: "Save language and continue",
              onPressed: onContinue,
            ),
        ],
      ),
    );
  }
}
