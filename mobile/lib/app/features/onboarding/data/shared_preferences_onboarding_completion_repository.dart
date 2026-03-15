import 'package:shared_preferences/shared_preferences.dart';

import '../domain/onboarding_completion_repository.dart';

class SharedPreferencesOnboardingCompletionRepository
    implements OnboardingCompletionRepository {
  static const String _storagePrefix = "onboarding_completed_at";

  String _storageKey(String userId) => "${_storagePrefix}_$userId";

  @override
  Future<DateTime?> getOnboardingCompletedAt(String userId) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    final String? rawValue = preferences.getString(_storageKey(userId));
    if (rawValue == null || rawValue.isEmpty) {
      return null;
    }
    return DateTime.tryParse(rawValue);
  }

  @override
  Future<void> persistOnboardingCompletedAt({
    required String userId,
    required DateTime completedAt,
  }) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    await preferences.setString(_storageKey(userId), completedAt.toUtc().toIso8601String());
  }
}
