import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;

/// Local Storage Service
/// Handles persistent storage using SharedPreferences and Secure Storage
class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  final Logger _logger = Logger();
  late SharedPreferences _prefs;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage(
    webOptions: WebOptions(
      dbName: 'redflag_storage',
      publicKey: 'redflag_public_key',
    ),
  );

  // Storage Keys
  static const String _keyAccessToken = 'access_token';
  static const String _keyUserEmail = 'user_email';
  static const String _keyUserId = 'user_id';
  static const String _keyOnboardingComplete = 'onboarding_complete';
  static const String _keyQuestionnaireProgress = 'questionnaire_progress';
  static const String _keyCachedQuestions = 'cached_questions';

  /// Initialize storage
  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    _logger.d('StorageService initialized');
  }

  // ========== AUTH TOKEN (Secure Storage) ==========

  Future<void> saveAccessToken(String token) async {
    await _secureStorage.write(key: _keyAccessToken, value: token);
    _logger.d('Access token saved');
  }

  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: _keyAccessToken);
  }

  Future<void> deleteAccessToken() async {
    await _secureStorage.delete(key: _keyAccessToken);
    _logger.d('Access token deleted');
  }

  // ========== USER DATA ==========

  Future<void> saveUserEmail(String email) async {
    await _prefs.setString(_keyUserEmail, email);
  }

  String? getUserEmail() {
    return _prefs.getString(_keyUserEmail);
  }

  Future<void> saveUserId(String userId) async {
    await _prefs.setString(_keyUserId, userId);
  }

  String? getUserId() {
    return _prefs.getString(_keyUserId);
  }

  // ========== ONBOARDING ==========

  Future<void> setOnboardingComplete(bool complete) async {
    await _prefs.setBool(_keyOnboardingComplete, complete);
  }

  bool isOnboardingComplete() {
    return _prefs.getBool(_keyOnboardingComplete) ?? false;
  }

  // ========== QUESTIONNAIRE PROGRESS ==========

  Future<void> saveQuestionnaireProgress(
    Map<String, int> responses,
    int currentIndex,
  ) async {
    final data = {
      'responses': responses,
      'currentIndex': currentIndex,
      'timestamp': DateTime.now().toIso8601String(),
    };
    await _prefs.setString(_keyQuestionnaireProgress, jsonEncode(data));
    _logger.d('Questionnaire progress saved: $currentIndex questions');
  }

  Map<String, dynamic>? getQuestionnaireProgress() {
    final String? data = _prefs.getString(_keyQuestionnaireProgress);
    if (data == null) return null;
    
    try {
      return jsonDecode(data) as Map<String, dynamic>;
    } catch (e) {
      _logger.e('Failed to decode questionnaire progress: $e');
      return null;
    }
  }

  Future<void> clearQuestionnaireProgress() async {
    await _prefs.remove(_keyQuestionnaireProgress);
    _logger.d('Questionnaire progress cleared');
  }

  // ========== CACHED QUESTIONS ==========

  Future<void> cacheQuestions(List<Map<String, dynamic>> questions) async {
    await _prefs.setString(_keyCachedQuestions, jsonEncode(questions));
    _logger.d('Cached ${questions.length} questions');
  }

  List<Map<String, dynamic>>? getCachedQuestions() {
    final String? data = _prefs.getString(_keyCachedQuestions);
    if (data == null) return null;
    
    try {
      final List<dynamic> decoded = jsonDecode(data) as List;
      return decoded.cast<Map<String, dynamic>>();
    } catch (e) {
      _logger.e('Failed to decode cached questions: $e');
      return null;
    }
  }

  // ========== CLEAR ALL DATA ==========

  Future<void> clearAll() async {
    await _prefs.clear();
    await _secureStorage.deleteAll();
    _logger.d('All storage cleared');
  }

  Future<void> logout() async {
    await deleteAccessToken();
    await _prefs.remove(_keyUserEmail);
    await _prefs.remove(_keyUserId);
    await clearQuestionnaireProgress();
    _logger.d('User logged out');
  }
}
