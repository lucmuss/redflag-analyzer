"""
Custom Django-Allauth Adapter
Synchronisiert das is_verified Feld mit allauth's E-Mail-Verifizierung
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Erweitert den Standard-Adapter um Custom-Logik:
    - Synchronisiert User.is_verified mit EmailAddress.verified
    - Erlaubt Login wenn User.is_verified=True (z.B. durch Admin gesetzt)
    """
    
    def is_open_for_signup(self, request):
        """
        Prüft ob Registrierung erlaubt ist.
        Kann später für Wartungsmodus o.ä. genutzt werden.
        """
        return True
    
    def confirm_email(self, request, email_address):
        """
        Wird aufgerufen wenn E-Mail bestätigt wird.
        Setze auch is_verified auf True im User-Model.
        """
        super().confirm_email(request, email_address)
        
        user = email_address.user
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified'])
    
    def login(self, request, user):
        """
        Custom Login-Logik: Synchronisiere EmailAddress verified status
        mit User.is_verified Feld.
        
        Wenn User.is_verified=True (z.B. durch Admin gesetzt), aber
        die EmailAddress noch nicht verified ist, setze sie auf verified.
        """
        # Hole oder erstelle EmailAddress-Objekt für diesen User
        email_address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email.lower(),
            defaults={'primary': True, 'verified': user.is_verified}
        )
        
        # Synchronisiere: Wenn User.is_verified=True, setze auch EmailAddress.verified=True
        if user.is_verified and not email_address.verified:
            email_address.verified = True
            email_address.save(update_fields=['verified'])
        
        # Führe Standard-Login aus
        return super().login(request, user)
    
    def save_user(self, request, user, form, commit=True):
        """
        Wird beim Signup aufgerufen.
        Setze is_verified initial auf False (wird durch E-Mail-Bestätigung auf True gesetzt).
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Initial ist User nicht verifiziert
        user.is_verified = False
        
        if commit:
            user.save()
        
        return user
