import 'package:personal_ai_assistant_mobile/app/features/auth/domain/auth_repository.dart';
import 'package:personal_ai_assistant_mobile/app/features/auth/domain/auth_user.dart';

class FakeAuthRepository implements AuthRepository {
  FakeAuthRepository({
    AuthUser? currentUser,
  }) : _currentUser = currentUser;

  AuthUser? _currentUser;

  @override
  Future<AuthUser?> currentUser() async => _currentUser;

  @override
  Future<AuthUser> signInWithPassword({
    required String email,
    required String password,
  }) async {
    _currentUser = AuthUser(id: "test-user", email: email);
    return _currentUser!;
  }

  @override
  Future<void> signOut() async {
    _currentUser = null;
  }
}
