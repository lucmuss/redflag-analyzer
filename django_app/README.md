# RedFlag Analyzer - Django Stack

**Moderne Django-Migration** vom bestehenden FastAPI/Flutter-Projekt zu einem hochperformanten, relationalen Django-Stack.

## 🎯 Tech Stack

- **Backend:** Django 5.0 (Latest Stable)
- **Datenbank:** PostgreSQL (Relational Integrity + Django ORM)
- **Interaktivität:** HTMX (Server-Side SPA ohne JS-Framework)
- **Styling:** Tailwind CSS (Utility-First, Mobile-First)
- **Deployment:** Vercel (Serverless Python Runtime)
- **Plattform:** PWA (Progressive Web App)

## 🏗️ Architektur-Vorteile

### HTMX statt Flutter/React
**Vorher (Flutter/React):**
```
Client State → API Call → JSON → State Update → Widget/Component Rebuild
```

**Jetzt (HTMX):**
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
Geschäftslogik liegt in Models und Service-Layern:
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
- **select_related/prefetch_related** für N+1 Query Prevention
- **JSONField** für flexible Daten (responses)

## 🚀 Setup & Installation

### 1. Virtuelle Umgebung erstellen
```bash
cd django_app
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 2. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
# Editiere .env und setze DATABASE_URL und SECRET_KEY
```

### 4. Datenbank erstellen
```bash
# PostgreSQL Datenbank erstellen
createdb redflag-analyzer

# Oder mit psql:
psql -U postgres
CREATE DATABASE "redflag-analyzer";
\q
```

### 5. Migrations ausführen
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Superuser erstellen
```bash
python manage.py createsuperuser
```

### 7. Questions seeden
```bash
python manage.py seed_questions
```

### 8. Server starten
```bash
python manage.py runserver
```

Öffne: http://localhost:8000

## 📁 Projektstruktur

```
django_app/
├── redflag_project/        # Django Projekt
│   ├── settings.py         # ← PostgreSQL, HTMX, PWA Config
│   ├── urls.py
│   └── wsgi.py            # ← Vercel Handler
├── accounts/              # User Management
│   ├── models.py          # ← User + UserProfile (1:1)
│   ├── views.py
│   └── admin.py
├── questionnaire/         # Fragebogen
│   ├── models.py          # ← Question Model
│   ├── views.py           # ← HTMX Views
│   └── management/
│       └── commands/
│           └── seed_questions.py
├── analyses/              # Analysen & Scores
│   ├── models.py          # ← Analysis + CategoryScore
│   ├── services.py        # ← ScoreCalculator (Service Layer)
│   └── views.py           # ← HTMX Unlock Pattern
├── templates/
│   ├── base.html          # ← Tailwind + HTMX Base
│   ├── questionnaire/
│   │   ├── home.html
│   │   └── questionnaire.html
│   └── analyses/
│       ├── detail.html
│       └── partials/
│           └── unlocked_content.html  # ← HTMX Partial
├── static/                # Static Files (Tailwind CSS)
├── vercel.json           # ← Vercel Config
└── requirements.txt
```

## 🔥 HTMX-Patterns

### 1. Fragebogen Submit
```html
<form hx-post="{% url 'questionnaire:submit' %}" 
      hx-indicator=".htmx-indicator">
    {% csrf_token %}
    <!-- Questions -->
    <button type="submit">Absenden</button>
</form>
```

### 2. Analysis Unlock
```html
<button hx-post="{% url 'analyses:unlock' pk=analysis.id %}"
        hx-target="#analysis-content"
        hx-swap="innerHTML">
    Für 1 Credit entsperren
</button>
```

Server returned HTML-Fragment → HTMX swapped automatisch!

## 🗄️ Datenbank-Schema

### User Model
```sql
users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE,
    password_hash VARCHAR(128),
    credits INTEGER DEFAULT 1,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
)
```

### Question Model
```sql
questions (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE,
    category VARCHAR(20),  -- TRUST, BEHAVIOR, VALUES, DYNAMICS
    default_weight INTEGER,
    text_de TEXT,
    text_en TEXT,
    is_active BOOLEAN
)
```

### Analysis Model
```sql
analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    is_unlocked BOOLEAN,
    responses JSONB,  -- [{"key": "...", "value": 4}, ...]
    snapshot_weights JSONB,
    score_total DECIMAL(4,2),
    created_at TIMESTAMP
)
```

## 🚢 Deployment auf Vercel

### 1. Vercel CLI installieren
```bash
npm install -g vercel
```

### 2. PostgreSQL Datenbank erstellen
Nutze einen dieser Provider:
- **Vercel Postgres** (empfohlen)
- **Neon** (https://neon.tech)
- **Supabase** (https://supabase.com)

### 3. Umgebungsvariablen in Vercel setzen
```bash
vercel env add SECRET_KEY
vercel env add DATABASE_URL
vercel env add DEBUG
vercel env add ALLOWED_HOSTS
```

### 4. Deploy
```bash
vercel deploy --prod
```

### 5. Migrations auf Production ausführen
```bash
vercel exec -- python manage.py migrate
vercel exec -- python manage.py seed_questions
vercel exec -- python manage.py createsuperuser
```

## 📊 Admin-Interface

Django Admin verfügbar unter: `/admin/`

Features:
- User-Management (Credits, Verification)
- Question-Management (Aktivierung, Gewichtung)
- Analysis-Übersicht mit Category Scores

## 🎨 PWA-Features

Die App ist installierbar als Progressive Web App:
- **Manifest:** `/manifest.json` (via django-pwa)
- **Service Worker:** Automatisch generiert
- **Icons:** In `/static/icons/`
- **Offline-Ready:** (optional implementierbar)

## 📝 Management Commands

```bash
# Questions seeden
python manage.py seed_questions

# Admin erstellen
python manage.py createsuperuser

# Static Files sammeln (Production)
python manage.py collectstatic --noinput

# Migrations
python manage.py makemigrations
python manage.py migrate
```

## 🔒 Security Features

- **Argon2** Password Hashing
- **CSRF** Protection
- **SQL Injection** Protection (Django ORM)
- **XSS** Protection in Templates
- **HTTPS** Redirect in Production
- **HSTS** Headers
- **Session Security**

## 📚 Weitere Dokumentation

- **Django Docs:** https://docs.djangoproject.com/
- **HTMX Docs:** https://htmx.org/docs/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Vercel Docs:** https://vercel.com/docs

---

**Entwickelt als Senior Django Architecture Migration**  
FastAPI/MongoDB → Django/PostgreSQL mit HTMX & Tailwind CSS
