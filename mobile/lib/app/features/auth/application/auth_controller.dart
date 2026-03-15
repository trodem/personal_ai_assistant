import 'package:flutter/foundation.dart';

import '../domain/auth_repository.dart';
import '../domain/auth_user.dart';

enum AuthStatus {
  loading,
  authenticated,
  unauthenticated,
}

class AuthController extends ChangeNotifier {
  AuthController({
    required AuthRepository repository,
  }) : _repository = repository;

  final AuthRepository _repository;

  AuthStatus _status = AuthStatus.loading;
  AuthStatus get status => _status;

  AuthUser? _user;
  AuthUser? get user => _user;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Future<void> loadSession() async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      _user = await _repository.currentUser();
      _status =
          _user == null ? AuthStatus.unauthenticated : AuthStatus.authenticated;
    } catch (error) {
      _errorMessage = error.toString();
      _status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }

  Future<void> signIn({
    required String email,
    required String password,
  }) async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      _user = await _repository.signInWithPassword(
        email: email,
        password: password,
      );
      _status = AuthStatus.authenticated;
    } catch (error) {
      _user = null;
      _errorMessage = error.toString();
      _status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }

  Future<void> signOut() async {
    await _repository.signOut();
    _user = null;
    _errorMessage = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }
}
