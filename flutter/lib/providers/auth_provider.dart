import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

import '../models/user.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  final StorageService _storageService;
  final Logger _logger = Logger();

  AuthStatus _status = AuthStatus.initial;
  User? _currentUser;
  String? _errorMessage;

  AuthProvider({
    required ApiService apiService,
    required StorageService storageService,
  })  : _apiService = apiService,
        _storageService = storageService;

  // Getters
  AuthStatus get status => _status;
  User? get currentUser => _currentUser;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get isLoading => _status == AuthStatus.loading;
  int get credits => _currentUser?.credits ?? 0;

  /// Initialize and check if user is already logged in
  Future<void> init() async {
    try {
      final token = await _storageService.getAccessToken();
      
      if (token != null) {
        _apiService.setAccessToken(token);
        await _loadCurrentUser();
      } else {
        _setStatus(AuthStatus.unauthenticated);
      }
    } catch (e) {
      _logger.e('Failed to initialize auth: $e');
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  /// Load current user from API
  Future<void> _loadCurrentUser() async {
    try {
      _currentUser = await _apiService.getCurrentUser();
      _setStatus(AuthStatus.authenticated);
      _logger.d('User loaded: ${_currentUser?.email}');
    } catch (e) {
      _logger.e('Failed to load user: $e');
      await logout();
    }
  }

  /// Register new user
  Future<bool> register(String email, String password) async {
    try {
      _setStatus(AuthStatus.loading);
      _errorMessage = null;

      final authResponse = await _apiService.register(email, password);
      
      // Save token
      await _storageService.saveAccessToken(authResponse.accessToken);
      await _storageService.saveUserEmail(email);
      
      // Set token in API service
      _apiService.setAccessToken(authResponse.accessToken);
      
      // Load user data
      await _loadCurrentUser();
      
      _logger.d('Registration successful: $email');
      return true;
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Registration failed: $e');
      _setStatus(AuthStatus.error);
      return false;
    }
  }

  /// Login user
  Future<bool> login(String email, String password) async {
    try {
      _setStatus(AuthStatus.loading);
      _errorMessage = null;

      final authResponse = await _apiService.login(email, password);
      
      // Save token
      await _storageService.saveAccessToken(authResponse.accessToken);
      await _storageService.saveUserEmail(email);
      
      // Set token in API service
      _apiService.setAccessToken(authResponse.accessToken);
      
      // Load user data
      await _loadCurrentUser();
      
      _logger.d('Login successful: $email');
      return true;
    } catch (e) {
      _errorMessage = _getErrorMessage(e);
      _logger.e('Login failed: $e');
      _setStatus(AuthStatus.error);
      return false;
    }
  }

  /// Logout user
  Future<void> logout() async {
    await _storageService.logout();
    _apiService.setAccessToken(null);
    _currentUser = null;
    _setStatus(AuthStatus.unauthenticated);
    _logger.d('User logged out');
  }

  /// Update user profile
  Future<bool> updateProfile(UserProfile profile) async {
    try {
      _currentUser = await _apiService.updateUserProfile(profile);
      notifyListeners();
      _logger.d('Profile updated');
      return true;
    } catch (e) {
      _logger.e('Failed to update profile: $e');
      return false;
    }
  }

  /// Refresh user data (e.g., after credit purchase)
  Future<void> refreshUser() async {
    try {
      await _loadCurrentUser();
    } catch (e) {
      _logger.e('Failed to refresh user: $e');
    }
  }

  /// Deduct credit (when unlocking analysis)
  void deductCredit() {
    if (_currentUser != null && _currentUser!.credits > 0) {
      _currentUser = User(
        id: _currentUser!.id,
        email: _currentUser!.email,
        createdAt: _currentUser!.createdAt,
        isVerified: _currentUser!.isVerified,
        profile: _currentUser!.profile,
        credits: _currentUser!.credits - 1,
      );
      notifyListeners();
    }
  }

  /// Clear error message
  void clearError() {
    _errorMessage = null;
    if (_status == AuthStatus.error) {
      _setStatus(AuthStatus.unauthenticated);
    }
  }

  void _setStatus(AuthStatus newStatus) {
    _status = newStatus;
    notifyListeners();
  }

  String _getErrorMessage(dynamic error) {
    if (error.toString().contains('Invalid')) {
      return 'Ungültige E-Mail oder Passwort';
    } else if (error.toString().contains('already exists')) {
      return 'E-Mail bereits registriert';
    } else if (error.toString().contains('Network')) {
      return 'Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.';
    }
    return 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.';
  }
}
