from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .streak_models import UserStreak
from .badges import award_badge


@login_required
def streak_dashboard(request):
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    streak.check_and_update_streak()
    
    return render(request, 'accounts/streak_dashboard.html', {
        'streak': streak,
        'can_freeze': not streak.freeze_used_at or (timezone.now().date() - streak.freeze_used_at).days > 30
    })


@login_required
def use_streak_freeze(request):
    if request.method == 'POST':
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        success = streak.use_freeze()
        
        return JsonResponse({
            'success': success,
            'message': 'Streak Freeze aktiviert!' if success else 'Freeze bereits verwendet (1x pro Monat)'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def streak_leaderboard(request):
    top_streaks = UserStreak.objects.select_related('user').order_by('-current_streak')[:50]
    
    user_rank = None
    if request.user.is_authenticated:
        user_streak = UserStreak.objects.filter(user=request.user).first()
        if user_streak:
            user_rank = UserStreak.objects.filter(current_streak__gt=user_streak.current_streak).count() + 1
    
    return render(request, 'accounts/streak_leaderboard.html', {
        'top_streaks': top_streaks,
        'user_rank': user_rank
    })
