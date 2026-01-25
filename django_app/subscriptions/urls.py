"""
URLs für Subscriptions App
"""
from django.urls import path
from .views import PremiumView, UpgradeToPremiumView, ManageSubscriptionView

app_name = 'subscriptions'

urlpatterns = [
    path('premium/', PremiumView.as_view(), name='premium'),
    path('upgrade/', UpgradeToPremiumView.as_view(), name='upgrade'),
    path('manage/', ManageSubscriptionView.as_view(), name='manage'),
]
