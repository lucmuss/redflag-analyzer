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
from .models import Question, WeightResponse
from analyses.models import Analysis, CategoryScore
from analyses.services import ScoreCalculator
from accounts.models import User


class HomeView(TemplateView):
    """
    Landing Page / Home
    Zeigt Startseite mit Info und CTA
    """
    template_name = 'questionnaire/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_questions'] = Question.objects.filter(is_active=True).count()
        
        # Social Proof Counter
        from django.utils import timezone
        from datetime import timedelta
        
        context['total_analyses'] = Analysis.objects.count()
        context['total_users'] = User.objects.count()
        
        # Analysen heute
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        context['analyses_today'] = Analysis.objects.filter(created_at__gte=today_start).count()
        
        return context


class OnboardingView(TemplateView):
    """
    Onboarding/Motivation Screen.
    Zeigt neue Usern warum sie RedFlag Analyzer nutzen sollten.
    """
    template_name = 'questionnaire/onboarding.html'


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


class PartnerInfoView(LoginRequiredMixin, TemplateView):
    """
    Screen zum Eingeben von Partner-Informationen vor dem Fragebogen.
    """
    template_name = 'questionnaire/partner_info.html'
    
    def post(self, request):
        partner_name = request.POST.get('partner_name', '')
        partner_age = request.POST.get('partner_age', '')
        
        # Speichere in Session für später
        request.session['partner_name'] = partner_name
        request.session['partner_age'] = int(partner_age) if partner_age else None
        
        return redirect('questionnaire:questionnaire')


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
        
        # Hole Partner-Informationen aus POST-Request
        partner_name = request.POST.get('partner_name', '').strip() or None
        partner_age_str = request.POST.get('partner_age', '').strip()
        partner_age = int(partner_age_str) if partner_age_str else None
        partner_country = request.POST.get('partner_country', '').strip() or None
        
        # Berechne Scores DYNAMISCH mit aktuellen Question.calculated_weight
        calculator = ScoreCalculator(responses)
        score_total = calculator.calculate_total_score()
        category_scores_dict = calculator.calculate_category_scores()
        
        # Erstelle Analysis (Fat Model Pattern)
        # KEIN snapshot_weights mehr - verwendet immer aktuelle calculated_weights
        analysis = Analysis.objects.create(
            user=request.user,
            partner_name=partner_name,
            partner_age=partner_age,
            partner_country=partner_country,
            responses=responses,
            score_total=score_total,
            is_unlocked=False  # User muss Credits verwenden
        )
        
        # Session cleanup
        if 'partner_name' in request.session:
            del request.session['partner_name']
        if 'partner_age' in request.session:
            del request.session['partner_age']
        
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


class ImportanceQuestionnaireView(LoginRequiredMixin, ListView):
    """
    Importance Questionnaire View.
    User bewertet die Wichtigkeit jeder Frage auf einer Skala von 1-5.
    Diese Bewertungen werden als dynamische Gewichte für Score-Berechnungen verwendet.
    """
    model = Question
    template_name = 'questionnaire/importance_questionnaire.html'
    context_object_name = 'questions'
    
    def get_queryset(self):
        return Question.objects.filter(is_active=True).select_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions_by_category'] = Question.get_active_by_category()
        
        # Hole bestehende Gewichtungen des Users (falls vorhanden)
        existing_weights = WeightResponse.get_user_weights(self.request.user)
        context['existing_weights'] = existing_weights
        context['has_completed'] = WeightResponse.has_completed_importance_questionnaire(self.request.user)
        
        # Erklärung für Nutzer
        context['importance_explanation'] = """
        Personalisiere deine Analyse! Bewerte, wie wichtig dir jede Frage ist.
        Fragen, die du als wichtiger bewertest, haben mehr Einfluss auf deinen Score.
        So erhältst du eine Analyse, die perfekt auf deine Prioritäten abgestimmt ist.
        """
        
        return context


class ImportanceQuestionnaireSubmitView(LoginRequiredMixin, View):
    """
    HTMX POST Handler für Importance Questionnaire Submission.
    Speichert oder aktualisiert die Wichtigkeitsbewertungen des Users.
    """
    
    def post(self, request):
        # Parse importance ratings aus POST-Daten
        importance_ratings = []
        for key in request.POST:
            if key.startswith('importance_'):
                question_key = key[11:]  # Remove 'importance_' prefix
                importance = int(request.POST[key])
                if 1 <= importance <= 5:
                    importance_ratings.append({'key': question_key, 'importance': importance})
        
        if not importance_ratings:
            messages.error(request, 'Bitte bewerte mindestens eine Frage.')
            return redirect('questionnaire:importance')
        
        # Hole alle aktiven Questions
        questions = {q.key: q for q in Question.objects.filter(is_active=True)}
        
        # Erstelle oder aktualisiere WeightResponses
        created_count = 0
        updated_count = 0
        
        for rating in importance_ratings:
            question = questions.get(rating['key'])
            if question:
                weight_response, created = WeightResponse.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'importance': rating['importance']}
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        messages.success(
            request, 
            f'Deine Bewertungen wurden gespeichert! ({created_count} neu, {updated_count} aktualisiert)'
        )
        
        # HTMX: Redirect zu Home
        if request.htmx:
            response = HttpResponse(status=204)
            response['HX-Redirect'] = '/'
            return response
        
        return redirect('questionnaire:home')
