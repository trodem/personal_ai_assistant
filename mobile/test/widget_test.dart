import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/app/core/state/app_state_controller.dart';

import 'package:personal_ai_assistant_mobile/main.dart';

void main() {
  testWidgets('App renders baseline title', (WidgetTester tester) async {
    await tester.pumpWidget(
      PersonalAIAssistantApp(
        controller: AppStateController(),
      ),
    );

    expect(find.text('Personal AI Assistant'), findsOneWidget);
  });
}
