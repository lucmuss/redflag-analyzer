"""
Management Command: Detaillierte Red Flag Score Berechnung
Zeigt jeden Schritt der Berechnung: Von Importance-Bewertungen bis zum finalen Score
"""
from django.core.management.base import BaseCommand
from django.db.models import Avg
from questionnaire.models import Question, WeightResponse
from analyses.services import ScoreCalculator
import statistics


class Command(BaseCommand):
    help = 'Zeigt detaillierte Berechnung des Red Flag Scores Schritt für Schritt'

    def add_arguments(self, parser):
        parser.add_argument(
            '--use-z-score',
            action='store_true',
            default=True,
            help='Verwende Z-Score Standardisierung (empfohlen)'
        )
        parser.add_argument(
            '--no-z-score',
            action='store_true',
            help='Verwende einfachen Durchschnitt (ohne Standardisierung)'
        )

    def handle(self, *args, **options):
        use_z_score = not options['no_z_score']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('RED FLAG SCORE BERECHNUNG - DETAILLIERTE ANALYSE'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        if use_z_score:
            self.stdout.write(self.style.WARNING('📊 Modus: Z-SCORE STANDARDISIERUNG (empfohlen)\n'))
        else:
            self.stdout.write(self.style.WARNING('📊 Modus: EINFACHER DURCHSCHNITT\n'))
        
        # SCHRITT 1: Zeige Importance-Bewertungen der Benutzer
        self._show_step_1_user_importance()
        
        # SCHRITT 2: Zeige Z-Score Berechnung (falls aktiviert)
        if use_z_score:
            self._show_step_2_z_score()
        
        # SCHRITT 3: Zeige globale Gewichte
        self._show_step_3_global_weights(use_z_score)
        
        # SCHRITT 4: Zeige Impact-Berechnung
        self._show_step_4_impact_calculation()
        
        # SCHRITT 5: Zeige finale Score-Berechnung
        self._show_step_5_final_score()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('BERECHNUNG ABGESCHLOSSEN'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

    def _show_step_1_user_importance(self):
        """Zeigt wie Benutzer die Wichtigkeit von Fragen bewerten"""
        self.stdout.write(self.style.SUCCESS('\n[SCHRITT 1] BENUTZER IMPORTANCE-BEWERTUNGEN (1-10)\n'))
        self.stdout.write('-' * 80)
        
        # Hole 3 Beispiel-Fragen
        questions = Question.objects.filter(is_active=True)[:3]
        
        for question in questions:
            self.stdout.write(f"\n📋 Frage: {question.key}")
            
            responses = WeightResponse.objects.filter(question=question)[:5]
            
            if responses.exists():
                self.stdout.write("   Benutzer-Bewertungen (Wie wichtig ist diese Frage?):")
                for wr in responses:
                    email_short = wr.user.email.split('@')[0]
                    self.stdout.write(f"      • {email_short:15} → {wr.importance}/10")
                
                if WeightResponse.objects.filter(question=question).count() > 5:
                    remaining = WeightResponse.objects.filter(question=question).count() - 5
                    self.stdout.write(f"      ... und {remaining} weitere Bewertungen")
            else:
                self.stdout.write("   (Keine User-Bewertungen vorhanden)")

    def _show_step_2_z_score(self):
        """Zeigt die Z-Score Standardisierung"""
        self.stdout.write(self.style.SUCCESS('\n[SCHRITT 2] Z-SCORE STANDARDISIERUNG\n'))
        self.stdout.write('-' * 80)
        
        self.stdout.write("\n❓ Warum Z-Score Standardisierung?")
        self.stdout.write("   Problem: Manche Benutzer bewerten immer hoch (8-10), andere niedrig (2-4)")
        self.stdout.write("   Lösung: Standardisiere jeden Benutzer auf seine eigene Bewertungs-Tendenz\n")
        
        # Zeige Beispiel für 2 Benutzer
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users_with_weights = User.objects.filter(
            weight_responses__isnull=False
        ).distinct()[:2]
        
        if users_with_weights.exists():
            example_question = Question.objects.filter(is_active=True).first()
            
            for user_obj in users_with_weights:
                email_short = user_obj.email.split('@')[0]
                self.stdout.write(f"\n👤 Benutzer: {email_short}")
                
                # Hole alle Bewertungen dieses Benutzers
                user_weights = list(WeightResponse.objects.filter(
                    user=user_obj
                ).values_list('importance', flat=True))
                
                if len(user_weights) >= 2:
                    user_mean = statistics.mean(user_weights)
                    user_std = statistics.stdev(user_weights)
                    
                    self.stdout.write(f"   Seine Bewertungen: {user_weights[:5]}{'...' if len(user_weights) > 5 else ''}")
                    self.stdout.write(f"   Durchschnitt (μ): {user_mean:.2f}")
                    self.stdout.write(f"   Standardabweichung (σ): {user_std:.2f}")
                    
                    # Zeige Z-Score für Beispiel-Frage
                    user_response = WeightResponse.objects.filter(
                        user=user_obj,
                        question=example_question
                    ).first()
                    
                    if user_response:
                        z_score = (user_response.importance - user_mean) / user_std if user_std > 0 else 0
                        self.stdout.write(f"\n   Beispiel-Frage '{example_question.key}':")
                        self.stdout.write(f"   Original-Bewertung: {user_response.importance}/10")
                        self.stdout.write(f"   Z-Score = ({user_response.importance} - {user_mean:.2f}) / {user_std:.2f} = {z_score:.2f}")
                        self.stdout.write(f"   ✓ Standardisierter Wert: {z_score:.2f}")

    def _show_step_3_global_weights(self, use_z_score):
        """Zeigt wie globale Gewichte berechnet werden"""
        self.stdout.write(self.style.SUCCESS('\n[SCHRITT 3] GLOBALE GEWICHTE BERECHNEN\n'))
        self.stdout.write('-' * 80)
        
        # Berechne globale Gewichte mit gewählter Methode
        global_weights = ScoreCalculator.create_weight_snapshot(use_z_score=use_z_score)
        
        questions = Question.objects.filter(is_active=True)[:5]
        
        self.stdout.write("\n📊 Globales Gewicht = Durchschnitt aller (standardisierten) Bewertungen\n")
        
        for question in questions:
            responses = WeightResponse.objects.filter(question=question)
            
            if responses.exists():
                raw_avg = responses.aggregate(avg=Avg('importance'))['avg']
                global_weight = global_weights.get(question.key, question.default_weight)
                
                self.stdout.write(f"\n📋 {question.key}")
                self.stdout.write(f"   Anzahl Bewertungen: {responses.count()}")
                self.stdout.write(f"   Einfacher Durchschnitt: {raw_avg:.2f}")
                
                if use_z_score:
                    self.stdout.write(f"   Z-Score standardisiert: {global_weight:.2f}")
                    self.stdout.write(f"   ✓ Globales Gewicht: {global_weight:.2f} (mit Z-Score)")
                else:
                    self.stdout.write(f"   ✓ Globales Gewicht: {global_weight:.2f}")
            else:
                self.stdout.write(f"\n📋 {question.key}")
                self.stdout.write(f"   ⚠ Keine User-Daten, Default: {question.default_weight}")

    def _show_step_4_impact_calculation(self):
        """Zeigt die Impact-Berechnung für einzelne Fragen"""
        self.stdout.write(self.style.SUCCESS('\n[SCHRITT 4] IMPACT-BERECHNUNG PRO FRAGE\n'))
        self.stdout.write('-' * 80)
        
        self.stdout.write("\n💡 Impact = Bewertung × Globales Gewicht\n")
        self.stdout.write("   Bewertung: 1-5 (Wie stark trifft Red Flag zu?)")
        self.stdout.write("   Globales Gewicht: Berechneter Durchschnitt aus Schritt 3\n")
        
        # Erstelle Beispiel-Antworten
        example_data = [
            {'key': 'lies_frequently', 'rating': 5, 'global_weight': 5.92},
            {'key': 'high_bodycount', 'rating': 4, 'global_weight': 5.78},
            {'key': 'social_media_active', 'rating': 3, 'global_weight': 5.12},
            {'key': 'travels_alone', 'rating': 2, 'global_weight': 4.70},
        ]
        
        self.stdout.write("📝 BEISPIEL: Ein Benutzer beantwortet den Fragebogen:")
        self.stdout.write("   (1=trifft gar nicht zu, 5=trifft sehr stark zu)\n")
        
        total_weighted_sum = 0
        max_possible = 0
        
        for data in example_data:
            impact = data['rating'] * data['global_weight']
            max_impact = 5 * data['global_weight']  # Maximum ist immer 5
            
            total_weighted_sum += impact
            max_possible += max_impact
            
            self.stdout.write(f"\n   {data['key']:25}")
            self.stdout.write(f"      Bewertung: {data['rating']}/5")
            self.stdout.write(f"      Globales Gewicht: {data['global_weight']:.2f}")
            self.stdout.write(f"      Impact = {data['rating']} × {data['global_weight']:.2f} = {impact:.2f}")
            self.stdout.write(f"      Max möglich = 5 × {data['global_weight']:.2f} = {max_impact:.2f}")
        
        self.stdout.write(f"\n   {'─' * 60}")
        self.stdout.write(f"   Gewichtete Summe: {total_weighted_sum:.2f}")
        self.stdout.write(f"   Max mögliche Summe: {max_possible:.2f}")
        
        return total_weighted_sum, max_possible

    def _show_step_5_final_score(self):
        """Zeigt die finale Score-Berechnung"""
        self.stdout.write(self.style.SUCCESS('\n[SCHRITT 5] FINALER RED FLAG SCORE (0-5)\n'))
        self.stdout.write('-' * 80)
        
        # Verwende Daten aus Schritt 4
        example_data = [
            {'key': 'lies_frequently', 'rating': 5, 'global_weight': 5.92},
            {'key': 'high_bodycount', 'rating': 4, 'global_weight': 5.78},
            {'key': 'social_media_active', 'rating': 3, 'global_weight': 5.12},
            {'key': 'travels_alone', 'rating': 2, 'global_weight': 4.70},
        ]
        
        total_weighted_sum = sum(d['rating'] * d['global_weight'] for d in example_data)
        max_possible = sum(5 * d['global_weight'] for d in example_data)
        
        score = (total_weighted_sum / max_possible) * 5
        
        self.stdout.write("\n📐 FORMEL:")
        self.stdout.write("   Score = (Gewichtete Summe / Max mögliche Summe) × 5\n")
        
        self.stdout.write("🔢 BERECHNUNG:")
        self.stdout.write(f"   Score = ({total_weighted_sum:.2f} / {max_possible:.2f}) × 5")
        self.stdout.write(f"   Score = {total_weighted_sum/max_possible:.4f} × 5")
        self.stdout.write(f"   Score = {score:.2f}\n")
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ FINALER RED FLAG SCORE: {score:.2f} von 5.00\n"))
        
        # Interpretation
        if score < 1.5:
            interpretation = "🟢 NIEDRIG - Wenige Red Flags erkannt"
            advice = "Die Beziehung zeigt wenige Warnsignale."
        elif score < 3.0:
            interpretation = "🟡 MITTEL - Einige Warnsignale vorhanden"
            advice = "Moderate Red Flags. Aufmerksamkeit empfohlen."
        elif score < 4.0:
            interpretation = "🟠 HOCH - Viele Red Flags"
            advice = "Viele Warnsignale. Vorsicht geboten!"
        else:
            interpretation = "🔴 SEHR HOCH - Kritische Anzahl Red Flags"
            advice = "Sehr viele Warnsignale. Situation genau prüfen!"
        
        self.stdout.write(f"   📊 Interpretation: {interpretation}")
        self.stdout.write(f"   💡 Empfehlung: {advice}\n")
        
        # Prozentuale Auslastung
        percentage = (score / 5) * 100
        bar_length = int(percentage / 2)  # 50 chars = 100%
        bar = '█' * bar_length + '░' * (50 - bar_length)
        self.stdout.write(f"   [{bar}] {percentage:.1f}%\n")
