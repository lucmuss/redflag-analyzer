# CLINE RULES - RedFlag Analyzer

## OUTPUT-REGELN (Kostenreduktion!)
- KEINE Erklärungen, nur Code
- KEINE Markdown-Dateien generieren (außer explizit angefragt)
- KEINE Code-Wiederholungen - nur geänderte Zeilen zeigen
- KEINE Bestätigungsfragen - sofort implementieren
- MAX 50 Zeilen pro Antwort wenn möglich
- Bei großen Files: Nur Diff/Änderungen, nicht komplette Datei

## IMPLEMENTIERUNGS-REGELN
- Features VOLLSTÄNDIG implementieren (Backend + Frontend + URLs + Templates)
- Django-Konventionen: Views, Models, Forms, URLs, Templates
- HTMX für Frontend-Interaktionen, kein JavaScript
- Tailwind CSS für Styling

## FEATURE-VOLLSTÄNDIGKEIT (KRITISCH!)
Jedes Feature muss 100% komplett sein:
1. **Backend:** Model → Migration → Admin → View → URL
2. **Frontend:** Template → Navigation-Link (Desktop + Mobile)
3. **Integration:** URL in redflag_project/urls.py registriert
4. **Security:** Secrets in .env/.env.example, NIE im Code
5. **Testing:** Manuelle Tests mit Browser (dev-login verwenden)

**KEINE LOSEN ENDEN:**
- Jede View braucht Template
- Jedes Template braucht URL
- Jede URL braucht Navigation-Link
- Jede neue App in INSTALLED_APPS + urls.py

## TEMPLATE-STANDARDS
- **Basis:** {% extends 'base.html' %}
- **Styling:** Tailwind CSS (text-red-flag, bg-red-50, etc.)
- **Responsiveness:** Mobile-first (hidden md:flex, etc.)
- **Icons:** Emojis verwenden (🔥, 📊, 💬, etc.)
- **Forms:** HTMX für alle Submissions (hx-post, hx-swap)
- **Messages:** Django Messages Framework verwenden

## CODE-QUALITÄT
- **DRY:** Keine Code-Duplikation
- **Indexes:** DB-Felder mit vielen Queries indizieren (db_index=True)
- **Queries:** Annotate/Prefetch für Performance
- **Security:** Rate Limiting (@login_required, @ratelimit)
- **DSGVO:** Auto-Delete für sensitive Daten (expires_at)

## FINALE PRÜFUNG VOR ABSCHLUSS
Vor attempt_completion IMMER prüfen:
- [ ] Alle Models haben Migrations
- [ ] Alle Views haben Templates
- [ ] Alle URLs registriert + Navigation-Links
- [ ] Alle Secrets in .env
- [ ] Admin-Interfaces vorhanden
- [ ] Browser-Tests erfolgreich

## PROJEKT-KONTEXT
- Working Dir: django_app/
- Venv: django_app/venv/
- Settings: redflag_project/settings.py
- Templates: django_app/templates/

## TESTACCOUNT FÜR GUI-TESTS
- Email: `os.getenv('TEST_USER_EMAIL')` aus django_app/.env
- Password: `os.getenv('TEST_USER_PASSWORD')` aus django_app/.env
- **AUTO-LOGIN:** Vor jedem Browser-Test diese URL aufrufen: `http://127.0.0.1:8000/accounts/dev-login/`
  - Loggt automatisch Test-User ein (nur DEBUG=True)
  - Danach zu Test-URL navigieren - User ist bereits eingeloggt
  - Erspart manuellen Login-Flow
- Testdaten: Credits, Analysen, alle Features verfügbar (is_staff=True, is_superuser=True)

## ANTWORT-FORMAT
Nur diese Struktur:
