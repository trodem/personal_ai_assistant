import 'package:flutter/material.dart';

import '../features/memory_capture/application/memory_capture_controller.dart';
import '../theme/app_tokens.dart';

class MemoryCaptureChatScreen extends StatefulWidget {
  const MemoryCaptureChatScreen({
    super.key,
    required this.controller,
    this.userEmail,
    this.onLogout,
    this.onResumeOnboarding,
  });

  final MemoryCaptureController controller;
  final String? userEmail;
  final VoidCallback? onLogout;
  final VoidCallback? onResumeOnboarding;

  @override
  State<MemoryCaptureChatScreen> createState() => _MemoryCaptureChatScreenState();
}

class _MemoryCaptureChatScreenState extends State<MemoryCaptureChatScreen> {
  late final TextEditingController _composerController;

  @override
  void initState() {
    super.initState();
    _composerController = TextEditingController();
    widget.controller.addListener(_syncComposerFromController);
  }

  @override
  void dispose() {
    widget.controller.removeListener(_syncComposerFromController);
    _composerController.dispose();
    super.dispose();
  }

  void _syncComposerFromController() {
    if (_composerController.text == widget.controller.composerText) {
      return;
    }
    _composerController.value = TextEditingValue(
      text: widget.controller.composerText,
      selection: TextSelection.collapsed(
        offset: widget.controller.composerText.length,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (BuildContext context, Widget? child) {
        return Scaffold(
          appBar: AppBar(
            title: const Text("Personal AI Assistant"),
            actions: <Widget>[
              if (widget.onResumeOnboarding != null)
                IconButton(
                  key: const Key("resume-onboarding-button"),
                  tooltip: "Resume onboarding",
                  onPressed: widget.onResumeOnboarding,
                  icon: const Icon(Icons.play_circle_outline),
                ),
              if (widget.onLogout != null)
                IconButton(
                  key: const Key("logout-button"),
                  tooltip: "Logout",
                  onPressed: widget.onLogout,
                  icon: const Icon(Icons.logout),
                ),
            ],
          ),
          body: Column(
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  AppSpacing.md,
                  AppSpacing.sm,
                  AppSpacing.md,
                  0,
                ),
                child: Row(
                  children: <Widget>[
                    Expanded(
                      child: Text(
                        "Memory Capture",
                        key: const Key("memory-capture-title"),
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                    ),
                  ],
                ),
              ),
              if (widget.userEmail != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(
                    AppSpacing.md,
                    AppSpacing.xs,
                    AppSpacing.md,
                    0,
                  ),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text("Signed in as ${widget.userEmail}"),
                  ),
                ),
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  AppSpacing.md,
                  AppSpacing.sm,
                  AppSpacing.md,
                  0,
                ),
                child: _AiStateBanner(
                  state: widget.controller.aiState,
                  statusMessage: widget.controller.statusMessage,
                  onRetry: widget.controller.retryableFailure
                      ? () {
                          widget.controller.retryLastAction();
                        }
                      : null,
                  onConfirm:
                      widget.controller.aiState == MemoryCaptureAiState.readyToConfirm
                      ? widget.controller.confirmDraft
                      : null,
                  onModify:
                      widget.controller.aiState == MemoryCaptureAiState.readyToConfirm
                      ? widget.controller.modifyDraft
                      : null,
                  onCancel: widget.controller.aiState == MemoryCaptureAiState.readyToConfirm ||
                          widget.controller.aiState == MemoryCaptureAiState.needsClarification
                      ? widget.controller.cancelDraft
                      : null,
                  onContinueAfterSave:
                      widget.controller.aiState == MemoryCaptureAiState.saved
                          ? widget.controller.resetAfterSaved
                          : null,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              Expanded(
                child: ListView.separated(
                  key: const Key("memory-chat-list"),
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                  itemCount: widget.controller.messages.length,
                  separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
                  itemBuilder: (BuildContext context, int index) {
                    final MemoryChatMessage message =
                        widget.controller.messages[index];
                    final bool isUser = message.author == MemoryMessageAuthor.user;
                    return Align(
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 320),
                        padding: const EdgeInsets.all(AppSpacing.sm),
                        decoration: BoxDecoration(
                          color: isUser ? AppColors.accent : AppColors.surface,
                          borderRadius: BorderRadius.circular(AppRadii.md),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: Text(
                          message.content,
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: isUser ? AppColors.onAccent : AppColors.ink,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              SafeArea(
                top: false,
                child: Container(
                  padding: const EdgeInsets.fromLTRB(
                    AppSpacing.sm,
                    AppSpacing.xs,
                    AppSpacing.sm,
                    AppSpacing.sm,
                  ),
                  decoration: const BoxDecoration(
                    color: AppColors.surface,
                    border: Border(
                      top: BorderSide(color: AppColors.border),
                    ),
                  ),
                  child: Row(
                    children: <Widget>[
                      IconButton(
                        key: const Key("memory-composer-attachment-button"),
                        tooltip: "Attach receipt",
                        onPressed: () {},
                        icon: const Icon(Icons.attach_file),
                      ),
                      IconButton(
                        key: const Key("memory-composer-microphone-button"),
                        tooltip: "Record voice memory",
                        onPressed: () {},
                        icon: const Icon(Icons.mic_none),
                      ),
                      Expanded(
                        child: TextField(
                          key: const Key("memory-composer-text-field"),
                          controller: _composerController,
                          onChanged: widget.controller.updateComposerText,
                          textInputAction: TextInputAction.send,
                          onSubmitted: (_) => widget.controller.submitComposer(),
                          decoration: const InputDecoration(
                            hintText: "Type a memory...",
                          ),
                        ),
                      ),
                      IconButton(
                        key: const Key("memory-composer-send-button"),
                        tooltip: "Send memory",
                        onPressed: widget.controller.canSend
                            ? () async {
                                await widget.controller.submitComposer();
                              }
                            : null,
                        icon: const Icon(Icons.send_rounded),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _AiStateBanner extends StatelessWidget {
  const _AiStateBanner({
    required this.state,
    required this.statusMessage,
    this.onRetry,
    this.onConfirm,
    this.onModify,
    this.onCancel,
    this.onContinueAfterSave,
  });

  final MemoryCaptureAiState state;
  final String statusMessage;
  final VoidCallback? onRetry;
  final VoidCallback? onConfirm;
  final VoidCallback? onModify;
  final VoidCallback? onCancel;
  final VoidCallback? onContinueAfterSave;

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key("memory-ai-state-banner"),
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.sm),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppRadii.md),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            "State: ${state.name}",
            key: const Key("memory-ai-state-text"),
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(statusMessage),
          if (onRetry != null) ...<Widget>[
            const SizedBox(height: AppSpacing.sm),
            OutlinedButton(
              key: const Key("memory-ai-retry-button"),
              onPressed: onRetry,
              child: const Text("Retry"),
            ),
          ],
          if (onConfirm != null || onModify != null || onCancel != null) ...<Widget>[
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              children: <Widget>[
                if (onConfirm != null)
                  OutlinedButton(
                    key: const Key("memory-ai-confirm-button"),
                    onPressed: onConfirm,
                    child: const Text("Confirm"),
                  ),
                if (onModify != null)
                  OutlinedButton(
                    key: const Key("memory-ai-modify-button"),
                    onPressed: onModify,
                    child: const Text("Modify"),
                  ),
                if (onCancel != null)
                  OutlinedButton(
                    key: const Key("memory-ai-cancel-button"),
                    onPressed: onCancel,
                    child: const Text("Cancel"),
                  ),
              ],
            ),
          ],
          if (onContinueAfterSave != null) ...<Widget>[
            const SizedBox(height: AppSpacing.sm),
            OutlinedButton(
              key: const Key("memory-ai-continue-after-save-button"),
              onPressed: onContinueAfterSave,
              child: const Text("Capture another memory"),
            ),
          ],
        ],
      ),
    );
  }
}
