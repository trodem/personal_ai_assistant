import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';
import '../widgets/app_primary_button.dart';
import '../widgets/app_surface_card.dart';

class ThemePreviewScreen extends StatelessWidget {
  const ThemePreviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final TextTheme text = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(title: const Text("Personal AI Assistant")),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: <Widget>[
          Text("Design System Baseline", style: text.headlineMedium),
          const SizedBox(height: AppSpacing.xs),
          Text(
            "Reusable widgets and centralized tokens are active for MVP UI.",
            style: text.bodyMedium,
          ),
          const SizedBox(height: AppSpacing.lg),
          AppSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text("Quick Memory", style: text.titleLarge),
                const SizedBox(height: AppSpacing.sm),
                const TextField(
                  decoration: InputDecoration(hintText: "I bought bread for 3 CHF at Coop"),
                ),
                const SizedBox(height: AppSpacing.md),
                const AppPrimaryButton(label: "Extract Memory", onPressed: null),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
