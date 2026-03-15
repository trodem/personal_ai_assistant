abstract class OnboardingCompletionRepository {
  Future<DateTime?> getOnboardingCompletedAt(String userId);

  Future<void> persistOnboardingCompletedAt({
    required String userId,
    required DateTime completedAt,
  });
}
