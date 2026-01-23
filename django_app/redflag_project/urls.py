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
    path('', include('pwa.urls')),
    
    # Authentication (Django Allauth)
    path('accounts/', include('allauth.urls')),
    
    # App URLs
    path('', include('questionnaire.urls')),
    path('analyses/', include('analyses.urls')),
    path('profile/', include('accounts.urls')),
]

# Static/Media Files in Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
