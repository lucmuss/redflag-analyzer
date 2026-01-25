"""
Custom Forms für erweiterte Registrierung
Erweitert django-allauth SignupForm mit UserProfile Feldern
"""
from django import forms
from allauth.account.forms import SignupForm
from django.core.validators import MinValueValidator
from datetime import date
from .models import UserProfile


class CustomSignupForm(SignupForm):
    """
    Erweiterte Registrierung mit Pflichtfeldern und optionalen Profil-Daten.
    
    Pflichtfelder:
    - Email, Passwort (von Allauth)
    - Vorname
    - Geburtsdatum
    - Land (ISO-dropdown)
    - Geschlecht
    
    Optional:
    - Beziehungsstatus
    - Anzahl bisheriger Beziehungen
    - Aktuelle Beziehungsdauer
    - Referral Source
    - Bildung
    - Wohnort
    """
    
    # PFLICHTFELDER
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Vorname',
        widget=forms.TextInput(attrs={
            'placeholder': 'Dein Vorname',
            'class': 'mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    birthdate = forms.DateField(
        required=True,
        label='Geburtsdatum',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'max': date.today().isoformat(),
            'class': 'mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        }),
        help_text='Du musst mindestens 18 Jahre alt sein'
    )
    
    country = forms.ChoiceField(
        required=True,
        label='Land',
        choices=[
            ('', '--- Wähle dein Land ---'),
            ('DE', 'Deutschland'),
            ('AT', 'Österreich'),
            ('CH', 'Schweiz'),
            ('US', 'USA'),
            ('GB', 'Großbritannien'),
            ('FR', 'Frankreich'),
            ('IT', 'Italien'),
            ('ES', 'Spanien'),
            ('NL', 'Niederlande'),
            ('BE', 'Belgien'),
            ('PL', 'Polen'),
            ('CZ', 'Tschechien'),
            ('OTHER', 'Sonstiges'),
        ],
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    gender = forms.ChoiceField(
        required=True,
        label='Geschlecht',
        choices=[
            ('', '--- Wähle dein Geschlecht ---'),
        ] + UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    # OPTIONALE FELDER
    relationship_status = forms.ChoiceField(
        required=False,
        label='Beziehungsstatus (optional)',
        choices=[
            ('', '--- Optional ---'),
        ] + UserProfile.RELATIONSHIP_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    previous_relationships_count = forms.ChoiceField(
        required=False,
        label='Anzahl bisheriger Beziehungen (optional)',
        choices=[
            ('', '--- Optional ---'),
        ] + UserProfile.PREVIOUS_RELATIONSHIPS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    current_relationship_duration = forms.IntegerField(
        required=False,
        label='Dauer der aktuellen Beziehung in Monaten (optional)',
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'placeholder': 'z.B. 12',
            'min': '0',
            'class': 'mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    referral_source = forms.ChoiceField(
        required=False,
        label='Wie hast du von uns erfahren? (optional)',
        choices=[
            ('', '--- Optional ---'),
        ] + UserProfile.REFERRAL_SOURCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    education = forms.ChoiceField(
        required=False,
        label='Höchster Bildungsabschluss (optional)',
        choices=[
            ('', '--- Optional ---'),
        ] + UserProfile.EDUCATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        label='Wohnort/Stadt (optional)',
        widget=forms.TextInput(attrs={
            'placeholder': 'z.B. Berlin',
            'class': 'mt-1 appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-red-flag focus:border-red-flag sm:text-sm'
        })
    )
    
    def clean_birthdate(self):
        """Validiere Mindestalter 18 Jahre"""
        birthdate = self.cleaned_data.get('birthdate')
        if birthdate:
            today = date.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            if age < 18:
                raise forms.ValidationError('Du musst mindestens 18 Jahre alt sein.')
        return birthdate
    
    def save(self, request):
        """
        Speichere User und erweiterte Profil-Daten.
        Wird von django-allauth automatisch aufgerufen.
        """
        # Rufe die Standard-Speichern-Methode auf (erstellt User)
        user = super().save(request)
        
        # Setze Vorname
        user.first_name = self.cleaned_data.get('first_name')
        user.save()
        
        # Erstelle oder aktualisiere UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Pflichtfelder
        profile.birthdate = self.cleaned_data.get('birthdate')
        profile.country = self.cleaned_data.get('country')
        profile.gender = self.cleaned_data.get('gender')
        
        # Optionale Felder (nur setzen wenn ausgefüllt)
        if self.cleaned_data.get('relationship_status'):
            profile.relationship_status = self.cleaned_data.get('relationship_status')
        
        if self.cleaned_data.get('previous_relationships_count'):
            profile.previous_relationships_count = self.cleaned_data.get('previous_relationships_count')
        
        if self.cleaned_data.get('current_relationship_duration'):
            profile.current_relationship_duration = self.cleaned_data.get('current_relationship_duration')
        
        if self.cleaned_data.get('referral_source'):
            profile.referral_source = self.cleaned_data.get('referral_source')
        
        if self.cleaned_data.get('education'):
            profile.education = self.cleaned_data.get('education')
        
        if self.cleaned_data.get('city'):
            profile.city = self.cleaned_data.get('city')
        
        profile.save()
        
        return user
