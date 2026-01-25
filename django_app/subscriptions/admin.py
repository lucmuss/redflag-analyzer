"""
Admin Interface für Subscriptions
"""
from django.contrib import admin
from .models import Subscription, CreditPurchase


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'is_active', 'free_analyses_used', 'expires_at', 'created_at']
    list_filter = ['tier', 'is_active', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Subscription', {'fields': ('tier', 'is_active')}),
        ('Premium Details', {'fields': ('started_at', 'expires_at', 'stripe_customer_id', 'stripe_subscription_id')}),
        ('Free Tier', {'fields': ('free_analyses_used', 'free_analyses_limit')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    actions = ['activate_premium', 'deactivate_premium', 'reset_free_analyses']
    
    def activate_premium(self, request, queryset):
        """Admin Action: Aktiviere Premium für ausgewählte User"""
        for subscription in queryset:
            subscription.activate_premium()
        self.message_user(request, f'{queryset.count()} Subscriptions auf Premium gesetzt.')
    activate_premium.short_description = 'Premium aktivieren (12 Monate)'
    
    def deactivate_premium(self, request, queryset):
        """Admin Action: Deaktiviere Premium"""
        for subscription in queryset:
            subscription.deactivate_premium()
        self.message_user(request, f'{queryset.count()} Subscriptions auf Free gesetzt.')
    deactivate_premium.short_description = 'Premium deaktivieren'
    
    def reset_free_analyses(self, request, queryset):
        """Admin Action: Reset Free Tier Counter"""
        queryset.update(free_analyses_used=0)
        self.message_user(request, f'{queryset.count()} Free Tier Counter zurückgesetzt.')
    reset_free_analyses.short_description = 'Free Analysen zurücksetzen'


@admin.register(CreditPurchase)
class CreditPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits_purchased', 'amount_paid', 'payment_status', 'purchased_at']
    list_filter = ['payment_status', 'purchased_at']
    search_fields = ['user__email', 'stripe_payment_intent_id']
    ordering = ['-purchased_at']
    readonly_fields = ['purchased_at']
    
    fieldsets = (
        ('Purchase Info', {'fields': ('user', 'credits_purchased', 'amount_paid')}),
        ('Payment', {'fields': ('payment_status', 'stripe_payment_intent_id')}),
        ('Timestamp', {'fields': ('purchased_at',)}),
    )
    
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        """Admin Action: Markiere Käufe als abgeschlossen und gebe Credits"""
        completed_count = 0
        for purchase in queryset.filter(payment_status='pending'):
            if purchase.complete_purchase():
                completed_count += 1
        self.message_user(request, f'{completed_count} Käufe abgeschlossen und Credits vergeben.')
    mark_as_completed.short_description = 'Als abgeschlossen markieren & Credits vergeben'
