"""
Legal URL Configuration
"""
from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('impressum/', views.ImpressumView.as_view(), name='impressum'),
    path('datenschutz/', views.DatenschutzView.as_view(), name='datenschutz'),
    path('agb/', views.AGBView.as_view(), name='agb'),
    path('disclaimer/', views.DisclaimerView.as_view(), name='disclaimer'),
]
