#!/bin/bash

# RedFlag Analyzer Flutter Setup Script für WSL Ubuntu
# Dieses Script automatisiert das komplette Flutter-Setup

set -e  # Exit on error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging Funktionen
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Banner
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   RedFlag Analyzer Flutter Setup (WSL Ubuntu)            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Schritt 1: Prüfe Flutter Installation
log_info "Prüfe Flutter Installation..."
if ! command -v flutter &> /dev/null; then
    log_warning "Flutter ist nicht installiert!"
    echo ""
    log_info "Snap funktioniert nicht in WSL - verwende manuelle Installation"
    read -p "Möchtest du Flutter jetzt installieren? (j/n): " install_flutter
    
    if [ "$install_flutter" = "j" ] || [ "$install_flutter" = "J" ]; then
        log_info "Installiere Flutter manuell..."
        
        # Save current directory
        FLUTTER_APP_DIR=$(pwd)
        
        # Download Flutter SDK
        cd ~
        log_info "Lade Flutter SDK herunter (~700MB)..."
        wget -q --show-progress https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
        
        # Extract
        log_info "Entpacke Flutter..."
        tar xf flutter_linux_3.16.0-stable.tar.xz
        rm flutter_linux_3.16.0-stable.tar.xz
        
        # Add to PATH
        log_info "Füge Flutter zu PATH hinzu..."
        if ! grep -q 'flutter/bin' ~/.bashrc; then
            echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
        fi
        export PATH="$HOME/flutter/bin:$PATH"
        
        # Run flutter doctor
        log_info "Initialisiere Flutter..."
        flutter doctor
        
        log_success "Flutter installiert in ~/flutter!"
        
        # Return to app directory
        cd "$FLUTTER_APP_DIR"
    else
        log_error "Flutter wird benötigt! Installiere es manuell:"
        echo "  wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz"
        echo "  tar xf flutter_linux_3.16.0-stable.tar.xz"
        echo "  echo 'export PATH=\"\$HOME/flutter/bin:\$PATH\"' >> ~/.bashrc"
        exit 1
    fi
else
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    log_success "Flutter gefunden: $FLUTTER_VERSION"
fi

# Schritt 2: Flutter Doctor
log_info "Prüfe Flutter Umgebung..."
flutter doctor

# Schritt 3: Web Support aktivieren
log_info "Aktiviere Flutter Web Support..."
flutter config --enable-web
log_success "Web Support aktiviert!"

# Schritt 4: Erstelle l10n Verzeichnis und Dateien (falls nicht vorhanden)
log_info "Prüfe Lokalisierungs-Setup..."
if [ ! -d "lib/l10n" ]; then
    log_info "Erstelle l10n Verzeichnis..."
    mkdir -p lib/l10n
fi

if [ ! -f "lib/l10n/app_de.arb" ]; then
    log_info "Erstelle Standard-Lokalisierungsdatei..."
    cat > lib/l10n/app_de.arb << 'EOF'
{
  "@@locale": "de",
  "appTitle": "RedFlag Analyzer",
  "@appTitle": {
    "description": "Der Titel der Anwendung"
  },
  "welcome": "Willkommen",
  "@welcome": {
    "description": "Begrüßungstext"
  },
  "startAnalysis": "Analyse starten",
  "@startAnalysis": {
    "description": "Button-Text zum Starten der Analyse"
  },
  "questions": "Fragen",
  "@questions": {
    "description": "Fragen-Titel"
  },
  "results": "Ergebnisse",
  "@results": {
    "description": "Ergebnisse-Titel"
  },
  "yes": "Ja",
  "@yes": {
    "description": "Ja-Antwort"
  },
  "no": "Nein",
  "@no": {
    "description": "Nein-Antwort"
  },
  "next": "Weiter",
  "@next": {
    "description": "Weiter-Button"
  },
  "back": "Zurück",
  "@back": {
    "description": "Zurück-Button"
  },
  "submit": "Absenden",
  "@submit": {
    "description": "Absenden-Button"
  },
  "cancel": "Abbrechen",
  "@cancel": {
    "description": "Abbrechen-Button"
  }
}
EOF
    log_success "Lokalisierungsdatei erstellt!"
fi

# Schritt 5: Installiere Dependencies
log_info "Installiere Flutter Dependencies..."
if [ -f "pubspec.yaml" ]; then
    flutter pub get
    log_success "Dependencies installiert!"
else
    log_error "pubspec.yaml nicht gefunden!"
    exit 1
fi

# Schritt 5: Chrome/Chromium Check (für Web)
log_info "Prüfe Browser für Flutter Web..."
if command -v google-chrome &> /dev/null; then
    log_success "Google Chrome gefunden!"
elif command -v chromium-browser &> /dev/null; then
    log_success "Chromium gefunden!"
else
    log_warning "Kein Chrome/Chromium gefunden!"
    log_info "Flutter Web benötigt Chrome. Installiere Chrome..."
    
    read -p "Chrome installieren? (j/n): " install_chrome
    if [ "$install_chrome" = "j" ] || [ "$install_chrome" = "J" ]; then
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        sudo apt update
        sudo apt install -y google-chrome-stable
        log_success "Chrome installiert!"
    fi
fi

# Schritt 6: Prüfe Backend Connection
log_info "Prüfe Backend Verbindung..."
BACKEND_URL="http://localhost:8000"

if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    log_success "Backend läuft auf $BACKEND_URL"
else
    log_warning "Backend läuft NICHT!"
    log_info "Bitte starte das Backend in einem anderen Terminal:"
    echo -e "  ${YELLOW}cd backend && source venv/bin/activate && uvicorn app.main:app --reload${NC}"
    echo ""
    read -p "Backend läuft bereits? Drücke Enter zum Fortfahren..."
fi

# Fertig!
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
echo -e "║   ✓ Flutter Setup erfolgreich abgeschlossen!            ║"
echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Flutter App starten:"
echo -e "  ${YELLOW}flutter run -d chrome${NC}"
echo -e "  ${BLUE}# Oder spezifischer:${NC}"
echo -e "  ${YELLOW}flutter run -d chrome --web-renderer html${NC}"
echo ""
log_info "Nützliche Befehle:"
echo -e "  ${YELLOW}flutter devices${NC}                 # Verfügbare Geräte"
echo -e "  ${YELLOW}flutter pub get${NC}                 # Dependencies aktualisieren"
echo -e "  ${YELLOW}flutter clean${NC}                   # Build-Cache löschen"
echo -e "  ${YELLOW}flutter build web${NC}               # Production Build"
echo ""

# Frage ob App direkt gestartet werden soll
read -p "Möchtest du die App jetzt im Browser starten? (j/n): " start_app
if [ "$start_app" = "j" ] || [ "$start_app" = "J" ]; then
    log_info "Starte Flutter App im Browser..."
    echo -e "${YELLOW}Drücke 'q' zum Beenden${NC}"
    echo ""
    
    # Setze Backend URL via dart-define
    flutter run -d chrome \
        --web-renderer html \
        --dart-define=API_BASE_URL=http://localhost:8000
fi
