"""
URLs für Questionnaire App
"""
from django.urls import path
from . import views

app_name = 'questionnaire'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('questionnaire/', views.QuestionnaireView.as_view(), name='questionnaire'),
    path('questionnaire/submit/', views.QuestionnaireSubmitView.as_view(), name='submit'),
]
