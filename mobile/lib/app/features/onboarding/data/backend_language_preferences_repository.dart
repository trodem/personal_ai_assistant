import 'dart:convert';
import 'dart:io';

import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../core/config/api_config.dart';
import '../domain/language_preferences_repository.dart';
import '../domain/preferred_language.dart';

class BackendLanguagePreferencesRepository
    implements LanguagePreferencesRepository {
  BackendLanguagePreferencesRepository({
    required ApiConfig apiConfig,
    required SupabaseClient supabaseClient,
  }) : _apiConfig = apiConfig,
       _supabaseClient = supabaseClient;

  final ApiConfig _apiConfig;
  final SupabaseClient _supabaseClient;

  @override
  Future<void> persistPreferredLanguage(PreferredLanguage language) async {
    if (!_apiConfig.isConfigured) {
      throw StateError("API_BASE_URL is not configured.");
    }

    final String? accessToken = _supabaseClient.auth.currentSession?.accessToken;
    if (accessToken == null || accessToken.isEmpty) {
      throw StateError("Missing auth session token.");
    }

    final HttpClient client = HttpClient();
    try {
      final Uri endpoint = Uri.parse(
        "${_apiConfig.baseUrl}/api/v1/me/settings/profile",
      );
      final HttpClientRequest request = await client.patchUrl(endpoint);
      request.headers.set(HttpHeaders.contentTypeHeader, "application/json");
      request.headers.set(HttpHeaders.authorizationHeader, "Bearer $accessToken");
      request.write(
        jsonEncode(<String, String>{
          "preferred_language": language.code,
        }),
      );

      final HttpClientResponse response = await request.close();
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw StateError(
          "Unable to persist preferred language. status=${response.statusCode}",
        );
      }
    } finally {
      client.close();
    }
  }
}
