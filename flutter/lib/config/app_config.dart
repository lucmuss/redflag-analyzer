/// App Configuration
/// Central configuration for API endpoints, constants, and settings
class AppConfig {
  // API Configuration
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  static const String apiVersion = '/api/v1';
  static const String apiUrl = '$baseUrl$apiVersion';
  
  // Endpoints
  static const String authRegister = '$apiUrl/auth/register';
  static const String authLogin = '$apiUrl/auth/login';
  static const String authMe = '$apiUrl/auth/me';
  static const String questions = '$apiUrl/questions';
  static const String analyses = '$apiUrl/analyses';
  static const String users = '$apiUrl/users';
  
  // App Settings
  static const String appName = 'RedFlag Analyzer';
  static const String appVersion = '1.0.0';
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String userIdKey = 'user_id';
  static const String userEmailKey = 'user_email';
  static const String questionnaireProgressKey = 'questionnaire_progress';
  static const String hasSeenOnboardingKey = 'has_seen_onboarding';
  
  // Feature Flags
  static const bool enableGuestMode = true;
  static const bool enablePushNotifications = false;
  static const bool enableOfflineMode = true;
  
  // Payment (Stripe/IAP)
  static const String stripePublishableKey = String.fromEnvironment(
    'STRIPE_PUBLISHABLE_KEY',
    defaultValue: 'pk_test_...',
  );
  
  static const String iapProductIdAndroid = 'analysis_credit_1';
  static const String iapProductIdIOS = 'com.redflag.analysis.credit.1';
  static const double creditPrice = 4.99; // EUR
  
  // UI Constants
  static const int questionsPerPage = 5;
  static const int maxQuestionsCount = 65;
  
  // Timeout & Retry
  static const Duration apiTimeout = Duration(seconds: 30);
  static const int maxRetries = 3;
  
  // Categories
  static const List<String> categories = [
    'TRUST',
    'BEHAVIOR',
    'VALUES',
    'DYNAMICS',
  ];
  
  // Score Ranges (for color coding)
  static const double lowScoreThreshold = 3.0;
  static const double mediumScoreThreshold = 6.0;
  static const double highScoreThreshold = 10.0;
}
