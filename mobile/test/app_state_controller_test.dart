import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';

void main() {
  test('AppStateController starts with themePreview screen', () {
    final AppStateController controller = AppStateController();

    expect(controller.state.screen, AppScreen.themePreview);
  });

  test('AppStateController does not notify when screen does not change', () {
    final AppStateController controller = AppStateController();
    var notifyCount = 0;
    controller.addListener(() => notifyCount++);

    controller.setScreen(AppScreen.themePreview);

    expect(notifyCount, 0);
  });
}
