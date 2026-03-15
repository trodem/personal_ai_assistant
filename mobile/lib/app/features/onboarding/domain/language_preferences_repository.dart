import 'preferred_language.dart';

abstract class LanguagePreferencesRepository {
  Future<void> persistPreferredLanguage(PreferredLanguage language);
}
