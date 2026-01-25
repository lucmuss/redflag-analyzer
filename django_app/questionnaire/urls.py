"""
URLs für Questionnaire App
"""
from django.urls import path
from . import views

app_name = 'questionnaire'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('partner-info/', views.PartnerInfoView.as_view(), name='partner_info'),
    path('questionnaire/', views.QuestionnaireView.as_view(), name='questionnaire'),
    path('questionnaire/submit/', views.QuestionnaireSubmitView.as_view(), name='submit'),
    path('importance/', views.ImportanceQuestionnaireView.as_view(), name='importance'),
    path('importance/submit/', views.ImportanceQuestionnaireSubmitView.as_view(), name='importance_submit'),
]
