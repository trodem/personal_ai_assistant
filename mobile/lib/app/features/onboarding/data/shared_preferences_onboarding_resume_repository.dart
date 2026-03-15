import 'package:shared_preferences/shared_preferences.dart';

import '../domain/onboarding_resume_point.dart';
import '../domain/onboarding_resume_repository.dart';

class SharedPreferencesOnboardingResumeRepository
    implements OnboardingResumeRepository {
  static const String _storagePrefix = "onboarding_resume_point";

  String _storageKey(String userId) => "${_storagePrefix}_$userId";

  @override
  Future<OnboardingResumePoint?> getResumePoint(String userId) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    final String? rawValue = preferences.getString(_storageKey(userId));
    if (rawValue == null || rawValue.isEmpty) {
      return null;
    }
    return OnboardingResumePointCodec.fromStorageValue(rawValue);
  }

  @override
  Future<void> persistResumePoint({
    required String userId,
    required OnboardingResumePoint resumePoint,
  }) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    await preferences.setString(_storageKey(userId), resumePoint.storageValue);
  }

  @override
  Future<void> clearResumePoint(String userId) async {
    final SharedPreferences preferences = await SharedPreferences.getInstance();
    await preferences.remove(_storageKey(userId));
  }
}
