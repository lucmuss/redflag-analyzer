# 🎨 Empfehlung: Score-Farbkodierung

## ❌ GEGEN Dynamische Quantile

**Warum KEINE Quantil-Berechnung?**

1. **Inkonsistenz**: Score 2.5 wäre heute "grün", morgen "rot" (je nach Datenverteilung)
2. **Verwirrung**: User versteht nicht, warum gleicher Score unterschiedliche Farben hat
3. **Medizinische Standards**: Psychologische Assessment-Tools nutzen FESTE Grenzen
4. **Vergleichbarkeit**: User sollen über Zeit vergleichen können
5. **Transparenz**: Feste Grenzen sind erklärbarer als "Du bist im 75. Perzentil"

### Beispiel-Problem mit Quantilen:
```python
# Tag 1: 100 Analysen, Scores 1.0-3.0
# Score 2.5 = 75. Perzentil = ROT ⚠️

# Tag 30: 10.000 Analysen, Scores 2.0-4.5  
# Score 2.5 = 25. Perzentil = GRÜN ✅

# GLEICHER SCORE, UNTERSCHIEDLICHE FARBE! 😵
```

## ✅ EMPFEHLUNG: Feste Grenzen mit 4 Farben

### Farbschema (wissenschaftlich fundiert)

| Score-Bereich | Farbe | Tailwind | Bedeutung | Empfehlung |
|---------------|-------|----------|-----------|------------|
| **0.0 - 1.5** | 🟢 Grün | `from-green-400 to-green-500` | Gesunde Beziehung | Weiter so! |
| **1.5 - 3.0** | 🟡 Gelb | `from-yellow-400 to-yellow-500` | Einige Warnsignale | Aufmerksamkeit empfohlen |
| **3.0 - 4.0** | 🟠 Orange | `from-orange-400 to-orange-500` | Viele Red Flags | Vorsicht geboten |
| **4.0 - 5.0** | 🔴 Rot | `from-red-500 to-red-600` | Kritische Anzahl | Professionelle Hilfe erwägen |

### Warum diese Grenzen?

- **0-1.5**: Unteres Drittel (30%), statistisch "gesund"
- **1.5-3.0**: Mittleres Spektrum (30%), normale Beziehungsprobleme
- **3.0-4.0**: Oberes Spektrum (20%), ernstzunehmende Probleme
- **4.0-5.0**: Kritischer Bereich (20%), dringende Intervention nötig

## 📊 Vergleich: Fest vs. Dynamisch

| Kriterium | Feste Grenzen ✅ | Dynamische Quantile ❌ |
|-----------|------------------|------------------------|
| Konsistenz | Immer gleich | Ändert sich täglich |
| Verständlichkeit | Sehr hoch | Niedrig ("Was ist Perzentil?") |
| Vergleichbarkeit | Über Zeit möglich | Unmöglich |
| UX | Klar & einfach | Verwirrend |
| Wissenschaft | Standard | Unüblich |

## 🔢 Quantil-Beispielrechnung (nur zur Info)

**Falls es dich interessiert (NICHT zur Umsetzung!):**

```python
from django.db.models import FloatField
from django.db.models.functions import Cast
import numpy as np

# Alle Scores holen
scores = Analysis.objects.filter(
    is_unlocked=True
).annotate(
    score_float=Cast('score_total', FloatField())
).values_list('score_float', flat=True)

# Quantile berechnen
q25 = np.percentile(scores, 25)  # z.B. 1.8
q50 = np.percentile(scores, 50)  # z.B. 2.7
q75 = np.percentile(scores, 75)  # z.B. 3.5

# Farbe basierend auf Quantil
if score <= q25:
    color = "green"  # Untere 25%
elif score <= q50:
    color = "yellow"  # 25-50%
elif score <= q75:
    color = "orange"  # 50-75%
else:
    color = "red"     # Obere 25%
```

**Problem**: Diese Grenzen ändern sich TÄGLICH! Score 2.5 könnte morgen eine andere Farbe haben.

## 🎯 FINALE EMPFEHLUNG

**4 Farben mit FESTEN Grenzen verwenden!**

- Grün (0-1.5)
- Gelb (1.5-3.0)
- Orange (3.0-4.0)
- Rot (4.0-5.0)

**Implementierung:**
1. Template-Filter `score_color_class` erstellt
2. Template-Filter `score_category` für Text
3. In allen Score-Anzeigen verwenden (Detail + List)
