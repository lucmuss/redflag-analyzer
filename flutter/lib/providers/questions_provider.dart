import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

import '../models/question.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

enum QuestionsStatus {
  initial,
  loading,
  loaded,
  error,
}

class QuestionsProvider with ChangeNotifier {
  final ApiService _apiService;
  final StorageService _storageService;
  final Logger _logger = Logger();

  QuestionsStatus _status = QuestionsStatus.initial;
  List<Question> _questions = [];
  Map<String, int> _responses = {};
  int _currentIndex = 0;
  String? _errorMessage;

  QuestionsProvider({
    required ApiService apiService,
    required StorageService storageService,
  })  : _apiService = apiService,
        _storageService = storageService;

  // Getters
  QuestionsStatus get status => _status;
  List<Question> get questions => _questions;
  Map<String, int> get responses => _responses;
  int get currentIndex => _currentIndex;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _status == QuestionsStatus.loading;
  bool get isComplete => _responses.length == _questions.length && _questions.isNotEmpty;
  double get progress => _questions.isEmpty ? 0.0 : _responses.length / _questions.length;

  /// Load questions from API or cache
  Future<void> loadQuestions({bool forceRefresh = false}) async {
    try {
      _setStatus(QuestionsStatus.loading);

      // Try cache first if not forcing refresh
      if (!forceRefresh) {
        final cached = _storageService.getCachedQuestions();
        if (cached != null && cached.isNotEmpty) {
          _questions = cached.map((json) => Question.fromJson(json)).toList();
          _setStatus(QuestionsStatus.loaded);
          _logger.d('Loaded ${_questions.length} questions from cache');
          return;
        }
      }

      // Load from API
      _questions = await _apiService.getQuestions();
      
      // Cache for offline use
      await _storageService.cacheQuestions(
        _questions.map((q) => q.toJson()).toList(),
      );

      _setStatus(QuestionsStatus.loaded);
      _logger.d('Loaded ${_questions.length} questions from API');
    } catch (e) {
      _errorMessage = 'Fehler beim Laden der Fragen: ${e.toString()}';
      _logger.e('Failed to load questions: $e');
      _setStatus(QuestionsStatus.error);
    }
  }

  /// Load saved progress from storage
  Future<void> loadProgress() async {
    final progress = _storageService.getQuestionnaireProgress();
    if (progress != null) {
      _currentIndex = progress['currentIndex'] as int? ?? 0;
      
      final savedResponses = progress['responses'] as Map<String, dynamic>?;
      if (savedResponses != null) {
        _responses = savedResponses.map(
          (key, value) => MapEntry(key, value as int),
        );
      }
      
      notifyListeners();
      _logger.d('Loaded progress: $_currentIndex questions answered');
    }
  }

  /// Set response for a question
  void setResponse(String questionKey, int value) {
    if (value < 1 || value > 5) {
      _logger.w('Invalid response value: $value');
      return;
    }

    _responses[questionKey] = value;
    notifyListeners();

    // Auto-save progress
    _saveProgress();
  }

  /// Remove response
  void removeResponse(String questionKey) {
    _responses.remove(questionKey);
    notifyListeners();
    _saveProgress();
  }

  /// Get response for a question
  int? getResponse(String questionKey) {
    return _responses[questionKey];
  }

  /// Move to next question
  void nextQuestion() {
    if (_currentIndex < _questions.length - 1) {
      _currentIndex++;
      notifyListeners();
      _saveProgress();
    }
  }

  /// Move to previous question
  void previousQuestion() {
    if (_currentIndex > 0) {
      _currentIndex--;
      notifyListeners();
      _saveProgress();
    }
  }

  /// Jump to specific question index
  void goToQuestion(int index) {
    if (index >= 0 && index < _questions.length) {
      _currentIndex = index;
      notifyListeners();
      _saveProgress();
    }
  }

  /// Get current question
  Question? get currentQuestion {
    if (_currentIndex >= 0 && _currentIndex < _questions.length) {
      return _questions[_currentIndex];
    }
    return null;
  }

  /// Save progress to storage
  Future<void> _saveProgress() async {
    await _storageService.saveQuestionnaireProgress(
      _responses,
      _currentIndex,
    );
  }

  /// Clear all responses and progress
  Future<void> reset() async {
    _responses.clear();
    _currentIndex = 0;
    await _storageService.clearQuestionnaireProgress();
    notifyListeners();
    _logger.d('Questionnaire reset');
  }

  /// Get questions by category
  List<Question> getQuestionsByCategory(QuestionCategory category) {
    return _questions.where((q) => q.category == category).toList();
  }

  /// Get response rate (percentage of answered questions)
  double getResponseRate() {
    if (_questions.isEmpty) return 0.0;
    return (_responses.length / _questions.length) * 100;
  }

  /// Validate all questions are answered
  bool validateComplete() {
    if (_questions.isEmpty) return false;
    
    for (final question in _questions) {
      if (!_responses.containsKey(question.key)) {
        return false;
      }
    }
    return true;
  }

  /// Get list of unanswered questions
  List<Question> getUnansweredQuestions() {
    return _questions.where((q) => !_responses.containsKey(q.key)).toList();
  }

  /// Prepare responses for API submission
  List<QuestionResponse> getResponsesForSubmission() {
    return _responses.entries
        .map((entry) => QuestionResponse(
              key: entry.key,
              value: entry.value,
            ))
        .toList();
  }

  void _setStatus(QuestionsStatus newStatus) {
    _status = newStatus;
    notifyListeners();
  }
}
