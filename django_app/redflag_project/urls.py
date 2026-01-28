"""
URL Configuration für RedFlag Analyzer
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # PWA URLs
    path('', include(('pwa.urls', 'pwa'), namespace='pwa')),
    
    # Authentication (Django Allauth)
    path('accounts/', include('allauth.urls')),
    
    # Custom Accounts (Profile, Credits, Dev-Login)
    path('accounts/', include('accounts.urls')),
    
    # App URLs
    path('', include('questionnaire.urls')),
    path('analyses/', include('analyses.urls')),
    path('feedback/', include('feedback.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('referrals/', include('referrals.urls')),
    path('blog/', include('blog.urls')),
    path('rankings/', include('rankings.urls')),
    path('', include('legal.urls')),
]

# Static/Media Files in Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
