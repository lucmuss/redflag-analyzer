import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:logger/logger.dart';

import '../config/app_config.dart';
import '../models/user.dart';
import '../models/question.dart';
import '../models/analysis.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => 'ApiException: $message (Status: $statusCode)';
}

class ApiService {
  final Logger _logger = Logger();
  String? _accessToken;

  // Set access token for authenticated requests
  void setAccessToken(String? token) {
    _accessToken = token;
  }

  // Get headers with optional auth
  Map<String, String> _getHeaders({bool includeAuth = false}) {
    final headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && _accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }

    return headers;
  }

  // Generic GET request
  Future<dynamic> _get(String url, {bool requiresAuth = false}) async {
    try {
      _logger.d('GET $url');
      
      final response = await http
          .get(
            Uri.parse(url),
            headers: _getHeaders(includeAuth: requiresAuth),
          )
          .timeout(AppConfig.apiTimeout);

      return _handleResponse(response);
    } catch (e) {
      _logger.e('GET request failed: $e');
      throw ApiException('Network error: ${e.toString()}');
    }
  }

  // Generic POST request
  Future<dynamic> _post(
    String url,
    Map<String, dynamic> body, {
    bool requiresAuth = false,
  }) async {
    try {
      _logger.d('POST $url');
      
      final response = await http
          .post(
            Uri.parse(url),
            headers: _getHeaders(includeAuth: requiresAuth),
            body: jsonEncode(body),
          )
          .timeout(AppConfig.apiTimeout);

      return _handleResponse(response);
    } catch (e) {
      _logger.e('POST request failed: $e');
      throw ApiException('Network error: ${e.toString()}');
    }
  }

  // Generic PUT request
  Future<dynamic> _put(
    String url,
    Map<String, dynamic> body, {
    bool requiresAuth = false,
  }) async {
    try {
      _logger.d('PUT $url');
      
      final response = await http
          .put(
            Uri.parse(url),
            headers: _getHeaders(includeAuth: requiresAuth),
            body: jsonEncode(body),
          )
          .timeout(AppConfig.apiTimeout);

      return _handleResponse(response);
    } catch (e) {
      _logger.e('PUT request failed: $e');
      throw ApiException('Network error: ${e.toString()}');
    }
  }

  // Handle HTTP response
  dynamic _handleResponse(http.Response response) {
    _logger.d('Response status: ${response.statusCode}');

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    }

    // Error handling
    String errorMessage = 'Request failed';
    try {
      final errorData = jsonDecode(response.body);
      errorMessage = errorData['detail'] ?? errorMessage;
    } catch (_) {
      errorMessage = response.body;
    }

    throw ApiException(errorMessage, response.statusCode);
  }

  // ========== AUTH ENDPOINTS ==========

  Future<AuthResponse> register(String email, String password) async {
    final data = await _post(AppConfig.authRegister, {
      'email': email,
      'password': password,
    });

    // Login after registration to get token
    return login(email, password);
  }

  Future<AuthResponse> login(String email, String password) async {
    final data = await _post(AppConfig.authLogin, {
      'email': email,
      'password': password,
    });

    return AuthResponse.fromJson(data);
  }

  Future<User> getCurrentUser() async {
    final data = await _get(AppConfig.authMe, requiresAuth: true);
    return User.fromJson(data);
  }

  // ========== QUESTIONS ENDPOINTS ==========

  Future<List<Question>> getQuestions() async {
    final data = await _get(AppConfig.questions) as List;
    return data.map((json) => Question.fromJson(json)).toList();
  }

  Future<Question> getQuestion(String key) async {
    final data = await _get('${AppConfig.questions}/$key');
    return Question.fromJson(data);
  }

  Future<List<Question>> getQuestionsByCategory(String category) async {
    final data = await _get('${AppConfig.questions}/category/$category') as List;
    return data.map((json) => Question.fromJson(json)).toList();
  }

  // ========== ANALYSES ENDPOINTS ==========

  Future<Analysis> createAnalysis(AnalysisCreateRequest request) async {
    final data = await _post(
      AppConfig.analyses,
      request.toJson(),
      requiresAuth: true,
    );

    return Analysis.fromJson(data);
  }

  Future<Analysis> unlockAnalysis(String analysisId) async {
    final data = await _post(
      '${AppConfig.analyses}/$analysisId/unlock',
      {},
      requiresAuth: true,
    );

    return Analysis.fromJson(data);
  }

  Future<Analysis> getAnalysis(String analysisId) async {
    final data = await _get(
      '${AppConfig.analyses}/$analysisId',
      requiresAuth: true,
    );

    return Analysis.fromJson(data);
  }

  Future<List<Analysis>> getUserAnalyses({int limit = 10, int skip = 0}) async {
    final data = await _get(
      '${AppConfig.analyses}?limit=$limit&skip=$skip',
      requiresAuth: true,
    ) as List;

    return data.map((json) => Analysis.fromJson(json)).toList();
  }

  // ========== USERS ENDPOINTS ==========

  Future<User> updateUserProfile(UserProfile profile) async {
    final data = await _put(
      '${AppConfig.users}/me',
      {'profile': profile.toJson()},
      requiresAuth: true,
    );

    return User.fromJson(data);
  }
}
