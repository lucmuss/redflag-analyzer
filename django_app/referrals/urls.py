"""
Referral URLs
"""
from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    path('dashboard/', views.ReferralDashboardView.as_view(), name='dashboard'),
    path('use-code/', views.use_referral_code, name='use_code'),
    path('share/<int:analysis_id>/', views.ShareScreenView.as_view(), name='share_screen'),
    path('track-share/<int:analysis_id>/', views.track_share, name='track_share'),
]
