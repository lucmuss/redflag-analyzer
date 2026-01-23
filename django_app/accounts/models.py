"""
User Models für PostgreSQL
Fat Models: Geschäftslogik in den Models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Erweitertes User-Model mit Credits und Profil.
    PostgreSQL-optimiert mit Index auf email.
    """
    email = models.EmailField(unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    credits = models.IntegerField(
        default=1, 
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Username nicht required für Email-basierte Auth
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def has_credits(self) -> bool:
        """Business Logic: Prüfe ob User Credits hat."""
        return self.credits > 0
    
    def consume_credit(self) -> bool:
        """
        Business Logic: Verbrauche 1 Credit atomisch.
        Returns True wenn erfolgreich, False wenn keine Credits.
        """
        if self.credits > 0:
            self.credits -= 1
            self.save(update_fields=['credits'])
            return True
        return False
    
    def add_credits(self, amount: int) -> None:
        """Business Logic: Füge Credits hinzu."""
        self.credits += amount
        self.save(update_fields=['credits'])


class UserProfile(models.Model):
    """
    OneToOne Relation zum User für zusätzliche Profil-Daten.
    Separiert für bessere Normalisierung.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    age = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(120)]
    )
    country = models.CharField(
        max_length=2, 
        null=True, 
        blank=True,
        help_text="ISO country code (DE, US, etc.)"
    )
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(
        max_length=10, 
        choices=GENDER_CHOICES,
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"
