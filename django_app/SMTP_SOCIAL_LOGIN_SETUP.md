# 📧 SMTP & Social Login Setup Guide

## 🔐 SMTP Configuration für Email-Verifizierung

### Option 1: Gmail SMTP (Empfohlen für Entwicklung)

1. **Google App Password erstellen:**
   - Gehe zu https://myaccount.google.com/security
   - Aktiviere 2-Faktor-Authentifizierung (falls nicht aktiv)
   - Gehe zu "App-Passwörter" (App passwords)
   - Wähle "Mail" → "Andere" → "Django RedFlag"
   - Kopiere das generierte 16-stellige Passwort

2. **`.env` File konfigurieren:**
```bash
# Email Settings (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # App-Passwort von Schritt 1
DEFAULT_FROM_EMAIL=noreply@redflag-analyzer.com
```

3. **Test:**
```bash
cd django_app
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test Email', 'noreply@redflag-analyzer.com', ['test@example.com'])
```

### Option 2: SendGrid (Empfohlen für Production)

1. **SendGrid Account erstellen:**
   - Registrieren auf https://sendgrid.com (Free Tier: 100 Emails/Tag)
   - API Key erstellen unter "Settings" → "API Keys"

2. **`.env` File konfigurieren:**
```bash
# Email Settings (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # SendGrid API Key
DEFAULT_FROM_EMAIL=noreply@redflag-analyzer.com
```

### Option 3: Mailgun (Alternative)

```bash
# Email Settings (Mailgun)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@redflag-analyzer.com
```

---

## 🔑 Social Login Setup

### Google OAuth

1. **Google Cloud Console:**
   - Gehe zu https://console.cloud.google.com
   - Erstelle neues Projekt "RedFlag Analyzer"
   - Aktiviere "Google+ API"
   - Credentials → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application Type: "Web application"
   - Authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     https://your-domain.com/accounts/google/login/callback/
     ```
   - Kopiere Client ID & Client Secret

2. **Django Admin konfigurieren:**
   - Starte Server: `python manage.py runserver`
   - Gehe zu http://localhost:8000/admin/
   - Login als Superuser
   - Navigiere zu "Sites" → Ändere "example.com" zu "localhost:8000"
   - Navigiere zu "Social applications" → "Add social application"
   - Provider: Google
   - Name: Google OAuth
   - Client ID: `dein-client-id.apps.googleusercontent.com`
   - Secret key: `dein-client-secret`
   - Sites: Wähle "localhost:8000" aus
   - Save

3. **Template anpassen** (bereits in `account/login.html`):
```html
{% load socialaccount %}

<!-- Google Login Button -->
<a href="{% provider_login_url 'google' %}" 
   class="flex items-center justify-center w-full bg-white border border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-50 transition">
    <img src="https://www.google.com/favicon.ico" class="w-5 h-5 mr-3">
    Mit Google anmelden
</a>
```

### GitHub OAuth

1. **GitHub Developer Settings:**
   - Gehe zu https://github.com/settings/developers
   - "New OAuth App"
   - Application name: RedFlag Analyzer
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`
   - Kopiere Client ID & Client Secret

2. **Django Admin konfigurieren:**
   - Admin → "Social applications" → "Add"
   - Provider: GitHub
   - Name: GitHub OAuth
   - Client ID: `dein-github-client-id`
   - Secret key: `dein-github-secret`
   - Sites: Wähle "localhost:8000"
   - Save

3. **Template anpassen:**
```html
<!-- GitHub Login Button -->
<a href="{% provider_login_url 'github' %}" 
   class="flex items-center justify-center w-full bg-gray-900 text-white font-semibold py-3 px-6 rounded-lg hover:bg-gray-800 transition">
    <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
    Mit GitHub anmelden
</a>
```

---

## 🔧 Troubleshooting

### Email funktioniert nicht

1. **Prüfe Credentials:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST)
>>> print(settings.EMAIL_HOST_USER)
>>> print(settings.EMAIL_USE_TLS)
```

2. **Test manuell:**
```python
from django.core.mail import send_mail
send_mail(
    'Test Subject',
    'Test Message',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
    fail_silently=False,
)
```

3. **Check Logs:**
```bash
tail -f django_app/logs/django.log
```

### Social Login funktioniert nicht

1. **Prüfe Site Configuration:**
   - Admin → Sites → domain muss korrekt sein (z.B. `localhost:8000` oder `your-domain.com`)

2. **Prüfe Redirect URLs:**
   - Müssen in Google/GitHub Console EXAKT mit Django übereinstimmen
   - Achte auf Trailing Slash: `/callback/` vs `/callback`

3. **Check Allauth Installation:**
```bash
python manage.py migrate
```

---

## 📝 Testing Checklist

### Email-Verifizierung
- [ ] User registriert sich
- [ ] Verification Email wird versendet
- [ ] Email enthält korrekten Verification Link
- [ ] Link funktioniert und verifiziert Account
- [ ] User kann sich einloggen

### Social Login
- [ ] Google Login Button ist sichtbar
- [ ] Redirect zu Google funktioniert
- [ ] Nach Google Auth: Redirect zurück zur App
- [ ] User Account wird automatisch erstellt
- [ ] is_verified=True bei Social Login

---

## 🚀 Production Deployment

### Environment Variables für Vercel/Railway

```bash
# Production SMTP (SendGrid empfohlen)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-production-key
DEFAULT_FROM_EMAIL=noreply@redflag-analyzer.com

# Production OAuth URLs
# Google: https://redflag-analyzer.com/accounts/google/login/callback/
# GitHub: https://redflag-analyzer.com/accounts/github/login/callback/

# Site Domain in Admin ändern auf: redflag-analyzer.com
```

### Additional Settings

1. **Domain Verification (SendGrid):**
   - Settings → Sender Authentication
   - Authenticate Domain → Folge DNS Setup

2. **Email Templates customizen:**
   - `templates/account/email/email_confirmation_message.txt`
   - `templates/account/email/email_confirmation_subject.txt`

---

## 💡 Best Practices

1. **App Passwords verwenden:** Niemals echtes Gmail-Passwort in Code!
2. **Environment Variables:** Alle Secrets in `.env` speichern
3. **Rate Limiting:** SendGrid Free Tier hat Limits (100/Tag)
4. **Testing:** Immer mit echten Email-Adressen testen
5. **Production:** Dedicated Email Service Provider (SendGrid/Mailgun)
