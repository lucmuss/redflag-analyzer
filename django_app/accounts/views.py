"""
Account Views für User-Profile
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User Profile View.
    Zeigt User-Daten, Credits, und Analyse-Historie.
    """
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['total_analyses'] = user.analyses.count()
        context['unlocked_analyses'] = user.analyses.filter(is_unlocked=True).count()
        return context
