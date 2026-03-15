enum OnboardingResumePoint {
  welcome,
  language,
  permissions,
  firstValue,
}

extension OnboardingResumePointCodec on OnboardingResumePoint {
  String get storageValue {
    switch (this) {
      case OnboardingResumePoint.welcome:
        return "welcome";
      case OnboardingResumePoint.language:
        return "language";
      case OnboardingResumePoint.permissions:
        return "permissions";
      case OnboardingResumePoint.firstValue:
        return "first_value";
    }
  }

  static OnboardingResumePoint? fromStorageValue(String value) {
    switch (value) {
      case "welcome":
        return OnboardingResumePoint.welcome;
      case "language":
        return OnboardingResumePoint.language;
      case "permissions":
        return OnboardingResumePoint.permissions;
      case "first_value":
        return OnboardingResumePoint.firstValue;
      default:
        return null;
    }
  }
}
