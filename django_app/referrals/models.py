"""
Referral Program Models
Fat Models: Geschäftslogik für virales Marketing
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
import secrets
import string


class ReferralCode(models.Model):
    """
    Referral Codes für 'Empfehle einen Freund, erhalte 3 Credits'.
    Admin kann Codes an User oder Email-Listen verschicken.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Eindeutiger Einladungscode"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_referral_codes',
        null=True,
        blank=True,
        help_text="User der den Code erstellt hat (null bei Admin-Codes)"
    )
    
    # Admin-Features
    is_admin_code = models.BooleanField(
        default=False,
        help_text="Von Admin für Marketing-Kampagnen erstellt"
    )
    sent_to_emails = models.TextField(
        blank=True,
        help_text="Komma-separierte Liste der Email-Adressen"
    )
    
    # Usage Limits
    max_uses = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximale Anzahl der Verwendungen"
    )
    current_uses = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Reward Configuration
    credits_per_referral = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Credits für jeden erfolgreichen Referral"
    )
    
    # Tracking
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional: Ablaufdatum"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'referral_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} ({self.current_uses}/{self.max_uses})"
    
    @classmethod
    def generate_code(cls, length=8) -> str:
        """
        Business Logic: Generiere unique Referral Code.
        Format: UPPERCASE + DIGITS für bessere Lesbarkeit.
        """
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(length))
            if not cls.objects.filter(code=code).exists():
                return code
    
    def is_valid(self) -> bool:
        """Business Logic: Prüfe ob Code noch gültig ist."""
        if not self.is_active:
            return False
        
        if self.current_uses >= self.max_uses:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return True
    
    def can_be_used_by(self, user) -> bool:
        """Business Logic: Prüfe ob User diesen Code benutzen kann."""
        if not self.is_valid():
            return False
        
        # User kann eigene Codes nicht benutzen
        if self.created_by == user:
            return False
        
        # User kann Code nur einmal benutzen
        if ReferralReward.objects.filter(
            referral_code=self,
            used_by=user
        ).exists():
            return False
        
        return True
    
    def use_code(self, user):
        """
        Business Logic: Code verwenden und Rewards verteilen.
        Atomische Operation mit Transaction.
        Returns (success: bool, reward: ReferralReward|None, message: str)
        """
        from django.db import transaction
        
        if not self.can_be_used_by(user):
            return False, None, "Code kann nicht verwendet werden"
        
        try:
            with transaction.atomic():
                # Erstelle Reward für neuen User
                new_user_reward = ReferralReward.objects.create(
                    referral_code=self,
                    used_by=user,
                    credits_earned=1,  # Neuer User bekommt 1 Bonus-Credit
                    reward_type='signup_bonus'
                )
                user.add_credits(1)
                
                # Belohne Referrer mit 3 Credits
                if self.created_by:
                    referrer_reward = ReferralReward.objects.create(
                        referral_code=self,
                        earned_by=self.created_by,
                        credits_earned=self.credits_per_referral,
                        reward_type='referral_reward'
                    )
                    self.created_by.add_credits(self.credits_per_referral)
                
                # Update Usage
                self.current_uses += 1
                self.save(update_fields=['current_uses', 'updated_at'])
                
                return True, new_user_reward, f"Code erfolgreich verwendet! Du hast 1 Bonus-Credit erhalten."
        
        except Exception as e:
            return False, None, f"Fehler beim Verwenden des Codes: {str(e)}"
    
    @property
    def usage_percentage(self) -> float:
        """Berechne Usage-Prozentsatz für Analytics."""
        if self.max_uses == 0:
            return 0
        return (self.current_uses / self.max_uses) * 100
    
    @property
    def email_list(self) -> list:
        """Parse Email-Liste."""
        if not self.sent_to_emails:
            return []
        return [email.strip() for email in self.sent_to_emails.split(',') if email.strip()]


class ReferralReward(models.Model):
    """
    Tracking von vergebenen Referral Rewards.
    Zwei Typen: signup_bonus (für neue User) und referral_reward (für Referrer).
    """
    REWARD_TYPES = [
        ('signup_bonus', 'Signup Bonus'),
        ('referral_reward', 'Referral Reward'),
    ]
    
    referral_code = models.ForeignKey(
        ReferralCode,
        on_delete=models.CASCADE,
        related_name='rewards'
    )
    
    # Wer hat den Reward bekommen
    earned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earned_referral_rewards',
        null=True,
        blank=True,
        help_text="User der Credits erhalten hat (Referrer)"
    )
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='used_referral_codes',
        null=True,
        blank=True,
        help_text="User der den Code verwendet hat (neuer User)"
    )
    
    reward_type = models.CharField(
        max_length=20,
        choices=REWARD_TYPES,
        default='referral_reward'
    )
    
    credits_earned = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'referral_rewards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['earned_by']),
            models.Index(fields=['used_by']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.earned_by:
            return f"{self.earned_by.email} earned {self.credits_earned} credits"
        return f"Signup bonus for {self.used_by.email}"


class ShareEvent(models.Model):
    """
    Tracking von Social Media Shares.
    Für Analytics: Welche Share-Screens sind am erfolgreichsten.
    """
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('link', 'Link kopiert'),
        ('other', 'Sonstiges'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='share_events'
    )
    
    analysis = models.ForeignKey(
        'analyses.Analysis',
        on_delete=models.CASCADE,
        related_name='share_events',
        null=True,
        blank=True,
        help_text="Welche Analyse wurde geteilt"
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='link'
    )
    
    share_type = models.CharField(
        max_length=50,
        default='score_card',
        help_text="Type des Shares (score_card, badge, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'share_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['platform']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} shared on {self.platform}"
