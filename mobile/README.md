# Personal AI Assistant - Mobile

## Architecture bootstrap

The mobile app uses a clean, layered baseline:

- `app/core/state`: application state model and controller
- `app/presentation`: app root composition and screen routing
- `app/features/onboarding`: first-run first-value onboarding flow
- `app/screens`: UI screens
- `app/widgets`: reusable UI components
- `app/theme`: centralized design tokens and theme

State management is fixed to:

- `ChangeNotifier` controller (`AppStateController`)
- `InheritedNotifier` scope (`AppStateScope`) for dependency access in the widget tree
- Auth state controller (`AuthController`) backed by Supabase Auth repository

## Supabase Auth setup

Run the app with Supabase credentials through dart defines:

```bash
flutter run \
  --dart-define=API_BASE_URL=http://127.0.0.1:8000 \
  --dart-define=SUPABASE_URL=http://127.0.0.1:54321 \
  --dart-define=SUPABASE_ANON_KEY=replace_me
```

## Local checks

```bash
flutter pub get
flutter analyze
flutter test
```
