# PostgreSQL Hilfe - Service starten

## Problem: `sudo service postgresql start` funktioniert nicht

Dies ist ein häufiges Problem bei WSL (Windows Subsystem for Linux) und manchen Ubuntu-Installationen.

## 🔧 Lösungen nach System

### Lösung 1: Für WSL/Ubuntu (Empfohlen)

#### A) Mit pg_ctlcluster
```bash
# Finde deine PostgreSQL Version heraus
psql --version
# z.B. PostgreSQL 14.x

# Starte PostgreSQL mit der gefundenen Version
sudo pg_ctlcluster 14 main start

# Status prüfen
sudo pg_ctlcluster 14 main status
```

#### B) Mit init.d
```bash
sudo /etc/init.d/postgresql start
```

#### C) PostgreSQL-Cluster neu erstellen (falls korrupt)
```bash
# Stoppe PostgreSQL (falls läuft)
sudo pg_ctlcluster 14 main stop

# Lösche alten Cluster (VORSICHT: Löscht Daten!)
sudo pg_dropcluster --stop 14 main

# Erstelle neuen Cluster
sudo pg_createcluster 14 main

# Starte PostgreSQL
sudo pg_ctlcluster 14 main start
```

### Lösung 2: Für moderne Linux-Systeme (systemd)

```bash
# Starte PostgreSQL
sudo systemctl start postgresql

# Status prüfen
sudo systemctl status postgresql

# Automatischer Start beim Booten
sudo systemctl enable postgresql
```

### Lösung 3: Für macOS (mit Homebrew)

```bash
# PostgreSQL starten
brew services start postgresql@14
# oder
brew services start postgresql

# Status prüfen
brew services list
```

---

## 🔍 Troubleshooting

### 1. Prüfe ob PostgreSQL installiert ist
```bash
psql --version
```

Falls nicht installiert:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql@14
```

### 2. Prüfe welche Cluster existieren
```bash
pg_lsclusters
```

Ausgabe sollte aussehen wie:
```
Ver Cluster Port Status Owner    Data directory
14  main    5432 online postgres /var/lib/postgresql/14/main
```

### 3. Prüfe ob Port 5432 belegt ist
```bash
sudo lsof -i :5432
```

Falls ein anderer Prozess läuft:
```bash
# Finde Prozess
sudo netstat -tlnp | grep 5432

# Stoppe Prozess (ersetze PID)
sudo kill -9 <PID>
```

### 4. PostgreSQL-Logs prüfen
```bash
# Hauptlog
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Oder
sudo journalctl -u postgresql -f
```

---

## ⚙️ WSL-Spezifische Konfiguration

### Automatischer PostgreSQL-Start in WSL

Da WSL kein systemd standardmäßig unterstützt, musst du PostgreSQL manuell starten.

**Option A: Alias in .bashrc**
```bash
# Füge zu ~/.bashrc hinzu:
echo 'alias pgstart="sudo service postgresql start"' >> ~/.bashrc
echo 'alias pgstop="sudo service postgresql stop"' >> ~/.bashrc
echo 'alias pgstatus="sudo service postgresql status"' >> ~/.bashrc

# Neu laden
source ~/.bashrc

# Jetzt kannst du einfach verwenden:
pgstart
```

**Option B: Auto-Start Script in .bashrc**
```bash
# Füge zu ~/.bashrc hinzu:
echo 'sudo service postgresql start 2>/dev/null' >> ~/.bashrc

# Neu laden
source ~/.bashrc
```

---

## 🔐 PostgreSQL Benutzer & Passwort

### Standard-User wechseln zu postgres
```bash
sudo -i -u postgres
psql
```

### Passwort für postgres-User setzen
```bash
# In der psql Shell:
ALTER USER postgres PASSWORD 'dein_neues_passwort';
\q
```

### Neuen Datenbank-User erstellen
```bash
# Als postgres-User
sudo -u postgres createuser --interactive --pwprompt

# Oder in psql:
CREATE USER redflag_user WITH PASSWORD 'sicheres_passwort';
CREATE DATABASE redflag_db OWNER redflag_user;
GRANT ALL PRIVILEGES ON DATABASE redflag_db TO redflag_user;
```

---

## 📝 Datenbank-Operationen

### Datenbank erstellen
```bash
# Als postgres-User
sudo -u postgres createdb redflag_db

# Oder als normaler User (wenn konfiguriert)
createdb redflag_db
```

### Datenbank löschen
```bash
dropdb redflag_db
```

### Alle Datenbanken anzeigen
```bash
psql -U postgres -l
```

### Verbindung testen
```bash
psql -U postgres -d redflag_db -c "SELECT 1;"
```

---

## 🚀 Quick-Fix für das Setup-Script

Wenn das `setup.sh` Script bei PostgreSQL hängt, versuche:

```bash
# Manuell PostgreSQL starten
sudo pg_ctlcluster 14 main start

# Dann Setup-Script ausführen
cd django_app
./setup.sh
```

---

## 💡 Häufige Fehler

### Fehler: "could not connect to server"
**Lösung:**
```bash
# PostgreSQL läuft nicht - starten:
sudo pg_ctlcluster 14 main start
```

### Fehler: "role 'postgres' does not exist"
**Lösung:**
```bash
# PostgreSQL-User erstellen
sudo -u postgres createuser -s $(whoami)
```

### Fehler: "permission denied for database"
**Lösung:**
```bash
# Als postgres-User Rechte geben
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE redflag_db TO dein_username;
\q
```

### Fehler: "port 5432 already in use"
**Lösung:**
```bash
# Alten Prozess finden und beenden
sudo lsof -ti:5432 | xargs kill -9

# PostgreSQL neu starten
sudo pg_ctlcluster 14 main restart
```

---

## 📚 Weiterführende Links

- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **WSL PostgreSQL Guide:** https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-database
- **Ubuntu PostgreSQL:** https://ubuntu.com/server/docs/databases-postgresql

---

## ✅ Schnell-Check ob PostgreSQL läuft

```bash
# Methode 1
sudo pg_ctlcluster 14 main status

# Methode 2
sudo systemctl status postgresql

# Methode 3
psql -U postgres -c "SELECT version();"

# Methode 4
pg_isready
```

Wenn einer dieser Befehle "online" oder die Version anzeigt, läuft PostgreSQL! ✅
