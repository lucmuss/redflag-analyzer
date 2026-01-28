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
- Nutze diesen Account für alle Browser-Tests
- Login-Flow: Browser öffnen → Login-Seite → Credentials eingeben → Einloggen
- Testdaten: Credits, Analysen, alle Features verfügbar

## ANTWORT-FORMAT
Nur diese Struktur:
