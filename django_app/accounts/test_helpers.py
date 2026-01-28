"""
Test Helper Views
NUR FÜR DEBUG=True - Automatisches Login für Entwicklung/Testing
"""
import os
from django.shortcuts import redirect
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from .models import User


def auto_login_test_user(request):
    """
    Auto-Login für Test-User (nur in DEBUG Mode)
    URL: /accounts/dev-login/
    
    Loggt automatisch den Test-User aus .env ein.
    """
    # Sicherheitscheck: Nur in DEBUG Mode erlaubt
    if not settings.DEBUG:
        return HttpResponseForbidden("⛔ Diese Funktion ist nur im DEBUG-Modus verfügbar.")
    
    # Test-User Credentials aus .env
    test_email = os.getenv('TEST_USER_EMAIL')
    
    if not test_email:
        return HttpResponse("❌ TEST_USER_EMAIL nicht in .env gefunden.", status=500)
    
    try:
        user = User.objects.get(email=test_email)
        
        # Django Session Login
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Redirect zur Homepage
        return redirect('questionnaire:home')
        
    except User.DoesNotExist:
        return HttpResponse(f"❌ Test-User '{test_email}' existiert nicht in der Datenbank.", status=404)
