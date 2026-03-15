import 'package:flutter/widgets.dart';

import 'app_state_controller.dart';

class AppStateScope extends InheritedNotifier<AppStateController> {
  const AppStateScope({
    super.key,
    required AppStateController controller,
    required super.child,
  }) : super(notifier: controller);

  static AppStateController of(BuildContext context) {
    final AppStateScope? scope =
        context.dependOnInheritedWidgetOfExactType<AppStateScope>();
    assert(scope != null, "AppStateScope is missing in the widget tree.");
    return scope!.notifier!;
  }
}
