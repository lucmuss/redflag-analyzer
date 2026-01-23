#!/bin/bash

# RedFlag Analyzer - Automatisches Setup Script
# Dieses Script führt dich durch die komplette Installation

set -e  # Stop bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║        🚩 RedFlag Analyzer - Setup Script 🚩         ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Funktion für Success-Messages
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Funktion für Error-Messages
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Funktion für Info-Messages
info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Funktion für Warning-Messages
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Funktion für User-Input
ask() {
    echo -e "${YELLOW}? $1${NC}"
}

# === SCHRITT 1: System-Checks ===
echo -e "${BLUE}=== Schritt 1: System-Checks ===${NC}"
echo ""

# Check Python Version
info "Prüfe Python Installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    success "Python $PYTHON_VERSION gefunden"
else
    error "Python3 nicht gefunden!"
    echo "Bitte installiere Python 3.10+ von https://www.python.org/downloads/"
    exit 1
fi

# Check PostgreSQL
info "Prüfe PostgreSQL Installation..."
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version 2>&1 | awk '{print $3}')
    success "PostgreSQL $PG_VERSION gefunden"
else
    error "PostgreSQL nicht gefunden!"
    echo ""
    echo "Installation je nach System:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  Mac (Homebrew): brew install postgresql@14"
    echo "  Windows: https://www.postgresql.org/download/windows/"
    exit 1
fi

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 2: PostgreSQL Service starten ===
echo -e "${BLUE}=== Schritt 2: PostgreSQL Service ===${NC}"
echo ""

info "Versuche PostgreSQL Service zu starten..."

# Verschiedene Methoden für verschiedene Systeme
if command -v systemctl &> /dev/null; then
    # systemd (moderne Linux-Systeme)
    if sudo systemctl is-active --quiet postgresql; then
        success "PostgreSQL läuft bereits"
    else
        info "Starte PostgreSQL mit systemctl..."
        if sudo systemctl start postgresql 2>/dev/null; then
            success "PostgreSQL erfolgreich gestartet"
        else
            warning "systemctl fehlgeschlagen, versuche service..."
            if sudo service postgresql start 2>/dev/null; then
                success "PostgreSQL erfolgreich gestartet"
            else
                error "Konnte PostgreSQL nicht starten!"
                echo ""
                echo "Mögliche Lösungen:"
                echo "1. Prüfe ob PostgreSQL installiert ist: psql --version"
                echo "2. Versuche manuell: sudo systemctl status postgresql"
                echo "3. Bei WSL: siehe unten für spezielle Anleitung"
                echo ""
                warning "===== WSL/Ubuntu Spezial-Lösung ====="
                echo "Falls du WSL verwendest, versuche:"
                echo "  sudo /etc/init.d/postgresql start"
                echo "oder:"
                echo "  sudo pg_ctlcluster <version> main start"
                echo ""
                ask "PostgreSQL läuft jetzt? (j/n): "
                read PG_RUNNING
                if [[ ! $PG_RUNNING =~ ^[Jj]$ ]]; then
                    exit 1
                fi
            fi
        fi
    fi
elif command -v brew &> /dev/null; then
    # macOS (Homebrew)
    info "Starte PostgreSQL mit Homebrew..."
    brew services start postgresql@14 2>/dev/null || brew services start postgresql
    success "PostgreSQL gestartet"
else
    warning "Kann PostgreSQL-Service nicht automatisch starten"
    ask "Ist PostgreSQL bereits gestartet? (j/n): "
    read PG_RUNNING
    if [[ ! $PG_RUNNING =~ ^[Jj]$ ]]; then
        error "Bitte starte PostgreSQL manuell und führe das Script erneut aus"
        exit 1
    fi
fi

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 3: Virtuelle Umgebung ===
echo -e "${BLUE}=== Schritt 3: Python Virtuelle Umgebung ===${NC}"
echo ""

if [ -d "venv" ]; then
    warning "venv existiert bereits"
    ask "Möchtest du sie neu erstellen? (j/n): "
    read RECREATE_VENV
    if [[ $RECREATE_VENV =~ ^[Jj]$ ]]; then
        info "Lösche alte venv..."
        rm -rf venv
        info "Erstelle neue venv..."
        python3 -m venv venv
        success "Neue venv erstellt"
    else
        success "Verwende existierende venv"
    fi
else
    info "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
    success "venv erstellt"
fi

# Aktiviere venv
info "Aktiviere virtuelle Umgebung..."
source venv/bin/activate
success "venv aktiviert"

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 4: Dependencies installieren ===
echo -e "${BLUE}=== Schritt 4: Python-Pakete installieren ===${NC}"
echo ""

info "Aktualisiere pip..."
pip install --upgrade pip -q
success "pip aktualisiert"

info "Installiere Requirements (dies kann 2-3 Minuten dauern)..."
pip install -r requirements.txt
success "Alle Pakete installiert"

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 5: PostgreSQL Datenbank ===
echo -e "${BLUE}=== Schritt 5: PostgreSQL Datenbank erstellen ===${NC}"
echo ""

ask "PostgreSQL Username (Standard: postgres): "
read PG_USER
PG_USER=${PG_USER:-postgres}

ask "PostgreSQL Password: "
read -s PG_PASSWORD
echo ""

DATABASE_NAME="redflag_db"

info "Prüfe ob Datenbank '$DATABASE_NAME' existiert..."

# Prüfe ob Datenbank existiert
export PGPASSWORD=$PG_PASSWORD
if psql -U $PG_USER -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw $DATABASE_NAME; then
    warning "Datenbank '$DATABASE_NAME' existiert bereits"
    ask "Möchtest du sie neu erstellen? (ACHTUNG: Löscht alle Daten!) (j/n): "
    read RECREATE_DB
    if [[ $RECREATE_DB =~ ^[Jj]$ ]]; then
        info "Lösche alte Datenbank..."
        dropdb -U $PG_USER $DATABASE_NAME 2>/dev/null || true
        info "Erstelle neue Datenbank..."
        createdb -U $PG_USER $DATABASE_NAME
        success "Datenbank neu erstellt"
    else
        success "Verwende existierende Datenbank"
    fi
else
    info "Erstelle Datenbank '$DATABASE_NAME'..."
    if createdb -U $PG_USER $DATABASE_NAME 2>/dev/null; then
        success "Datenbank erstellt"
    else
        error "Konnte Datenbank nicht erstellen"
        echo "Versuche als postgres-User:"
        sudo -u postgres createdb $DATABASE_NAME
        success "Datenbank erstellt (mit sudo)"
    fi
fi

unset PGPASSWORD

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 6: .env Datei ===
echo -e "${BLUE}=== Schritt 6: Umgebungsvariablen (.env) ===${NC}"
echo ""

if [ -f ".env" ]; then
    warning ".env existiert bereits"
    ask "Möchtest du sie überschreiben? (j/n): "
    read RECREATE_ENV
    if [[ ! $RECREATE_ENV =~ ^[Jj]$ ]]; then
        success "Verwende existierende .env"
        source .env
        DB_URL_EXISTS=true
    fi
fi

if [ ! -f ".env" ] || [[ $RECREATE_ENV =~ ^[Jj]$ ]]; then
    info "Generiere SECRET_KEY..."
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    info "Erstelle .env Datei..."
    cat > .env << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgresql://$PG_USER:$PG_PASSWORD@localhost:5432/$DATABASE_NAME
EOF
    success ".env erstellt"
fi

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 7: Django Migrationen ===
echo -e "${BLUE}=== Schritt 7: Django Datenbank-Migrationen ===${NC}"
echo ""

info "Erstelle Migrationen..."
python manage.py makemigrations

info "Führe Migrationen aus..."
python manage.py migrate

success "Datenbank-Schema erstellt"

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 8: Fragen laden ===
echo -e "${BLUE}=== Schritt 8: Fragen-Daten laden ===${NC}"
echo ""

info "Lade 65 Fragen aus seed_data/questions.json..."
python manage.py seed_questions

success "Fragen geladen"

echo ""
read -p "Drücke Enter um fortzufahren..."
echo ""

# === SCHRITT 9: Superuser ===
echo -e "${BLUE}=== Schritt 9: Admin-Benutzer erstellen ===${NC}"
echo ""

ask "Möchtest du einen Admin-Benutzer erstellen? (j/n): "
read CREATE_SUPERUSER

if [[ $CREATE_SUPERUSER =~ ^[Jj]$ ]]; then
    info "Erstelle Superuser..."
    echo ""
    python manage.py createsuperuser
    echo ""
    success "Superuser erstellt"
else
    warning "Übersprungen - du kannst später einen erstellen mit: python manage.py createsuperuser"
fi

echo ""
echo ""

# === FERTIG ===
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║               ✅ SETUP ERFOLGREICH! ✅               ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

success "RedFlag Analyzer ist bereit!"
echo ""
echo -e "${BLUE}Nächste Schritte:${NC}"
echo ""
echo "1. Server starten:"
echo -e "   ${GREEN}python manage.py runserver${NC}"
echo ""
echo "2. Im Browser öffnen:"
echo -e "   ${GREEN}http://localhost:8000${NC}"
echo ""
echo "3. Admin-Interface:"
echo -e "   ${GREEN}http://localhost:8000/admin${NC}"
echo ""
echo ""

ask "Möchtest du den Server jetzt starten? (j/n): "
read START_SERVER

if [[ $START_SERVER =~ ^[Jj]$ ]]; then
    echo ""
    info "Starte Development Server..."
    echo ""
    success "Server läuft auf http://localhost:8000"
    echo ""
    echo -e "${YELLOW}Drücke STRG+C zum Beenden${NC}"
    echo ""
    python manage.py runserver
else
    echo ""
    info "Du kannst den Server später starten mit:"
    echo -e "   ${GREEN}cd django_app${NC}"
    echo -e "   ${GREEN}source venv/bin/activate${NC}"
    echo -e "   ${GREEN}python manage.py runserver${NC}"
    echo ""
fi
