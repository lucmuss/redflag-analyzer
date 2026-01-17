#!/bin/bash

# RedFlag Analyzer Flutter Setup Script für WSL Ubuntu
# Dieses Script automatisiert das komplette Flutter-Setup

# Hinweis: set -e wird NICHT verwendet, damit wir Fehler manuell behandeln können

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

# Schritt 0: Prüfe und installiere benötigte Tools
log_info "Prüfe benötigte System-Tools..."

# Prüfe unzip
if ! command -v unzip &> /dev/null; then
    log_warning "unzip ist nicht installiert (wird für Flutter Upgrade benötigt)"
    read -p "Möchtest du unzip installieren? (j/n): " install_unzip
    if [ "$install_unzip" = "j" ] || [ "$install_unzip" = "J" ]; then
        log_info "Installiere unzip..."
        sudo apt update
        sudo apt install -y unzip
        log_success "unzip installiert!"
    else
        log_warning "unzip nicht installiert - Flutter Upgrade wird nicht funktionieren"
    fi
else
    log_success "unzip gefunden!"
fi

# Prüfe curl und wget
if ! command -v curl &> /dev/null; then
    log_warning "curl ist nicht installiert"
    sudo apt install -y curl
fi

if ! command -v wget &> /dev/null; then
    log_warning "wget ist nicht installiert"
    sudo apt install -y wget
fi

# Schritt 0.5: Installiere Linux toolchain für Flutter Desktop Support
log_info "Prüfe Linux toolchain für Flutter Desktop Development..."

MISSING_TOOLS=()
if ! command -v clang++ &> /dev/null; then
    MISSING_TOOLS+=("clang")
fi
if ! command -v cmake &> /dev/null; then
    MISSING_TOOLS+=("cmake")
fi
if ! command -v ninja &> /dev/null; then
    MISSING_TOOLS+=("ninja-build")
fi
if ! command -v pkg-config &> /dev/null; then
    MISSING_TOOLS+=("pkg-config")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    log_warning "Fehlende Linux development tools: ${MISSING_TOOLS[*]}"
    read -p "Möchtest du die Linux toolchain installieren? (j/n): " install_toolchain
    if [ "$install_toolchain" = "j" ] || [ "$install_toolchain" = "J" ]; then
        log_info "Installiere Linux toolchain..."
        sudo apt update
        sudo apt install -y clang cmake ninja-build pkg-config libgtk-3-dev mesa-utils
        log_success "Linux toolchain installiert!"
    else
        log_warning "Linux toolchain nicht installiert - Linux Desktop Support wird nicht funktionieren"
    fi
else
    log_success "Linux toolchain vollständig installiert!"
    # Prüfe auch GTK 3.0 und mesa-utils
    if ! dpkg -l | grep -q libgtk-3-dev; then
        log_warning "GTK 3.0 development libraries fehlen"
        read -p "Möchtest du GTK 3.0 libraries installieren? (j/n): " install_gtk
        if [ "$install_gtk" = "j" ] || [ "$install_gtk" = "J" ]; then
            sudo apt update
            sudo apt install -y libgtk-3-dev mesa-utils
            log_success "GTK 3.0 libraries installiert!"
        fi
    fi
fi

# Schritt 1: Prüfe Flutter Installation
log_info "Prüfe Flutter Installation..."
if ! command -v flutter &> /dev/null; then
    # Flutter nicht im PATH - prüfe ob es im Home-Verzeichnis existiert
    if [ -d "$HOME/flutter" ]; then
        log_warning "Flutter gefunden in ~/flutter, aber nicht im PATH!"
        log_info "Füge Flutter zu PATH hinzu..."
        
        # Add to PATH for current session
        export PATH="$HOME/flutter/bin:$PATH"
        
        # Add to .bashrc if not already there
        if ! grep -q 'flutter/bin' ~/.bashrc; then
            echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
            log_success "Flutter zu ~/.bashrc hinzugefügt!"
            log_info "Führe 'source ~/.bashrc' aus oder starte das Terminal neu, damit Flutter permanent verfügbar ist."
        fi
        
        FLUTTER_VERSION=$(flutter --version | head -n 1)
        log_success "Flutter gefunden: $FLUTTER_VERSION"
    else
        # Flutter existiert nicht - Installation nötig
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
            log_info "Führe 'source ~/.bashrc' aus oder starte das Terminal neu, damit Flutter permanent verfügbar ist."
            
            # Return to app directory
            cd "$FLUTTER_APP_DIR"
        else
            log_error "Flutter wird benötigt! Installiere es manuell:"
            echo "  wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz"
            echo "  tar xf flutter_linux_3.16.0-stable.tar.xz"
            echo "  echo 'export PATH=\"\$HOME/flutter/bin:\$PATH\"' >> ~/.bashrc"
            exit 1
        fi
    fi
else
    FLUTTER_VERSION=$(flutter --version | head -n 1)
    log_success "Flutter gefunden: $FLUTTER_VERSION"
fi

# Schritt 2: Flutter Doctor
log_info "Prüfe Flutter Umgebung..."
flutter doctor

# Schritt 2.5: Optional Android SDK Installation
echo ""
log_info "Möchtest du Android SDK installieren? (Nur nötig für Android-Entwicklung, NICHT für Web)"
log_warning "Hinweis: Wird nur für Android-Apps benötigt. Für Web-Entwicklung NICHT erforderlich."
read -p "Android SDK installieren? (j/n): " install_android

if [ "$install_android" = "j" ] || [ "$install_android" = "J" ]; then
    log_info "Installiere Android Command Line Tools..."
    
    # Erstelle Android SDK Verzeichnis
    mkdir -p "$HOME/Android/Sdk"
    cd "$HOME/Android/Sdk"
    
    # Download Android Command Line Tools
    log_info "Lade Android Command Line Tools herunter..."
    wget -q --show-progress https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
    
    # Extract
    log_info "Entpacke Android Tools..."
    unzip -q commandlinetools-linux-9477386_latest.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm commandlinetools-linux-9477386_latest.zip
    
    # Setup environment variables
    export ANDROID_HOME="$HOME/Android/Sdk"
    export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
    
    # Add to .bashrc if not already there
    if ! grep -q 'ANDROID_HOME' ~/.bashrc; then
        log_info "Füge Android SDK zu ~/.bashrc hinzu..."
        echo '' >> ~/.bashrc
        echo '# Android SDK' >> ~/.bashrc
        echo 'export ANDROID_HOME="$HOME/Android/Sdk"' >> ~/.bashrc
        echo 'export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"' >> ~/.bashrc
    fi
    
    # Accept licenses and install platform-tools
    log_info "Installiere Android SDK Platform Tools..."
    yes | sdkmanager --licenses > /dev/null 2>&1 || true
    sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" > /dev/null
    
    # Configure Flutter to use Android SDK
    flutter config --android-sdk "$ANDROID_HOME"
    
    log_success "Android SDK installiert in $ANDROID_HOME"
    log_info "Starte das Terminal neu oder führe 'source ~/.bashrc' aus"
    
    # Zurück zum Flutter-Verzeichnis
    cd - > /dev/null
else
    log_info "Android SDK Installation übersprungen (nur für Web-Entwicklung)"
fi

# Schritt 2.6: Optional Flutter Upgrade
echo ""
log_info "Möchtest du Flutter auf die neueste Version upgraden? (j/n)"
log_warning "Hinweis: Das kann einige Minuten dauern und erfordert unzip"
read -p "> " upgrade_flutter

if [ "$upgrade_flutter" = "j" ] || [ "$upgrade_flutter" = "J" ]; then
    # Prüfe ob unzip verfügbar ist
    if ! command -v unzip &> /dev/null; then
        log_error "unzip ist nicht installiert!"
        log_info "Installiere unzip zuerst mit: sudo apt install unzip"
        read -p "Trotzdem fortfahren mit Flutter Upgrade? (j/n): " continue_upgrade
        if [ "$continue_upgrade" != "j" ] && [ "$continue_upgrade" != "J" ]; then
            log_warning "Flutter Upgrade übersprungen"
        else
            log_info "Upgrading Flutter..."
            flutter upgrade || log_warning "Flutter Upgrade fehlgeschlagen - fahre trotzdem fort"
        fi
    else
        log_info "Upgrading Flutter..."
        flutter upgrade
        log_success "Flutter erfolgreich upgegraded!"
        
        # Flutter doctor erneut ausführen
        log_info "Prüfe Flutter nach Upgrade..."
        flutter doctor
    fi
else
    log_info "Flutter Upgrade übersprungen"
fi

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
    # Versuche flutter pub get
    if ! flutter pub get 2>&1 | tee /tmp/flutter_pub_get.log; then
        # Prüfe ob es ein intl oder dependency Konflikt ist
        if grep -q "version solving failed" /tmp/flutter_pub_get.log || grep -q "intl" /tmp/flutter_pub_get.log; then
            log_warning "Dependency-Konflikt erkannt (vermutlich intl-Version)!"
            log_info "Versuche Major-Version-Upgrade der Dependencies..."
            
            if flutter pub upgrade --major-versions; then
                log_success "Dependencies erfolgreich mit Major-Upgrade installiert!"
            else
                log_error "Konnte Dependencies nicht installieren!"
                log_info "Bitte führe manuell aus: flutter pub upgrade --major-versions"
                exit 1
            fi
        else
            log_error "Fehler beim Installieren der Dependencies!"
            cat /tmp/flutter_pub_get.log
            exit 1
        fi
    else
        log_success "Dependencies installiert!"
    fi
    
    # Cleanup
    rm -f /tmp/flutter_pub_get.log
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
echo -e "  ${BLUE}# Mit Backend URL:${NC}"
echo -e "  ${YELLOW}flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000${NC}"
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
    
    # Starte Flutter Web App (--web-renderer wurde in Flutter 3.38.7 entfernt)
    flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
fi
