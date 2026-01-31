# 🐳 Docker - Korrekte Verwendung

## Problem: "connection to server at localhost failed"

Das passiert, wenn du Django-Befehle **direkt im Terminal** ausführst, statt im **Docker-Container**.

---

## ✅ RICHTIG: Mit Docker arbeiten

### Option 1: App über Browser nutzen
```bash
docker-compose up -d
# Dann im Browser: http://localhost:3000
# Fertig! Keine CLI-Befehle nötig
```

### Option 2: CLI-Befehle IM Container ausführen
```bash
# Migrations (falls nötig)
docker-compose exec web python manage.py migrate

# Django Shell
docker-compose exec web python manage.py shell

# Als Admin einloggen
docker-compose exec web python manage.py shell
# >>> from django.contrib.auth import get_user_model
# >>> User = get_user_model()
# >>> user = User.objects.first()
```

---

## ❌ FALSCH: Direkt im Terminal

```bash
# ❌ NICHT MACHEN!
python manage.py migrate          # → Fehler: PostgreSQL nicht erreichbar
python manage.py runserver        # → Fehler: Keine Datenbank
manage.py createsuperuser         # → Fehler: DB Connection refused
```

---

## 🚀 Für Railway.app

**Vergiss die lokalen CLI-Befehle** - Railway macht alles automatisch:
- ✅ Migrations: railway.toml + docker-entrypoint.sh
- ✅ Superuser: docker-entrypoint.sh
- ✅ Static Files: docker-entrypoint.sh

```bash
# NUR das hier brauchen:
railway up
# Fertig!
```

---

## 📝 Zusammenfassung

| Where | Command | Status |
|-------|---------|--------|
| **Browser** | http://localhost:3000 | ✅ Works |
| **Docker Container** | `docker-compose exec web python manage.py ...` | ✅ Works |
| **Direct Terminal** | `python manage.py ...` | ❌ FAILS |
| **Railway** | `railway up` | ✅ Auto-Magic |

**Merke:** Nutze entweder Browser ODER `docker-compose exec web` - nie direkt `python manage.py`!
