"""
Referral Views
Thin Views: Delegation an Models
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ReferralCode, ReferralReward, ShareEvent


class ReferralDashboardView(LoginRequiredMixin, TemplateView):
    """
    Benutzer-Dashboard für Referral-Codes.
    User kann eigenen Code generieren und Statistiken sehen.
    """
    template_name = 'referrals/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Hole oder erstelle User Referral Code
        referral_code, created = ReferralCode.objects.get_or_create(
            created_by=user,
            is_admin_code=False,
            defaults={
                'code': ReferralCode.generate_code(),
                'max_uses': 100,  # User haben höheres Limit
                'is_active': True
            }
        )
        
        # Statistiken
        context['referral_code'] = referral_code
        context['total_referrals'] = referral_code.current_uses
        context['total_credits_earned'] = ReferralReward.objects.filter(
            earned_by=user,
            reward_type='referral_reward'
        ).count() * referral_code.credits_per_referral
        
        context['recent_rewards'] = ReferralReward.objects.filter(
            earned_by=user
        )[:10]
        
        # Share URL
        context['share_url'] = self.request.build_absolute_uri(
            f'/accounts/signup/?ref={referral_code.code}'
        )
        
        return context


@login_required
def use_referral_code(request):
    """
    POST: Code einlösen.
    User kann Referral-Code beim Signup oder später einlösen.
    """
    if request.method == 'POST':
        code_str = request.POST.get('code', '').strip().upper()
        
        if not code_str:
            messages.error(request, 'Bitte gib einen Code ein.')
            return redirect('referrals:dashboard')
        
        try:
            code = ReferralCode.objects.get(code=code_str)
            success, reward, message = code.use_code(request.user)
            
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        
        except ReferralCode.DoesNotExist:
            messages.error(request, 'Ungültiger Code.')
        
        return redirect('referrals:dashboard')
    
    return redirect('referrals:dashboard')


class ShareScreenView(LoginRequiredMixin, TemplateView):
    """
    Share-Screen: 'Mein Red-Flag-Score: 7.2/10'
    Ästhetische, teilbare Grafik für Social Media.
    """
    template_name = 'referrals/share_screen.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analysis_id = self.kwargs.get('analysis_id')
        
        from analyses.models import Analysis
        analysis = get_object_or_404(
            Analysis,
            id=analysis_id,
            user=self.request.user
        )
        
        context['analysis'] = analysis
        
        # Referral Code für Share-Link
        referral_code, _ = ReferralCode.objects.get_or_create(
            created_by=self.request.user,
            is_admin_code=False,
            defaults={
                'code': ReferralCode.generate_code(),
                'max_uses': 100,
                'is_active': True
            }
        )
        context['referral_code'] = referral_code
        context['share_url'] = self.request.build_absolute_uri(
            f'/accounts/signup/?ref={referral_code.code}'
        )
        
        return context


@login_required
def track_share(request, analysis_id):
    """
    POST: Track Share Event für Analytics.
    """
    if request.method == 'POST':
        platform = request.POST.get('platform', 'link')
        share_type = request.POST.get('share_type', 'score_card')
        
        from analyses.models import Analysis
        try:
            analysis = Analysis.objects.get(id=analysis_id, user=request.user)
            
            ShareEvent.objects.create(
                user=request.user,
                analysis=analysis,
                platform=platform,
                share_type=share_type
            )
            
            messages.success(request, '📤 Geteilt! Danke fürs Teilen.')
        except Analysis.DoesNotExist:
            messages.error(request, 'Analyse nicht gefunden.')
        
        return redirect('analyses:detail', pk=analysis_id)
    
    return redirect('questionnaire:home')
