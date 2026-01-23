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
        
        if analysis.is_unlocked:
            # Hole Category Scores (optimiert mit prefetch)
            context['category_scores'] = analysis.category_scores.all()
            # Hole Top Red Flags (Business Logic im Model)
            context['top_red_flags'] = analysis.get_top_red_flags(limit=5)
        
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
