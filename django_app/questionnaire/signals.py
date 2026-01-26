"""
Signals für automatische Gewichts-Updates
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import WeightResponse, Question
from django.contrib.auth import get_user_model
import statistics


@receiver(post_save, sender=WeightResponse)
@receiver(post_delete, sender=WeightResponse)
def update_calculated_weights(sender, instance, **kwargs):
    """
    Aktualisiert Question.calculated_weight automatisch wenn WeightResponse gespeichert/gelöscht wird.
    Verwendet Z-Score Standardisierung.
    """
    User = get_user_model()
    
    # Hole alle Benutzer mit Gewichtungen
    users_with_weights = User.objects.filter(
        weight_responses__isnull=False
    ).distinct()
    
    if not users_with_weights.exists():
        return
    
    # Hole alle aktiven Questions
    questions = Question.objects.filter(is_active=True)
    
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
