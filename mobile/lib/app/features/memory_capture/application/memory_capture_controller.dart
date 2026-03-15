import 'package:flutter/foundation.dart';

enum MemoryCaptureAiState {
  idle,
  processing,
  needsClarification,
  readyToConfirm,
  saved,
  failed,
}

enum MemoryMessageAuthor { user, assistant }

@immutable
class MemoryChatMessage {
  const MemoryChatMessage({
    required this.content,
    required this.author,
  });

  final String content;
  final MemoryMessageAuthor author;
}

class MemoryCaptureController extends ChangeNotifier {
  final List<MemoryChatMessage> _messages = <MemoryChatMessage>[
    const MemoryChatMessage(
      content:
          "Start by writing or speaking a memory. I will extract a proposal for your confirmation.",
      author: MemoryMessageAuthor.assistant,
    ),
  ];

  List<MemoryChatMessage> get messages => List<MemoryChatMessage>.unmodifiable(_messages);

  MemoryCaptureAiState _aiState = MemoryCaptureAiState.idle;
  MemoryCaptureAiState get aiState => _aiState;

  String _composerText = "";
  String get composerText => _composerText;

  String _statusMessage = "Idle. Add a memory with text or voice.";
  String get statusMessage => _statusMessage;

  bool _retryableFailure = false;
  bool get retryableFailure => _retryableFailure;

  bool get canSend => _composerText.trim().isNotEmpty && _aiState != MemoryCaptureAiState.processing;

  Future<void> submitComposer() async {
    if (!canSend) {
      return;
    }
    if (_aiState == MemoryCaptureAiState.needsClarification) {
      final String answer = _composerText;
      _composerText = "";
      notifyListeners();
      await submitClarification(answer);
      return;
    }
    await submitTextMemory();
  }

  void updateComposerText(String value) {
    _composerText = value;
    notifyListeners();
  }

  Future<void> submitTextMemory() async {
    final String payload = _composerText.trim();
    if (payload.isEmpty || _aiState == MemoryCaptureAiState.processing) {
      return;
    }
    _messages.add(MemoryChatMessage(content: payload, author: MemoryMessageAuthor.user));
    _composerText = "";
    notifyListeners();
    _setState(MemoryCaptureAiState.processing, "Processing memory extraction...");
    await Future<void>.delayed(const Duration(milliseconds: 100));

    final String lowered = payload.toLowerCase();
    if (lowered.contains("fail") || lowered.contains("error")) {
      _messages.add(
        const MemoryChatMessage(
          content:
              "Temporary extraction failure. Retry or edit your memory text.",
          author: MemoryMessageAuthor.assistant,
        ),
      );
      _retryableFailure = true;
      _setState(MemoryCaptureAiState.failed, "Failed. Retry is available.");
      return;
    }

    if (_looksAmbiguous(payload)) {
      _messages.add(
        const MemoryChatMessage(
          content: "Clarification needed: what amount or quantity should I save?",
          author: MemoryMessageAuthor.assistant,
        ),
      );
      _retryableFailure = false;
      _setState(
        MemoryCaptureAiState.needsClarification,
        "Needs clarification. One missing field is required.",
      );
      return;
    }

    _messages.add(
      const MemoryChatMessage(
        content: "Draft ready. Review and confirm to save this memory.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _retryableFailure = false;
    _setState(
      MemoryCaptureAiState.readyToConfirm,
      "Ready to confirm. Use Confirm, Modify, or Cancel.",
    );
  }

  Future<void> retryLastAction() async {
    if (!_retryableFailure || _aiState != MemoryCaptureAiState.failed) {
      return;
    }
    _setState(MemoryCaptureAiState.processing, "Retrying extraction...");
    await Future<void>.delayed(const Duration(milliseconds: 100));
    _messages.add(
      const MemoryChatMessage(
        content: "Retry successful. Draft is ready for confirmation.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _retryableFailure = false;
    _setState(
      MemoryCaptureAiState.readyToConfirm,
      "Ready to confirm. Use Confirm, Modify, or Cancel.",
    );
  }

  Future<void> submitClarification(String answer) async {
    if (_aiState != MemoryCaptureAiState.needsClarification) {
      return;
    }
    final String trimmed = answer.trim();
    if (trimmed.isEmpty) {
      return;
    }
    _messages.add(MemoryChatMessage(content: trimmed, author: MemoryMessageAuthor.user));
    _setState(MemoryCaptureAiState.processing, "Processing clarification...");
    await Future<void>.delayed(const Duration(milliseconds: 100));
    _messages.add(
      const MemoryChatMessage(
        content: "Clarification received. Draft is ready for confirmation.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _setState(
      MemoryCaptureAiState.readyToConfirm,
      "Ready to confirm. Use Confirm, Modify, or Cancel.",
    );
  }

  void confirmDraft() {
    if (_aiState != MemoryCaptureAiState.readyToConfirm) {
      return;
    }
    _messages.add(
      const MemoryChatMessage(
        content: "Memory saved successfully.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _setState(MemoryCaptureAiState.saved, "Saved.");
  }

  void modifyDraft() {
    if (_aiState != MemoryCaptureAiState.readyToConfirm) {
      return;
    }
    _messages.add(
      const MemoryChatMessage(
        content: "Modify selected. Update your message and send again.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _setState(MemoryCaptureAiState.idle, "Idle. Draft reset for modification.");
  }

  void cancelDraft() {
    if (_aiState != MemoryCaptureAiState.readyToConfirm &&
        _aiState != MemoryCaptureAiState.needsClarification) {
      return;
    }
    _messages.add(
      const MemoryChatMessage(
        content: "Draft canceled. Nothing was saved.",
        author: MemoryMessageAuthor.assistant,
      ),
    );
    _setState(MemoryCaptureAiState.idle, "Idle. Add a new memory.");
  }

  void resetAfterSaved() {
    if (_aiState != MemoryCaptureAiState.saved) {
      return;
    }
    _setState(MemoryCaptureAiState.idle, "Idle. Add another memory.");
  }

  bool _looksAmbiguous(String payload) {
    final String lowered = payload.toLowerCase();
    final bool hasAmount = RegExp(r"\d").hasMatch(lowered);
    final bool hasExpenseSignal =
        lowered.contains("chf") || lowered.contains("eur") || lowered.contains("usd");
    return !hasAmount && !hasExpenseSignal;
  }

  void _setState(MemoryCaptureAiState state, String statusMessage) {
    _aiState = state;
    _statusMessage = statusMessage;
    notifyListeners();
  }
}
