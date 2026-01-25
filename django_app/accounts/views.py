"""
Account Views für Profil-Verwaltung
"""
from django.views.generic import TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import User, UserProfile
from .badges import (
    get_user_badges, 
    get_user_badge_progress, 
    BadgeDefinition,
    check_and_award_badges
)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Profil-Ansicht zeigt User-Informationen und Credits.
    """
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Hole oder erstelle UserProfile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Profil bearbeiten - Name, Email, etc.
    """
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil erfolgreich aktualisiert!')
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, View):
    """
    DSGVO-konforme Account-Löschung.
    User muss "DELETE" eingeben zur Bestätigung.
    """
    template_name = 'accounts/delete_confirm.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        if request.POST.get('confirm') == 'DELETE':
            user = request.user
            logout(request)
            user.delete()  # CASCADE löscht alle zugehörigen Daten
            messages.success(request, 'Dein Account wurde permanent gelöscht.')
            return redirect('questionnaire:home')
        
        messages.error(request, 'Bestätigung fehlgeschlagen. Bitte tippe exakt "DELETE" ein.')
        return redirect('accounts:delete')


class BadgesView(LoginRequiredMixin, TemplateView):
    """
    Badge-Übersicht: Zeigt verdiente Badges und Fortschritt.
    """
    template_name = 'accounts/badges.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Prüfe und vergebe neue Badges
        newly_awarded = check_and_award_badges(self.request.user)
        
        # Zeige Notification für neu verdiente Badges
        for badge in newly_awarded:
            messages.success(
                self.request, 
                f'🎉 Neues Badge verdient: {badge.title}! +{badge.points} Punkte'
            )
        
        # Hole alle Badges und Fortschritt
        context['earned_badges'] = get_user_badges(self.request.user)
        context['progress'] = get_user_badge_progress(self.request.user)
        context['all_badges'] = BadgeDefinition.all_badges()
        context['earned_badge_keys'] = set(b.badge_key for b in context['earned_badges'])
        
        return context
