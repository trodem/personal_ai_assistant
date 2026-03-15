import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/language_preferences_repository.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/preferred_language.dart';

class FakeLanguagePreferencesRepository implements LanguagePreferencesRepository {
  PreferredLanguage? lastSaved;

  @override
  Future<void> persistPreferredLanguage(PreferredLanguage language) async {
    lastSaved = language;
  }
}
