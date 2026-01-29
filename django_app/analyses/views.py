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
from .pdf_export import export_analysis_pdf
from .trend_analysis import TrendAnalysisService
import logging

logger = logging.getLogger(__name__)


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
            context['top_red_flags'] = analysis.get_top_red_flags(limit=10)
            
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
                    'top_red_flags': analysis.get_top_red_flags(limit=10),
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


class DeleteAnalysisView(LoginRequiredMixin, View):
    """
    Lösche eine Analyse.
    User kann nur eigene Analysen löschen.
    """
    
    def post(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
        
        # Speichere Info für Nachricht
        partner_name = analysis.partner_name or f"Analyse #{analysis.id}"
        
        # Lösche Analyse (CASCADE löscht auch CategoryScores)
        analysis.delete()
        
        messages.success(request, f'"{partner_name}" wurde erfolgreich gelöscht.')
        return redirect('analyses:list')


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


class ExportAnalysisPDFView(LoginRequiredMixin, View):
    """
    Exportiert eine Analyse als PDF-Report.
    Nur für entsperrte Analysen verfügbar.
    """
    
    def get(self, request, pk):
        # Hole Analysis und prüfe Berechtigung
        analysis = get_object_or_404(
            Analysis, 
            pk=pk, 
            user=request.user, 
            is_unlocked=True
        )
        
        try:
            logger.info(f"PDF export requested for analysis {pk} by user {request.user.id}")
            
            # Generiere PDF
            response = export_analysis_pdf(analysis)
            
            logger.info(f"PDF export successful for analysis {pk}")
            return response
            
        except Exception as e:
            logger.error(f"PDF export failed for analysis {pk}: {str(e)}")
            messages.error(request, 'PDF-Export ist fehlgeschlagen. Bitte versuche es später erneut.')
            return redirect('analyses:detail', pk=pk)


class LoadMoreRedFlagsView(LoginRequiredMixin, View):
    """
    HTMX-Endpoint zum Nachladen weiterer Red Flags.
    Pagination für Top Red Flags.
    """
    
    def get(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, user=request.user, is_unlocked=True)
        
        # Hole Offset aus Query-Parameter (default: 10)
        offset = int(request.GET.get('offset', 10))
        limit = 10
        
        # Hole Red Flags mit Offset + Limit
        all_flags = analysis.get_top_red_flags(limit=offset + limit)
        flags = all_flags[offset:offset + limit]
        
        # Prüfe ob weitere Flags vorhanden
        has_more = len(all_flags) > offset + limit
        next_offset = offset + limit
        
        context = {
            'flags': flags,
            'offset': offset,
            'has_more': has_more,
            'next_offset': next_offset,
            'analysis_id': analysis.id,
        }
        
        return render(request, 'analyses/partials/red_flags_items.html', context)


class TrendsView(LoginRequiredMixin, DetailView):
    """
    Zeigt Trend-Analyse für User Scores über Zeit.
    """
    model = Analysis
    template_name = 'analyses/trends.html'
    context_object_name = 'analysis'
    
    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hole Trend-Daten
        trend_data = TrendAnalysisService.get_user_score_trend(self.request.user, days=90)
        trend_stats = TrendAnalysisService.get_trend_statistics(self.request.user)
        comparison = TrendAnalysisService.compare_with_previous_analysis(self.object)
        
        context['trend_data'] = trend_data
        context['trend_stats'] = trend_stats
        context['comparison'] = comparison
        
        # Category Trends
        context['category_trends'] = {
            'TRUST': TrendAnalysisService.get_category_trends(self.request.user, 'TRUST'),
            'BEHAVIOR': TrendAnalysisService.get_category_trends(self.request.user, 'BEHAVIOR'),
            'VALUES': TrendAnalysisService.get_category_trends(self.request.user, 'VALUES'),
            'DYNAMICS': TrendAnalysisService.get_category_trends(self.request.user, 'DYNAMICS'),
        }
        
        return context
