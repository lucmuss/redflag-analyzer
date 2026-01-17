# 🚀 RedFlag Analyzer - Quick Start Guide

> **Für neuen Computer/WSL Setup** - Komplette Anleitung in 5 Minuten

## 📋 Voraussetzungen

Stelle sicher, dass folgendes installiert ist:
- ✅ WSL2 oder Ubuntu Linux
- ✅ Git
- ✅ Internet-Verbindung

Das wars! Alles andere wird automatisch installiert.

---

## 🎯 Setup in 3 Schritten

### Schritt 1: Repository klonen

```bash
# Clone Repository
git clone https://github.com/YOUR_USERNAME/redflag-analyzer.git
cd redflag-analyzer

# Prüfe ob alle Dateien da sind
ls -la
# Sollte zeigen: backend/, flutter/, README.md, etc.
```

---

### Schritt 2: Backend Setup (5 Minuten)

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

**Was passiert:**
1. ✅ Installiert Python 3.10+
2. ✅ Installiert MongoDB (Docker oder Apt)
3. ✅ Erstellt Virtual Environment
4. ✅ Installiert Dependencies
5. ✅ Generiert `.env` mit Secret Key
6. ✅ Seeded Datenbank mit 65 Fragen

**Interaktiv:**
- MongoDB Installation wählen (Docker empfohlen)
- Tests optional ausführen
- Server direkt starten (optional)

**Bei Problemen:**
- MongoDB startet nicht? → `sudo systemctl start mongod`
- Port 8000 belegt? → `lsof -ti:8000 | xargs kill -9`

---

### Schritt 3: Flutter Setup (5 Minuten)

```bash
cd ../flutter
chmod +x setup.sh
./setup.sh
```

**Was passiert:**
1. ✅ Installiert Flutter SDK (~700MB Download)
2. ✅ Aktiviert Web Support
3. ✅ Installiert Dependencies
4. ✅ Installiert Chrome (falls nötig)
5. ✅ Prüft Backend-Verbindung

**Interaktiv:**
- Flutter Installation bestätigen
- Chrome Installation (optional)
- App direkt starten (optional)

**Bei Problemen:**
- Flutter nicht gefunden? → `export PATH="$HOME/flutter/bin:$PATH"`
- Chrome startet nicht? → Siehe Troubleshooting unten

---

## ▶️ App Starten

### Backend starten (Terminal 1):

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

✅ **Backend läuft auf:** http://localhost:8000
📚 **API Docs:** http://localhost:8000/docs

### Flutter starten (Terminal 2):

```bash
cd flutter
export PATH="$HOME/flutter/bin:$PATH"
flutter run -d chrome
```

✅ **App öffnet im Browser**

---

## ✅ Verifikation

### Backend testen:

```bash
# Health Check
curl http://localhost:8000/health

# Fragen abrufen
curl http://localhost:8000/api/v1/questions | jq length
# Erwarte: 65

# Tests ausführen
cd backend
pytest tests/ -v
# Erwarte: 15/15 passed
```

### Flutter testen:

```bash
cd flutter
flutter test
# Erwarte: 7/7 passed in ~3s
```

---

## 🐛 Troubleshooting

### Backend Probleme:

**MongoDB startet nicht:**
```bash
# Ubuntu/WSL:
sudo systemctl start mongod
sudo systemctl status mongod

# Oder mit Docker:
docker start mongodb-redflag
```

**libssl1.1 fehlt (Ubuntu 22.04):**
```bash
# Setup-Script handled dies automatisch
# Falls manuell:
wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb
```

**Port 8000 belegt:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Dependencies Fehler:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Flutter Probleme:

**Flutter Command not found:**
```bash
export PATH="$HOME/flutter/bin:$PATH"
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Chrome startet nicht (WSL):**
```bash
# Option 1: Windows Chrome nutzen
export CHROME_EXECUTABLE="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"

# Option 2: Linux Chrome installieren
sudo apt update
sudo apt install google-chrome-stable
```

**Dependencies Fehler:**
```bash
cd flutter
flutter pub get
flutter clean
flutter pub get
```

**Build Fehler:**
```bash
flutter clean
flutter pub get
flutter run -d chrome --web-renderer html
```

---

## 📂 Projekt-Struktur verstehen

```
redflag-analyzer/
├── backend/              # Python FastAPI Backend
│   ├── app/             # Source Code
│   ├── tests/           # Backend Tests (15)
│   ├── scripts/         # seed_db.py
│   ├── setup.sh         # Backend Setup Script
│   ├── requirements.txt # Dependencies
│   └── .env             # Config (auto-generiert)
│
├── flutter/              # Flutter Frontend
│   ├── lib/
│   │   ├── screens/     # UI Screens
│   │   ├── services/    # API, Storage, PDF
│   │   ├── providers/   # State Management
│   │   └── l10n/        # Translations (DE/EN)
│   ├── test/            # Flutter Tests (7)
│   ├── web/             # Web Config
│   ├── setup.sh         # Flutter Setup Script
│   └── pubspec.yaml     # Dependencies
│
├── README.md            # Main Documentation
├── QUICK_START.md       # This file
└── DEVELOPMENT_STATUS.md # Detailed Status
```

---

## 🎓 Nächste Schritte

### Nach erfolgreichem Setup:

1. **API erkunden:**
   - Öffne http://localhost:8000/docs
   - Teste `/health`, `/api/v1/questions`
   - Register einen User

2. **App testen:**
   - Registriere einen Account
   - Fülle Fragebogen aus
   - Sieh Results an

3. **Code verstehen:**
   - Lies `DEVELOPMENT_STATUS.md`
   - Check `backend/app/main.py`
   - Check `flutter/lib/main.dart`

4. **Tests ausführen:**
   ```bash
   # Backend:
   cd backend && pytest tests/ -v
   
   # Flutter:
   cd flutter && flutter test
   ```

---

## 💡 Wichtige Commands

### Backend:
```bash
# Start
uvicorn app.main:app --reload

# Tests
pytest tests/ -v

# Datenbank neu seeden
python -m scripts.seed_db

# MongoDB starten
sudo systemctl start mongod           # Apt Installation
docker start mongodb-redflag          # Docker Installation
```

### Flutter:
```bash
# Start
flutter run -d chrome

# Tests
flutter test

# Build für Production
flutter build web --release

# Dependencies updaten
flutter pub get

# Cache löschen
flutter clean
```

---

## 📊 Erwartete Tests Output

### Backend (pytest):
```
===== 15 passed in 2.34s =====
✅ test_health_endpoint
✅ test_register_user
✅ test_login_user
✅ test_get_questions
✅ test_create_analysis
... (15 total)
```

### Flutter (flutter test):
```
00:03 +7: All tests passed!
✅ Score calculation - all 1s should give 0
✅ Score calculation - all 5s should give 10
✅ Score calculation - mixed values
... (7 total)
```

---

## 🎯 Schnell-Übersicht auf neuem Computer

**Absolute Minimum:**
```bash
# 1. Clone
git clone <repo-url> && cd redflag-analyzer

# 2. Backend
cd backend && ./setup.sh && source venv/bin/activate && uvicorn app.main:app --reload &

# 3. Flutter (neues Terminal)
cd flutter && ./setup.sh && flutter run -d chrome
```

**Duration:** ~10 Minuten (abhängig von Internet-Geschwindigkeit)

---

## ✅ Erfolgs-Checkliste

Prüfe diese Punkte nach Setup:

- [ ] Backend läuft auf http://localhost:8000
- [ ] API Docs erreichbar: http://localhost:8000/docs
- [ ] MongoDB läuft (check: `pgrep mongod` oder `docker ps`)
- [ ] 65 Fragen in DB (curl endpoint)
- [ ] Backend Tests passing (15/15)
- [ ] Flutter App startet in Chrome
- [ ] Flutter Tests passing (7/7)
- [ ] Kann User registrieren
- [ ] Kann Fragebogen ausfüllen

**Alles ✅? Gratulation - Setup erfolgreich!** 🎉

---

## 📚 Weitere Dokumentation

- **README.md** - Projekt-Übersicht & Features
- **DEVELOPMENT_STATUS.md** - Vollständiger Status
- **backend/SETUP-WSL.md** - Backend-Details
- **flutter/SETUP-WEB.md** - Flutter-Details
- **API Docs** - http://localhost:8000/docs

---

## 🆘 Hilfe

**Bei Problemen:**
1. Lies Troubleshooting Section oben
2. Check `DEVELOPMENT_STATUS.md`
3. Prüfe Git Issues
4. Check API Logs

**Logs ansehen:**
```bash
# Backend Logs
cd backend
tail -f logs/app.log

# MongoDB Logs
tail -f ~/data/mongodb.log
```

---

## 🎊 Bereit zum Entwickeln!

Nach erfolgreichem Setup kannst du:
- ✅ Features hinzufügen
- ✅ Tests schreiben
- ✅ UI anpassen
- ✅ Backend erweitern
- ✅ Deployen

**Viel Erfolg!** 🚀
