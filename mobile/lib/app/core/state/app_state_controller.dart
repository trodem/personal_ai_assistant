import 'package:flutter/foundation.dart';

import 'app_state.dart';

class AppStateController extends ChangeNotifier {
  AppStateController({
    AppState initialState = AppState.initial,
  }) : _state = initialState;

  AppState _state;

  AppState get state => _state;

  void setScreen(AppScreen screen) {
    if (_state.screen == screen) {
      return;
    }
    _state = _state.copyWith(screen: screen);
    notifyListeners();
  }
}
