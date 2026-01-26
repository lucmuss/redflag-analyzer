# Red Flag Score Berechnung - Beispielrechnung

## System-Übersicht

### Wichtigkeit-Skala (Weight/Gewicht):
- Benutzer bewerten jede Frage von 1-10, wie wichtig sie ihnen ist
- **Globales Gewicht** = Standardisierter Durchschnitt aller Benutzerbewertungen
- Beispiel aus Excel: Frage "Sie ist eine Feministin..." hat Gewicht 6.13

### Z-Score Standardisierung (WICHTIG!)

**Problem ohne Standardisierung:**
- Benutzer A gibt immer 8-10 (optimistisch)
- Benutzer B gibt immer 3-5 (konservativ)  
- Einfacher Durchschnitt wird von Benutzer A dominiert!

**Lösung mit Z-Score Standardisierung:**

1. **Für jeden Benutzer einzeln:**
   - Berechne Durchschnitt (μ) und Standardabweichung (σ) seiner Bewertungen
   - Standardisiere jede seiner Bewertungen: Z = (X - μ) / σ

2. **Über alle Benutzer:**
   - Berechne Durchschnitt der Z-Scores für jede Frage
   - Transformiere zurück auf 1-10 Skala

**Beispiel:**
```
Benutzer A (optimistisch):
- Seine Bewertungen: [8, 9, 10, 8, 9] → Durchschnitt = 8.8, StdDev = 0.75
- Frage "Feministin" bewertet er mit 10
- Z-Score = (10 - 8.8) / 0.75 = 1.6

Benutzer B (konservativ):
- Seine Bewertungen: [3, 4, 5, 3, 4] → Durchschnitt = 3.8, StdDev = 0.75
- Frage "Feministin" bewertet er mit 5
- Z-Score = (5 - 3.8) / 0.75 = 1.6

Beide haben Z-Score = 1.6 → Gleicher Einfluss auf das globale Gewicht!
```

### Bewertungs-Skala (Rating):
- **In der Excel**: Bewertungen von 1-10 (wie stark trifft dies zu)
- **In unserem Django-System**: Bewertungen von 1-5 (wie stark trifft dies zu)

---

## Beispielrechnung aus der Excel (Skala 1-10)

### Nehmen wir 4 Beispiel-Fragen:

| Frage | Globales Gewicht | Bewertung | Impact (Bewertung × Gewicht) |
|-------|-----------------|-----------|------------------------------|
| Feministin | 6.13 | 10 | 10 × 6.13 = **61.3** |
| Geschieden | 6.43 | 8 | 8 × 6.43 = **51.44** |
| Hoher Bodycount | 5.78 | 9 | 9 × 5.78 = **52.02** |
| Social Media aktiv | 5.12 | 7 | 7 × 5.12 = **35.84** |

**Gewichtete Summe** = 61.3 + 51.44 + 52.02 + 35.84 = **200.6**

**Maximale mögliche Summe** = (10 × 6.13) + (10 × 6.43) + (10 × 5.78) + (10 × 5.12) = **234.6**

**Normalisierter Score (0-10)** = (200.6 / 234.6) × 10 = **8.55** von 10

---

## Angepasste Berechnung für unser Django-System (Skala 1-5)

### Dieselben 4 Fragen, aber mit Bewertungen 1-5:

| Frage | Globales Gewicht | Bewertung (1-5) | Impact (Bewertung × Gewicht) |
|-------|-----------------|-----------------|------------------------------|
| Feministin | 6.13 | 5 | 5 × 6.13 = **30.65** |
| Geschieden | 6.43 | 4 | 4 × 6.43 = **25.72** |
| Hoher Bodycount | 5.78 | 5 | 5 × 5.78 = **28.9** |
| Social Media aktiv | 5.12 | 3 | 3 × 5.12 = **15.36** |

**Gewichtete Summe** = 30.65 + 25.72 + 28.9 + 15.36 = **100.63**

**Maximale mögliche Summe** = (5 × 6.13) + (5 × 6.43) + (5 × 5.78) + (5 × 5.12) = **117.3**

**Normalisierter Score (0-5)** = (100.63 / 117.3) × 5 = **4.29** von 5

---

## Warum ist die maximale Summe NICHT einfach "Anzahl Fragen × 25" (bei Skala 1-5)?

❌ **Falsch**: Max = 4 Fragen × 25 = 100

✅ **Richtig**: Max = Σ (5 × Globales Gewicht jeder Frage) = 117.3

### Erklärung:

Jede Frage hat ein **unterschiedliches globales Gewicht**, basierend darauf, wie wichtig die Benutzer sie finden:

- Frage mit Gewicht 6.43: Max Impact = 5 × 6.43 = **32.15**
- Frage mit Gewicht 5.12: Max Impact = 5 × 5.12 = **25.60**
- Frage mit Gewicht 3.75: Max Impact = 5 × 3.75 = **18.75**

Das ist der **Kerngedanke des crowd-sourced Gewichtungssystems**:
- Wichtigere Fragen (hohes Gewicht) tragen mehr zum Score bei
- Unwichtigere Fragen (niedriges Gewicht) tragen weniger bei

---

## Code-Implementierung in Django (`analyses/services.py`)

```python
def calculate_total_score(self):
    """
    Berechnet den gewichteten Score (0-5)
    """
    total_weighted_sum = 0
    max_possible = 0
    
    for response in self.responses.all():
        question = response.question
        rating = response.rating  # 1-5
        
        # Globales Gewicht aus dem Snapshot
        global_weight = self.weight_snapshot.get(question.key, 5.0)
        
        # Impact = Rating × Globales Gewicht
        impact = rating * global_weight
        total_weighted_sum += impact
        
        # Maximaler Impact für diese Frage = 5 × Globales Gewicht
        max_possible += (5 * global_weight)
    
    # Normalisierung auf 0-5 Skala
    if max_possible > 0:
        score = (total_weighted_sum / max_possible) * 5
        return round(score, 2)
    
    return 0
```

---

## Zusammenfassung

### Excel-System (1-10 Skala):
- Bewertung: 1-10
- Gewichte: Durchschnitt der Wichtigkeitsbewertungen (z.B. 6.13)
- Max pro Frage: 10 × Gewicht
- Finaler Score: (Summe / Max) × 10 = Score von 0-10

### Django-System (1-5 Skala):
- Bewertung: 1-5
- Gewichte: Durchschnitt der Wichtigkeitsbewertungen (z.B. 6.13)
- Max pro Frage: 5 × Gewicht
- Finaler Score: (Summe / Max) × 5 = Score von 0-5

**Beide Systeme verwenden dieselbe Logik**, nur mit unterschiedlichen Bewertungs-Skalen!
