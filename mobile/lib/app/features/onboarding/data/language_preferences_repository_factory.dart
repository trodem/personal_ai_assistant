import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../core/config/api_config.dart';
import '../domain/language_preferences_repository.dart';
import 'backend_language_preferences_repository.dart';
import 'in_memory_language_preferences_repository.dart';

class LanguagePreferencesRepositoryFactory {
  static LanguagePreferencesRepository create() {
    const ApiConfig config = ApiConfig.fromEnvironment;
    if (!config.isConfigured) {
      return InMemoryLanguagePreferencesRepository();
    }
    return BackendLanguagePreferencesRepository(
      apiConfig: config,
      supabaseClient: Supabase.instance.client,
    );
  }
}
