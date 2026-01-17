import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_de.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('de'),
    Locale('en')
  ];

  /// Application name
  ///
  /// In de, this message translates to:
  /// **'RedFlag Analyzer'**
  String get appName;

  /// No description provided for @homeWelcome.
  ///
  /// In de, this message translates to:
  /// **'Willkommen beim RedFlag Analyzer'**
  String get homeWelcome;

  /// No description provided for @homeSubtitle.
  ///
  /// In de, this message translates to:
  /// **'Analysieren Sie Beziehungen objektiv'**
  String get homeSubtitle;

  /// No description provided for @homeStartButton.
  ///
  /// In de, this message translates to:
  /// **'Jetzt starten'**
  String get homeStartButton;

  /// No description provided for @homeFeature1.
  ///
  /// In de, this message translates to:
  /// **'65 wissenschaftlich fundierte Fragen'**
  String get homeFeature1;

  /// No description provided for @homeFeature2.
  ///
  /// In de, this message translates to:
  /// **'Detaillierte Analyse mit Kategorien'**
  String get homeFeature2;

  /// No description provided for @homeFeature3.
  ///
  /// In de, this message translates to:
  /// **'PDF Export für Ihre Berichte'**
  String get homeFeature3;

  /// No description provided for @homeFeature4.
  ///
  /// In de, this message translates to:
  /// **'100% anonym und privat'**
  String get homeFeature4;

  /// No description provided for @loginTitle.
  ///
  /// In de, this message translates to:
  /// **'Anmelden'**
  String get loginTitle;

  /// No description provided for @loginEmail.
  ///
  /// In de, this message translates to:
  /// **'E-Mail'**
  String get loginEmail;

  /// No description provided for @loginPassword.
  ///
  /// In de, this message translates to:
  /// **'Passwort'**
  String get loginPassword;

  /// No description provided for @loginButton.
  ///
  /// In de, this message translates to:
  /// **'Anmelden'**
  String get loginButton;

  /// No description provided for @loginNoAccount.
  ///
  /// In de, this message translates to:
  /// **'Noch kein Konto? Registrieren'**
  String get loginNoAccount;

  /// No description provided for @loginError.
  ///
  /// In de, this message translates to:
  /// **'Anmeldung fehlgeschlagen'**
  String get loginError;

  /// No description provided for @registerTitle.
  ///
  /// In de, this message translates to:
  /// **'Registrieren'**
  String get registerTitle;

  /// No description provided for @registerButton.
  ///
  /// In de, this message translates to:
  /// **'Registrieren'**
  String get registerButton;

  /// No description provided for @registerHasAccount.
  ///
  /// In de, this message translates to:
  /// **'Bereits ein Konto? Anmelden'**
  String get registerHasAccount;

  /// No description provided for @registerSuccess.
  ///
  /// In de, this message translates to:
  /// **'Registrierung erfolgreich!'**
  String get registerSuccess;

  /// No description provided for @questionnaireTitle.
  ///
  /// In de, this message translates to:
  /// **'Fragebogen'**
  String get questionnaireTitle;

  /// No description provided for @questionnaireProgress.
  ///
  /// In de, this message translates to:
  /// **'Frage {current} von {total}'**
  String questionnaireProgress(int current, int total);

  /// No description provided for @questionnaireNext.
  ///
  /// In de, this message translates to:
  /// **'Weiter'**
  String get questionnaireNext;

  /// No description provided for @questionnaireBack.
  ///
  /// In de, this message translates to:
  /// **'Zurück'**
  String get questionnaireBack;

  /// No description provided for @questionnaireSubmit.
  ///
  /// In de, this message translates to:
  /// **'Abschließen'**
  String get questionnaireSubmit;

  /// No description provided for @questionnaireNotApply.
  ///
  /// In de, this message translates to:
  /// **'Trifft nicht zu'**
  String get questionnaireNotApply;

  /// No description provided for @questionnaireFullyApply.
  ///
  /// In de, this message translates to:
  /// **'Trifft voll zu'**
  String get questionnaireFullyApply;

  /// No description provided for @resultsTitle.
  ///
  /// In de, this message translates to:
  /// **'Analyseergebnis'**
  String get resultsTitle;

  /// No description provided for @resultsLocked.
  ///
  /// In de, this message translates to:
  /// **'Analyse gesperrt'**
  String get resultsLocked;

  /// No description provided for @resultsUnlockMessage.
  ///
  /// In de, this message translates to:
  /// **'Verwenden Sie einen Credit, um das vollständige Ergebnis freizuschalten.'**
  String get resultsUnlockMessage;

  /// No description provided for @resultsYourCredits.
  ///
  /// In de, this message translates to:
  /// **'Ihre Credits:'**
  String get resultsYourCredits;

  /// No description provided for @resultsUnlockButton.
  ///
  /// In de, this message translates to:
  /// **'Jetzt freischalten (1 Credit)'**
  String get resultsUnlockButton;

  /// No description provided for @resultsBuyCredits.
  ///
  /// In de, this message translates to:
  /// **'Credits kaufen (5€)'**
  String get resultsBuyCredits;

  /// No description provided for @resultsOverallScore.
  ///
  /// In de, this message translates to:
  /// **'Gesamtscore'**
  String get resultsOverallScore;

  /// No description provided for @resultsCategoryAnalysis.
  ///
  /// In de, this message translates to:
  /// **'Kategorie-Analyse'**
  String get resultsCategoryAnalysis;

  /// No description provided for @resultsTopRedFlags.
  ///
  /// In de, this message translates to:
  /// **'Top Red Flags'**
  String get resultsTopRedFlags;

  /// No description provided for @resultsExportPDF.
  ///
  /// In de, this message translates to:
  /// **'Als PDF exportieren'**
  String get resultsExportPDF;

  /// No description provided for @resultsBackHome.
  ///
  /// In de, this message translates to:
  /// **'Zurück zur Startseite'**
  String get resultsBackHome;

  /// No description provided for @profileTitle.
  ///
  /// In de, this message translates to:
  /// **'Profil'**
  String get profileTitle;

  /// No description provided for @profileCredits.
  ///
  /// In de, this message translates to:
  /// **'Credits'**
  String get profileCredits;

  /// No description provided for @profileEdit.
  ///
  /// In de, this message translates to:
  /// **'Profil bearbeiten'**
  String get profileEdit;

  /// No description provided for @profileAge.
  ///
  /// In de, this message translates to:
  /// **'Alter'**
  String get profileAge;

  /// No description provided for @profileCountry.
  ///
  /// In de, this message translates to:
  /// **'Land'**
  String get profileCountry;

  /// No description provided for @profileGender.
  ///
  /// In de, this message translates to:
  /// **'Geschlecht'**
  String get profileGender;

  /// No description provided for @profileGenderMale.
  ///
  /// In de, this message translates to:
  /// **'Männlich'**
  String get profileGenderMale;

  /// No description provided for @profileGenderFemale.
  ///
  /// In de, this message translates to:
  /// **'Weiblich'**
  String get profileGenderFemale;

  /// No description provided for @profileGenderOther.
  ///
  /// In de, this message translates to:
  /// **'Divers'**
  String get profileGenderOther;

  /// No description provided for @profileGenderNotSay.
  ///
  /// In de, this message translates to:
  /// **'Keine Angabe'**
  String get profileGenderNotSay;

  /// No description provided for @profileSave.
  ///
  /// In de, this message translates to:
  /// **'Profil speichern'**
  String get profileSave;

  /// No description provided for @profileStatistics.
  ///
  /// In de, this message translates to:
  /// **'Statistiken'**
  String get profileStatistics;

  /// No description provided for @profileTotalAnalyses.
  ///
  /// In de, this message translates to:
  /// **'Analysen gesamt'**
  String get profileTotalAnalyses;

  /// No description provided for @profileUnlocked.
  ///
  /// In de, this message translates to:
  /// **'Freigeschaltet'**
  String get profileUnlocked;

  /// No description provided for @profileLocked.
  ///
  /// In de, this message translates to:
  /// **'Gesperrt'**
  String get profileLocked;

  /// No description provided for @categoryTrust.
  ///
  /// In de, this message translates to:
  /// **'Vertrauen'**
  String get categoryTrust;

  /// No description provided for @categoryBehavior.
  ///
  /// In de, this message translates to:
  /// **'Verhalten'**
  String get categoryBehavior;

  /// No description provided for @categoryValues.
  ///
  /// In de, this message translates to:
  /// **'Werte'**
  String get categoryValues;

  /// No description provided for @categoryDynamics.
  ///
  /// In de, this message translates to:
  /// **'Dynamik'**
  String get categoryDynamics;

  /// No description provided for @scoreLowRisk.
  ///
  /// In de, this message translates to:
  /// **'Niedrig - Wenig Risiko'**
  String get scoreLowRisk;

  /// No description provided for @scoreMediumRisk.
  ///
  /// In de, this message translates to:
  /// **'Mittel - Einige Bedenken'**
  String get scoreMediumRisk;

  /// No description provided for @scoreHighRisk.
  ///
  /// In de, this message translates to:
  /// **'Hoch - Viele Warnsignale'**
  String get scoreHighRisk;

  /// No description provided for @scoreCritical.
  ///
  /// In de, this message translates to:
  /// **'Sehr Hoch - Kritisch'**
  String get scoreCritical;

  /// No description provided for @errorGeneric.
  ///
  /// In de, this message translates to:
  /// **'Ein Fehler ist aufgetreten'**
  String get errorGeneric;

  /// No description provided for @errorNetwork.
  ///
  /// In de, this message translates to:
  /// **'Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.'**
  String get errorNetwork;

  /// No description provided for @errorInvalidEmail.
  ///
  /// In de, this message translates to:
  /// **'Ungültige E-Mail-Adresse'**
  String get errorInvalidEmail;

  /// No description provided for @errorInvalidPassword.
  ///
  /// In de, this message translates to:
  /// **'Passwort muss mindestens 6 Zeichen lang sein'**
  String get errorInvalidPassword;

  /// No description provided for @loadingPleaseWait.
  ///
  /// In de, this message translates to:
  /// **'Bitte warten...'**
  String get loadingPleaseWait;

  /// No description provided for @success.
  ///
  /// In de, this message translates to:
  /// **'Erfolg!'**
  String get success;

  /// No description provided for @cancel.
  ///
  /// In de, this message translates to:
  /// **'Abbrechen'**
  String get cancel;

  /// No description provided for @ok.
  ///
  /// In de, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @save.
  ///
  /// In de, this message translates to:
  /// **'Speichern'**
  String get save;

  /// No description provided for @delete.
  ///
  /// In de, this message translates to:
  /// **'Löschen'**
  String get delete;

  /// No description provided for @share.
  ///
  /// In de, this message translates to:
  /// **'Teilen'**
  String get share;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['de', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'de':
      return AppLocalizationsDe();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
