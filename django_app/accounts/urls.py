"""
URLs für Accounts App
"""
from django.urls import path
from .views import ProfileView, ProfileEditView, AccountDeleteView, BadgesView
from .credit_views import CreditPurchaseView, purchase_credits

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('delete/', AccountDeleteView.as_view(), name='delete'),
    path('badges/', BadgesView.as_view(), name='badges'),
    path('credits/buy/', CreditPurchaseView.as_view(), name='credit_purchase'),
    path('credits/purchase/<int:package_id>/', purchase_credits, name='purchase_credits'),
]
