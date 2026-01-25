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
        help_text="Name der analysierten Partnerin"
    )
    partner_age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        help_text="Alter der Partnerin"
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
    # Snapshot der Gewichte zum Zeitpunkt der Analyse
    snapshot_weights = models.JSONField(
        help_text="Snapshot of weights used at analysis time"
    )
    score_total = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Total weighted score (0-10)"
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
        Dies wird normalerweise bei Erstellung aufgerufen.
        """
        from analyses.services import ScoreCalculator
        calculator = ScoreCalculator(self.responses, self.snapshot_weights)
        return calculator.calculate_category_scores()
    
    def get_top_red_flags(self, limit=5):
        """
        Business Logic: Hole Top Red Flags basierend auf Impact.
        Impact = response_value * weight
        """
        if not self.is_unlocked:
            return None
        
        red_flags = []
        for response in self.responses:
            key = response['key']
            value = response['value']
            weight = self.snapshot_weights.get(key, 3)
            impact = value * weight
            red_flags.append({
                'key': key,
                'value': value,
                'weight': weight,
                'impact': impact
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
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    class Meta:
        db_table = 'category_scores'
        unique_together = ['analysis', 'category']
        indexes = [
            models.Index(fields=['analysis', 'category']),
        ]
    
    def __str__(self):
        return f"{self.category}: {self.score}"
