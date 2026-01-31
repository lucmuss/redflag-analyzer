# 🚂 Railway.app Deployment Guide für RedFlag Analyzer

## Setup in 5 Minuten

### 1. Railway CLI installieren
```bash
npm i -g @railway/cli
railway login
```

### 2. Environment Variables in Railway Dashboard setzen
Nach dem Login im [Railway Dashboard](https://railway.app/dashboard):

```
SECRET_KEY = "dein-sicherer-secret-key-hier"
DB_PASSWORD = "sichere-db-password"
DJANGO_SUPERUSER_PASSWORD = "sicheres-admin-passwort"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "dein-email@gmail.com"
EMAIL_HOST_PASSWORD = "dein-app-passwort"
SENTRY_DSN = "optional"
GOOGLE_ANALYTICS_ID = "optional"
```

### 3. Deployen
```bash
cd /home/skymuss/projects/redflag-analyzer
railway up
```

### 4. Domain einrichten
Im Railway Dashboard:
- Settings → Domain → Generate Domain
- App wird automatisch unter `https://redflag-analyzer-xxxx.railway.app` verfügbar

---

## 📱 Weitere Apps deployen (Verschiedene Prototypen)

### Neues Projekt = Neuer Service

**Option A: Neuer Railway Service (Same Account)**
```bash
mkdir ~/my-other-app
cd ~/my-other-app
railway init
# Wähle: Create new Project
railway up
```

**Option B: Bestehende Git-Repos verbinden**
```bash
railway link
railway up
```

---

## 🔧 Troubleshooting

**Build fehlgeschlagen?**
```bash
railway logs -f  # Live Logs ansehen
```

**Datenbank-Fehler?**
```bash
# SSH ins Container
railway shell
python manage.py migrate
```

**Statische Files nicht geladen?**
```bash
railway run python manage.py collectstatic --noinput
```

---

## 💰 Kosten
- **Gratis:** Erste ~$5 monatlich
- **Danach:** ~$0.50/Stunde pro Service (also ~$3-5/Monat pro App bei Idle)
- **Ideal für:** 3-5 kleine Prototypen kostenlos

---

## 📝 Checkliste vor Deploy
- [ ] `.env` Secrets nicht in Git committed
- [ ] DEBUG=false in production
- [ ] DATABASE_URL konfiguriert
- [ ] SECRET_KEY generiert
- [ ] Email Credentials gespeichert
- [ ] railway.toml im Root-Verzeichnis

✅ Fertig!
