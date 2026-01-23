"""
URLs für Analyses App
"""
from django.urls import path
from . import views

app_name = 'analyses'

urlpatterns = [
    path('', views.AnalysisListView.as_view(), name='list'),
    path('<int:pk>/', views.AnalysisDetailView.as_view(), name='detail'),
    path('<int:pk>/unlock/', views.UnlockAnalysisView.as_view(), name='unlock'),
]
