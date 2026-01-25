"""
Badge & Achievement System
Gamification für User Engagement
"""
from django.db import models
from django.utils import timezone


class BadgeDefinition:
    """
    Statische Badge-Definitionen.
    Definiert alle verfügbaren Badges mit Namen, Beschreibung, Icon etc.
    """
    BADGES = {
        'first_analysis': {
            'name': 'First Analysis',
            'title': '🎯 Erste Analyse',
            'description': 'Du hast deine erste RedFlag-Analyse erstellt!',
            'icon': '🎯',
            'points': 10,
        },
        'truth_seeker': {
            'name': 'Truth Seeker',
            'title': '🔍 Wahrheitssucher',
            'description': 'Du hast 3 Analysen durchgeführt. Du nimmst Beziehungen ernst!',
            'icon': '🔍',
            'points': 25,
            'required_count': 3,
        },
        'self_aware': {
            'name': 'Self-Aware',
            'title': '🧠 Selbstreflektiert',
            'description': 'Du hast den Importance Questionnaire ausgefüllt und weißt was dir wichtig ist.',
            'icon': '🧠',
            'points': 15,
        },
        'community_helper': {
            'name': 'Community Helper',
            'title': '💬 Community Helper',
            'description': 'Du hast Feedback gegeben und hilfst uns besser zu werden!',
            'icon': '💬',
            'points': 10,
        },
        'relationship_expert': {
            'name': 'Relationship Expert',
            'title': '💎 Beziehungsexperte',
            'description': 'Du hast 5 Analysen durchgeführt. Du bist ein echter Experte!',
            'icon': '💎',
            'points': 50,
            'required_count': 5,
        },
        'profile_complete': {
            'name': 'Profile Complete',
            'title': '✅ Profil Komplett',
            'description': 'Du hast dein Profil vollständig ausgefüllt.',
            'icon': '✅',
            'points': 5,
        },
    }
    
    @classmethod
    def get_badge(cls, badge_key):
        """Hole Badge-Definition nach Key."""
        return cls.BADGES.get(badge_key)
    
    @classmethod
    def all_badges(cls):
        """Hole alle Badge-Definitionen."""
        return cls.BADGES


# Badge-Checker Funktionen
def check_first_analysis(user):
    """Prüfe ob User First Analysis Badge verdient hat."""
    from analyses.models import Analysis
    count = Analysis.objects.filter(user=user).count()
    return count >= 1


def check_truth_seeker(user):
    """Prüfe ob User Truth Seeker Badge verdient hat (3 Analysen)."""
    from analyses.models import Analysis
    count = Analysis.objects.filter(user=user).count()
    return count >= 3


def check_relationship_expert(user):
    """Prüfe ob User Relationship Expert Badge verdient hat (5 Analysen)."""
    from analyses.models import Analysis
    count = Analysis.objects.filter(user=user).count()
    return count >= 5


def check_self_aware(user):
    """Prüfe ob User Self-Aware Badge verdient hat (Importance Questionnaire)."""
    from questionnaire.models import WeightResponse
    count = WeightResponse.objects.filter(user=user).count()
    return count > 0


def check_community_helper(user):
    """Prüfe ob User Community Helper Badge verdient hat (Feedback gegeben)."""
    from feedback.models import Feedback
    count = Feedback.objects.filter(user=user).count()
    return count >= 1


def check_profile_complete(user):
    """Prüfe ob User Profile Complete Badge verdient hat."""
    try:
        profile = user.profile
        # Prüfe ob alle wichtigen Felder ausgefüllt sind
        if all([
            profile.birthdate,
            profile.country,
            profile.gender,
            user.first_name,
        ]):
            return True
    except Exception:
        pass
    return False


# Badge-Checker Mapping
BADGE_CHECKERS = {
    'first_analysis': check_first_analysis,
    'truth_seeker': check_truth_seeker,
    'relationship_expert': check_relationship_expert,
    'self_aware': check_self_aware,
    'community_helper': check_community_helper,
    'profile_complete': check_profile_complete,
}


def award_badge(user, badge_key):
    """
    Vergebe ein Badge an einen User.
    Returns: (UserBadge, created) Tuple
    """
    from .models import UserBadge
    
    badge_def = BadgeDefinition.get_badge(badge_key)
    if not badge_def:
        return None, False
    
    # Prüfe ob User Badge bereits hat
    existing = UserBadge.objects.filter(user=user, badge_key=badge_key).first()
    if existing:
        return existing, False
    
    # Erstelle neues Badge
    badge = UserBadge.objects.create(
        user=user,
        badge_key=badge_key,
        name=badge_def['name'],
        title=badge_def['title'],
        description=badge_def['description'],
        icon=badge_def['icon'],
        points=badge_def['points'],
    )
    
    return badge, True


def check_and_award_badges(user):
    """
    Prüfe alle Badges und vergebe neue Badges an User.
    Returns: Liste von neu vergebenen Badges
    """
    newly_awarded = []
    
    for badge_key, checker_func in BADGE_CHECKERS.items():
        if checker_func(user):
            badge, created = award_badge(user, badge_key)
            if created and badge:
                newly_awarded.append(badge)
    
    return newly_awarded


def get_user_badges(user):
    """Hole alle Badges eines Users."""
    from .models import UserBadge
    return UserBadge.objects.filter(user=user).order_by('-earned_at')


def get_user_badge_progress(user):
    """
    Berechne Badge-Fortschritt für User.
    Returns: Dictionary mit Fortschritt-Informationen
    """
    from analyses.models import Analysis
    from questionnaire.models import WeightResponse
    from feedback.models import Feedback
    
    analysis_count = Analysis.objects.filter(user=user).count()
    has_weights = WeightResponse.objects.filter(user=user).exists()
    has_feedback = Feedback.objects.filter(user=user).exists()
    
    earned_badges = get_user_badges(user)
    earned_badge_keys = set(b.badge_key for b in earned_badges)
    
    total_badges = len(BadgeDefinition.BADGES)
    earned_count = len(earned_badges)
    
    progress = {
        'total_badges': total_badges,
        'earned_count': earned_count,
        'percentage': int((earned_count / total_badges) * 100) if total_badges > 0 else 0,
        'total_points': sum(b.points for b in earned_badges),
        'next_badges': [],
    }
    
    # Berechne nächste erreichbare Badges
    if 'first_analysis' not in earned_badge_keys and analysis_count == 0:
        progress['next_badges'].append({
            'key': 'first_analysis',
            'title': '🎯 Erste Analyse',
            'hint': 'Erstelle deine erste Analyse'
        })
    
    if 'truth_seeker' not in earned_badge_keys and analysis_count < 3:
        progress['next_badges'].append({
            'key': 'truth_seeker',
            'title': '🔍 Wahrheitssucher',
            'hint': f'{analysis_count}/3 Analysen erstellt',
            'progress_count': analysis_count,
            'required_count': 3,
        })
    
    if 'self_aware' not in earned_badge_keys and not has_weights:
        progress['next_badges'].append({
            'key': 'self_aware',
            'title': '🧠 Selbstreflektiert',
            'hint': 'Fülle den Importance Questionnaire aus'
        })
    
    if 'community_helper' not in earned_badge_keys and not has_feedback:
        progress['next_badges'].append({
            'key': 'community_helper',
            'title': '💬 Community Helper',
            'hint': 'Gib uns Feedback'
        })
    
    return progress
