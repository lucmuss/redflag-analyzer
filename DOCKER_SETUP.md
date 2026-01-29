# 🐳 Docker Setup - RedFlag Analyzer

## Schnellstart

```bash
# 1. Docker Container starten
docker-compose up --build

# 2. Browser öffnen
http://localhost
```

**Admin-Login:**
- Email: `admin@example.com`
- Password: `admin123`

## Services

- **nginx** → http://localhost (Port 80)
- **PostgreSQL** → Port 5433 (5432 intern)
- **Django** → Port 8000 (intern)

## Commands

```bash
# Container starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f web

# Migrations ausführen
docker-compose exec web python manage.py migrate

# Superuser erstellen
docker-compose exec web python manage.py createsuperuser

# Django Shell
docker-compose exec web python manage.py shell

# Container stoppen
docker-compose down

# Container + Volumes löschen
docker-compose down -v

# Rebuild nach Code-Änderungen
docker-compose up --build
```

## Konfiguration

Alle Einstellungen in `django_app/.env.docker` anpassen.

## Production

Für Production:
1. `.env.docker` kopieren → `.env.production`
2. `SECRET_KEY` generieren: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
3. `DEBUG=False` setzen
4. `ALLOWED_HOSTS` anpassen
5. `DB_PASSWORD` ändern
6. Stripe Keys hinzufügen
7. Email SMTP konfigurieren
