"""
Management Command: Zeige globale Durchschnittsgewichte
Berechnet den Durchschnitt aller User-Importance-Werte pro Frage
"""
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from questionnaire.models import Question, WeightResponse


class Command(BaseCommand):
    help = 'Berechnet und zeigt globale Durchschnittsgewichte aller Benutzer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== GLOBALE GEWICHTE BERECHNUNG ===\n'))
        
        # Hole alle aktiven Questions
        questions = Question.objects.filter(is_active=True).order_by('category', 'key')
        
        self.stdout.write(f"Anzahl aktiver Fragen: {questions.count()}\n")
        
        # Berechne globale Gewichte
        global_weights = {}
        
        for question in questions:
            # Berechne Durchschnitt aller importance-Werte für diese Frage
            stats = WeightResponse.objects.filter(question=question).aggregate(
                avg_importance=Avg('importance'),
                count=Count('id')
            )
            
            avg_importance = stats['avg_importance']
            count = stats['count']
            
            # Wenn keine Responses vorhanden, verwende default_weight
            if avg_importance is None:
                global_weights[question.key] = float(question.default_weight)
                weight_display = f"{question.default_weight:.1f} (default, keine User-Daten)"
            else:
                global_weights[question.key] = float(avg_importance)
                weight_display = f"{avg_importance:.2f} (Ø von {count} Benutzern)"
            
            # Ausgabe mit Formatierung
            category_emoji = {
                'TRUST': '🤝',
                'BEHAVIOR': '🎭',
                'VALUES': '💎',
                'DYNAMICS': '⚡'
            }
            emoji = category_emoji.get(question.category, '📊')
            
            self.stdout.write(
                f"{emoji} {question.category:10} | {question.key:30} | "
                f"Gewicht: {weight_display}"
            )
        
        # Zusammenfassung nach Kategorie
        self.stdout.write(self.style.SUCCESS('\n=== ZUSAMMENFASSUNG PRO KATEGORIE ===\n'))
        
        for category, _ in Question.CATEGORY_CHOICES:
            category_questions = questions.filter(category=category)
            category_weights = [
                global_weights[q.key] for q in category_questions 
                if q.key in global_weights
            ]
            
            if category_weights:
                avg_weight = sum(category_weights) / len(category_weights)
                self.stdout.write(
                    f"{category:10} | Ø Gewicht: {avg_weight:.2f} "
                    f"({len(category_weights)} Fragen)"
                )
        
        # Gesamtstatistik
        self.stdout.write(self.style.SUCCESS('\n=== GESAMTSTATISTIK ===\n'))
        
        total_users = WeightResponse.objects.values('user').distinct().count()
        total_responses = WeightResponse.objects.count()
        
        if global_weights:
            overall_avg = sum(global_weights.values()) / len(global_weights)
            self.stdout.write(f"Gesamtanzahl Benutzer mit Importance-Daten: {total_users}")
            self.stdout.write(f"Gesamtanzahl WeightResponses: {total_responses}")
            self.stdout.write(f"Durchschnittliches globales Gewicht: {overall_avg:.2f}")
        
        # Beispielberechnung: Globales Gewicht
        self.stdout.write(self.style.SUCCESS('\n=== BEISPIEL 1: GLOBALES GEWICHT ===\n'))
        
        example_question = questions.first()
        if example_question:
            responses = WeightResponse.objects.filter(question=example_question)
            
            self.stdout.write(f"\nFrage: {example_question.key}")
            self.stdout.write(f"Default Weight aus Question-Tabelle: {example_question.default_weight}")
            
            if responses.exists():
                self.stdout.write(f"\nImportance-Werte von Benutzern:")
                for wr in responses[:5]:
                    self.stdout.write(f"  - {wr.user.email}: {wr.importance}/10")
                
                if responses.count() > 5:
                    self.stdout.write(f"  ... und {responses.count() - 5} weitere")
                
                avg = responses.aggregate(avg=Avg('importance'))['avg']
                self.stdout.write(f"\nBerechnung: Summe aller Importance / Anzahl Benutzer")
                total = sum([wr.importance for wr in responses])
                self.stdout.write(f"           = {total} / {responses.count()}")
                self.stdout.write(f"           = {avg:.2f}")
                self.stdout.write(f"\n✓ Globales Gewicht: {avg:.2f}")
            else:
                self.stdout.write("Keine User-Daten vorhanden, würde default_weight verwenden")
        
        # Beispielberechnung: Red Flag Score
        self.stdout.write(self.style.SUCCESS('\n=== BEISPIEL 2: RED FLAG SCORE BERECHNUNG (0-5) ===\n'))
        
        self.stdout.write("\nAngenommen, ein Benutzer hat folgende Fragebogen-Antworten:")
        self.stdout.write("(Bewertung: 1=gar nicht, 5=sehr stark)\n")
        
        # Erstelle Beispiel-Daten
        example_responses = [
            {'key': 'high_bodycount', 'value': 5, 'global_weight': 5.0},
            {'key': 'lies_frequently', 'value': 4, 'global_weight': 5.0},
            {'key': 'travels_alone', 'value': 2, 'global_weight': 2.0},
            {'key': 'social_media_active', 'value': 3, 'global_weight': 2.0},
        ]
        
        total_weighted_sum = 0
        max_possible = 0
        
        for resp in example_responses:
            impact = resp['value'] * resp['global_weight']
            max_impact = 5 * resp['global_weight']
            
            self.stdout.write(
                f"  {resp['key']:30} | "
                f"Bewertung: {resp['value']}/5 × "
                f"Globales Gewicht: {resp['global_weight']:.1f} = "
                f"Impact: {impact:.1f}"
            )
            
            total_weighted_sum += impact
            max_possible += max_impact
        
        # Berechne Score
        if max_possible > 0:
            score = (total_weighted_sum / max_possible) * 5
            
            self.stdout.write(f"\nGewichtete Summe: {total_weighted_sum:.1f}")
            self.stdout.write(f"Max mögliche Summe: {max_possible:.1f}")
            self.stdout.write(f"\nRed Flag Score = (Gewichtete Summe / Max möglich) × 5")
            self.stdout.write(f"               = ({total_weighted_sum:.1f} / {max_possible:.1f}) × 5")
            self.stdout.write(f"               = {score:.2f}/5")
            
            self.stdout.write(f"\n✓ Red Flag Score: {score:.2f} von 5 Punkten")
            
            # Interpretation
            if score < 1.5:
                interpretation = "Niedrig - Wenige Red Flags"
            elif score < 3.0:
                interpretation = "Mittel - Einige Warnsignale"
            else:
                interpretation = "Hoch - Viele Red Flags"
            
            self.stdout.write(f"  → Interpretation: {interpretation}")
        
        self.stdout.write(self.style.SUCCESS('\n=== FERTIG ===\n'))
