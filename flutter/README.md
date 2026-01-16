# RedFlag Analyzer - Flutter App

## 📱 Cross-Platform Mobile & Web App

Diese Flutter App ist das Frontend für den RedFlag Analyzer und läuft auf:
- 📱 iOS (iPhone/iPad)
- 🤖 Android (Smartphone/Tablet)
- 🌐 Web (PWA - Progressive Web App)

---

## 🎯 Features

### ✅ Bereits implementiert:
- **Models**: User, Question, Analysis, CategoryScores
- **API Service**: Vollständige Backend-Integration
  - Authentication (Register, Login)
  - Questions (alle 65 Fragen abrufen)
  - Analyses (Erstellen, Freischalten, Abrufen)
- **Configuration**: Zentrale App-Config mit Endpoints

### 🚧 Nächste Schritte:
1. **Storage Service** - Lokale Datenpersistenz
2. **Auth Provider** - State Management für User
3. **UI Screens** - Material Design 3 UI
   - Onboarding
   - Fragebogen (65 Fragen, paginiert)
   - Ergebnis-Screen
   - Profile
4. **Chart Widgets** - Tachometer & Radar Chart
5. **PDF Export** - Analyse als PDF exportieren
6. **IAP Integration** - In-App Käufe für Credits

---

## 🚀 Setup & Installation

### Voraussetzungen
- Flutter SDK ≥3.0.0
- Dart SDK ≥3.0.0
- Android Studio / Xcode (für Mobile)
- Chrome (für Web)

### Installation

```bash
# 1. In Flutter-Verzeichnis wechseln
cd flutter

# 2. Dependencies installieren
flutter pub get

# 3. Code generieren (falls nötig)
flutter pub run build_runner build

# 4. App starten (wähle Platform)
```

### Verschiedene Platforms starten:

```bash
# Web (PWA)
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000

# Android Emulator
flutter run -d android --dart-define=API_BASE_URL=http://10.0.2.2:8000

# iOS Simulator
flutter run -d ios --dart-define=API_BASE_URL=http://localhost:8000

# Physisches Gerät (mit eigener IP)
flutter run --dart-define=API_BASE_URL=http://192.168.1.100:8000
```

**Wichtig:** `API_BASE_URL` muss auf das laufende Backend zeigen!

---

## 📂 Projekt-Struktur

```
flutter/
├── lib/
│   ├── config/
│   │   └── app_config.dart           # Zentrale Konfiguration
│   ├── models/
│   │   ├── user.dart                # User & Auth Models
│   │   ├── question.dart            # Question & Response Models
│   │   └── analysis.dart            # Analysis & Scores Models
│   ├── services/
│   │   ├── api_service.dart         # Backend API Client
│   │   ├── storage_service.dart     # Local Storage (TODO)
│   │   └── auth_service.dart        # Auth Logic (TODO)
│   ├── providers/
│   │   ├── auth_provider.dart       # User State (TODO)
│   │   ├── questionnaire_provider.dart  # Fragebogen State (TODO)
│   │   └── analysis_provider.dart   # Analysis State (TODO)
│   ├── screens/
│   │   ├── onboarding/              # Onboarding Screens (TODO)
│   │   ├── questionnaire/           # Fragebogen UI (TODO)
│   │   ├── results/                 # Ergebnis-Screens (TODO)
│   │   └── profile/                 # Profil & Settings (TODO)
│   ├── widgets/
│   │   ├── charts/
│   │   │   ├── tachometer.dart      # Score Tachometer (TODO)
│   │   │   └── radar_chart.dart     # Category Radar Chart (TODO)
│   │   └── common/                  # Reusable Widgets (TODO)
│   ├── l10n/                         # Internationalization
│   │   ├── app_de.arb               # Deutsche Texte (TODO)
│   │   └── app_en.arb               # Englische Texte (TODO)
│   └── main.dart                     # App Entry Point (TODO)
├── assets/
│   ├── images/
│   └── fonts/
├── test/                             # Unit & Widget Tests
├── android/                          # Android Config
├── ios/                              # iOS Config
├── web/                              # Web (PWA) Config
└── pubspec.yaml                      # Dependencies
```

---

## 🔌 API Integration Beispiel

```dart
import 'package:redflag_analyzer/services/api_service.dart';
import 'package:redflag_analyzer/models/question.dart';

// API Service initialisieren
final api = ApiService();

// User registrieren
final authResponse = await api.register('test@example.com', 'Test1234');
api.setAccessToken(authResponse.accessToken);

// Alle Fragen abrufen
final questions = await api.getQuestions();
print('${questions.length} Fragen geladen'); // 65

// Analyse erstellen
final analysisRequest = AnalysisCreateRequest(
  responses: [
    QuestionResponse(key: 'father_absence', value: 4),
    QuestionResponse(key: 'feminist_blames_men', value: 5),
    // ... weitere 63 Responses
  ],
);

final analysis = await api.createAnalysis(analysisRequest);
print('Analyse erstellt: ${analysis.id}');

// Analyse freischalten (1 Credit)
final unlockedAnalysis = await api.unlockAnalysis(analysis.id);
print('Score: ${unlockedAnalysis.scoreTotal}'); // z.B. 6.23
```

---

## 🎨 UI/UX Design Prinzipien

- **Material Design 3** für konsistentes Look & Feel
- **Responsive** für Mobile & Web
- **Accessibility** - Screen Reader Support
- **Dark Mode** Support (optional)
- **Animationen** für bessere UX

---

## 📦 Dependencies

### Core
- `provider` - State Management
- `http` / `dio` - HTTP Client
- `shared_preferences` - Local Storage
- `flutter_secure_storage` - Secure Token Storage

### UI & Visualizations
- `fl_chart` - Charts & Graphs
- `syncfusion_flutter_gauges` - Tachometer Widget
- `flutter_form_builder` - Form Handling

### Features
- `pdf` & `printing` - PDF Generation & Export
- `in_app_purchase` - IAP für Credits
- `share_plus` - Native Share Dialog

### Utils
- `intl` - Internationalization (DE/EN)
- `logger` - Logging
- `equatable` - Value Equality

---

## 🧪 Testing

```bash
# Unit Tests
flutter test

# Widget Tests
flutter test test/widgets/

# Integration Tests
flutter drive --target=test_driver/app.dart
```

---

## 🏗️ Build & Deploy

### Android (APK/AAB)
```bash
flutter build apk --release
flutter build appbundle --release
```

### iOS (IPA)
```bash
flutter build ios --release
```

### Web (PWA)
```bash
flutter build web --release
# Deploy zu Vercel/Netlify
```

---

## 🔐 Environment Configuration

Für verschiedene Umgebungen (Dev/Prod):

```bash
# Development
flutter run --dart-define=API_BASE_URL=http://localhost:8000

# Production
flutter run --dart-define=API_BASE_URL=https://api.redflag-analyzer.com
```

---

## 📝 Nächste Implementierungsschritte

1. **main.dart** - App Entry Point mit Theme & Navigation
2. **Localization** - DE/EN Texte für alle 65 Fragen
3. **Auth Provider** - Login/Logout State Management
4. **Questionnaire Screen** - Paginiertes Formular (5 Fragen/Seite)
5. **Results Screen** - Tachometer + Radar Chart + Top 5 Red Flags
6. **PDF Service** - PDF mit Grafiken generieren
7. **IAP Service** - Stripe/Play Store/App Store Integration

---

## 🆘 Troubleshooting

**Problem:** API not reachable  
**Lösung:** Backend läuft? `API_BASE_URL` korrekt gesetzt?

**Problem:** Dependencies nicht gefunden  
**Lösung:** `flutter pub get` ausführen

**Problem:** Build Fehler  
**Lösung:** `flutter clean && flutter pub get`

---

## 📄 License

MIT License
