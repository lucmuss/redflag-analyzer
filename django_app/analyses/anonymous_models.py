from django.db import models
from django.utils import timezone
from datetime import timedelta


class AnonymousAnalysis(models.Model):
    """
    Anonymous Analysen ohne Login
    Email required für Conversion-Tracking
    """
    email = models.EmailField(db_index=True)
    session_key = models.CharField(max_length=40, db_index=True)
    
    # Analysis Data (temporary)
    partner_name = models.CharField(max_length=100, blank=True)
    analysis_data = models.JSONField(help_text="Gespeicherte Antworten")
    score_total = models.FloatField(null=True, blank=True)
    
    # Conversion Tracking
    converted_to_user = models.BooleanField(default=False)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # Source Tracking
    SOURCE_CHOICES = [
        ('landing', 'Landing Page'),
        ('social', 'Social Media'),
        ('blog', 'Blog'),
        ('referral', 'Referral'),
        ('direct', 'Direct'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')
    
    # Privacy: Auto-Delete nach 7 Tagen
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    
    class Meta:
        db_table = 'anonymous_analyses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Set expiration: 7 Tage ab jetzt
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @classmethod
    def cleanup_expired(cls):
        """Lösche abgelaufene anonyme Analysen (Privacy)"""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count
    
    def mark_converted(self):
        """Markiere als zu User konvertiert"""
        self.converted_to_user = True
        self.converted_at = timezone.now()
        self.save(update_fields=['converted_to_user', 'converted_at'])
