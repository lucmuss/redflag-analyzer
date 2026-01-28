from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, UserBadge
from .streak_models import UserStreak, EmailNotification

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ('badge_key', 'title', 'earned_at')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserBadgeInline)
    list_display = ('email', 'username', 'is_staff', 'credits', 'is_banned')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__is_banned')
    
    def is_banned(self, obj):
        return obj.profile.is_banned if hasattr(obj, 'profile') else False
    is_banned.boolean = True


admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'relationship_status', 'is_banned', 'created_at')
    list_filter = ('is_banned', 'referral_source', 'relationship_status')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_key', 'title', 'earned_at')
    list_filter = ('badge_key', 'earned_at')
    search_fields = ('user__email',)


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'last_active', 'streak_frozen')
    list_filter = ('streak_frozen', 'last_active')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-current_streak']


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'subject', 'sent_at', 'opened', 'clicked')
    list_filter = ('notification_type', 'opened', 'clicked', 'sent_at')
    search_fields = ('user__email', 'subject')
    readonly_fields = ('sent_at',)
    date_hierarchy = 'sent_at'
