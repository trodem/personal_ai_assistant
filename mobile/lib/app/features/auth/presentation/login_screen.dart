import 'package:flutter/material.dart';

import '../../../theme/app_tokens.dart';
import '../../../widgets/app_primary_button.dart';
import '../../../widgets/app_surface_card.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({
    super.key,
    required this.onSubmit,
    this.errorMessage,
  });

  final Future<void> Function(String email, String password) onSubmit;
  final String? errorMessage;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    await widget.onSubmit(
      _emailController.text.trim(),
      _passwordController.text,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Personal AI Assistant")),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 440),
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: AppSurfaceCard(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Text("Sign in", style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: AppSpacing.sm),
                  const Text("Use your Supabase email/password credentials."),
                  const SizedBox(height: AppSpacing.md),
                  TextField(
                    key: const Key("login-email-field"),
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(labelText: "Email"),
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  TextField(
                    key: const Key("login-password-field"),
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: "Password"),
                  ),
                  if (widget.errorMessage != null) ...<Widget>[
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      widget.errorMessage!,
                      style: AppTextStyles.error,
                    ),
                  ],
                  const SizedBox(height: AppSpacing.md),
                  AppPrimaryButton(
                    key: const Key("login-submit-button"),
                    label: "Sign in",
                    onPressed: _submit,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
