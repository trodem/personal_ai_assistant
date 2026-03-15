import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/features/memory_capture/application/memory_capture_controller.dart';

void main() {
  test("controller starts in idle state", () {
    final MemoryCaptureController controller = MemoryCaptureController();

    expect(controller.aiState, MemoryCaptureAiState.idle);
    expect(controller.canSend, isFalse);
  });

  test("submit non-ambiguous memory reaches ready_to_confirm", () async {
    final MemoryCaptureController controller = MemoryCaptureController();

    controller.updateComposerText("I bought bread for 3 CHF at Coop");
    await controller.submitComposer();

    expect(controller.aiState, MemoryCaptureAiState.readyToConfirm);
  });

  test("submit ambiguous memory reaches needs_clarification then ready_to_confirm", () async {
    final MemoryCaptureController controller = MemoryCaptureController();

    controller.updateComposerText("I bought bread");
    await controller.submitComposer();
    expect(controller.aiState, MemoryCaptureAiState.needsClarification);

    controller.updateComposerText("3 CHF");
    await controller.submitComposer();
    expect(controller.aiState, MemoryCaptureAiState.readyToConfirm);
  });

  test("confirm from ready_to_confirm reaches saved", () async {
    final MemoryCaptureController controller = MemoryCaptureController();

    controller.updateComposerText("I bought bread for 3 CHF at Coop");
    await controller.submitComposer();
    controller.confirmDraft();

    expect(controller.aiState, MemoryCaptureAiState.saved);
  });

  test("failed extraction supports retry and returns ready_to_confirm", () async {
    final MemoryCaptureController controller = MemoryCaptureController();

    controller.updateComposerText("error while parsing this memory");
    await controller.submitComposer();
    expect(controller.aiState, MemoryCaptureAiState.failed);
    expect(controller.retryableFailure, isTrue);

    await controller.retryLastAction();
    expect(controller.aiState, MemoryCaptureAiState.readyToConfirm);
  });
}
