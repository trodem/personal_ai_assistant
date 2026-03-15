import '../domain/onboarding_completion_repository.dart';
import 'in_memory_onboarding_completion_repository.dart';
import 'shared_preferences_onboarding_completion_repository.dart';

class OnboardingCompletionRepositoryFactory {
  static OnboardingCompletionRepository create() {
    try {
      return SharedPreferencesOnboardingCompletionRepository();
    } catch (_) {
      return InMemoryOnboardingCompletionRepository();
    }
  }
}
