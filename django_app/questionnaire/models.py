"""
Question Models für PostgreSQL
Relationaler Ansatz mit Foreign Keys
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    default_weight = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Default importance weight (1-5)"
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
