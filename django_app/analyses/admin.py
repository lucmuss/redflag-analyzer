"""
Admin Interface für Analyses
"""
from django.contrib import admin
from .models import Analysis, CategoryScore


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
    readonly_fields = ['user', 'responses', 'snapshot_weights', 'score_total', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User & Status', {
            'fields': ('user', 'is_unlocked', 'score_total')
        }),
        ('Data', {
            'fields': ('responses', 'snapshot_weights'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Analysen sollen nur über Frontend erstellt werden
        return False
