import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';

class OnboardingPermissionsScreen extends StatelessWidget {
  const OnboardingPermissionsScreen({
    super.key,
    required this.microphoneGranted,
    required this.cameraGranted,
    required this.onRequestMicrophone,
    required this.onRequestCamera,
    required this.onContinue,
    required this.onOpenSettings,
    required this.showPermissionDeniedFallback,
    required this.onSkip,
    this.errorMessage,
  });

  final bool microphoneGranted;
  final bool cameraGranted;
  final VoidCallback onRequestMicrophone;
  final VoidCallback onRequestCamera;
  final VoidCallback onContinue;
  final VoidCallback onOpenSettings;
  final bool showPermissionDeniedFallback;
  final VoidCallback onSkip;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
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
          Text(
            "Permissions",
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: AppSpacing.sm),
          const Text(
            "Microphone is required for voice capture. Camera is optional for receipt photos.",
          ),
          const SizedBox(height: AppSpacing.md),
          AppSurfaceCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                _PermissionRow(
                  title: "Microphone (required)",
                  granted: microphoneGranted,
                  buttonKey: const Key("permissions-request-microphone-button"),
                  buttonLabel: "Request microphone",
                  onPressed: onRequestMicrophone,
                ),
                const SizedBox(height: AppSpacing.md),
                _PermissionRow(
                  title: "Camera (optional)",
                  granted: cameraGranted,
                  buttonKey: const Key("permissions-request-camera-button"),
                  buttonLabel: "Request camera",
                  onPressed: onRequestCamera,
                ),
              ],
            ),
          ),
          if (errorMessage != null) ...<Widget>[
            const SizedBox(height: AppSpacing.sm),
            Text(
              errorMessage!,
              style: TextStyle(color: Colors.red.shade700),
            ),
          ],
          if (showPermissionDeniedFallback) ...<Widget>[
            const SizedBox(height: AppSpacing.md),
            AppSurfaceCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text(
                    "Microphone permission is denied",
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  const Text(
                    "Use Retry to request permission again or open OS settings to enable microphone access manually.",
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Wrap(
                    spacing: AppSpacing.sm,
                    runSpacing: AppSpacing.sm,
                    children: <Widget>[
                      SizedBox(
                        width: 170,
                        child: AppPrimaryButton(
                          key: const Key("permissions-retry-microphone-button"),
                          label: "Retry microphone",
                          onPressed: onRequestMicrophone,
                        ),
                      ),
                      SizedBox(
                        width: 170,
                        child: AppPrimaryButton(
                          key: const Key("permissions-open-settings-button"),
                          label: "Open settings",
                          onPressed: onOpenSettings,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: AppSpacing.lg),
          AppPrimaryButton(
            key: const Key("permissions-continue-button"),
            label: "Continue onboarding",
            onPressed: onContinue,
          ),
        ],
      ),
    );
  }
}

class _PermissionRow extends StatelessWidget {
  const _PermissionRow({
    required this.title,
    required this.granted,
    required this.buttonKey,
    required this.buttonLabel,
    required this.onPressed,
  });

  final String title;
  final bool granted;
  final Key buttonKey;
  final String buttonLabel;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final String status = granted ? "Granted" : "Not granted";
    return Row(
      children: <Widget>[
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: AppSpacing.xs),
              Text(status, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
        SizedBox(
          width: 170,
          child: AppPrimaryButton(
            key: buttonKey,
            label: buttonLabel,
            onPressed: onPressed,
          ),
        ),
      ],
    );
  }
}
