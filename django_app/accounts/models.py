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
        # Testbenutzer hat unendliche Credits
        if self.email == 'skymuss@gmail.com':
            return True
        return self.credits > 0
    
    def consume_credit(self) -> bool:
        """
        Business Logic: Verbrauche 1 Credit atomisch.
        Returns True wenn erfolgreich, False wenn keine Credits.
        """
        # Testbenutzer verbraucht keine Credits
        if self.email == 'skymuss@gmail.com':
            return True
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
    birthdate = models.DateField(
        null=True,
        blank=True,
        help_text="Geburtsdatum für Altersberechnung"
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
    
    # Beziehungsinformationen
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'Single'),
        ('in_relationship', 'In einer Beziehung'),
        ('married', 'Verheiratet'),
        ('divorced', 'Geschieden'),
        ('complicated', 'Es ist kompliziert'),
    ]
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        null=True,
        blank=True
    )
    
    PREVIOUS_RELATIONSHIPS_CHOICES = [
        ('0', 'Keine'),
        ('1-3', '1-3'),
        ('4-7', '4-7'),
        ('8+', '8+'),
    ]
    previous_relationships_count = models.CharField(
        max_length=10,
        choices=PREVIOUS_RELATIONSHIPS_CHOICES,
        null=True,
        blank=True,
        help_text="Anzahl bisheriger Beziehungen"
    )
    
    current_relationship_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Dauer in Monaten"
    )
    
    # Marketing & Demographics
    REFERRAL_SOURCE_CHOICES = [
        ('google', 'Google Suche'),
        ('social_media', 'Social Media'),
        ('friend', 'Freund/Bekannter'),
        ('advertisement', 'Werbung'),
        ('other', 'Sonstiges'),
    ]
    referral_source = models.CharField(
        max_length=20,
        choices=REFERRAL_SOURCE_CHOICES,
        null=True,
        blank=True,
        help_text="Wie hast du von uns erfahren?"
    )
    
    EDUCATION_CHOICES = [
        ('hauptschule', 'Hauptschule'),
        ('realschule', 'Realschule'),
        ('abitur', 'Abitur'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD/Doktor'),
    ]
    education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        null=True,
        blank=True
    )
    
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Wohnort (Stadt)"
    )
    
    # Ban-System für Missbrauch
    is_banned = models.BooleanField(default=False)
    banned_reason = models.TextField(null=True, blank=True)
    banned_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"
    
    @property
    def age(self) -> int:
        """Business Logic: Berechne Alter aus Geburtsdatum."""
        if not self.birthdate:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.birthdate.year - (
            (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
        )


class BannedIP(models.Model):
    """
    IP-Adressen sperren für Missbrauch-Prävention.
    """
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.TextField()
    banned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='banned_ips'
    )
    banned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'banned_ips'
        ordering = ['-banned_at']
    
    def __str__(self):
        return f"Banned IP: {self.ip_address}"


class BannedEmail(models.Model):
    """
    E-Mail-Adressen dauerhaft sperren.
    """
    email = models.EmailField(unique=True, db_index=True)
    reason = models.TextField()
    banned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='banned_emails'
    )
    banned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'banned_emails'
        ordering = ['-banned_at']
    
    def __str__(self):
        return f"Banned Email: {self.email}"


class UserBadge(models.Model):
    """
    Gamification: User Badges & Achievements
    Motiviert User zur Nutzung der App.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge_key = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Eindeutiger Badge-Identifier"
    )
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')
    points = models.IntegerField(default=0)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_badges'
        ordering = ['-earned_at']
        unique_together = [['user', 'badge_key']]
        indexes = [
            models.Index(fields=['user', 'badge_key']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
