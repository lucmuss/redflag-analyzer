"""
Analysis Models für PostgreSQL
Relationale Struktur mit ForeignKeys und JSONField für Flexibilität
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from questionnaire.models import Question


class Analysis(models.Model):
    """
    Haupt-Analyse-Model mit User-Relation.
    Verwendet JSONField für responses (flexibel) und separate Category-Scores.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses'
    )
    
    # Partner-Information
    partner_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name der analysierten Partnerin (optional)"
    )
    partner_age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        help_text="Alter der Partnerin (optional)"
    )
    partner_country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Herkunftsland der Partnerin (optional)"
    )
    
    is_unlocked = models.BooleanField(
        default=False,
        help_text="Whether analysis is unlocked (paid)"
    )
    # JSON für responses ermöglicht Flexibilität
    # Format: [{"key": "father_absence", "value": 4}, ...]
    responses = models.JSONField(
        help_text="Question responses as JSON array"
    )
    score_total = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Total weighted score (0-5)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analyses'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_unlocked']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.id} by {self.user.email}"
    
    def unlock(self) -> bool:
        """
        Business Logic: Entsperre die Analyse.
        Prüft ob User genug Credits hat.
        """
        if not self.is_unlocked and self.user.consume_credit():
            self.is_unlocked = True
            self.save(update_fields=['is_unlocked'])
            return True
        return False
    
    def calculate_scores(self):
        """
        Business Logic: Berechne Category Scores aus responses.
        Verwendet DYNAMISCH aktuelle Question.calculated_weight Werte.
        """
        from analyses.services import ScoreCalculator
        calculator = ScoreCalculator(self.responses)
        return calculator.calculate_category_scores()
    
    def get_top_red_flags(self, limit=5):
        """
        Business Logic: Hole Top Red Flags basierend auf Impact.
        Impact = response_value * calculated_weight (DYNAMISCH aus Question)
        Verwendet kompakte Texte für bessere mobile Darstellung.
        """
        if not self.is_unlocked:
            return None
        
        # Hole aktuelle calculated_weights UND Texte aus Question Model
        questions = {q.key: q for q in Question.objects.filter(is_active=True)}
        
        red_flags = []
        for response in self.responses:
            key = response['key']
            value = response['value']
            
            # DYNAMISCH: Hole aktuelles calculated_weight und Text
            question = questions.get(key)
            weight = question.calculated_weight if question else 5.0
            
            # Verwende kompakten Text falls vorhanden, sonst normalen Text
            if question:
                text = question.text_short_de if question.text_short_de else question.text_de
                number = question.get_display_number()
            else:
                text = key.replace('_', ' ').title()
                number = 0
            
            impact = value * weight
            max_possible = 5 * weight  # Maximum möglich: 5 × Gewicht
            red_flags.append({
                'key': key,
                'text': text,
                'number': number,
                'value': value,
                'weight': weight,
                'impact': impact,
                'max_possible': max_possible
            })
        
        # Sortiere nach Impact (absteigend)
        red_flags.sort(key=lambda x: x['impact'], reverse=True)
        return red_flags[:limit]


class CategoryScore(models.Model):
    """
    Separate Tabelle für Category Scores (normalisiert).
    Ermöglicht effiziente Queries nach Kategorien.
    """
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name='category_scores'
    )
    category = models.CharField(
        max_length=20,
        choices=Question.CATEGORY_CHOICES
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    class Meta:
        db_table = 'category_scores'
        unique_together = ['analysis', 'category']
        indexes = [
            models.Index(fields=['analysis', 'category']),
        ]
    
    def __str__(self):
        return f"{self.category}: {self.score}"
