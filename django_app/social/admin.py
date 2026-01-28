from django.contrib import admin
from .models import SharedAnalysis


@admin.register(SharedAnalysis)
class SharedAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shared_platform', 'views_count', 'clicks_count', 'conversions_count', 'viral_coefficient', 'created_at')
    list_filter = ('shared_platform', 'created_at')
    search_fields = ('user__email', 'id')
    readonly_fields = ('id', 'share_url', 'views_count', 'clicks_count', 'conversions_count', 'viral_coefficient', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def viral_coefficient(self, obj):
        return obj.viral_coefficient
    viral_coefficient.short_description = 'Viral K-Factor'
