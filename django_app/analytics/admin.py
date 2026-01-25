"""
Analytics Admin Interface
KPI Dashboard und Settings-Management
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Avg
from django.urls import path
from django.shortcuts import render
from .models import AnalyticsSettings, DailyMetrics, UserSession


@admin.register(AnalyticsSettings)
class AnalyticsSettingsAdmin(admin.ModelAdmin):
    """
    Singleton Admin für Analytics-Konfiguration.
    Zeigt immer nur das eine Settings-Objekt.
    """
    list_display = ['ga_status', 'hotjar_status', 'updated_at']
    
    fieldsets = (
        ('Google Analytics', {
            'fields': ('google_analytics_id', 'ga_enabled'),
            'description': 'Gib deine Google Analytics Measurement ID ein (z.B. G-XXXXXXXXXX)'
        }),
        ('Hotjar', {
            'fields': ('hotjar_id', 'hotjar_enabled'),
            'description': 'Gib deine Hotjar Site ID ein (nur Zahlen)'
        }),
        ('Info', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['updated_at', 'updated_by']
    
    def ga_status(self, obj):
        if obj.ga_enabled and obj.google_analytics_id:
            return format_html('<span style="color: green;">✓ Aktiv ({})</span>', obj.google_analytics_id)
        return format_html('<span style="color: gray;">○ Inaktiv</span>')
    ga_status.short_description = 'Google Analytics'
    
    def hotjar_status(self, obj):
        if obj.hotjar_enabled and obj.hotjar_id:
            return format_html('<span style="color: green;">✓ Aktiv ({})</span>', obj.hotjar_id)
        return format_html('<span style="color: gray;">○ Inaktiv</span>')
    hotjar_status.short_description = 'Hotjar'
    
    def has_add_permission(self, request):
        """Nur ein Settings-Objekt erlaubt."""
        return not AnalyticsSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Settings können nicht gelöscht werden."""
        return False
    
    def save_model(self, request, obj, form, change):
        """Speichere updated_by."""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    """
    KPI Dashboard mit Visualisierungen.
    """
    list_display = [
        'date', 'dau', 'mau', 'new_signups', 'total_analyses_created',
        'new_premium_users', 'revenue_eur_display'
    ]
    list_filter = ['date']
    readonly_fields = [
        'date', 'new_signups', 'dau', 'mau', 'signup_conversion_rate',
        'total_analyses_created', 'avg_analyses_per_user', 'avg_session_duration_seconds',
        'retention_day1', 'retention_day7', 'retention_day30',
        'new_premium_users', 'total_premium_users', 'free_to_premium_conversion_rate',
        'revenue_eur', 'arpu', 'referral_codes_used', 'referral_conversion_rate',
        'created_at'
    ]
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('📅 Date', {
            'fields': ('date',)
        }),
        ('👥 User Acquisition', {
            'fields': ('new_signups', 'dau', 'mau', 'signup_conversion_rate')
        }),
        ('📊 Engagement', {
            'fields': ('total_analyses_created', 'avg_analyses_per_user', 'avg_session_duration_seconds')
        }),
        ('🔄 Retention', {
            'fields': ('retention_day1', 'retention_day7', 'retention_day30')
        }),
        ('💰 Monetization', {
            'fields': ('new_premium_users', 'total_premium_users', 'free_to_premium_conversion_rate', 'revenue_eur', 'arpu')
        }),
        ('🎁 Referrals', {
            'fields': ('referral_codes_used', 'referral_conversion_rate')
        }),
        ('ℹ️ Meta', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def revenue_eur_display(self, obj):
        return format_html('<strong>€{}</strong>', obj.revenue_eur)
    revenue_eur_display.short_description = 'Revenue'
    
    def has_add_permission(self, request):
        """Metrics werden per Management Command erstellt."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Metrics nicht löschbar."""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Erweitere Changelist mit Aggregaten."""
        response = super().changelist_view(request, extra_context)
        
        try:
            qs = self.get_queryset(request)
            
            # Berechne Aggregat-Metriken
            total_revenue = qs.aggregate(Sum('revenue_eur'))['revenue_eur__sum'] or 0
            avg_dau = qs.aggregate(Avg('dau'))['dau__avg'] or 0
            avg_conversion = qs.aggregate(Avg('free_to_premium_conversion_rate'))['free_to_premium_conversion_rate__avg'] or 0
            
            extra_context = extra_context or {}
            extra_context['total_revenue'] = total_revenue
            extra_context['avg_dau'] = round(avg_dau, 1)
            extra_context['avg_conversion'] = round(avg_conversion, 2)
            
            if hasattr(response, 'context_data'):
                response.context_data.update(extra_context)
        except:
            pass
        
        return response


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Session-Tracking Admin (Read-Only).
    """
    list_display = ['session_id', 'user', 'started_at', 'duration_display', 'pages_visited', 'analyses_created']
    list_filter = ['started_at']
    search_fields = ['user__email', 'session_id']
    readonly_fields = ['user', 'session_id', 'started_at', 'ended_at', 'duration_seconds', 'pages_visited', 'analyses_created']
    date_hierarchy = 'started_at'
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = 'Duration'
    
    def has_add_permission(self, request):
        """Sessions werden automatisch erstellt."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Read-Only."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Sessions nicht löschbar."""
        return False
