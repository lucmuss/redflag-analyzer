"""
Blog URL Configuration
"""
from django.urls import path
from . import views
from . import admin_views
from . import category_views
from . import newsletter_views

app_name = 'blog'

urlpatterns = [
    # Admin Panel URLs (nur für Staff/Superuser)
    path('admin-panel/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/posts/', admin_views.BlogPostListView.as_view(), name='admin_posts'),
    path('admin-panel/posts/new/', admin_views.BlogPostCreateView.as_view(), name='admin_post_create'),
    path('admin-panel/posts/<int:pk>/edit/', admin_views.BlogPostUpdateView.as_view(), name='admin_post_edit'),
    path('admin-panel/posts/<int:pk>/delete/', admin_views.BlogPostDeleteView.as_view(), name='admin_post_delete'),
    path('admin-panel/categories/', admin_views.CategoryListView.as_view(), name='admin_categories'),
    path('admin-panel/categories/new/', category_views.CategoryCreateView.as_view(), name='admin_category_create'),
    path('admin-panel/categories/<int:pk>/edit/', category_views.CategoryUpdateView.as_view(), name='admin_category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', category_views.CategoryDeleteView.as_view(), name='admin_category_delete'),
    path('admin-panel/subscribers/', admin_views.SubscriberListView.as_view(), name='admin_subscribers'),
    path('admin-panel/subscribers/<int:pk>/delete/', admin_views.SubscriberDeleteView.as_view(), name='admin_subscriber_delete'),
    path('admin-panel/newsletter/', newsletter_views.NewsletterComposeView.as_view(), name='newsletter_compose'),
    
    # Email Capture Landing Page
    path('landing/', views.landing_page, name='landing'),
    
    # Blog Übersicht & Detail
    path('', views.blog_list, name='list'),
    
    # Kategorie-spezifische Listen
    path('category/<slug:category_slug>/', views.blog_category, name='category'),
    
    # Email Subscription
    path('subscribe/', views.subscribe_email, name='subscribe'),
    
    # Blog Detail (muss am Ende sein wegen slug)
    path('<slug:slug>/', views.blog_detail, name='detail'),
]
