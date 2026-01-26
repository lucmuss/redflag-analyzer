"""
Management Command: Update Global Weights
Berechnet Z-Score standardisierte globale Gewichte und speichert sie in Question.calculated_weight
"""
from django.core.management.base import BaseCommand
from django.db.models import Avg
from questionnaire.models import Question, WeightResponse
from django.contrib.auth import get_user_model
import statistics


class Command(BaseCommand):
    help = 'Berechnet und aktualisiert globale Gewichte mit Z-Score Standardisierung'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-z-score',
            action='store_true',
            help='Verwende einfachen Durchschnitt statt Z-Score (nicht empfohlen)'
        )

    def handle(self, *args, **options):
        use_z_score = not options['no_z_score']
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('GLOBALE GEWICHTE AKTUALISIEREN'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))
        
        if use_z_score:
            self.stdout.write('📊 Modus: Z-SCORE STANDARDISIERUNG\n')
        else:
            self.stdout.write('📊 Modus: EINFACHER DURCHSCHNITT\n')
        
        User = get_user_model()
        questions = Question.objects.filter(is_active=True)
        
        # Prüfe ob überhaupt User-Daten vorhanden sind
        users_with_weights = User.objects.filter(
            weight_responses__isnull=False
        ).distinct()
        
        if not users_with_weights.exists():
            self.stdout.write(self.style.ERROR(
                '❌ FEHLER: Keine Benutzer-Gewichtungen gefunden!\n'
                'Bitte stelle sicher, dass mindestens ein Benutzer den Importance-Fragebogen ausgefüllt hat.\n'
            ))
            return
        
        self.stdout.write(f'Gefundene Benutzer mit Gewichtungen: {users_with_weights.count()}\n')
        
        updated_count = 0
        
        if not use_z_score:
            # EINFACHER DURCHSCHNITT
            self.stdout.write('Berechne einfache Durchschnitte...\n')
            for question in questions:
                avg_importance = WeightResponse.objects.filter(
                    question=question
                ).aggregate(avg=Avg('importance'))['avg']
                
                if avg_importance is not None:
                    question.calculated_weight = round(float(avg_importance), 2)
                    question.save(update_fields=['calculated_weight'])
                    updated_count += 1
                    
                    self.stdout.write(
                        f'  ✓ {question.key:40} → {question.calculated_weight:.2f}'
                    )
        else:
            # Z-SCORE STANDARDISIERUNG
            self.stdout.write('Berechne Z-Score standardisierte Gewichte...\n')
            
            for question in questions:
                z_scores = []
                
                # Für jeden Benutzer: Berechne Z-Score
                for user_obj in users_with_weights:
                    # Hole alle Importance-Bewertungen dieses Benutzers
                    user_weights = list(WeightResponse.objects.filter(
                        user=user_obj
                    ).values_list('importance', flat=True))
                    
                    if len(user_weights) < 2:
                        continue
                    
                    # Hole die Bewertung dieses Benutzers für diese Frage
                    user_response = WeightResponse.objects.filter(
                        user=user_obj,
                        question=question
                    ).first()
                    
                    if not user_response:
                        continue
                    
                    # Berechne Durchschnitt und StdDev der Bewertungen dieses Benutzers
                    user_mean = statistics.mean(user_weights)
                    user_std = statistics.stdev(user_weights)
                    
                    # Z-Score: (X - μ) / σ
                    if user_std > 0:
                        z_score = (float(user_response.importance) - user_mean) / user_std
                        z_scores.append(z_score)
                
                # Berechne Durchschnitt der Z-Scores
                if z_scores:
                    avg_z_score = statistics.mean(z_scores)
                    
                    # Transformiere zurück auf ursprüngliche Skala (1-5)
                    all_importances = list(WeightResponse.objects.values_list('importance', flat=True))
                    if all_importances:
                        global_mean = statistics.mean(all_importances)
                        global_std = statistics.stdev(all_importances) if len(all_importances) > 1 else 1
                        
                        # Rücktransformation: X = μ + (Z × σ)
                        weight = global_mean + (avg_z_score * global_std)
                        
                        # Begrenze auf 1-5 Skala
                        weight = max(1.0, min(5.0, weight))
                        
                        question.calculated_weight = round(weight, 2)
                        question.save(update_fields=['calculated_weight'])
                        updated_count += 1
                        
                        self.stdout.write(
                            f'  ✓ {question.key:40} → {question.calculated_weight:.2f} '
                            f'(Z-Scores: {len(z_scores)} Benutzer)'
                        )
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {updated_count} Gewichte erfolgreich aktualisiert!\n'))
        
        # Zeige Zusammenfassung
        self.stdout.write('\n' + '='*80)
        self.stdout.write('ZUSAMMENFASSUNG')
        self.stdout.write('='*80 + '\n')
        
        all_weights = [q.calculated_weight for q in questions]
        if all_weights:
            avg_weight = statistics.mean(all_weights)
            min_weight = min(all_weights)
            max_weight = max(all_weights)
            
            self.stdout.write(f'Durchschnittliches Gewicht: {avg_weight:.2f}')
            self.stdout.write(f'Niedrigstes Gewicht: {min_weight:.2f}')
            self.stdout.write(f'Höchstes Gewicht: {max_weight:.2f}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ ABGESCHLOSSEN\n'))
