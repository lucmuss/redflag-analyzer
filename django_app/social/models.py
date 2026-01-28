from django.db import models
from django.conf import settings
from django.urls import reverse
import uuid


class SharedAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey('analyses.Analysis', on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_analyses')
    share_url = models.URLField(blank=True)
    share_image = models.ImageField(upload_to='shares/', blank=True, null=True)
    views_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    conversions_count = models.IntegerField(default=0)
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('telegram', 'Telegram'),
        ('link', 'Direct Link'),
        ('other', 'Other'),
    ]
    shared_platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='link')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shared_analyses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-views_count']),
        ]
    
    def __str__(self):
        return f"Share {self.id}"
    
    def get_absolute_url(self):
        return reverse('social:share_detail', kwargs={'uuid': self.id})
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_clicks(self):
        self.clicks_count += 1
        self.save(update_fields=['clicks_count'])
    
    def increment_conversions(self):
        self.conversions_count += 1
        self.save(update_fields=['conversions_count'])
    
    @property
    def viral_coefficient(self):
        if self.views_count == 0:
            return 0
        return round(self.conversions_count / self.views_count, 3)
