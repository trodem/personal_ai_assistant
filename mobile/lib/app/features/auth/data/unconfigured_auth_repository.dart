import '../domain/auth_repository.dart';
import '../domain/auth_user.dart';

class UnconfiguredAuthRepository implements AuthRepository {
  static const String message =
      "Supabase Auth is not configured. Provide SUPABASE_URL and SUPABASE_ANON_KEY via --dart-define.";

  @override
  Future<AuthUser?> currentUser() async {
    return null;
  }

  @override
  Future<AuthUser> signInWithPassword({
    required String email,
    required String password,
  }) async {
    throw StateError(message);
  }

  @override
  Future<void> signOut() async {}
}
