from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class UserStreak(models.Model):
    """Weekly Streak System for User Engagement"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    
    current_streak = models.IntegerField(default=0, help_text="Current weekly streak")
    longest_streak = models.IntegerField(default=0, help_text="All-time longest streak")
    last_active = models.DateField(null=True, blank=True, help_text="Last activity date")
    streak_frozen = models.BooleanField(default=False, help_text="Streak freeze active?")
    freeze_used_at = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_streaks'
        indexes = [
            models.Index(fields=['user', '-current_streak']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.current_streak} weeks"
    
    def check_and_update_streak(self):
        """Check if streak should continue or break"""
        today = timezone.now().date()
        
        if not self.last_active:
            self.current_streak = 1
            self.last_active = today
            self.save()
            return
        
        days_inactive = (today - self.last_active).days
        
        if days_inactive == 0:
            return
        elif days_inactive <= 7:
            weeks_passed = days_inactive // 7
            if weeks_passed > 0:
                self.current_streak += weeks_passed
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
                self.last_active = today
                self.save()
        elif days_inactive > 14:
            if not self.streak_frozen:
                self.current_streak = 0
            else:
                self.streak_frozen = False
            self.last_active = today
            self.save()
    
    def use_freeze(self):
        """Use one-time streak freeze"""
        if not self.freeze_used_at or (timezone.now().date() - self.freeze_used_at).days > 30:
            self.streak_frozen = True
            self.freeze_used_at = timezone.now().date()
            self.save()
            return True
        return False
    
    def award_streak_reward(self):
        """Award credit bonus for 4-week streak"""
        if self.current_streak >= 4 and self.current_streak % 4 == 0:
            self.user.add_credits(1)
            from accounts.badges import award_badge
            if self.current_streak == 4:
                award_badge(self.user, 'streak_4weeks')
            return True
        return False


class EmailNotification(models.Model):
    """Track email notifications sent to users"""
    NOTIFICATION_TYPES = [
        ('daily_tip', 'Daily Tip'),
        ('friend_activity', 'Friend Activity'),
        ('re_engagement', 'Re-Engagement'),
        ('streak_reminder', 'Streak Reminder'),
        ('credit_reminder', 'Credit Reminder'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_notifications'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['notification_type', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} to {self.user.email}"
