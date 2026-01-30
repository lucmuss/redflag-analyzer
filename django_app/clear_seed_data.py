#!/usr/bin/env python
"""
Script to clear all seed data from database before fresh seeding.
"""
import os

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redflag_project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from questionnaire.models import Question, WeightResponse
from analyses.models import Analysis, CategoryScore
from accounts.models import UserProfile, UserBadge
from blog.models import BlogPost as Post, BlogCategory as Category, BlogTag, EmailSubscriber  # Blog models
from community.models import CommunityPost, PostComment, PostVote, PostReport  # Community models
from feedback.models import Feedback
from referrals.models import ReferralCode, ReferralReward, ShareEvent
from social.models import SharedAnalysis  # Only model in social
from subscriptions.models import Subscription, CreditPurchase  # Subscription models
from analytics.models import AnalyticsSettings, DailyMetrics, UserSession  # Analytics models

# Clear all seed data in correct order (respecting FK constraints)
models_to_clear = [
    # Analytics models
    UserSession,
    DailyMetrics,
    AnalyticsSettings,
    # Social models
    SharedAnalysis,
    # Community models - reverse order for FK constraints
    PostReport,
    PostVote,
    PostComment,
    CommunityPost,
    # Referral models
    ShareEvent,
    ReferralReward,
    ReferralCode,
    # Subscription models
    CreditPurchase,
    Subscription,
    # Feedback models
    Feedback,
    # Blog models
    EmailSubscriber,
    BlogTag,
    Post,  # BlogPost
    Category,  # BlogCategory
    # Analysis models
    Analysis,
    CategoryScore,
    # Questionnaire models
    WeightResponse,
    Question,
    # Account models
    UserBadge,
    UserProfile,
    get_user_model(),
]

print('Clearing existing data before seeding...')
for model in models_to_clear:
    try:
        count = model.objects.count()
        if count > 0:
            model.objects.all().delete()
            print(f'Cleared {count} records from {model.__name__}')
    except Exception as e:
        print(f'Error clearing {model.__name__}: {e}')

print('Database cleared for fresh seeding')