"""
Referral Admin Interface
Bulk-Einladungen und Code-Management
"""
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.html import format_html
from .models import ReferralCode, ReferralReward, ShareEvent


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'created_by', 'current_uses', 'max_uses', 
        'usage_percentage_display', 'is_active', 'is_admin_code', 
        'expires_at', 'created_at'
    ]
    list_filter = ['is_active', 'is_admin_code', 'created_at']
    search_fields = ['code', 'created_by__email', 'sent_to_emails']
    readonly_fields = ['current_uses', 'created_at', 'updated_at', 'usage_percentage_display']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'created_by', 'is_admin_code')
        }),
        ('Usage Configuration', {
            'fields': ('max_uses', 'current_uses', 'credits_per_referral', 'is_active', 'expires_at')
        }),
        ('Email Distribution', {
            'fields': ('sent_to_emails',),
            'description': 'Komma-separierte Email-Adressen für Bulk-Einladungen'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['send_invitation_emails', 'deactivate_codes', 'activate_codes']
    
    def usage_percentage_display(self, obj):
        """Zeige Usage als Prozentsatz mit Color-Coding."""
        percentage = obj.usage_percentage
        if percentage >= 90:
            color = 'red'
        elif percentage >= 70:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    usage_percentage_display.short_description = 'Usage %'
    
    def send_invitation_emails(self, request, queryset):
        """
        Admin Action: Verschicke Einladungs-Emails an die hinterlegten Adressen.
        """
        total_sent = 0
        
        for code in queryset:
            if not code.sent_to_emails:
                continue
            
            email_list = code.email_list
            
            for email in email_list:
                try:
                    # Email-Template für Einladungen
                    subject = '🎁 Du wurdest zu RedFlag Analyzer eingeladen!'
                    message = f"""
Hallo!

Du wurdest eingeladen, RedFlag Analyzer auszuprobieren - die intelligente App zur Analyse von Beziehungs-Red-Flags.

Dein persönlicher Einladungscode: {code.code}

Mit diesem Code erhältst du:
✅ 1 Bonus-Credit beim Signup
✅ Vollständigen Zugang zur App

Registriere dich jetzt: {settings.ALLOWED_HOSTS[0]}/accounts/signup/?ref={code.code}

Die Person, die dich eingeladen hat, erhält {code.credits_per_referral} Credits, sobald du dich registrierst.

Viel Spaß beim Entdecken!
Das RedFlag Analyzer Team
                    """
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    total_sent += 1
                    
                except Exception as e:
                    self.message_user(
                        request, 
                        f"Fehler beim Senden an {email}: {str(e)}", 
                        level=messages.ERROR
                    )
        
        self.message_user(
            request, 
            f"✅ {total_sent} Einladungs-Emails erfolgreich verschickt!", 
            level=messages.SUCCESS
        )
    
    send_invitation_emails.short_description = "📧 Einladungs-Emails verschicken"
    
    def deactivate_codes(self, request, queryset):
        """Deaktiviere ausgewählte Codes."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f"{updated} Code(s) deaktiviert", 
            level=messages.SUCCESS
        )
    deactivate_codes.short_description = "❌ Codes deaktivieren"
    
    def activate_codes(self, request, queryset):
        """Aktiviere ausgewählte Codes."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f"{updated} Code(s) aktiviert", 
            level=messages.SUCCESS
        )
    activate_codes.short_description = "✅ Codes aktivieren"
    
    def save_model(self, request, obj, form, change):
        """Auto-generiere Code falls leer."""
        if not obj.code:
            obj.code = ReferralCode.generate_code()
        super().save_model(request, obj, form, change)


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'referral_code', 'reward_type', 'earned_by', 
        'used_by', 'credits_earned', 'created_at'
    ]
    list_filter = ['reward_type', 'created_at']
    search_fields = ['earned_by__email', 'used_by__email', 'referral_code__code']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Reward Information', {
            'fields': ('referral_code', 'reward_type', 'credits_earned')
        }),
        ('Participants', {
            'fields': ('earned_by', 'used_by')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def has_add_permission(self, request):
        """Rewards werden nur programmatisch erstellt."""
        return False


@admin.register(ShareEvent)
class ShareEventAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'analysis', 'platform', 'share_type', 'created_at'
    ]
    list_filter = ['platform', 'share_type', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Share Events werden nur programmatisch erstellt."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Share Events sind read-only."""
        return False
