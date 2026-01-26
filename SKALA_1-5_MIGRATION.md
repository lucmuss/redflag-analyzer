# Skala-Umstellung auf 1-5 – Zusammenfassung

## ✅ Durchgeführte Änderungen

### 1. **Models (Datenbank)**
**Datei**: `django_app/questionnaire/models.py`

- `Question.calculated_weight`: 
  - Validator: `MaxValueValidator(10.0)` → `MaxValueValidator(5.0)`
  - Default: `5.0` → `3.0`
  - Help-Text: "1-10" → "1-5"

- `WeightResponse.importance`:
  - Validator: `MaxValueValidator(10)` → `MaxValueValidator(5)`
  - Help-Text: "1-10" → "1-5"
  - `__str__` Methode: `/10` → `/5`

### 2. **Gewichts-Berechnung**
**Dateien**: 
- `django_app/questionnaire/management/commands/update_global_weights.py`
- `django_app/questionnaire/signals.py`

Beide Dateien aktualisiert:
- Z-Score Rücktransformation: `max(1.0, min(10.0, weight))` → `max(1.0, min(5.0, weight))`
- Kommentare: "1-10 Skala" → "1-5 Skala"

### 3. **Serverstart-Hook**
**Datei**: `django_app/questionnaire/apps.py`

Neuer Code hinzugefügt:
```python
def ready(self):
    import questionnaire.signals
    
    # Berechne globale Gewichte beim Serverstart
    try:
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            logger.info('🔄 Berechne globale Gewichte beim Serverstart...')
            call_command('update_global_weights', verbosity=0)
            logger.info('✅ Globale Gewichte aktualisiert')
    except Exception as e:
        logger.warning(f'⚠️ Globale Gewichte konnten nicht beim Start berechnet werden: {e}')
```

### 4. **Templates**
**Dateien aktualisiert**:
- `django_app/templates/analyses/partials/unlocked_content.html`
  - Beispiel-Bewertungen: "8-10" / "2-4" → "4-5" / "1-2"
  
- `django_app/templates/referrals/share_screen.html`
  - Score-Anzeigen: `/10` → `/5`
  - JavaScript shareText: `/10` → `/5`

### 5. **Admin-Interfaces**
**Dateien aktualisiert**:
- `django_app/questionnaire/admin.py`
  - `default_weight` Referenzen → `calculated_weight`
  
- `django_app/analyses/admin.py`
  - `snapshot_weights` entfernt (obsolet - Snapshots wurden entfernt)

## 📋 Nächste Schritte (Benutzer muss durchführen)

### 1. Migration erstellen und ausführen

```bash
# Virtual Environment aktivieren
cd /home/skymuss/projects/redflag-analyzer/django_app
source venv/bin/activate  # oder: source env/bin/activate

# Migration erstellen
python manage.py makemigrations questionnaire -n "update_scale_to_1_5"

# Migration anwenden
python manage.py migrate
```

### 2. Globale Gewichte neu berechnen

```bash
# Mit Z-Score (empfohlen)
python manage.py update_global_weights

# ODER ohne Z-Score (einfacher Durchschnitt)
python manage.py update_global_weights --no-z-score
```

### 3. Server neustarten

```bash
# Development Server
python manage.py runserver

# Production (mit Gunicorn)
gunicorn redflag_project.wsgi:application
```

## 🎯 Wichtige Hinweise

### Skalen im System (EINHEITLICH 1-5)

1. **Benutzer-Antworten** (Response.value): **1-5**
   - Fragebogen-Antworten auf alle Fragen
   - Skala: 1 (niedriger) bis 5 (höher)

2. **Wichtigkeits-Bewertungen** (WeightResponse.importance): **1-5**
   - Benutzer bewerten wie wichtig jede Frage ist
   - Skala: 1 (niedrig wichtig) bis 5 (sehr wichtig)

3. **Globale Gewichte** (Question.calculated_weight): **1-5**
   - Aus WeightResponse via Z-Score aggregiert
   - Skala: 1.0 bis 5.0 (Float)

4. **Analyse-Scores** (Analysis.score_total): **0-5**
   - Gesamtscore der Analyse
   - Formel: `(Gewichtete Summe / Max Möglich) × 5`
   - Skala: 0.0 bis 5.0

### Automatische Updates

- **Beim Serverstart**: Globale Gewichte werden automatisch neu berechnet
- **Bei neuen WeightResponse**: Django Signals aktualisieren `calculated_weight` automatisch
- **Dynamisch**: Keine Snapshots mehr – immer aktuelle Gewichte aus DB

### Z-Score Standardisierung

Verhindert Bias durch optimistische/konservative Bewerter:
```
Für jeden Benutzer:
  1. Berechne μ (Durchschnitt) und σ (StdDev) seiner Bewertungen
  2. Z-Score jeder Bewertung: Z = (X - μ) / σ
  
Global:
  3. Durchschnitt aller Z-Scores bilden
  4. Zurück transformieren auf 1-5 Skala
  5. Begrenzen: max(1.0, min(5.0, weight))
```

## 🔍 Überprüfung

Nach der Migration solltest du überprüfen:

1. **Alte Daten**: Existierende WeightResponse-Einträge mit Werten > 5 müssen manuell korrigiert werden
2. **Question.calculated_weight**: Sollten alle zwischen 1.0 und 5.0 liegen
3. **Analysis.score_total**: Sollten alle zwischen 0.0 und 5.0 liegen
4. **Frontend**: Alle Anzeigen sollten "/5" zeigen

## 🚨 Datenmigration für existierende Daten

Falls du bereits Daten in der Datenbank hast, musst du diese skalieren:

```python
# Django Shell
python manage.py shell

from questionnaire.models import WeightResponse, Question

# WeightResponse von 1-10 zu 1-5 skalieren
for wr in WeightResponse.objects.all():
    wr.importance = round((wr.importance / 10.0) * 5.0)
    wr.save()

# Question calculated_weight von 1-10 zu 1-5 skalieren
for q in Question.objects.all():
    q.calculated_weight = round((q.calculated_weight / 10.0) * 5.0, 2)
    q.save()

# Globale Gewichte neu berechnen
exit()
python manage.py update_global_weights
```

## ✅ Ergebnis

Das **gesamte System** verwendet nun **ausschließlich die 1-5 Skala**:
- ✅ Keine 0-10 Skala mehr
- ✅ Keine 1-10 Skala mehr
- ✅ Einheitlich: 1-5 für Wichtigkeit/Gewichte
- ✅ Einheitlich: 0-5 für Scores (da gewichtete Summe bei 0 beginnen kann)
- ✅ Z-Score Normalisierung auf 1-5 Skala
- ✅ Automatische Updates beim Serverstart
- ✅ Frontend zeigt korrekte Skala

**Status**: Bereit für Migration ✅
