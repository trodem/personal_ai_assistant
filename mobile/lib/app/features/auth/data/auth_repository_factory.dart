import 'package:supabase_flutter/supabase_flutter.dart';

import '../../../core/config/supabase_config.dart';
import '../domain/auth_repository.dart';
import 'supabase_auth_repository.dart';
import 'unconfigured_auth_repository.dart';

class AuthRepositoryFactory {
  static bool _initialized = false;

  static Future<AuthRepository> create() async {
    const SupabaseConfig config = SupabaseConfig.fromEnvironment;
    if (!config.isConfigured) {
      return UnconfiguredAuthRepository();
    }
    if (!_initialized) {
      await Supabase.initialize(
        url: config.url,
        anonKey: config.anonKey,
      );
      _initialized = true;
    }
    return SupabaseAuthRepository(Supabase.instance.client);
  }
}
