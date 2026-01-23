"""
Questionnaire Views mit HTMX-Integration
Thin Views: Logik liegt in Models/Services
"""
from django.views.generic import TemplateView, ListView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from .models import Question
from analyses.models import Analysis, CategoryScore
from analyses.services import ScoreCalculator


class HomeView(TemplateView):
    """
    Landing Page / Home
    Zeigt Startseite mit Info und CTA
    """
    template_name = 'questionnaire/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_questions'] = Question.objects.filter(is_active=True).count()
        return context


class QuestionnaireView(LoginRequiredMixin, ListView):
    """
    Fragebogen-View mit HTMX-Support.
    
    ARCHITEKTUR-VORTEIL:
    - Statt React State Management -> Server rendert HTML-Fragmente
    - Keine komplexe Client-Side Logik nötig
    - SEO-freundlich, kein JS-Bundle
    """
    model = Question
    template_name = 'questionnaire/questionnaire.html'
    context_object_name = 'questions'
    
    def get_queryset(self):
        return Question.objects.filter(is_active=True).select_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Gruppiere Fragen nach Kategorie für bessere UX
        context['questions_by_category'] = Question.get_active_by_category()
        context['user_credits'] = self.request.user.credits
        return context


class QuestionnaireSubmitView(LoginRequiredMixin, View):
    """
    HTMX POST Handler für Fragebogen-Submission.
    
    HTMX-PATTERN:
    - Client sendet hx-post mit Form-Daten
    - Server berechnet Score (Fat Model/Service Layer)
    - Server returned HTML-Fragment (nicht JSON!)
    - HTMX swapped Fragment in DOM
    
    VORTEIL vs. FastAPI/Flutter:
    - Keine separate API-Layer
    - Kein JSON-Serialization Overhead
    - Validierung auf Server (sicher!)
    """
    
    def post(self, request):
        # Parse responses aus POST-Daten
        responses = []
        for key in request.POST:
            if key.startswith('q_'):
                question_key = key[2:]  # Remove 'q_' prefix
                value = int(request.POST[key])
                if 1 <= value <= 5:
                    responses.append({'key': question_key, 'value': value})
        
        if not responses:
            messages.error(request, 'Bitte beantworte mindestens eine Frage.')
            return redirect('questionnaire:questionnaire')
        
        # Erstelle Weight Snapshot
        snapshot_weights = ScoreCalculator.create_weight_snapshot()
        
        # Berechne Scores
        calculator = ScoreCalculator(responses, snapshot_weights)
        score_total = calculator.calculate_total_score()
        category_scores_dict = calculator.calculate_category_scores()
        
        # Erstelle Analysis (Fat Model Pattern)
        analysis = Analysis.objects.create(
            user=request.user,
            responses=responses,
            snapshot_weights=snapshot_weights,
            score_total=score_total,
            is_unlocked=False  # User muss Credits verwenden
        )
        
        # Erstelle Category Scores (Normalisiert in separater Tabelle)
        for category, score in category_scores_dict.items():
            CategoryScore.objects.create(
                analysis=analysis,
                category=category,
                score=score
            )
        
        messages.success(request, 'Analyse erfolgreich erstellt!')
        
        # HTMX: Redirect zu Results
        if request.htmx:
            response = HttpResponse(status=204)
            response['HX-Redirect'] = f'/analyses/{analysis.id}/'
            return response
        
        return redirect('analyses:detail', pk=analysis.id)
