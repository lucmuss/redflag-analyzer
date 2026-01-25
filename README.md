# 🚩 RedFlag Analyzer

Ein **Django-basiertes Web-Tool** zur Analyse von Red Flags in Beziehungen mit wissenschaftlich fundierter Methodik.

## 🎯 Tech Stack

- **Backend:** Django 5.0 + PostgreSQL
- **Frontend:** HTMX + Tailwind CSS (Server-Side Rendering)
- **Deployment:** Vercel (Serverless)
- **Plattform:** Progressive Web App (PWA)

## 🚀 Schnellstart

### Lokale Entwicklung

Vollständige Anleitung siehe: **[SETUP_LOKAL.md](SETUP_LOKAL.md)**

**Kurzversion:**
```bash
# 1. In Django-App wechseln
cd django_app

# 2. Virtuelle Umgebung erstellen & aktivieren
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. PostgreSQL Datenbank erstellen
createdb redflag-analyzer

# 5. .env konfigurieren
cp .env.example .env
# Bearbeite .env und setze DATABASE_URL und SECRET_KEY

# 6. Datenbank initialisieren
python manage.py migrate
python manage.py seed_questions
python manage.py createsuperuser

# 7. Server starten
python manage.py runserver
```

Öffne: **http://localhost:8000**

## 📁 Projektstruktur

```
redflag-analyzer/
├── django_app/              # Django-Anwendung
│   ├── accounts/            # User Management
│   ├── questionnaire/       # Fragebogen & Questions
│   ├── analyses/            # Score-Berechnung & Ergebnisse
│   ├── templates/           # HTML Templates (HTMX + Tailwind)
│   ├── static/              # Static Files
│   ├── redflag_project/     # Django Settings
│   ├── manage.py
│   ├── requirements.txt
│   ├── vercel.json          # Vercel Deployment Config
│   └── README.md            # Detaillierte Dokumentation
├── seed_data/               # Seed-Daten (Questions JSON)
├── SETUP_LOKAL.md           # 📖 Lokales Setup Tutorial
└── README.md                # Diese Datei
```

## ✨ Features

### ✅ Implementiert

- 🔐 **User Authentication** (Django Allauth)
  - Email-basierte Registrierung & Login
  - Passwort-Hashing mit Argon2
  
- 📊 **Fragebogen-System**
  - 65 Fragen in 4 Kategorien (Trust, Behavior, Values, Dynamics)
  - HTMX-basiertes interaktives Formular
  - Mobile-First Design (Tailwind CSS)

- 📈 **Score-Berechnung**
  - Gewichtete Algorithmus (Service Layer)
  - Gesamt-Score (0-10) + Category Scores
  - Top 5 Red Flags basierend auf Impact

- 💳 **Credit-System**
  - User erhält 1 Credit bei Registrierung
  - Analyse-Unlock für 1 Credit
  - Admin kann Credits verwalten

- 🎨 **Progressive Web App (PWA)**
  - Installierbar auf Smartphones
  - Manifest & Service Worker

- 🛡️ **Security**
  - CSRF Protection
  - SQL Injection Prevention (Django ORM)
  - HTTPS Redirect in Production
  - HSTS Headers

### 🔜 Geplant

- 💰 Stripe Payment Integration
- 📧 Email Verification
- 🌐 Multi-Language Support (DE/EN)
- 📱 Native Mobile App (optional)
- 📊 Advanced Analytics Dashboard

## 🏗️ Architektur

### HTMX statt React/Flutter

**Traditionell (React/Flutter):**
```
Client State → API Call → JSON → State Update → Component Rebuild
```

**Mit HTMX:**
```
User Action → Server Logic → HTML Fragment → DOM Swap
```

**Vorteile:**
- ✅ Keine komplexe Client-Side State Management
- ✅ Server kontrolliert UI-Logik (sicherer)
- ✅ SEO-freundlich (Server-Side Rendering)
- ✅ Weniger Code, weniger Bugs
- ✅ Progressive Enhancement

### Fat Models, Thin Views

```python
# Business Logic im Model
class User(AbstractUser):
    def consume_credit(self) -> bool:
        if self.credits > 0:
            self.credits -= 1
            self.save()
            return True
        return False

# View = nur Koordination
class UnlockAnalysisView(View):
    def post(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
        success = analysis.unlock()  # ← Business Logic
        return render(request, 'partial.html', {...})
```

### PostgreSQL Optimierung

- **Foreign Keys** statt JSON-Referenzen
- **Indizes** auf häufig abgefragte Felder
- **select_related/prefetch_related** für Performance
- **JSONField** für flexible Daten (responses)

## 🗄️ Datenbank-Schema

```sql
-- Users
users (id, email, password_hash, credits, is_verified, created_at)

-- Questions
questions (id, key, category, default_weight, text_de, text_en, is_active)

-- Analyses
analyses (id, user_id FK, is_unlocked, responses JSONB, score_total, created_at)

-- Category Scores
category_scores (id, analysis_id FK, category, score)
```

## 🚢 Deployment

### Vercel (Empfohlen)

1. Vercel Account erstellen
2. PostgreSQL Datenbank (Vercel Postgres/Neon/Supabase)
3. Umgebungsvariablen in Vercel Dashboard setzen
4. Deploy: `vercel deploy --prod`

Detaillierte Anleitung: `django_app/README.md`

### Alternativen

- **Railway:** https://railway.app
- **Heroku:** https://heroku.com
- **DigitalOcean:** App Platform

## 📊 Admin-Interface

Django Admin: **http://localhost:8000/admin**

Features:
- User-Management (Credits, Verification)
- Question-Management (Gewichtung, Aktivierung)
- Analysis-Übersicht

## 📝 Management Commands

```bash
# Questions seeden
python manage.py seed_questions

# Superuser erstellen
python manage.py createsuperuser

# Migrationen
python manage.py makemigrations
python manage.py migrate

# Static Files sammeln (Production)
python manage.py collectstatic
```

## 🧪 Testing

```bash
# Alle Tests ausführen
python manage.py test

# Mit Coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📚 Dokumentation

- **Lokales Setup:** [SETUP_LOKAL.md](SETUP_LOKAL.md) ⭐
- **Django App Details:** [django_app/README.md](django_app/README.md)
- **Django Docs:** https://docs.djangoproject.com/
- **HTMX Docs:** https://htmx.org/docs/
- **Tailwind CSS:** https://tailwindcss.com/docs

## 🔒 Security

- Argon2 Password Hashing
- CSRF Protection
- SQL Injection Prevention (Django ORM)
- XSS Protection in Templates
- HTTPS Redirect (Production)
- HSTS Headers
- Session Security

## 🤝 Contributing

1. Fork das Repository
2. Feature Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

## 📄 License

Dieses Projekt ist privat. Alle Rechte vorbehalten.

## 👨‍💻 Entwickler

**Lucas Mussmann**
- GitHub: [@lucmuss](https://github.com/lucmuss)

---

## 🛠️ Development Status

**Status:** ✅ Production Ready (MVP)

**Version:** 1.0.0

**Letzte Aktualisierung:** Januar 2026

---

**Entwickelt mit Django, HTMX, Tailwind CSS & PostgreSQL** 🚀
