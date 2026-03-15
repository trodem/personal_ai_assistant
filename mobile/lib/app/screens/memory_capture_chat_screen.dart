import 'package:flutter/material.dart';

import '../theme/app_tokens.dart';

class MemoryCaptureChatScreen extends StatefulWidget {
  const MemoryCaptureChatScreen({
    super.key,
    this.userEmail,
    this.onLogout,
    this.onResumeOnboarding,
  });

  final String? userEmail;
  final VoidCallback? onLogout;
  final VoidCallback? onResumeOnboarding;

  @override
  State<MemoryCaptureChatScreen> createState() =>
      _MemoryCaptureChatScreenState();
}

class _MemoryCaptureChatScreenState extends State<MemoryCaptureChatScreen> {
  final TextEditingController _composerController = TextEditingController();
  final List<_ChatMessage> _messages = <_ChatMessage>[
    const _ChatMessage(
      content:
          "Start by writing or speaking a memory. I will extract a proposal for your confirmation.",
      author: _ChatAuthor.assistant,
    ),
  ];

  @override
  void dispose() {
    _composerController.dispose();
    super.dispose();
  }

  void _sendTextMemory() {
    final String value = _composerController.text.trim();
    if (value.isEmpty) {
      return;
    }
    setState(() {
      _messages.add(_ChatMessage(content: value, author: _ChatAuthor.user));
      _messages.add(
        const _ChatMessage(
          content:
              "Memory draft captured. Confirmation flow will follow in the next task.",
          author: _ChatAuthor.assistant,
        ),
      );
      _composerController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
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
          const SizedBox(height: AppSpacing.sm),
          Expanded(
            child: ListView.separated(
              key: const Key("memory-chat-list"),
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
              itemCount: _messages.length,
              separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
              itemBuilder: (BuildContext context, int index) {
                final _ChatMessage message = _messages[index];
                final bool isUser = message.author == _ChatAuthor.user;
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
                      style: TextStyle(
                        color: isUser ? Colors.white : AppColors.ink,
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
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendTextMemory(),
                      decoration: const InputDecoration(
                        hintText: "Type a memory...",
                      ),
                    ),
                  ),
                  IconButton(
                    key: const Key("memory-composer-send-button"),
                    tooltip: "Send memory",
                    onPressed: _sendTextMemory,
                    icon: const Icon(Icons.send_rounded),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

enum _ChatAuthor { user, assistant }

class _ChatMessage {
  const _ChatMessage({
    required this.content,
    required this.author,
  });

  final String content;
  final _ChatAuthor author;
}
