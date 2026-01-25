"""
Analytics Models
Tracking-Integration und KPI-Metriken
"""
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings


class AnalyticsSettings(models.Model):
    """
    Singleton Model für Analytics-Konfiguration.
    Admin kann GA und Hotjar IDs hier eintragen.
    """
    # Google Analytics
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        validators=[RegexValidator(r'^(G|UA)-[A-Z0-9-]+$', 'Ungültiges GA-Format (z.B. G-XXXXXXXXXX oder UA-XXXXXXXXX-X)')],
        help_text="Google Analytics Measurement ID (z.B. G-XXXXXXXXXX oder UA-XXXXXXXXX-X)"
    )
    ga_enabled = models.BooleanField(
        default=False,
        help_text="Google Analytics aktivieren"
    )
    
    # Hotjar
    hotjar_id = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\d+$', 'Hotjar ID muss numerisch sein')],
        help_text="Hotjar Site ID (nur Zahlen)"
    )
    hotjar_enabled = models.BooleanField(
        default=False,
        help_text="Hotjar Tracking aktivieren"
    )
    
    # Metadaten
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_updates'
    )
    
    class Meta:
        db_table = 'analytics_settings'
        verbose_name = 'Analytics Settings'
        verbose_name_plural = 'Analytics Settings'
    
    def save(self, *args, **kwargs):
        """Singleton Pattern: Nur ein Settings-Objekt erlaubt."""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Verhindere Löschen des Singleton."""
        pass
    
    @classmethod
    def load(cls):
        """Lade oder erstelle Settings."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"Analytics Settings (GA: {self.ga_enabled}, Hotjar: {self.hotjar_enabled})"


class DailyMetrics(models.Model):
    """
    Tägliche KPI-Metriken für Dashboard.
    Wird täglich per Cronjob/Management Command berechnet.
    """
    date = models.DateField(unique=True, db_index=True)
    
    # User Acquisition
    new_signups = models.IntegerField(default=0)
    dau = models.IntegerField(
        default=0,
        help_text="Daily Active Users"
    )
    mau = models.IntegerField(
        default=0,
        help_text="Monthly Active Users (rolling 30 days)"
    )
    signup_conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="% der Besucher die sich registrieren"
    )
    
    # Engagement
    total_analyses_created = models.IntegerField(default=0)
    avg_analyses_per_user = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    avg_session_duration_seconds = models.IntegerField(
        default=0,
        help_text="Durchschnittliche Session-Dauer in Sekunden"
    )
    
    # Retention
    retention_day1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="% der User die nach 1 Tag wiederkommen"
    )
    retention_day7 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="% der User die nach 7 Tagen wiederkommen"
    )
    retention_day30 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="% der User die nach 30 Tagen wiederkommen"
    )
    
    # Monetization
    new_premium_users = models.IntegerField(default=0)
    total_premium_users = models.IntegerField(default=0)
    free_to_premium_conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="% der Free User die Premium werden"
    )
    revenue_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    arpu = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Average Revenue Per User"
    )
    
    # Referrals
    referral_codes_used = models.IntegerField(default=0)
    referral_conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_metrics'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"Metrics for {self.date}"
    
    @classmethod
    def get_latest(cls, days=30):
        """Hole die letzten N Tage für Dashboard."""
        return cls.objects.all()[:days]


class UserSession(models.Model):
    """
    Session-Tracking für Engagement-Metriken.
    Leichtgewichtig: nur essenzielle Daten.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Simplified tracking
    pages_visited = models.IntegerField(default=0)
    analyses_created = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['session_id']),
        ]
    
    def end_session(self):
        """Beende Session und berechne Duration."""
        from django.utils import timezone
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.save(update_fields=['ended_at', 'duration_seconds'])
