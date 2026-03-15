# Personal AI Assistant - Mobile

## Architecture bootstrap

The mobile app uses a clean, layered baseline:

- `app/core/state`: application state model and controller
- `app/presentation`: app root composition and screen routing
- `app/screens`: UI screens
- `app/widgets`: reusable UI components
- `app/theme`: centralized design tokens and theme

State management is fixed to:

- `ChangeNotifier` controller (`AppStateController`)
- `InheritedNotifier` scope (`AppStateScope`) for dependency access in the widget tree

## Local checks

```bash
flutter pub get
flutter analyze
flutter test
```
