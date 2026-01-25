"""
URLs für Feedback App
"""
from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('create/', views.FeedbackCreateView.as_view(), name='create'),
    path('list/', views.FeedbackListView.as_view(), name='list'),
]
