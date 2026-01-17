#!/bin/bash

# RedFlag Analyzer Backend Setup Script für WSL Ubuntu
# Dieses Script automatisiert das komplette Backend-Setup

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
echo "║   RedFlag Analyzer Backend Setup (WSL Ubuntu)            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Schritt 1: Prüfe Python Installation
log_info "Prüfe Python Installation..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 ist nicht installiert!"
    log_info "Installiere Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi
PYTHON_VERSION=$(python3 --version)
log_success "Python gefunden: $PYTHON_VERSION"

# Schritt 2: Prüfe MongoDB
log_info "Prüfe MongoDB Installation..."
if ! command -v mongod &> /dev/null; then
    log_warning "MongoDB ist nicht installiert!"
    echo ""
    echo "Wähle eine Installationsmethode:"
    echo "  1) Docker (empfohlen für WSL)"
    echo "  2) Apt Package (Standard)"
    echo "  3) Überspringen"
    read -p "Auswahl (1-3): " install_choice
    
    case $install_choice in
        1)
            log_info "MongoDB via Docker..."
            if ! command -v docker &> /dev/null; then
                log_warning "Docker ist nicht installiert!"
                log_info "Installiere Docker..."
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                rm get-docker.sh
                log_success "Docker installiert! (Neustart erforderlich für sudo-freie Nutzung)"
            fi
            log_info "Starte MongoDB Container..."
            docker run -d --name mongodb-redflag \
                -p 27017:27017 \
                -v ~/data/db:/data/db \
                mongo:latest
            sleep 3
            if docker ps | grep -q mongodb-redflag; then
                log_success "MongoDB Container läuft!"
            else
                log_error "MongoDB Container Start fehlgeschlagen"
            fi
            ;;
        2)
            log_info "Installiere MongoDB via Apt..."
            # Ubuntu 22.04 (Jammy) benötigt libssl1.1 Workaround
            if ! dpkg -l | grep -q libssl1.1; then
                log_info "Installiere libssl1.1 (Abhängigkeit)..."
                wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
                sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb
                rm libssl1.1_1.1.1f-1ubuntu2_amd64.deb
            fi
            wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
            echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
            sudo apt update
            sudo apt install -y mongodb-org
            log_success "MongoDB installiert!"
            ;;
        3)
            log_warning "MongoDB Installation übersprungen"
            log_info "Du kannst MongoDB später manuell installieren oder Docker verwenden"
            ;;
        *)
            log_error "Ungültige Auswahl"
            ;;
    esac
else
    log_success "MongoDB gefunden: $(mongod --version | head -n 1)"
fi

# Schritt 3: Erstelle Virtual Environment
log_info "Erstelle Python Virtual Environment..."
if [ -d "venv" ]; then
    log_warning "Virtual Environment existiert bereits. Überspringe..."
else
    python3 -m venv venv
    log_success "Virtual Environment erstellt!"
fi

# Schritt 4: Aktiviere Virtual Environment und installiere Dependencies
log_info "Installiere Python Dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Installiere requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_success "Dependencies installiert!"
else
    log_error "requirements.txt nicht gefunden!"
    exit 1
fi

# Schritt 5: Erstelle .env Datei
log_info "Konfiguriere .env Datei..."
if [ -f ".env" ]; then
    log_warning ".env existiert bereits"
    read -p "Möchtest du die .env Datei überschreiben? (j/n): " overwrite
    if [ "$overwrite" != "j" ] && [ "$overwrite" != "J" ]; then
        log_info "Behalte existierende .env Datei"
    else
        rm .env
    fi
fi

if [ ! -f ".env" ]; then
    log_info "Generiere SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    cat > .env << 'EOF'
# Environment
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=REPLACE_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=redflag_analyzer

# CORS (must be JSON string with quotes)
BACKEND_CORS_ORIGINS='["http://localhost:3000","http://localhost:8080","http://localhost:5173"]'

# Optional (für später)
SENDGRID_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=
EOF
    
    # Replace SECRET_KEY
    sed -i "s/REPLACE_SECRET_KEY/$SECRET_KEY/" .env
    log_success ".env Datei erstellt!"
fi

# Schritt 6: Starte MongoDB (falls nicht läuft)
log_info "Prüfe MongoDB Status..."
if ! pgrep -x "mongod" > /dev/null; then
    log_warning "MongoDB läuft nicht!"
    log_info "Versuche MongoDB zu starten..."
    
    # Erstelle Datenverzeichnis falls nicht vorhanden
    mkdir -p ~/data/db
    
    # Starte MongoDB im Hintergrund
    mongod --dbpath ~/data/db --fork --logpath ~/data/mongodb.log > /dev/null 2>&1 || true
    
    sleep 2
    
    if pgrep -x "mongod" > /dev/null; then
        log_success "MongoDB gestartet!"
    else
        log_warning "MongoDB konnte nicht automatisch gestartet werden"
        log_info "Bitte starte MongoDB manuell mit: mongod --dbpath ~/data/db"
    fi
else
    log_success "MongoDB läuft bereits!"
fi

# Schritt 7: Initialisiere Datenbank
log_info "Initialisiere Datenbank mit Seed-Daten..."
if [ -f "scripts/seed_db.py" ]; then
    python -m scripts.seed_db
    log_success "Datenbank initialisiert mit 65 Fragen!"
else
    log_warning "Seed-Script nicht gefunden. Überspringe..."
fi

# Schritt 8: Tests ausführen (optional)
log_info "Möchtest du die Tests ausführen? (j/n)"
read -p "> " run_tests
if [ "$run_tests" = "j" ] || [ "$run_tests" = "J" ]; then
    log_info "Führe Tests aus..."
    pytest tests/ -v
    log_success "Tests abgeschlossen!"
fi

# Fertig!
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
echo -e "║   ✓ Setup erfolgreich abgeschlossen!                    ║"
echo -e "╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Nächste Schritte:"
echo -e "  1. Aktiviere Virtual Environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "  2. Starte Backend: ${YELLOW}uvicorn app.main:app --reload${NC}"
echo -e "  3. Öffne API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
log_info "Optionale Befehle:"
echo -e "  - Tests ausführen: ${YELLOW}pytest tests/ -v${NC}"
echo -e "  - MongoDB stoppen: ${YELLOW}pkill mongod${NC}"
echo -e "  - Logs ansehen: ${YELLOW}tail -f ~/data/mongodb.log${NC}"
echo ""

# Frage ob Server direkt gestartet werden soll
read -p "Möchtest du den Backend-Server jetzt starten? (j/n): " start_server
if [ "$start_server" = "j" ] || [ "$start_server" = "J" ]; then
    log_info "Starte Backend-Server..."
    echo -e "${YELLOW}Drücke CTRL+C zum Beenden${NC}"
    echo ""
    uvicorn app.main:app --reload
fi
