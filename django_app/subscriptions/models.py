"""
Subscription Models für Freemium & Premium Tiers
"""
from django.db import models
from django.utils import timezone
from accounts.models import User


class SubscriptionTier(models.TextChoices):
    """Subscription Tiers für Freemium-Modell"""
    FREE = 'free', 'Free Tier (3 Analysen)'
    PREMIUM = 'premium', 'Premium (€20 - Unbegrenzt)'


class Subscription(models.Model):
    """
    User Subscription Model.
    Tracked Premium-Status und Subscription-Details.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.FREE
    )
    
    # Premium Subscription Fields
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Payment Details
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Free Tier Analytics Counter
    free_analyses_used = models.IntegerField(default=0)
    free_analyses_limit = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        indexes = [
            models.Index(fields=['user', 'tier']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_tier_display()}"
    
    @property
    def is_premium(self) -> bool:
        """Business Logic: Prüfe ob User Premium hat."""
        if self.tier == SubscriptionTier.PREMIUM and self.is_active:
            # Prüfe ob nicht abgelaufen
            if self.expires_at and self.expires_at < timezone.now():
                return False
            return True
        return False
    
    @property
    def is_free(self) -> bool:
        """Business Logic: Prüfe ob User Free Tier hat."""
        return self.tier == SubscriptionTier.FREE or not self.is_premium
    
    def can_create_analysis(self) -> bool:
        """
        Business Logic: Prüfe ob User eine Analyse erstellen darf.
        Premium: Unbegrenzt
        Free: 3 Analysen max
        """
        if self.is_premium:
            return True
        
        # Free Tier: Max 3 Analysen
        return self.free_analyses_used < self.free_analyses_limit
    
    def consume_free_analysis(self) -> bool:
        """
        Business Logic: Verbrauche eine Free Analysis.
        Returns True wenn erfolgreich, False wenn Limit erreicht.
        """
        if self.is_premium:
            return True  # Premium hat unbegrenzt
        
        if self.free_analyses_used < self.free_analyses_limit:
            self.free_analyses_used += 1
            self.save(update_fields=['free_analyses_used'])
            return True
        
        return False
    
    def activate_premium(self, months=12):
        """
        Business Logic: Aktiviere Premium Subscription.
        Standard: 12 Monate für €20
        """
        self.tier = SubscriptionTier.PREMIUM
        self.is_active = True
        self.started_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(days=30 * months)
        self.save()
    
    def deactivate_premium(self):
        """Business Logic: Deaktiviere Premium Subscription."""
        self.tier = SubscriptionTier.FREE
        self.is_active = False
        self.expires_at = None
        self.save()
    
    @property
    def remaining_free_analyses(self) -> int:
        """Berechne verbleibende Free Analysen."""
        if self.is_premium:
            return float('inf')  # Unbegrenzt
        return max(0, self.free_analyses_limit - self.free_analyses_used)


class CreditPurchase(models.Model):
    """
    One-Time Credit Purchases.
    1 Credit = €2 für eine zusätzliche Analyse (für Free Users).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='credit_purchases'
    )
    credits_purchased = models.IntegerField(default=1)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)  # In EUR
    
    # Payment Details
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_purchases'
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['user', 'payment_status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.credits_purchased} Credits (€{self.amount_paid})"
    
    def complete_purchase(self):
        """Business Logic: Schließe Kauf ab und gebe Credits."""
        if self.payment_status == 'pending':
            self.payment_status = 'completed'
            self.user.add_credits(self.credits_purchased)
            self.save()
            return True
        return False
