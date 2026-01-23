# 🚀 Lokales Setup - RedFlag Analyzer (Django)

## 🎯 Schnellstart mit Setup-Script (Empfohlen!)

**Automatisches Setup:**
```bash
cd django_app
./setup.sh
```

Das Script führt dich interaktiv durch alle Schritte! 🎉

**Bei PostgreSQL-Problemen:** Siehe [POSTGRESQL_HILFE.md](django_app/POSTGRESQL_HILFE.md)

---

## 📖 Manuelle Installation

Falls du das Setup manuell durchführen möchtest:

## Voraussetzungen

Stelle sicher, dass folgende Software installiert ist:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 14+** ([Download](https://www.postgresql.org/download/))
- **Git** (für Version Control)

### Python Version prüfen
```bash
python3 --version
# Sollte 3.10 oder höher sein
```

### PostgreSQL prüfen
```bash
psql --version
# Sollte 14 oder höher sein
```

---

## 📦 Schritt-für-Schritt Installation

### 1. Repository klonen (falls noch nicht geschehen)
```bash
git clone https://github.com/lucmuss/redflag-analyzer.git
cd redflag-analyzer
```

### 2. In Django-App Verzeichnis wechseln
```bash
cd django_app
```

### 3. Virtuelle Python-Umgebung erstellen
```bash
python3 -m venv venv
```

### 4. Virtuelle Umgebung aktivieren

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

✅ Du solltest jetzt `(venv)` vor deiner Kommandozeile sehen.

### 5. Python-Pakete installieren
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ Dies dauert ca. 2-3 Minuten.

---

## 🗄️ PostgreSQL Datenbank einrichten

### 6. PostgreSQL Service starten

**Linux:**
```bash
sudo service postgresql start
```

**Mac (mit Homebrew):**
```bash
brew services start postgresql@14
```

**Windows:**
PostgreSQL läuft normalerweise automatisch nach Installation.

### 7. Datenbank erstellen

**Option A - Mit createdb Kommando:**
```bash
createdb redflag_db
```

**Option B - Mit psql:**
```bash
# PostgreSQL Shell öffnen
psql -U postgres

# In der psql Shell:
CREATE DATABASE redflag_db;
\q
```

**Option C - Mit pgAdmin:**
1. pgAdmin öffnen
2. Rechtsklick auf "Databases" → "Create" → "Database"
3. Name: `redflag_db`
4. Save

---

## ⚙️ Django-Projekt konfigurieren

### 8. Umgebungsvariablen einrichten
```bash
# .env Datei aus Vorlage erstellen
cp .env.example .env
```

### 9. .env Datei bearbeiten
Öffne `.env` in einem Text-Editor und passe an:

```env
# Django Settings
SECRET_KEY=dein-super-geheimer-schluessel-hier
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
# Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/redflag_db
```

🔑 **SECRET_KEY generieren:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Kopiere den Output und füge ihn als `SECRET_KEY` in `.env` ein.

**PostgreSQL Zugangsdaten:**
- Standard-User: `postgres`
- Standard-Password: Dein bei Installation festgelegtes Passwort
- Host: `localhost`
- Port: `5432`

---

## 🏗️ Datenbank initialisieren

### 10. Migrationen erstellen und ausführen
```bash
# Migrationen erstellen
python manage.py makemigrations

# Migrationen ausführen (erstellt Tabellen)
python manage.py migrate
```

✅ Ausgabe sollte enden mit: `Applying ...` für jede Migration

### 11. Fragen-Daten laden (Seed)
```bash
python manage.py seed_questions
```

✅ Ausgabe: `Seeding complete! Created: 65, Updated: 0, Total: 65`

### 12. Admin-Benutzer erstellen
```bash
python manage.py createsuperuser
```

Eingabe:
- **Email:** deine@email.de
- **Password:** (mindestens 8 Zeichen)
- **Password (again):** (wiederholen)

---

## 🎉 Anwendung starten!

### 13. Development Server starten
```bash
python manage.py runserver
```

✅ Ausgabe:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 14. Im Browser öffnen

Öffne deinen Browser und gehe zu:

- 🏠 **Hauptseite:** http://localhost:8000
- 🔐 **Admin-Interface:** http://localhost:8000/admin

---

## 🧪 Testen

### Registrierung testen
1. Gehe zu http://localhost:8000
2. Klicke auf "Registrieren"
3. Erstelle einen Account
4. Login mit deinen Credentials

### Fragebogen ausfüllen
1. Nach Login auf "Fragebogen starten"
2. Beantworte die Fragen (1-5 Skala)
3. Submit → Analyse wird erstellt
4. Mit 1 Credit entsperren

### Admin-Interface nutzen
1. Gehe zu http://localhost:8000/admin
2. Login mit Superuser-Credentials
3. Verwalte Users, Questions, Analyses

---

## 🛠️ Nützliche Kommandos

### Server stoppen
```bash
# Im Terminal: STRG+C (oder CMD+C auf Mac)
```

### Neue Änderungen an Models?
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files neu sammeln
```bash
python manage.py collectstatic --noinput
```

### Shell öffnen (Django-Console)
```bash
python manage.py shell
```

### Tests ausführen
```bash
python manage.py test
```

### Virtuelle Umgebung deaktivieren
```bash
deactivate
```

---

## 🐛 Troubleshooting

### Problem: `psycopg2` Installation fehlgeschlagen
**Lösung:**
```bash
# Auf Linux/Mac:
sudo apt-get install libpq-dev python3-dev  # Ubuntu/Debian
# oder
brew install postgresql  # Mac

# Dann:
pip install psycopg2-binary
```

### Problem: "Database connection error"
**Lösung:**
1. PostgreSQL läuft? → `sudo service postgresql status`
2. Credentials in `.env` korrekt?
3. Datenbank existiert? → `psql -U postgres -l`

### Problem: "Port already in use"
**Lösung:**
```bash
# Anderen Port verwenden:
python manage.py runserver 8001
```

### Problem: Migrationen schlagen fehl
**Lösung:**
```bash
# Migrations zurücksetzen (VORSICHT - löscht Daten!)
python manage.py migrate --fake-initial

# Oder Datenbank komplett neu:
dropdb redflag_db
createdb redflag_db
python manage.py migrate
python manage.py seed_questions
```

### Problem: "No module named 'django'"
**Lösung:**
```bash
# Virtuelle Umgebung aktiviert?
source venv/bin/activate  # Linux/Mac

# Dependencies neu installieren:
pip install -r requirements.txt
```

---

## 📚 Weitere Schritte

Nach erfolgreichem Setup:

1. **Code erkunden:** Schau dir die Models in `accounts/models.py`, `questionnaire/models.py`, `analyses/models.py` an
2. **Templates anpassen:** Schau dir `templates/` an und passe das Design an
3. **HTMX verstehen:** Schau dir `templates/analyses/detail.html` an für HTMX-Patterns
4. **Admin erweitern:** Passe `*/admin.py` an

---

## 🚀 Nächste Schritte: Deployment

Wenn du die App deployen willst:

1. **Vercel:** Siehe `django_app/README.md` → "Deployment auf Vercel"
2. **Railway:** https://railway.app (einfaches Django Hosting)
3. **Heroku:** https://www.heroku.com (mit Postgres Add-on)
4. **DigitalOcean:** App Platform oder Droplet

---

## 📞 Support

Bei Fragen oder Problemen:
- 📖 Haupt-README: `django_app/README.md`
- 🐛 Issues: GitHub Issues erstellen
- 📧 Email: (deine Email)

---

**Viel Erfolg! 🎉**
