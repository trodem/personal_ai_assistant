import 'package:flutter/foundation.dart';

enum AppScreen {
  themePreview,
}

@immutable
class AppState {
  const AppState({
    required this.screen,
  });

  final AppScreen screen;

  AppState copyWith({
    AppScreen? screen,
  }) {
    return AppState(
      screen: screen ?? this.screen,
    );
  }

  static const AppState initial = AppState(screen: AppScreen.themePreview);
}
