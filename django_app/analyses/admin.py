"""
Admin Interface für Analyses
"""
from django.contrib import admin
from django.utils import timezone
from .models import Analysis, CategoryScore
from .anonymous_models import AnonymousAnalysis


class CategoryScoreInline(admin.TabularInline):
    model = CategoryScore
    extra = 0
    can_delete = False
    readonly_fields = ['category', 'score']


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    inlines = [CategoryScoreInline]
    list_display = ['id', 'user', 'score_total', 'is_unlocked', 'created_at']
    list_filter = ['is_unlocked', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['user', 'responses', 'score_total', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User & Status', {
            'fields': ('user', 'is_unlocked', 'score_total')
        }),
        ('Data', {
            'fields': ('responses',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Analysen sollen nur über Frontend erstellt werden
        return False


@admin.register(AnonymousAnalysis)
class AnonymousAnalysisAdmin(admin.ModelAdmin):
    list_display = ('email', 'partner_name', 'score_total', 'source', 'converted_to_user', 'created_at', 'expires_at')
    list_filter = ('converted_to_user', 'source', 'created_at')
    search_fields = ('email', 'session_key', 'partner_name')
    readonly_fields = ('created_at', 'expires_at', 'converted_at', 'session_key')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['mark_as_converted', 'delete_expired']
    
    def mark_as_converted(self, request, queryset):
        for obj in queryset:
            obj.mark_converted()
        self.message_user(request, f"{queryset.count()} Analysen als konvertiert markiert.")
    mark_as_converted.short_description = "Als konvertiert markieren"
    
    def delete_expired(self, request, queryset):
        count = queryset.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(request, f"{count} abgelaufene Analysen gelöscht.")
    delete_expired.short_description = "Abgelaufene löschen"
