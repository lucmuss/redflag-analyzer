"""
Analysis Views mit HTMX-Integration
Zeigt Analyse-Ergebnisse und Unlock-Funktionalität
"""
from django.views.generic import ListView, DetailView
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from .models import Analysis
from .analytics import AnalyticsService
from .image_generator import ShareImageGenerator
from .statistics import StatisticsService
from subscriptions.models import Subscription
from django.http import FileResponse


class AnalysisListView(LoginRequiredMixin, ListView):
    """
    Liste aller Analysen des Users.
    Nutzt select_related für Performance-Optimierung (PostgreSQL JOIN).
    """
    model = Analysis
    template_name = 'analyses/list.html'
    context_object_name = 'analyses'
    paginate_by = 10
    
    def get_queryset(self):
        return Analysis.objects.filter(
            user=self.request.user
        ).prefetch_related('category_scores').order_by('-created_at')


class AnalysisDetailView(LoginRequiredMixin, DetailView):
    """
    Detail-View einer Analyse.
    Zeigt gesperrte/entsperrte Inhalte basierend auf is_unlocked.
    
    HTMX-PATTERN:
    - Unlock-Button hat hx-post zu unlock-URL
    - Nach Success: Server returned updated HTML-Fragment
    - HTMX swapped das gesperrte Content-Div mit entsperrtem Content
    """
    model = Analysis
    template_name = 'analyses/detail.html'
    context_object_name = 'analysis'
    
    def get_queryset(self):
        # User kann nur eigene Analysen sehen
        return Analysis.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analysis = self.object
        
        # Subscription Status holen
        subscription, _ = Subscription.objects.get_or_create(user=self.request.user)
        context['subscription'] = subscription
        context['is_premium'] = subscription.is_premium
        
        if analysis.is_unlocked:
            # Hole Category Scores (optimiert mit prefetch)
            context['category_scores'] = analysis.category_scores.all()
            # Hole Top Red Flags (Business Logic im Model)
            context['top_red_flags'] = analysis.get_top_red_flags(limit=5)
            
            # Compare with Average
            context['comparison'] = StatisticsService.compare_with_average(analysis)
            
            # PREMIUM FEATURES: Analytics & Insights
            if subscription.is_premium:
                # Generiere Premium Insights
                premium_insights = AnalyticsService.get_user_premium_insights(analysis)
                context['premium_insights'] = premium_insights
                context['show_premium_features'] = True
            else:
                context['show_premium_features'] = False
                context['show_premium_paywall'] = True
        
        context['user_credits'] = self.request.user.credits
        return context


class UnlockAnalysisView(LoginRequiredMixin, View):
    """
    HTMX-Endpoint für Analyse-Unlock.
    
    HTMX vs. FLUTTER VORTEIL:
    - Flutter: API-Call -> JSON -> State Update -> Widget Rebuild
    - HTMX: POST -> Server Logic -> HTML-Fragment -> DOM Swap
    - Weniger Code, Server-Side Validierung, keine Client-State-Bugs
    """
    
    def post(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
        
        # Business Logic im Model (Fat Model Pattern)
        success = analysis.unlock()
        
        if success:
            messages.success(request, f'Analyse erfolgreich entsperrt! Verbleibende Credits: {request.user.credits}')
            
            # HTMX: Returniere updated Analysis-Detail Fragment
            if request.htmx:
                context = {
                    'analysis': analysis,
                    'category_scores': analysis.category_scores.all(),
                    'top_red_flags': analysis.get_top_red_flags(limit=5),
                    'user_credits': request.user.credits,
                }
                return render(request, 'analyses/partials/unlocked_content.html', context)
        else:
            messages.error(request, 'Nicht genug Credits! Bitte kaufe Credits.')
            
            if request.htmx:
                return render(request, 'analyses/partials/no_credits.html', {
                    'user_credits': request.user.credits
                })
        
        # Fallback für Non-HTMX Requests
        return redirect('analyses:detail', pk=pk)


class GenerateShareImageView(LoginRequiredMixin, View):
    """
    Generiert und liefert Share-Grafik für eine Analyse.
    Format: 'story' für Instagram Story (1080x1920), 'post' für Standard (1200x630)
    """
    
    def get(self, request, pk, format='post'):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user, is_unlocked=True)
        
        # Generiere Grafik basierend auf Format
        if format == 'story':
            filepath = ShareImageGenerator.generate_instagram_story(analysis)
        else:
            filepath = ShareImageGenerator.generate_standard_post(analysis)
        
        # Liefere Datei als Download
        return FileResponse(
            open(filepath, 'rb'),
            as_attachment=True,
            filename=f'redflag_analysis_{analysis.id}_{format}.png'
        )
