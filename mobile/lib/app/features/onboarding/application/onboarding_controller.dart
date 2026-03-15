import 'package:flutter/foundation.dart';

import '../domain/device_permissions_gateway.dart';
import '../domain/language_preferences_repository.dart';
import '../domain/onboarding_completion_repository.dart';
import '../domain/preferred_language.dart';

class OnboardingController extends ChangeNotifier {
  OnboardingController({
    bool completed = false,
    required LanguagePreferencesRepository languagePreferencesRepository,
    required DevicePermissionsGateway devicePermissionsGateway,
    required OnboardingCompletionRepository onboardingCompletionRepository,
  }) : _completed = completed,
       _languagePreferencesRepository = languagePreferencesRepository,
       _devicePermissionsGateway = devicePermissionsGateway,
       _onboardingCompletionRepository = onboardingCompletionRepository;

  bool _completed;
  bool get completed => _completed;

  final LanguagePreferencesRepository _languagePreferencesRepository;
  final DevicePermissionsGateway _devicePermissionsGateway;
  final OnboardingCompletionRepository _onboardingCompletionRepository;

  String? _hydratedUserId;
  String? _hydratingUserId;
  bool _isHydratingCompletion = false;
  bool get isHydratingCompletion => _isHydratingCompletion;

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

  bool _permissionsStepDone = false;
  bool get permissionsStepDone => _permissionsStepDone;

  bool _microphoneGranted = false;
  bool get microphoneGranted => _microphoneGranted;

  bool _cameraGranted = false;
  bool get cameraGranted => _cameraGranted;

  String? _permissionsError;
  String? get permissionsError => _permissionsError;

  bool _firstMemoryDone = false;
  bool get firstMemoryDone => _firstMemoryDone;

  String _firstMemoryDraft = "";
  String get firstMemoryDraft => _firstMemoryDraft;

  bool _firstMemoryProposalReady = false;
  bool get firstMemoryProposalReady => _firstMemoryProposalReady;

  String? _firstMemoryError;
  String? get firstMemoryError => _firstMemoryError;

  bool _firstQuestionDone = false;
  bool get firstQuestionDone => _firstQuestionDone;

  String _firstQuestionDraft = "";
  String get firstQuestionDraft => _firstQuestionDraft;

  String _firstQuestionAnswer = "";
  String get firstQuestionAnswer => _firstQuestionAnswer;

  String _firstQuestionConfidence = "medium";
  String get firstQuestionConfidence => _firstQuestionConfidence;

  List<String> _firstQuestionSourceIds = const <String>[];
  List<String> get firstQuestionSourceIds => _firstQuestionSourceIds;

  bool _firstQuestionAnswerReady = false;
  bool get firstQuestionAnswerReady => _firstQuestionAnswerReady;

  bool _firstQuestionWhyExpanded = false;
  bool get firstQuestionWhyExpanded => _firstQuestionWhyExpanded;

  String? _firstQuestionError;
  String? get firstQuestionError => _firstQuestionError;

  bool get canFinish => _firstMemoryDone && _firstQuestionDone;

  Future<void> hydrateCompletionForUser(String? userId) async {
    if (userId == null || userId.isEmpty) {
      _clearHydrationState();
      return;
    }
    if (_hydratedUserId == userId || _hydratingUserId == userId) {
      return;
    }

    _isHydratingCompletion = true;
    _hydratingUserId = userId;
    _completed = false;
    notifyListeners();

    final DateTime? completedAt = await _onboardingCompletionRepository
        .getOnboardingCompletedAt(userId);

    if (_hydratingUserId != userId) {
      return;
    }

    _hydratedUserId = userId;
    _hydratingUserId = null;
    _isHydratingCompletion = false;
    _completed = completedAt != null;
    notifyListeners();
  }

  void _clearHydrationState() {
    final bool shouldNotify = _hydratedUserId != null || _completed || _isHydratingCompletion;
    _hydratedUserId = null;
    _hydratingUserId = null;
    _isHydratingCompletion = false;
    _completed = false;
    if (shouldNotify) {
      notifyListeners();
    }
  }

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

  Future<void> requestMicrophonePermission() async {
    _permissionsError = null;
    final bool granted = await _devicePermissionsGateway.request(
      AppPermission.microphone,
    );
    _microphoneGranted = granted;
    if (!granted) {
      _permissionsError =
          "Microphone permission is required to continue onboarding.";
    }
    notifyListeners();
  }

  Future<void> requestCameraPermission() async {
    _permissionsError = null;
    _cameraGranted = await _devicePermissionsGateway.request(
      AppPermission.camera,
    );
    notifyListeners();
  }

  void completePermissionsStep() {
    _permissionsError = null;
    if (!_microphoneGranted) {
      _permissionsError =
          "Microphone permission is required to continue onboarding.";
      notifyListeners();
      return;
    }
    _permissionsStepDone = true;
    notifyListeners();
  }

  void completeFirstMemory() {
    if (_firstMemoryDone) {
      return;
    }
    _firstMemoryDone = true;
    notifyListeners();
  }

  void updateFirstMemoryDraft(String value) {
    _firstMemoryDraft = value;
    _firstMemoryError = null;
    notifyListeners();
  }

  void prepareFirstMemoryProposal() {
    _firstMemoryError = null;
    if (_firstMemoryDraft.trim().isEmpty) {
      _firstMemoryProposalReady = false;
      _firstMemoryError = "Please enter a memory sentence before extraction.";
      notifyListeners();
      return;
    }
    _firstMemoryProposalReady = true;
    notifyListeners();
  }

  void confirmFirstMemory() {
    _firstMemoryProposalReady = false;
    completeFirstMemory();
  }

  void modifyFirstMemoryProposal() {
    _firstMemoryProposalReady = false;
    notifyListeners();
  }

  void cancelFirstMemoryProposal() {
    _firstMemoryDraft = "";
    _firstMemoryProposalReady = false;
    _firstMemoryError = null;
    notifyListeners();
  }

  void completeFirstQuestion() {
    if (_firstQuestionDone) {
      return;
    }
    if (!_firstQuestionAnswerReady) {
      _firstQuestionError =
          "Ask your first question and review the answer before completing this step.";
      notifyListeners();
      return;
    }
    _firstQuestionDone = true;
    _firstQuestionError = null;
    notifyListeners();
  }

  void updateFirstQuestionDraft(String value) {
    _firstQuestionDraft = value;
    _firstQuestionError = null;
    _firstQuestionAnswerReady = false;
    _firstQuestionWhyExpanded = false;
    notifyListeners();
  }

  void prepareFirstQuestionAnswer() {
    _firstQuestionError = null;
    final String trimmedQuestion = _firstQuestionDraft.trim();
    if (trimmedQuestion.isEmpty) {
      _firstQuestionAnswerReady = false;
      _firstQuestionWhyExpanded = false;
      _firstQuestionError = "Please enter a question before asking the assistant.";
      notifyListeners();
      return;
    }

    const String fallbackAnswer = "Your memory timeline is ready for this question.";
    final String contextualAnswer = _firstMemoryDraft.trim().isEmpty
        ? fallbackAnswer
        : "From your first saved memory: ${_firstMemoryDraft.trim()}";
    _firstQuestionAnswer = contextualAnswer;
    _firstQuestionConfidence = "high";
    _firstQuestionSourceIds = const <String>["onboarding-first-memory"];
    _firstQuestionAnswerReady = true;
    _firstQuestionWhyExpanded = false;
    notifyListeners();
  }

  void toggleFirstQuestionWhyDisclosure() {
    if (!_firstQuestionAnswerReady) {
      return;
    }
    _firstQuestionWhyExpanded = !_firstQuestionWhyExpanded;
    notifyListeners();
  }

  Future<void> finish() async {
    if (!canFinish || _completed) {
      return;
    }
    _completed = true;
    notifyListeners();

    if (_hydratedUserId == null || _hydratedUserId!.isEmpty) {
      return;
    }
    await _onboardingCompletionRepository.persistOnboardingCompletedAt(
      userId: _hydratedUserId!,
      completedAt: DateTime.now().toUtc(),
    );
  }

  void reset() {
    _completed = false;
    _welcomeStepDone = false;
    _languageStepDone = false;
    _selectedLanguage = PreferredLanguage.en;
    _isSavingLanguage = false;
    _languageError = null;
    _permissionsStepDone = false;
    _microphoneGranted = false;
    _cameraGranted = false;
    _permissionsError = null;
    _firstMemoryDone = false;
    _firstMemoryDraft = "";
    _firstMemoryProposalReady = false;
    _firstMemoryError = null;
    _firstQuestionDone = false;
    _firstQuestionDraft = "";
    _firstQuestionAnswer = "";
    _firstQuestionConfidence = "medium";
    _firstQuestionSourceIds = const <String>[];
    _firstQuestionAnswerReady = false;
    _firstQuestionWhyExpanded = false;
    _firstQuestionError = null;
    notifyListeners();
  }
}
