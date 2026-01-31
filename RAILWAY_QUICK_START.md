# 🚀 Railway.app Deployment - Schritt-für-Schritt

## ✅ Schritt 1: Railway CLI installieren & Login
```bash
npm i -g @railway/cli
railway login
# Öffnet Browser → Autorisieren
```

## ✅ Schritt 2: Projekt mit Railway verbinden
```bash
cd /home/skymuss/projects/redflag-analyzer
railway init
# Wähle: Create a new Project
# Project name: "redflag-analyzer"
```

## ✅ Schritt 3: Environment Variables setzen
Im Railway Dashboard (https://railway.app/dashboard):
1. Gehe zu deinem Projekt
2. Klick auf den "Deploy" Service
3. Variables tab → Folgende hinzufügen:

```
SECRET_KEY=random-geheimnis-hier-einfügen
DEBUG=false
ENVIRONMENT=production
ALLOWED_HOSTS=*.railway.app,localhost
DATABASE_URL=postgresql://postgres:password@db:5432/redflag_db
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=sicheres-passwort
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=dein-app-passwort-von-gmail
DEFAULT_FROM_EMAIL=noreply@redflag-analyzer.com
```

## ✅ Schritt 4: Projekt deployen
```bash
railway up
# Wartet auf Build & Deploy (~5-10 min beim ersten Mal)
```

## ✅ Schritt 5: Domain anschauen
Nach Deploy:
```bash
railway status
# Zeigt: https://redflag-analyzer-xxxx.railway.app
```

Oder im Dashboard:
- Settings → Domains → Domain generieren

---

## 🆘 Wenn etwas schiefgeht

```bash
# Live Logs ansehen
railway logs -f

# SSH in den Container
railway shell

# Manuell Migrations laufen
python manage.py migrate

# Statische Files neu sammeln
python manage.py collectstatic --noinput
```

---

## 📱 2. App deployen (Neues Projekt)
```bash
mkdir ~/my-app-2
cd ~/my-app-2
railway init
# Neuer Service in GLEICHER Organisation
railroad up
```

## ✨ FERTIG! 
Deine App läuft jetzt online! 🎉
