import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

import '../models/analysis.dart';
import '../models/question.dart';
import '../services/api_service.dart';

enum AnalysisStatus {
  initial,
  loading,
  loaded,
  error,
}

class AnalysisProvider with ChangeNotifier {
  final ApiService _apiService;
  final Logger _logger = Logger();

  AnalysisStatus _status = AnalysisStatus.initial;
  List<Analysis> _analyses = [];
  Analysis? _currentAnalysis;
  String? _errorMessage;

  AnalysisProvider({required ApiService apiService})
      : _apiService = apiService;

  // Getters
  AnalysisStatus get status => _status;
  List<Analysis> get analyses => _analyses;
  Analysis? get currentAnalysis => _currentAnalysis;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _status == AnalysisStatus.loading;

  /// Create new analysis
  Future<Analysis?> createAnalysis(List<QuestionResponse> responses) async {
    try {
      _setStatus(AnalysisStatus.loading);
      _errorMessage = null;

      final request = AnalysisCreateRequest(responses: responses);
      final analysis = await _apiService.createAnalysis(request);

      _currentAnalysis = analysis;
      _analyses.insert(0, analysis); // Add to beginning
      
      _setStatus(AnalysisStatus.loaded);
      _logger.d('Analysis created: ${analysis.id}');
      
      return analysis;
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Failed to create analysis: $e');
      _setStatus(AnalysisStatus.error);
      return null;
    }
  }

  /// Unlock analysis with credit
  Future<bool> unlockAnalysis(String analysisId) async {
    try {
      _setStatus(AnalysisStatus.loading);
      _errorMessage = null;

      final unlockedAnalysis = await _apiService.unlockAnalysis(analysisId);
      
      // Update in list
      final index = _analyses.indexWhere((a) => a.id == analysisId);
      if (index != -1) {
        _analyses[index] = unlockedAnalysis;
      }
      
      // Update current if it's the same
      if (_currentAnalysis?.id == analysisId) {
        _currentAnalysis = unlockedAnalysis;
      }

      _setStatus(AnalysisStatus.loaded);
      _logger.d('Analysis unlocked: $analysisId');
      
      return true;
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Failed to unlock analysis: $e');
      _setStatus(AnalysisStatus.error);
      return false;
    }
  }

  /// Load user's analyses
  Future<void> loadUserAnalyses({int limit = 10, int skip = 0}) async {
    try {
      _setStatus(AnalysisStatus.loading);

      _analyses = await _apiService.getUserAnalyses(limit: limit, skip: skip);
      
      _setStatus(AnalysisStatus.loaded);
      _logger.d('Loaded ${_analyses.length} analyses');
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Failed to load analyses: $e');
      _setStatus(AnalysisStatus.error);
    }
  }

  /// Load specific analysis
  Future<bool> loadAnalysis(String analysisId) async {
    try {
      _setStatus(AnalysisStatus.loading);

      _currentAnalysis = await _apiService.getAnalysis(analysisId);
      
      _setStatus(AnalysisStatus.loaded);
      _logger.d('Analysis loaded: $analysisId');
      
      return true;
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Failed to load analysis: $e');
      _setStatus(AnalysisStatus.error);
      return false;
    }
  }

  /// Set current analysis
  void setCurrentAnalysis(Analysis? analysis) {
    _currentAnalysis = analysis;
    notifyListeners();
  }

  /// Clear current analysis
  void clearCurrentAnalysis() {
    _currentAnalysis = null;
    notifyListeners();
  }

  /// Get unlocked analyses
  List<Analysis> get unlockedAnalyses {
    return _analyses.where((a) => a.isUnlocked).toList();
  }

  /// Get locked analyses
  List<Analysis> get lockedAnalyses {
    return _analyses.where((a) => !a.isUnlocked).toList();
  }

  /// Clear error
  void clearError() {
    _errorMessage = null;
    if (_status == AnalysisStatus.error) {
      _setStatus(AnalysisStatus.initial);
    }
  }

  void _setStatus(AnalysisStatus newStatus) {
    _status = newStatus;
    notifyListeners();
  }

  String _getErrorMessage(dynamic error) {
    if (error.toString().contains('credit')) {
      return 'Nicht genügend Credits. Bitte kaufen Sie Credits.';
    } else if (error.toString().contains('Network')) {
      return 'Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.';
    } else if (error.toString().contains('401')) {
      return 'Sitzung abgelaufen. Bitte melden Sie sich erneut an.';
    }
    return 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.';
  }
}
