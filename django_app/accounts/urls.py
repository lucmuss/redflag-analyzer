"""
URLs für Accounts App
"""
from django.urls import path
from .views import ProfileView, ProfileEditView, AccountDeleteView, BadgesView

app_name = 'accounts'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('delete/', AccountDeleteView.as_view(), name='delete'),
    path('badges/', BadgesView.as_view(), name='badges'),
]
