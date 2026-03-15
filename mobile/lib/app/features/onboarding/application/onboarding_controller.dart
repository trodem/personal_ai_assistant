import 'package:flutter/foundation.dart';

class OnboardingController extends ChangeNotifier {
  OnboardingController({
    bool completed = false,
  }) : _completed = completed;

  bool _completed;
  bool get completed => _completed;

  bool _firstMemoryDone = false;
  bool get firstMemoryDone => _firstMemoryDone;

  bool _firstQuestionDone = false;
  bool get firstQuestionDone => _firstQuestionDone;

  bool get canFinish => _firstMemoryDone && _firstQuestionDone;

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
    _firstMemoryDone = false;
    _firstQuestionDone = false;
    notifyListeners();
  }
}
