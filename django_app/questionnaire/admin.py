"""
Admin Interface für Questions
"""
from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['key', 'category', 'default_weight', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'default_weight']
    search_fields = ['key', 'text_de', 'text_en']
    list_editable = ['default_weight', 'is_active']
    ordering = ['category', 'key']
    
    fieldsets = (
        ('Identifikation', {
            'fields': ('key', 'category', 'default_weight', 'is_active')
        }),
        ('Texte', {
            'fields': ('text_de', 'text_en')
        }),
    )
