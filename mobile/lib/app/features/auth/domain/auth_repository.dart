import 'auth_user.dart';

abstract class AuthRepository {
  Future<AuthUser?> currentUser();

  Future<AuthUser> signInWithPassword({
    required String email,
    required String password,
  });

  Future<void> signOut();
}
