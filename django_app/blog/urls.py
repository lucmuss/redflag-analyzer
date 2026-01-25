"""
Blog URL Configuration
"""
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Email Capture Landing Page
    path('landing/', views.landing_page, name='landing'),
    
    # Blog Übersicht & Detail
    path('', views.blog_list, name='list'),
    path('<slug:slug>/', views.blog_detail, name='detail'),
    
    # Kategorie-spezifische Listen
    path('category/<slug:category_slug>/', views.blog_category, name='category'),
    
    # Email Subscription
    path('subscribe/', views.subscribe_email, name='subscribe'),
]
