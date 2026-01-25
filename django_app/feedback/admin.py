"""
Admin Interface für Feedback
"""
from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'feedback_type', 'subject', 'status', 'created_at']
    list_filter = ['feedback_type', 'status', 'created_at']
    search_fields = ['subject', 'message', 'user__email']
    list_editable = ['status']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'subject', 'message', 'status')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'responded_by', 'responded_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """Auto-fill responded_by when admin_response is added."""
        if obj.admin_response and not obj.responded_by:
            obj.responded_by = request.user
            from django.utils import timezone
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)
