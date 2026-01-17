# Backend Setup für WSL Ubuntu

## 🚀 Schnellstart (Automatisch)

### 1-Kommando Setup:
```bash
cd backend && ./setup.sh
```

Das Script macht **alles automatisch**:
- ✅ Prüft/Installiert Python3
- ✅ Prüft/Installiert MongoDB
- ✅ Erstellt Virtual Environment
- ✅ Installiert alle Dependencies
- ✅ Generiert .env Datei mit SECRET_KEY
- ✅ Startet MongoDB
- ✅ Initialisiert Datenbank (65 Fragen)
- ✅ Führt Tests aus (optional)
- ✅ Startet Backend-Server (optional)

---

## 📋 Manuelle Installation (falls gewünscht)

### Schritt 1: Python & MongoDB installieren
```bash
# Python3
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
```

### Schritt 2: Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Schritt 3: Konfiguration
```bash
# .env erstellen
cp .env.example .env

# SECRET_KEY generieren
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env

# .env bearbeiten (optional)
nano .env
```

### Schritt 4: MongoDB starten
```bash
# Datenverzeichnis erstellen
mkdir -p ~/data/db

# MongoDB starten
mongod --dbpath ~/data/db --fork --logpath ~/data/mongodb.log
```

### Schritt 5: Datenbank initialisieren
```bash
source venv/bin/activate
python -m scripts.seed_db
```

### Schritt 6: Backend starten
```bash
uvicorn app.main:app --reload
```

**Backend läuft:** http://localhost:8000/docs

---

## 🧪 Tests ausführen

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Erwartete Ausgabe:** 17 Tests passed

---

## 🔧 Nützliche Befehle

### MongoDB
```bash
# Status prüfen
pgrep -x mongod

# Stoppen
pkill mongod

# Logs ansehen
tail -f ~/data/mongodb.log

# Datenbank löschen (Reset)
rm -rf ~/data/db/*
python -m scripts.seed_db
```

### Backend
```bash
# Server starten
uvicorn app.main:app --reload

# Server mit anderem Port
uvicorn app.main:app --reload --port 8080

# Tests mit Coverage
pytest tests/ --cov=app --cov-report=html

# Dependencies aktualisieren
pip install -r requirements.txt --upgrade
```

### Virtual Environment
```bash
# Aktivieren
source venv/bin/activate

# Deaktivieren
deactivate

# Neu erstellen
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### Problem: MongoDB startet nicht
```bash
# Prüfe ob Port 27017 belegt ist
sudo lsof -i :27017

# Stoppe alte Instanz
pkill mongod

# Starte neu
mongod --dbpath ~/data/db
```

### Problem: Import Errors
```bash
# Virtual Environment prüfen
which python  # Sollte .../venv/bin/python sein

# Dependencies neu installieren
pip install -r requirements.txt --force-reinstall
```

### Problem: .env Fehler
```bash
# .env Format prüfen
cat .env

# Neu erstellen
rm .env
./setup.sh
```

### Problem: Port 8000 bereits belegt
```bash
# Prüfe welcher Prozess Port 8000 nutzt
sudo lsof -i :8000

# Stoppe Prozess
kill -9 <PID>

# Oder starte auf anderem Port
uvicorn app.main:app --reload --port 8080
```

---

## 📊 API Testen

### Swagger UI (empfohlen)
```
http://localhost:8000/docs
```

### cURL Beispiele
```bash
# Health Check
curl http://localhost:8000/health

# Fragen abrufen
curl http://localhost:8000/api/v1/questions

# User registrieren
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'
```

---

## 🎯 Produktions-Deployment

Für Production siehe:
- **Dockerfile** - Container Build
- **docker-compose.yml** - Lokales Setup
- **render.yaml** - Render.com Deployment

```bash
# Docker Build
cd backend
docker build -t redflag-backend .

# Docker Run
docker run -p 8000:8000 redflag-backend
```

---

## 📖 Weitere Dokumentation

- **README.md** - Haupt-Dokumentation
- **QUICKSTART.md** - Quick Start Guide
- **IMPLEMENTATION_STATUS.md** - Feature-Übersicht
- **requirements.txt** - Python Dependencies

---

## ✅ Checkliste

Nach erfolgreichem Setup solltest du haben:

- [ ] Python 3.10+ installiert
- [ ] MongoDB läuft
- [ ] Virtual Environment aktiviert
- [ ] Dependencies installiert
- [ ] .env Datei erstellt
- [ ] Datenbank initialisiert (65 Fragen)
- [ ] Tests laufen durch (17 passed)
- [ ] Backend erreichbar unter http://localhost:8000/docs

**Happy Coding! 🚀**
