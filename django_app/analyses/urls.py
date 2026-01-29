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
    path('<int:pk>/delete/', views.DeleteAnalysisView.as_view(), name='delete'),
    path('<int:pk>/share/<str:format>/', views.GenerateShareImageView.as_view(), name='share_image'),
    path('<int:pk>/export/pdf/', views.ExportAnalysisPDFView.as_view(), name='export_pdf'),
    path('<int:pk>/trends/', views.TrendsView.as_view(), name='trends'),
    path('<int:pk>/load-more-flags/', views.LoadMoreRedFlagsView.as_view(), name='load_more_flags'),
]
