import '../domain/language_preferences_repository.dart';
import '../domain/preferred_language.dart';

class InMemoryLanguagePreferencesRepository
    implements LanguagePreferencesRepository {
  PreferredLanguage? lastSaved;

  @override
  Future<void> persistPreferredLanguage(PreferredLanguage language) async {
    lastSaved = language;
  }
}
