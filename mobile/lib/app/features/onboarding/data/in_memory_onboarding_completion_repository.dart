import '../domain/onboarding_completion_repository.dart';

class InMemoryOnboardingCompletionRepository
    implements OnboardingCompletionRepository {
  final Map<String, DateTime> _completedAtByUserId = <String, DateTime>{};

  @override
  Future<DateTime?> getOnboardingCompletedAt(String userId) async {
    return _completedAtByUserId[userId];
  }

  @override
  Future<void> persistOnboardingCompletedAt({
    required String userId,
    required DateTime completedAt,
  }) async {
    _completedAtByUserId[userId] = completedAt;
  }
}
