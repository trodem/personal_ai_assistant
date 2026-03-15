import '../domain/onboarding_resume_point.dart';
import '../domain/onboarding_resume_repository.dart';

class InMemoryOnboardingResumeRepository implements OnboardingResumeRepository {
  final Map<String, OnboardingResumePoint> _resumePointsByUserId =
      <String, OnboardingResumePoint>{};

  @override
  Future<OnboardingResumePoint?> getResumePoint(String userId) async {
    return _resumePointsByUserId[userId];
  }

  @override
  Future<void> persistResumePoint({
    required String userId,
    required OnboardingResumePoint resumePoint,
  }) async {
    _resumePointsByUserId[userId] = resumePoint;
  }

  @override
  Future<void> clearResumePoint(String userId) async {
    _resumePointsByUserId.remove(userId);
  }
}
