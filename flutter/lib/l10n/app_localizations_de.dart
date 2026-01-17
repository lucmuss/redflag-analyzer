// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for German (`de`).
class AppLocalizationsDe extends AppLocalizations {
  AppLocalizationsDe([String locale = 'de']) : super(locale);

  @override
  String get appName => 'RedFlag Analyzer';

  @override
  String get homeWelcome => 'Willkommen beim RedFlag Analyzer';

  @override
  String get homeSubtitle => 'Analysieren Sie Beziehungen objektiv';

  @override
  String get homeStartButton => 'Jetzt starten';

  @override
  String get homeFeature1 => '65 wissenschaftlich fundierte Fragen';

  @override
  String get homeFeature2 => 'Detaillierte Analyse mit Kategorien';

  @override
  String get homeFeature3 => 'PDF Export für Ihre Berichte';

  @override
  String get homeFeature4 => '100% anonym und privat';

  @override
  String get loginTitle => 'Anmelden';

  @override
  String get loginEmail => 'E-Mail';

  @override
  String get loginPassword => 'Passwort';

  @override
  String get loginButton => 'Anmelden';

  @override
  String get loginNoAccount => 'Noch kein Konto? Registrieren';

  @override
  String get loginError => 'Anmeldung fehlgeschlagen';

  @override
  String get registerTitle => 'Registrieren';

  @override
  String get registerButton => 'Registrieren';

  @override
  String get registerHasAccount => 'Bereits ein Konto? Anmelden';

  @override
  String get registerSuccess => 'Registrierung erfolgreich!';

  @override
  String get questionnaireTitle => 'Fragebogen';

  @override
  String questionnaireProgress(int current, int total) {
    return 'Frage $current von $total';
  }

  @override
  String get questionnaireNext => 'Weiter';

  @override
  String get questionnaireBack => 'Zurück';

  @override
  String get questionnaireSubmit => 'Abschließen';

  @override
  String get questionnaireNotApply => 'Trifft nicht zu';

  @override
  String get questionnaireFullyApply => 'Trifft voll zu';

  @override
  String get resultsTitle => 'Analyseergebnis';

  @override
  String get resultsLocked => 'Analyse gesperrt';

  @override
  String get resultsUnlockMessage =>
      'Verwenden Sie einen Credit, um das vollständige Ergebnis freizuschalten.';

  @override
  String get resultsYourCredits => 'Ihre Credits:';

  @override
  String get resultsUnlockButton => 'Jetzt freischalten (1 Credit)';

  @override
  String get resultsBuyCredits => 'Credits kaufen (5€)';

  @override
  String get resultsOverallScore => 'Gesamtscore';

  @override
  String get resultsCategoryAnalysis => 'Kategorie-Analyse';

  @override
  String get resultsTopRedFlags => 'Top Red Flags';

  @override
  String get resultsExportPDF => 'Als PDF exportieren';

  @override
  String get resultsBackHome => 'Zurück zur Startseite';

  @override
  String get profileTitle => 'Profil';

  @override
  String get profileCredits => 'Credits';

  @override
  String get profileEdit => 'Profil bearbeiten';

  @override
  String get profileAge => 'Alter';

  @override
  String get profileCountry => 'Land';

  @override
  String get profileGender => 'Geschlecht';

  @override
  String get profileGenderMale => 'Männlich';

  @override
  String get profileGenderFemale => 'Weiblich';

  @override
  String get profileGenderOther => 'Divers';

  @override
  String get profileGenderNotSay => 'Keine Angabe';

  @override
  String get profileSave => 'Profil speichern';

  @override
  String get profileStatistics => 'Statistiken';

  @override
  String get profileTotalAnalyses => 'Analysen gesamt';

  @override
  String get profileUnlocked => 'Freigeschaltet';

  @override
  String get profileLocked => 'Gesperrt';

  @override
  String get categoryTrust => 'Vertrauen';

  @override
  String get categoryBehavior => 'Verhalten';

  @override
  String get categoryValues => 'Werte';

  @override
  String get categoryDynamics => 'Dynamik';

  @override
  String get scoreLowRisk => 'Niedrig - Wenig Risiko';

  @override
  String get scoreMediumRisk => 'Mittel - Einige Bedenken';

  @override
  String get scoreHighRisk => 'Hoch - Viele Warnsignale';

  @override
  String get scoreCritical => 'Sehr Hoch - Kritisch';

  @override
  String get errorGeneric => 'Ein Fehler ist aufgetreten';

  @override
  String get errorNetwork =>
      'Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.';

  @override
  String get errorInvalidEmail => 'Ungültige E-Mail-Adresse';

  @override
  String get errorInvalidPassword =>
      'Passwort muss mindestens 6 Zeichen lang sein';

  @override
  String get loadingPleaseWait => 'Bitte warten...';

  @override
  String get success => 'Erfolg!';

  @override
  String get cancel => 'Abbrechen';

  @override
  String get ok => 'OK';

  @override
  String get save => 'Speichern';

  @override
  String get delete => 'Löschen';

  @override
  String get share => 'Teilen';
}
