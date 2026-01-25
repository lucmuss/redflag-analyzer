"""
Admin Interface für Questions
"""
from django.contrib import admin
from .models import Question, WeightResponse


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


@admin.register(WeightResponse)
class WeightResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'importance', 'created_at', 'updated_at']
    list_filter = ['importance', 'created_at', 'question__category']
    search_fields = ['user__email', 'question__key', 'question__text_de']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Bewertung', {
            'fields': ('user', 'question', 'importance')
        }),
        ('Metadaten', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
