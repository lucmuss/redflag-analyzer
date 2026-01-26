"""
Question Models für PostgreSQL
Relationaler Ansatz mit Foreign Keys
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Question(models.Model):
    """
    Fragen mit Kategorisierung und Gewichtung.
    PostgreSQL-optimiert mit Indizes auf key und category.
    """
    CATEGORY_CHOICES = [
        ('TRUST', 'Trust'),
        ('BEHAVIOR', 'Behavior'),
        ('VALUES', 'Values'),
        ('DYNAMICS', 'Dynamics'),
    ]
    
    key = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True,
        help_text="Unique question identifier (snake_case)"
    )
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    calculated_weight = models.FloatField(
        default=3.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text="Calculated global weight from Z-Score standardization (1-5)"
    )
    text_de = models.TextField(help_text="German question text")
    text_en = models.TextField(help_text="English question text")
    
    # Metadaten
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} ({self.category})"
    
    @classmethod
    def get_active_by_category(cls):
        """Business Logic: Gruppiere aktive Fragen nach Kategorie."""
        return {
            category: list(cls.objects.filter(category=category, is_active=True))
            for category, _ in cls.CATEGORY_CHOICES
        }
    
    def get_text(self, language='de'):
        """Business Logic: Hole Text in bevorzugter Sprache."""
        return self.text_de if language == 'de' else self.text_en


class WeightResponse(models.Model):
    """
    User-spezifische Gewichtungen für Questions.
    Erlaubt personalisierte Score-Berechnungen basierend auf individueller Wichtigkeit.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weight_responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='weight_responses'
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's importance rating (1-5)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'weight_responses'
        unique_together = [['user', 'question']]
        indexes = [
            models.Index(fields=['user', 'question']),
        ]
        ordering = ['question__category', 'question__key']
    
    def __str__(self):
        return f"{self.user.email} - {self.question.key}: {self.importance}/5"
    
    @classmethod
    def get_user_weights(cls, user) -> dict:
        """
        Business Logic: Hole alle Gewichtungen eines Users.
        Returns: {question_key: importance_value}
        """
        weights = cls.objects.filter(user=user).select_related('question')
        return {wr.question.key: wr.importance for wr in weights}
    
    @classmethod
    def has_completed_importance_questionnaire(cls, user) -> bool:
        """
        Business Logic: Prüfe ob User Importance Questionnaire ausgefüllt hat.
        """
        active_questions_count = Question.objects.filter(is_active=True).count()
        user_weights_count = cls.objects.filter(user=user).count()
        return user_weights_count == active_questions_count
