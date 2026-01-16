# 🚀 RedFlag Analyzer - Quickstart Guide

## Backend sofort starten (5 Minuten)

### 1️⃣ MongoDB starten (Docker)

```bash
# MongoDB Container starten
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Prüfen ob läuft
docker ps | grep mongodb
```

### 2️⃣ Backend Setup

```bash
cd backend

# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 3️⃣ Konfiguration

```bash
# .env Datei erstellen
cp .env.example .env

# SECRET_KEY generieren und in .env einfügen
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Wichtig:** Kopiere den generierten Key in `.env` bei `SECRET_KEY=...`

### 4️⃣ Datenbank mit Fragen füllen

```bash
# Seed-Script ausführen (importiert alle 65 Fragen)
python -m scripts.seed_db

# Erwartete Ausgabe:
# ✅ Database seeding completed successfully!
# Total questions in database: 65
```

### 5️⃣ API starten

```bash
# Development Server starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Oder direkt via Python
python -m app.main
```

✅ **API läuft jetzt auf:** http://localhost:8000

---

## 📝 API Testen

### Swagger UI (interaktive Dokumentation)

Öffne: http://localhost:8000/docs

### cURL Beispiele

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. User registrieren
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

#### 3. Login (JWT Token erhalten)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'

# Antwort speichern:
# {"access_token":"eyJ...", "token_type":"bearer"}
```

#### 4. Fragen abrufen
```bash
curl http://localhost:8000/api/v1/questions
```

#### 5. Analyse erstellen (mit JWT Token)
```bash
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DEIN_JWT_TOKEN_HIER" \
  -d '{
    "responses": [
      {"key": "father_absence", "value": 4},
      {"key": "bad_father_relationship", "value": 2},
      {"key": "feminist_blames_men", "value": 5}
    ]
  }'

# Antwort: {"_id":"...", "is_unlocked":false, "created_at":"..."}
```

#### 6. Analyse freischalten (1 Credit)
```bash
curl -X POST http://localhost:8000/api/v1/analyses/ANALYSIS_ID/unlock \
  -H "Authorization: Bearer DEIN_JWT_TOKEN_HIER"

# Antwort: Vollständiges Ergebnis mit Scores!
```

---

## 🧪 Tests ausführen

```bash
# Unit Tests für Score-Berechnung
pytest backend/tests/test_score.py -v

# Mit Coverage
pytest backend/tests/ --cov=app --cov-report=html

# Coverage Report öffnen
open htmlcov/index.html
```

**Erwartete Coverage:** ≥80%

---

## 🔍 Debugging

### MongoDB Daten prüfen

```bash
# MongoDB Shell öffnen
docker exec -it mongodb mongosh

# In der Shell:
use redflag_analyzer
db.questions.countDocuments()  # Sollte 65 sein
db.users.find().pretty()
db.analyses.find().pretty()
```

### Logs anschauen

```bash
# API läuft mit Live-Logging
# Alle Requests werden mit Timing geloggt
```

### Häufige Fehler

**Problem:** `SECRET_KEY not set`
- **Lösung:** `.env` Datei erstellen und SECRET_KEY setzen

**Problem:** `MongoDB connection failed`
- **Lösung:** `docker ps` prüfen, MongoDB läuft?

**Problem:** `No questions found`
- **Lösung:** Seed-Script ausführen: `python -m scripts.seed_db`

---

## 📊 API Endpoints Übersicht

### Auth
- `POST /api/v1/auth/register` - User registrieren
- `POST /api/v1/auth/login` - Login (JWT Token)
- `GET /api/v1/auth/me` - Aktueller User

### Questions
- `GET /api/v1/questions` - Alle Fragen (65 Stück)
- `GET /api/v1/questions/{key}` - Eine Frage
- `GET /api/v1/questions/category/{category}` - Fragen nach Kategorie

### Analyses
- `POST /api/v1/analyses` - Neue Analyse erstellen (locked)
- `POST /api/v1/analyses/{id}/unlock` - Analyse freischalten (1 Credit)
- `GET /api/v1/analyses/{id}` - Analyse abrufen
- `GET /api/v1/analyses` - Alle User-Analysen (Pagination)

### Users
- `GET /api/v1/users/me` - User Profil
- `PUT /api/v1/users/me` - Profil aktualisieren

---

## 🎯 Nächste Schritte

1. **Frontend:** Flutter App entwickeln
2. **IAP:** Stripe Integration für Credits
3. **PDF:** Export-Funktionalität
4. **Deploy:** Render.com / Fly.io

---

## 🆘 Support

- **Logs:** Prüfe Terminal-Output
- **Swagger UI:** http://localhost:8000/docs
- **MongoDB:** `docker logs mongodb`

Happy Coding! 🚀
