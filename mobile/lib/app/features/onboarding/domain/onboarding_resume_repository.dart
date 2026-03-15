import 'onboarding_resume_point.dart';

abstract class OnboardingResumeRepository {
  Future<OnboardingResumePoint?> getResumePoint(String userId);

  Future<void> persistResumePoint({
    required String userId,
    required OnboardingResumePoint resumePoint,
  });

  Future<void> clearResumePoint(String userId);
}
