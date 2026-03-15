import 'package:flutter/foundation.dart';

import '../domain/language_preferences_repository.dart';
import '../domain/preferred_language.dart';

class OnboardingController extends ChangeNotifier {
  OnboardingController({
    bool completed = false,
    required LanguagePreferencesRepository languagePreferencesRepository,
  }) : _completed = completed,
       _languagePreferencesRepository = languagePreferencesRepository;

  bool _completed;
  bool get completed => _completed;

  final LanguagePreferencesRepository _languagePreferencesRepository;

  bool _welcomeStepDone = false;
  bool get welcomeStepDone => _welcomeStepDone;

  bool _languageStepDone = false;
  bool get languageStepDone => _languageStepDone;

  PreferredLanguage _selectedLanguage = PreferredLanguage.en;
  PreferredLanguage get selectedLanguage => _selectedLanguage;

  bool _isSavingLanguage = false;
  bool get isSavingLanguage => _isSavingLanguage;

  String? _languageError;
  String? get languageError => _languageError;

  bool _firstMemoryDone = false;
  bool get firstMemoryDone => _firstMemoryDone;

  bool _firstQuestionDone = false;
  bool get firstQuestionDone => _firstQuestionDone;

  bool get canFinish => _firstMemoryDone && _firstQuestionDone;

  void completeWelcomeStep() {
    if (_welcomeStepDone) {
      return;
    }
    _welcomeStepDone = true;
    notifyListeners();
  }

  void selectLanguage(PreferredLanguage language) {
    if (_selectedLanguage == language) {
      return;
    }
    _selectedLanguage = language;
    notifyListeners();
  }

  Future<void> persistLanguageStep() async {
    _isSavingLanguage = true;
    _languageError = null;
    notifyListeners();

    try {
      await _languagePreferencesRepository.persistPreferredLanguage(
        _selectedLanguage,
      );
      _languageStepDone = true;
    } catch (error) {
      _languageError = error.toString();
    } finally {
      _isSavingLanguage = false;
      notifyListeners();
    }
  }

  void completeFirstMemory() {
    if (_firstMemoryDone) {
      return;
    }
    _firstMemoryDone = true;
    notifyListeners();
  }

  void completeFirstQuestion() {
    if (_firstQuestionDone) {
      return;
    }
    _firstQuestionDone = true;
    notifyListeners();
  }

  void finish() {
    if (!canFinish || _completed) {
      return;
    }
    _completed = true;
    notifyListeners();
  }

  void reset() {
    _completed = false;
    _welcomeStepDone = false;
    _languageStepDone = false;
    _selectedLanguage = PreferredLanguage.en;
    _isSavingLanguage = false;
    _languageError = null;
    _firstMemoryDone = false;
    _firstQuestionDone = false;
    notifyListeners();
  }
}
