import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_ai_assistant_mobile/main.dart';

void main() {
  testWidgets("app boots with themed preview screen", (WidgetTester tester) async {
    await tester.pumpWidget(const PersonalAIAssistantApp());

    expect(find.text("Personal AI Assistant"), findsOneWidget);
    expect(find.text("Design System Baseline"), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);

    final MaterialApp appWidget = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(appWidget.theme?.scaffoldBackgroundColor, isNotNull);
  });
}
