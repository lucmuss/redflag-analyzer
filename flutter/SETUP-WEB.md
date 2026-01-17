# Flutter Web Setup für WSL Ubuntu

## 🚀 Schnellstart (Automatisch)

### 1-Kommando Setup:
```bash
cd flutter && ./setup.sh
```

Das Script macht **alles automatisch**:
- ✅ Prüft/Installiert Flutter
- ✅ Aktiviert Web Support
- ✅ Installiert Dependencies (pub get)
- ✅ Prüft Chrome/Chromium
- ✅ Testet Backend-Verbindung
- ✅ Startet App im Browser (optional)

---

## 📋 Manuelle Installation (falls gewünscht)

### Schritt 1: Flutter installieren
```bash
# Via Snap (empfohlen)
sudo snap install flutter --classic

# Initialisieren
flutter doctor
```

### Schritt 2: Web Support aktivieren
```bash
flutter config --enable-web

# Prüfen
flutter devices
# Sollte "Chrome" oder "Web Server" zeigen
```

### Schritt 3: Dependencies installieren
```bash
cd flutter
flutter pub get
```

### Schritt 4: App im Browser starten
```bash
# Backend muss laufen!
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

---

## 🌐 Flutter Web - Ja, das funktioniert!

Flutter kompiliert zu **JavaScript/WebAssembly** und läuft in jedem modernen Browser!

**Vorteile:**
- ✅ Gleicher Code für Mobile + Web
- ✅ Keine zusätzliche Installation nötig
- ✅ Schnelle Entwicklung (Hot Reload)
- ✅ Native Performance im Browser

**Nachteile:**
- ⚠️ Größere Bundle Size als native Web-App
- ⚠️ SEO nicht optimal (SPA)

---

## 🔧 Nützliche Befehle

### Development
```bash
# App starten (Chrome)
flutter run -d chrome

# Mit Backend URL
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000

# Hot Reload: 'r' drücken
# Hot Restart: 'R' drücken
# Quit: 'q' drücken
```

### Devices
```bash
# Verfügbare Geräte
flutter devices

# Erwartete Ausgabe:
# Chrome (web)   • chrome   • web-javascript • Google Chrome ...
# Web Server (web) • web-server • web-javascript • Flutter Tools
```

### Build
```bash
# Production Build
flutter build web --release

# Mit optimierungen
flutter build web --release --web-renderer html

# Output in: build/web/
```

### Debugging
```bash
# Pub Dependencies aktualisieren
flutter pub get

# Cache löschen
flutter clean

# Pub upgrade
flutter pub upgrade

# Analyze Code
flutter analyze
```

---

## 🐛 Troubleshooting

### Problem: "flutter: command not found"
```bash
# Flutter via Snap installieren
sudo snap install flutter --classic

# Environment neu laden
source ~/.bashrc
```

### Problem: "Chrome not available"
```bash
# Chrome installieren
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable
```

### Problem: "Web is not enabled"
```bash
flutter config --enable-web
flutter doctor
```

### Problem: "Cannot connect to backend"
```bash
# Prüfe ob Backend läuft
curl http://localhost:8000/health

# Starte Backend (in anderem Terminal)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Problem: "Hot Reload funktioniert nicht"
```bash
# Neustart mit --web-renderer
flutter run -d chrome --web-renderer html

# Oder kompletter Rebuild
flutter clean
flutter pub get
flutter run -d chrome
```

---

## 📊 Flutter Web vs Native App

| Feature | Web | Mobile |
|---------|-----|--------|
| Installation | ❌ Keine | ✅ App Store |
| Performance | 🟡 Gut | 🟢 Exzellent |
| Bundle Size | 🔴 ~2MB | 🟡 10-20MB |
| Offline | 🟡 PWA | ✅ Nativ |
| Updates | 🟢 Sofort | 🟡 Store Review |
| Development | 🟢 Hot Reload | 🟢 Hot Reload |

**Für Testing: Web ist perfekt!** ✅

---

## 🎯 Production Deployment

### Build für Production
```bash
cd flutter
flutter build web --release --web-renderer html

# Output: build/web/
```

### Deploy auf Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd build/web
vercel --prod
```

### Deploy auf Firebase Hosting
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Init
firebase init hosting

# Deploy
firebase deploy
```

---

## ✅ Pre-Flight Checklist

Vor dem Start prüfen:

- [ ] Flutter installiert (`flutter --version`)
- [ ] Web Support aktiviert (`flutter devices` zeigt Chrome)
- [ ] Dependencies installiert (`flutter pub get`)
- [ ] Chrome/Chromium installiert
- [ ] **Backend läuft** (`curl http://localhost:8000/health`)

**Wenn alles ✅:** `flutter run -d chrome`

---

## 🚀 Quick Start Commands

```bash
# Alles auf einmal (Empfohlen)
cd flutter && ./setup.sh

# Oder manuell
cd flutter
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

---

## 📖 Weitere Infos

- **Flutter Docs:** https://docs.flutter.dev/get-started/web
- **pubspec.yaml** - Dependencies
- **lib/main.dart** - App Entry Point
- **lib/config/app_config.dart** - API Configuration

**Happy Coding! 🎨**
