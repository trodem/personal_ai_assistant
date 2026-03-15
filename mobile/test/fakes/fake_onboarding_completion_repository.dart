import 'package:personal_ai_assistant_mobile/app/features/onboarding/domain/onboarding_completion_repository.dart';

class FakeOnboardingCompletionRepository
    implements OnboardingCompletionRepository {
  final Map<String, DateTime> _completedAtByUserId = <String, DateTime>{};

  DateTime? completedAtForUser(String userId) => _completedAtByUserId[userId];

  void setCompletedAtForUser(String userId, DateTime completedAt) {
    _completedAtByUserId[userId] = completedAt;
  }

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
