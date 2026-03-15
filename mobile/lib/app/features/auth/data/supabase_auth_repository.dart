import 'package:supabase_flutter/supabase_flutter.dart';

import '../domain/auth_repository.dart';
import '../domain/auth_user.dart' as domain;

class SupabaseAuthRepository implements AuthRepository {
  SupabaseAuthRepository(this._client);

  final SupabaseClient _client;

  @override
  Future<domain.AuthUser?> currentUser() async {
    final User? user = _client.auth.currentUser;
    if (user == null) {
      return null;
    }
    return domain.AuthUser(id: user.id, email: user.email);
  }

  @override
  Future<domain.AuthUser> signInWithPassword({
    required String email,
    required String password,
  }) async {
    final AuthResponse response = await _client.auth.signInWithPassword(
      email: email,
      password: password,
    );
    final User? user = response.user;
    if (user == null) {
      throw StateError("Supabase sign-in returned no user.");
    }
    return domain.AuthUser(id: user.id, email: user.email);
  }

  @override
  Future<void> signOut() {
    return _client.auth.signOut();
  }
}
