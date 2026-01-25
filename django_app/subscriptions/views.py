"""
Subscription Views für Premium Features
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import Subscription


class PremiumView(LoginRequiredMixin, TemplateView):
    """
    Premium-Übersicht zeigt Features und Upgrade-CTA.
    """
    template_name = 'subscriptions/premium.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hole oder erstelle Subscription
        subscription, created = Subscription.objects.get_or_create(user=self.request.user)
        
        context['subscription'] = subscription
        context['is_premium'] = subscription.is_premium
        context['remaining_analyses'] = subscription.remaining_free_analyses
        
        return context


class UpgradeToPremiumView(LoginRequiredMixin, TemplateView):
    """
    Upgrade zu Premium - Zeigt Payment-Optionen.
    """
    template_name = 'subscriptions/upgrade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription, _ = Subscription.objects.get_or_create(user=self.request.user)
        context['subscription'] = subscription
        return context


class ManageSubscriptionView(LoginRequiredMixin, TemplateView):
    """
    Subscription Management für Premium Users.
    """
    template_name = 'subscriptions/manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription, _ = Subscription.objects.get_or_create(user=self.request.user)
        context['subscription'] = subscription
        context['credit_purchases'] = self.request.user.credit_purchases.all()[:10]
        return context
