"""
Admin Interface für Users und Profiles
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, BannedIP, BannedEmail, UserBadge


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['email', 'is_verified', 'credits', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_verified', 'created_at']
    search_fields = ['email']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Credits', {'fields': ('credits',)}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    readonly_fields = ['created_at']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'credits'),
        }),
    )


@admin.register(BannedIP)
class BannedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'banned_by', 'banned_at']
    list_filter = ['banned_at']
    search_fields = ['ip_address', 'reason']
    ordering = ['-banned_at']
    readonly_fields = ['banned_at']


@admin.register(BannedEmail)
class BannedEmailAdmin(admin.ModelAdmin):
    list_display = ['email', 'reason', 'banned_by', 'banned_at']
    list_filter = ['banned_at']
    search_fields = ['email', 'reason']
    ordering = ['-banned_at']
    readonly_fields = ['banned_at']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'icon', 'points', 'earned_at']
    list_filter = ['badge_key', 'earned_at']
    search_fields = ['user__email', 'title', 'badge_key']
    ordering = ['-earned_at']
    readonly_fields = ['earned_at']
    
    fieldsets = (
        ('Badge Info', {'fields': ('user', 'badge_key', 'name', 'title', 'icon')}),
        ('Details', {'fields': ('description', 'points')}),
        ('Timestamps', {'fields': ('earned_at',)}),
    )
