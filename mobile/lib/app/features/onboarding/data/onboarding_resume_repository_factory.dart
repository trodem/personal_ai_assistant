import '../domain/onboarding_resume_repository.dart';
import 'in_memory_onboarding_resume_repository.dart';
import 'shared_preferences_onboarding_resume_repository.dart';

class OnboardingResumeRepositoryFactory {
  static OnboardingResumeRepository create() {
    try {
      return SharedPreferencesOnboardingResumeRepository();
    } catch (_) {
      return InMemoryOnboardingResumeRepository();
    }
  }
}
