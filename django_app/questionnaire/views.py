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
        from django.db.models import Avg
        
        context['total_analyses'] = Analysis.objects.count()
        context['total_users'] = User.objects.count()
        
        # Analysen heute
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        context['analyses_today'] = Analysis.objects.filter(created_at__gte=today_start).count()
        
        # Durchschnittlicher Red Flag Score über alle Analysen
        avg_score = Analysis.objects.aggregate(avg=Avg('score_total'))['avg']
        context['average_redflag_score'] = round(float(avg_score), 2) if avg_score else 0.0
        
        return context


class OnboardingView(TemplateView):
    """
    Onboarding/Motivation Screen.
    Zeigt neue Usern warum sie RedFlag Analyzer nutzen sollten.
    """
    template_name = 'questionnaire/onboarding.html'


class QuestionnaireView(LoginRequiredMixin, TemplateView):
    """
    Single-Question Fragebogen-View.
    Zeigt eine Frage zur Zeit mit Vor/Zurück Navigation.
    """
    template_name = 'questionnaire/questionnaire.html'
    
    def get(self, request):
        # Hole aktuelle Fragen-Index aus Query-Parameter
        current_index = int(request.GET.get('q', 1))
        
        # Hole alle aktiven Fragen
        questions = list(Question.objects.filter(is_active=True).order_by('id'))
        total_questions = len(questions)
        
        # Validiere Index
        if current_index < 1:
            current_index = 1
        elif current_index > total_questions:
            current_index = total_questions
        
        # Hole aktuelle Frage (Index ist 1-basiert)
        current_question = questions[current_index - 1] if questions else None
        
        # Hole gespeicherte Antworten aus Session
        responses = request.session.get('questionnaire_responses', {})
        partner_data = request.session.get('questionnaire_partner', {})
        
        context = {
            'current_question': current_question,
            'current_index': current_index,
            'total_questions': total_questions,
            'progress_percentage': int((current_index / total_questions * 100)) if total_questions > 0 else 0,
            'has_previous': current_index > 1,
            'has_next': current_index < total_questions,
            'current_answer': responses.get(current_question.key) if current_question else None,
            'partner_data': partner_data,
            'user_credits': request.user.credits,
            'answered_count': len(responses),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Speichere Antwort in Session
        current_index = int(request.POST.get('current_index', 1))
        answer = request.POST.get('answer')
        question_key = request.POST.get('question_key')
        
        # Hole oder initialisiere Session-Daten
        responses = request.session.get('questionnaire_responses', {})
        
        if answer and question_key:
            responses[question_key] = int(answer)
            request.session['questionnaire_responses'] = responses
        
        # Speichere Partner-Daten wenn auf erster Seite
        if current_index == 1:
            partner_data = {
                'partner_name': request.POST.get('partner_name', '').strip() or None,
                'partner_age': int(request.POST.get('partner_age')) if request.POST.get('partner_age') else None,
                'partner_country': request.POST.get('partner_country', '').strip() or None,
            }
            request.session['questionnaire_partner'] = partner_data
        
        # Navigation
        action = request.POST.get('action', 'next')
        
        if action == 'next':
            next_index = current_index + 1
        elif action == 'previous':
            next_index = current_index - 1
        elif action == 'submit':
            # Finale Submission
            return self._submit_questionnaire(request)
        else:
            next_index = current_index
        
        return redirect(f'{request.path}?q={next_index}')
    
    def _submit_questionnaire(self, request):
        """Erstelle finale Analyse aus Session-Daten"""
        responses_dict = request.session.get('questionnaire_responses', {})
        partner_data = request.session.get('questionnaire_partner', {})
        
        if not responses_dict:
            messages.error(request, 'Bitte beantworte mindestens eine Frage.')
            return redirect('questionnaire:questionnaire')
        
        # Konvertiere zu Liste-Format für ScoreCalculator
        responses = [{'key': key, 'value': value} for key, value in responses_dict.items()]
        
        # Berechne Scores
        calculator = ScoreCalculator(responses)
        score_total = calculator.calculate_total_score()
        category_scores_dict = calculator.calculate_category_scores()
        
        # Erstelle Analysis
        analysis = Analysis.objects.create(
            user=request.user,
            partner_name=partner_data.get('partner_name'),
            partner_age=partner_data.get('partner_age'),
            partner_country=partner_data.get('partner_country'),
            responses=responses,
            score_total=score_total,
            is_unlocked=False
        )
        
        # Erstelle Category Scores
        for category, score in category_scores_dict.items():
            CategoryScore.objects.create(
                analysis=analysis,
                category=category,
                score=score
            )
        
        # Clear Session
        request.session.pop('questionnaire_responses', None)
        request.session.pop('questionnaire_partner', None)
        
        messages.success(request, 'Analyse erfolgreich erstellt!')
        return redirect('analyses:detail', pk=analysis.id)


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


class ImportanceQuestionnaireView(LoginRequiredMixin, TemplateView):
    """
    Single-Question Importance Questionnaire View.
    Zeigt eine Frage zur Zeit mit Vor/Zurück Navigation.
    """
    template_name = 'questionnaire/importance_questionnaire.html'
    
    def get(self, request):
        # Hole aktuelle Fragen-Index
        current_index = int(request.GET.get('q', 1))
        
        # Hole alle aktiven Fragen
        questions = list(Question.objects.filter(is_active=True).order_by('id'))
        total_questions = len(questions)
        
        # Validiere Index
        if current_index < 1:
            current_index = 1
        elif current_index > total_questions:
            current_index = total_questions
        
        # Hole aktuelle Frage
        current_question = questions[current_index - 1] if questions else None
        
        # Hole gespeicherte Bewertungen aus Session
        importance_ratings = request.session.get('importance_ratings', {})
        
        # Hole existierende DB-Werte falls vorhanden
        existing_weights = WeightResponse.get_user_weights(request.user)
        
        # Verwende Session-Wert oder DB-Wert
        current_importance = importance_ratings.get(current_question.key) if current_question else None
        if current_importance is None and current_question:
            current_importance = existing_weights.get(current_question.key)
        
        context = {
            'current_question': current_question,
            'current_index': current_index,
            'total_questions': total_questions,
            'progress_percentage': int((current_index / total_questions * 100)) if total_questions > 0 else 0,
            'has_previous': current_index > 1,
            'has_next': current_index < total_questions,
            'current_importance': current_importance,
            'answered_count': len(importance_ratings),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Speichere Wichtigkeit in Session
        current_index = int(request.POST.get('current_index', 1))
        importance = request.POST.get('importance')
        question_key = request.POST.get('question_key')
        
        # Hole oder initialisiere Session-Daten
        importance_ratings = request.session.get('importance_ratings', {})
        
        if importance and question_key:
            importance_ratings[question_key] = int(importance)
            request.session['importance_ratings'] = importance_ratings
        
        # Navigation
        action = request.POST.get('action', 'next')
        
        if action == 'next':
            next_index = current_index + 1
        elif action == 'previous':
            next_index = current_index - 1
        elif action == 'submit':
            # Finale Submission
            return self._submit_importance(request)
        else:
            next_index = current_index
        
        return redirect(f'{request.path}?q={next_index}')
    
    def _submit_importance(self, request):
        """Speichere Wichtigkeits-Bewertungen in DB"""
        importance_ratings = request.session.get('importance_ratings', {})
        
        if not importance_ratings:
            messages.error(request, 'Bitte bewerte mindestens eine Frage.')
            return redirect('questionnaire:importance')
        
        # Hole alle aktiven Questions
        questions = {q.key: q for q in Question.objects.filter(is_active=True)}
        
        # Erstelle oder aktualisiere WeightResponses
        created_count = 0
        updated_count = 0
        
        for question_key, importance in importance_ratings.items():
            question = questions.get(question_key)
            if question:
                weight_response, created = WeightResponse.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'importance': importance}
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        # Clear Session
        request.session.pop('importance_ratings', None)
        
        messages.success(
            request, 
            f'Deine Bewertungen wurden gespeichert! ({created_count} neu, {updated_count} aktualisiert)'
        )
        
        return redirect('questionnaire:home')


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
