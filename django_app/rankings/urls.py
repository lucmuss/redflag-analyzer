"""
Rankings URL Configuration
"""
from django.urls import path
from . import views

app_name = 'rankings'

urlpatterns = [
    path('', views.leaderboard, name='leaderboard'),
]
