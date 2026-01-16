# RedFlag Analyzer - Production-Ready App

## 🎯 Projektübersicht

Eine Cross-Platform App (iOS/Android/Web PWA) zur objektiven Bewertung von Beziehungs-Red Flags basierend auf einem 65-Fragen-Fragebogen. Fokus auf Privacy, Viral Growth und Passive Income durch Freemium-Modell.

---

## 🏗️ Architektur-Diagramm (High-Level)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   Flutter Web    │  │  Flutter Mobile  │  │   Flutter    │ │
│  │     (PWA)        │  │   (iOS/Android)  │  │    Shared    │ │
│  │                  │  │                  │  │    Widgets   │ │
│  │  • Vercel Deploy │  │  • IAP Support   │  │  • Material  │ │
│  │  • Responsive    │  │  • Native Share  │  │  • Charts    │ │
│  │  • Offline First │  │  • Push Notif.   │  │  • PDF Gen   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           └────────────┬─────────┘                   │          │
│                        │    HTTP/REST (JSON)         │          │
└────────────────────────┼─────────────────────────────┼──────────┘
                         │                             │
                    ┌────▼─────────────────────────────▼─────┐
                    │        API GATEWAY / LOAD BALANCER      │
                    │              (Nginx/Render)             │
                    └────┬────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                       BACKEND LAYER                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              FastAPI (Python 3.11+)                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │   Auth API   │  │  Analysis API │  │  Payment API     │ │ │
│  │  │              │  │               │  │                  │ │ │
│  │  │ • JWT Tokens │  │ • Score Calc  │  │ • Stripe Webhks │ │ │
│  │  │ • Email Ver. │  │ • PDF Export  │  │ • IAP Validate  │ │ │
│  │  │ • Rate Limit │  │ • Caching     │  │ • Credit Mgmt   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │  User API    │  │ Question API  │  │  Community API   │ │ │
│  │  │              │  │               │  │                  │ │ │
│  │  │ • Profile    │  │ • CRUD        │  │ • Weight Aggr.  │ │ │
│  │  │ • History    │  │ • i18n        │  │ • Gamification  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Business Logic Layer                        │ │
│  │  • Pydantic Models (Validation)                             │ │
│  │  • Score Calculation Engine (weighted avg)                  │ │
│  │  • Security: bcrypt, JWT, input sanitization                │ │
│  │  • Error Handling: Centralized logger                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────┐
│                       DATA LAYER                                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               MongoDB Atlas (NoSQL)                         │ │
│  │                                                             │ │
│  │  Collections:                                               │ │
│  │  • users         {email, password_hash, credits, profile}  │ │
│  │  • questions     {key, category, default_weight}           │ │
│  │  • analyses      {user_id, responses, scores, unlocked}    │ │
│  │  • weights       {user_id, question_key, weight}           │ │
│  │                                                             │ │
│  │  Indexes: email(unique), key(unique), user_id+created_at   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                  
┌────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                               │
├────────────────────────────────────────────────────────────────────┤
│  • Stripe (Payments/Webhooks)  • SendGrid (Email)                 │
│  • App Store Connect (IAP)      • Google Play Billing             │
│  • Firebase (Push Notifications - optional)                       │
│  • Sentry (Error Tracking - optional)                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Projektstruktur (Monorepo)

```
redflag-analyzer/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI App Entry
│   │   ├── config.py                 # Environment Config
│   │   ├── database.py               # MongoDB Connection
│   │   ├── models/                   # Pydantic Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── question.py
│   │   │   ├── analysis.py
│   │   │   └── payment.py
│   │   ├── routes/                   # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── questions.py
│   │   │   ├── analyses.py
│   │   │   └── payments.py
│   │   ├── services/                 # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── score_calculator.py
│   │   │   ├── pdf_generator.py
│   │   │   └── email_service.py
│   │   ├── utils/                    # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # JWT, bcrypt
│   │   │   ├── validators.py
│   │   │   └── logger.py
│   │   └── middleware/               # Custom Middleware
│   │       ├── __init__.py
│   │       ├── rate_limiter.py
│   │       └── error_handler.py
│   ├── scripts/
│   │   └── seed_db.py                # Import Questions CSV
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_score.py
│   │   └── test_api.py
│   ├── requirements.txt              # Python Dependencies
│   ├── Dockerfile                    # Backend Container
│   └── .env.example
│
├── flutter/                          # Flutter App
│   ├── lib/
│   │   ├── main.dart                 # App Entry Point
│   │   ├── config/
│   │   │   └── app_config.dart       # API URLs, Constants
│   │   ├── models/                   # Data Models
│   │   │   ├── user.dart
│   │   │   ├── question.dart
│   │   │   ├── analysis.dart
│   │   │   └── category.dart
│   │   ├── services/                 # API & Business Logic
│   │   │   ├── api_service.dart      # HTTP Client
│   │   │   ├── auth_service.dart
│   │   │   ├── storage_service.dart  # Local Storage
│   │   │   ├── iap_service.dart      # In-App Purchase
│   │   │   └── pdf_service.dart
│   │   ├── screens/                  # UI Screens
│   │   │   ├── onboarding/
│   │   │   ├── questionnaire/
│   │   │   ├── results/
│   │   │   ├── profile/
│   │   │   └── community/
│   │   ├── widgets/                  # Reusable Widgets
│   │   │   ├── charts/
│   │   │   │   ├── tachometer.dart
│   │   │   │   └── radar_chart.dart
│   │   │   ├── custom_button.dart
│   │   │   └── question_card.dart
│   │   ├── providers/                # State Management
│   │   │   ├── auth_provider.dart
│   │   │   ├── questionnaire_provider.dart
│   │   │   └── analysis_provider.dart
│   │   ├── l10n/                     # Internationalization
│   │   │   ├── app_de.arb
│   │   │   └── app_en.arb
│   │   ├── theme/
│   │   │   └── app_theme.dart        # Material Design 3
│   │   └── utils/
│   │       ├── validators.dart
│   │       └── constants.dart
│   ├── assets/
│   │   ├── images/
│   │   └── fonts/
│   ├── test/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── widget/
│   ├── pubspec.yaml                  # Flutter Dependencies
│   ├── android/                      # Android Config
│   ├── ios/                          # iOS Config
│   └── web/                          # Web PWA Config
│
├── docs/
│   ├── API.md                        # API Documentation
│   ├── DEPLOYMENT.md                 # Deployment Guide
│   └── ARCHITECTURE.md               # Detailed Architecture
│
├── scripts/
│   ├── deploy_backend.sh
│   └── deploy_flutter.sh
│
├── seed_data/
│   └── questions.json                # 65 Questions Master Data
│
├── .github/
│   └── workflows/
│       ├── backend_ci.yml            # Backend CI/CD
│       └── flutter_ci.yml            # Flutter CI/CD
│
├── docker-compose.yml                # Local Development
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔢 Score-Berechnungs-Mathematik

### Eingabeskalen
- **Antworten**: 1-5 (1 = "Trifft gar nicht zu", 5 = "Trifft voll zu")
- **Gewichtungen**: 1-5 (1 = "Unwichtig", 5 = "Dealbreaker")

### Formeln

```python
# 1. Response-Faktor berechnen (0-10 Skala)
def calculate_factor(response: int) -> float:
    """Konvertiert 1-5 Response zu 0-10 Faktor"""
    return (response - 1) * 2.5

# 2. Gewichteter Durchschnitt
def calculate_score(responses: List[Response], weights: Dict[str, int]) -> float:
    """
    Total Score = SUM(factor * weight) / SUM(weight)
    
    Beispiel:
    - Frage 1: Response=5, Weight=4 → Factor=10, Weighted=40
    - Frage 2: Response=1, Weight=2 → Factor=0,  Weighted=0
    Total = (40 + 0) / (4 + 2) = 6.67
    """
    weighted_sum = 0
    total_weight = 0
    
    for response in responses:
        factor = calculate_factor(response.value)
        weight = weights.get(response.key, 3)  # Default=3
        weighted_sum += factor * weight
        total_weight += weight
    
    return weighted_sum / total_weight if total_weight > 0 else 0

# 3. Kategorie-Scores (gleiches Prinzip, gruppenweise)
def calculate_category_scores(responses, weights, categories):
    category_scores = {}
    for category in categories:
        category_responses = [r for r in responses if r.category == category]
        category_scores[category] = calculate_score(category_responses, weights)
    return category_scores
```

### Legacy-Daten Migration
```python
# Alte 1-10 Skala zu neue 1-5 Skala
def convert_old_weight(old_weight: int) -> int:
    """Konvertiert 1-10 zu 1-5"""
    return math.ceil(old_weight / 2)
```

---

## 💰 Business Modell & Monetarisierung

### Freemium Mechanik
1. **Neue User**: 1 gratis Credit bei Registration
2. **Weitere Analysen**: 5€ per Analysis (Consumable IAP)
3. **Unlocked Features**:
   - Vollständige Score-Visualisierung (Tachometer)
   - Detaillierter Radar Chart
   - PDF Export mit Top 5 Red Flags
   - Share-Funktionalität

### Viral Hooks
- PDF Watermark: "Generiert von RedFlag Analyzer – Teste deinen Partner gratis!"
- Deep Links für Einladungen
- Anonyme Nutzung ohne Login (reduziert Barriere)

### Conversion Funnel
```
Guest User → Fragebogen → Ergebnis-Teaser (verschwommen) 
  → CTA "Registrieren & Freischalten" → Erste Analyse gratis 
  → Zweite Analyse → Purchase Prompt (5€) → Upsell
```

---

## 🔐 Sicherheit & Best Practices

### Backend Security
- ✅ JWT mit 1h Expiry + Refresh Tokens
- ✅ bcrypt für Passwort-Hashing (cost factor: 12)
- ✅ Rate Limiting: 100 req/min per IP
- ✅ Input Validation (Pydantic)
- ✅ HTTPS Only (HSTS Header)
- ✅ CORS mit Whitelist
- ✅ SQL Injection: N/A (NoSQL mit Parameterisierung)
- ✅ XSS Prevention: Sanitization bei PDF Export

### Frontend Security
- ✅ Secure Storage für JWT (flutter_secure_storage)
- ✅ HTTPS für alle API Calls
- ✅ Certificate Pinning (optional für v2)

---

## 🌍 Internationalisierung (i18n)

### Unterstützte Sprachen
- Deutsch (de) - Primär
- Englisch (en) - Sekundär

### Implementierung
- **Flutter**: ARB-Dateien (`app_de.arb`, `app_en.arb`) mit `intl` Package
- **Backend**: Nur Keys speichern (z.B. "father_absence"), Texte bleiben in App
- **Auto-Detection**: Device Locale on first start
- **Fallback**: EN wenn DE nicht verfügbar

---

## 📊 Datenbank-Schema (MongoDB)

### Collections

#### 1. users
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "is_verified": false,
  "profile": {
    "age": 28,
    "country": "DE",
    "gender": "male"
  },
  "credits": 1
}
```
**Indexes**: `email` (unique), `created_at`

#### 2. questions
```json
{
  "_id": ObjectId,
  "key": "father_absence",
  "category": "DYNAMICS",
  "default_weight": 3
}
```
**Indexes**: `key` (unique)

#### 3. analyses
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "is_unlocked": true,
  "responses": [
    {"key": "father_absence", "value": 4},
    {"key": "bad_father_relationship", "value": 2}
  ],
  "snapshot_weights": {
    "father_absence": 5,
    "bad_father_relationship": 4
  },
  "score_total": 6.23,
  "category_scores": {
    "TRUST": 5.1,
    "BEHAVIOR": 7.8,
    "VALUES": 6.0,
    "DYNAMICS": 5.9
  },
  "created_at": ISODate("2024-01-15T12:00:00Z")
}
```
**Indexes**: `user_id + created_at`

#### 4. community_weights (für Aggregation)
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "question_key": "father_absence",
  "weight": 5,
  "submitted_at": ISODate("2024-01-15T12:00:00Z")
}
```
**Indexes**: `question_key`, `submitted_at`

---

## 🧪 Testing-Strategie

### Coverage Ziel: ≥80%

#### Backend Tests (pytest)
```bash
backend/tests/
├── test_auth.py           # JWT, Login, Registration
├── test_score.py          # Score Calculation Unit Tests
├── test_api.py            # Integration Tests (API Endpoints)
└── test_validators.py     # Input Validation
```

#### Flutter Tests
```bash
flutter/test/
├── unit/
│   ├── score_test.dart
│   └── validation_test.dart
├── widget/
│   ├── question_card_test.dart
│   └── chart_test.dart
└── integration/
    └── questionnaire_flow_test.dart
```

### Edge Cases
- Division by Zero (alle weights = 0)
- Offline-Modus
- Low Credits (Payment Flow)
- Invalid JWT
- Fehlende Fragen-Texte (Fallback zu EN)

---

## 🚀 Deployment-Architektur

### Backend (FastAPI)
- **Hosting**: Render.com / Fly.io (Auto-Scaling)
- **Container**: Docker (Python 3.11-slim)
- **Database**: MongoDB Atlas (Shared Cluster → M10 bei Skalierung)
- **CDN**: Cloudflare (für PDF Caching optional)

### Flutter
- **Mobile**: App Store + Google Play (via Fastlane)
- **Web**: Vercel / Netlify (PWA mit Service Worker)
- **CI/CD**: GitHub Actions
  - Lint: `flutter analyze`, `flake8`
  - Test: `flutter test`, `pytest`
  - Build: APK/AAB/IPA + Web Bundle

---

## 📈 Implementierungs-Roadmap

### Phase 1: MVP Backend (Woche 1-2)
- [x] Projektstruktur Setup
- [ ] MongoDB Connection + Models
- [ ] Auth API (JWT, Register, Login)
- [ ] Questions API + Seed Script
- [ ] Analysis API (Submit, Calculate Score)
- [ ] Unit Tests (≥80% Coverage)

### Phase 2: MVP Frontend (Woche 3-4)
- [ ] Flutter Setup + Navigation
- [ ] Onboarding + Guest Mode
- [ ] Fragebogen UI (65 Fragen, Pagination)
- [ ] Ergebnis-Screen (Tachometer, Radar Chart)
- [ ] Lokalisierung (DE/EN)

### Phase 3: Premium Features (Woche 5-6)
- [ ] IAP Integration (Stripe + App Store)
- [ ] PDF Export
- [ ] Share-Funktionalität
- [ ] Payment Webhooks (Credit Management)

### Phase 4: Polish & Launch (Woche 7-8)
- [ ] Offline-Modus
- [ ] Performance-Optimierung
- [ ] A/B Testing (optional)
- [ ] Beta Testing (TestFlight, Google Play Beta)
- [ ] App Store Submission

---

## 🛠️ Tech Stack Zusammenfassung

| Layer | Technologie | Zweck |
|-------|-------------|-------|
| **Frontend** | Flutter 3.x | Cross-Platform UI |
| **State Mgmt** | Provider/Riverpod | Reactive State |
| **Backend** | FastAPI (Python 3.11+) | REST API |
| **Database** | MongoDB (Motor) | NoSQL Persistence |
| **Auth** | JWT + bcrypt | Secure Sessions |
| **Payments** | Stripe + IAP | Monetization |
| **Charts** | fl_chart | Visualizations |
| **PDF** | pdf (Flutter) | Export |
| **i18n** | flutter_intl | Localization |
| **CI/CD** | GitHub Actions | Automation |
| **Hosting** | Render + Vercel | Production Deploy |

---

## 📝 Nächste Schritte

1. ✅ Projektstruktur erstellt
2. → **Backend Setup starten** (MongoDB + FastAPI)
3. → Seed Script für 65 Fragen
4. → Auth + Core APIs
5. → Flutter UI Prototyp

---

## 📄 Lizenz

MIT License - Siehe LICENSE Datei

---

**Status**: 🚧 In Entwicklung | **Version**: 0.1.0 (MVP)
