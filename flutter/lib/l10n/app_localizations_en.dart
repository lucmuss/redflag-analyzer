// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'RedFlag Analyzer';

  @override
  String get homeWelcome => 'Welcome to RedFlag Analyzer';

  @override
  String get homeSubtitle => 'Analyze relationships objectively';

  @override
  String get homeStartButton => 'Start Now';

  @override
  String get homeFeature1 => '65 scientifically-based questions';

  @override
  String get homeFeature2 => 'Detailed analysis with categories';

  @override
  String get homeFeature3 => 'PDF export for your reports';

  @override
  String get homeFeature4 => '100% anonymous and private';

  @override
  String get loginTitle => 'Login';

  @override
  String get loginEmail => 'Email';

  @override
  String get loginPassword => 'Password';

  @override
  String get loginButton => 'Login';

  @override
  String get loginNoAccount => 'No account yet? Register';

  @override
  String get loginError => 'Login failed';

  @override
  String get registerTitle => 'Register';

  @override
  String get registerButton => 'Register';

  @override
  String get registerHasAccount => 'Already have an account? Login';

  @override
  String get registerSuccess => 'Registration successful!';

  @override
  String get questionnaireTitle => 'Questionnaire';

  @override
  String questionnaireProgress(int current, int total) {
    return 'Question $current of $total';
  }

  @override
  String get questionnaireNext => 'Next';

  @override
  String get questionnaireBack => 'Back';

  @override
  String get questionnaireSubmit => 'Submit';

  @override
  String get questionnaireNotApply => 'Does not apply';

  @override
  String get questionnaireFullyApply => 'Fully applies';

  @override
  String get resultsTitle => 'Analysis Results';

  @override
  String get resultsLocked => 'Analysis Locked';

  @override
  String get resultsUnlockMessage =>
      'Use one credit to unlock the complete results.';

  @override
  String get resultsYourCredits => 'Your Credits:';

  @override
  String get resultsUnlockButton => 'Unlock Now (1 Credit)';

  @override
  String get resultsBuyCredits => 'Buy Credits (€5)';

  @override
  String get resultsOverallScore => 'Overall Score';

  @override
  String get resultsCategoryAnalysis => 'Category Analysis';

  @override
  String get resultsTopRedFlags => 'Top Red Flags';

  @override
  String get resultsExportPDF => 'Export as PDF';

  @override
  String get resultsBackHome => 'Back to Home';

  @override
  String get profileTitle => 'Profile';

  @override
  String get profileCredits => 'Credits';

  @override
  String get profileEdit => 'Edit Profile';

  @override
  String get profileAge => 'Age';

  @override
  String get profileCountry => 'Country';

  @override
  String get profileGender => 'Gender';

  @override
  String get profileGenderMale => 'Male';

  @override
  String get profileGenderFemale => 'Female';

  @override
  String get profileGenderOther => 'Other';

  @override
  String get profileGenderNotSay => 'Prefer not to say';

  @override
  String get profileSave => 'Save Profile';

  @override
  String get profileStatistics => 'Statistics';

  @override
  String get profileTotalAnalyses => 'Total Analyses';

  @override
  String get profileUnlocked => 'Unlocked';

  @override
  String get profileLocked => 'Locked';

  @override
  String get categoryTrust => 'Trust';

  @override
  String get categoryBehavior => 'Behavior';

  @override
  String get categoryValues => 'Values';

  @override
  String get categoryDynamics => 'Dynamics';

  @override
  String get scoreLowRisk => 'Low - Little Risk';

  @override
  String get scoreMediumRisk => 'Medium - Some Concerns';

  @override
  String get scoreHighRisk => 'High - Many Warning Signs';

  @override
  String get scoreCritical => 'Very High - Critical';

  @override
  String get errorGeneric => 'An error occurred';

  @override
  String get errorNetwork => 'Network error. Please check your connection.';

  @override
  String get errorInvalidEmail => 'Invalid email address';

  @override
  String get errorInvalidPassword => 'Password must be at least 6 characters';

  @override
  String get loadingPleaseWait => 'Please wait...';

  @override
  String get success => 'Success!';

  @override
  String get cancel => 'Cancel';

  @override
  String get ok => 'OK';

  @override
  String get save => 'Save';

  @override
  String get delete => 'Delete';

  @override
  String get share => 'Share';
}
