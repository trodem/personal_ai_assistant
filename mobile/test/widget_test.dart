import 'package:flutter_test/flutter_test.dart';

import 'package:personal_ai_assistant_mobile/main.dart';

void main() {
  testWidgets('App renders baseline title', (WidgetTester tester) async {
    await tester.pumpWidget(const PersonalAIAssistantApp());

    expect(find.text('Personal AI Assistant'), findsOneWidget);
  });
}
