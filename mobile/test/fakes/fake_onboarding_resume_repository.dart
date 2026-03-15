import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/onboarding_resume_point.dart';
import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/onboarding_resume_repository.dart';

class FakeOnboardingResumeRepository implements OnboardingResumeRepository {
  final Map<String, OnboardingResumePoint> _resumePointByUserId =
      <String, OnboardingResumePoint>{};

  OnboardingResumePoint? resumePointForUser(String userId) =>
      _resumePointByUserId[userId];

  void setResumePointForUser(String userId, OnboardingResumePoint resumePoint) {
    _resumePointByUserId[userId] = resumePoint;
  }

  @override
  Future<OnboardingResumePoint?> getResumePoint(String userId) async {
    return _resumePointByUserId[userId];
  }

  @override
  Future<void> persistResumePoint({
    required String userId,
    required OnboardingResumePoint resumePoint,
  }) async {
    _resumePointByUserId[userId] = resumePoint;
  }

  @override
  Future<void> clearResumePoint(String userId) async {
    _resumePointByUserId.remove(userId);
  }
}
