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
