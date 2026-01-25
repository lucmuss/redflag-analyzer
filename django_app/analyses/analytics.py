"""
Analytics Service für Data-Driven Insights
Percentile-Berechnung, Altersgruppen-Vergleiche, Regional Stats
"""
from django.db.models import Avg, Count, Q
from django.db.models.functions import Cast
from django.db.models import FloatField
from .models import Analysis, CategoryScore
from accounts.models import UserProfile
import math


class AnalyticsService:
    """
    Service für fortgeschrittene Analytics und Insights.
    Fat Service Layer für komplexe Business Logic.
    """
    
    # Altersgruppen in 5-Jahres-Schritten
    AGE_GROUPS = [
        (18, 23, '18-23'),
        (23, 28, '23-28'),
        (28, 33, '28-33'),
        (33, 38, '33-38'),
        (38, 43, '38-43'),
        (43, 48, '43-48'),
        (48, 53, '48-53'),
        (53, 100, '53+'),
    ]
    
    @classmethod
    def get_user_age_group(cls, user):
        """Bestimme Altersgruppe des Users."""
        try:
            age = user.profile.age
            if not age:
                return None
            
            for min_age, max_age, label in cls.AGE_GROUPS:
                if min_age <= age < max_age:
                    return label
        except Exception:
            pass
        return None
    
    @classmethod
    def calculate_percentile(cls, score_total, age_group=None, country=None):
        """
        Berechne Percentile für einen Score.
        
        Premium Feature: "Du bist im 68. Percentile in deiner Altersgruppe"
        
        Args:
            score_total: Der Score des Users
            age_group: Altersgruppe (optional, z.B. "18-23")
            country: Land-Code (optional, z.B. "DE")
        
        Returns:
            dict mit Percentile-Info
        """
        # Base Query: Alle Analysen
        query = Analysis.objects.filter(is_unlocked=True)
        
        # Filter nach Altersgruppe
        if age_group:
            min_age, max_age, _ = next((g for g in cls.AGE_GROUPS if g[2] == age_group), (None, None, None))
            if min_age and max_age:
                # Komplexe Query: Join mit UserProfile über User
                from datetime import date
                today = date.today()
                
                # Berechne Geburtsjahr-Range für Altersgruppe
                min_birth_year = today.year - max_age
                max_birth_year = today.year - min_age
                
                query = query.filter(
                    user__profile__birthdate__year__gte=min_birth_year,
                    user__profile__birthdate__year__lt=max_birth_year
                )
        
        # Filter nach Land
        if country:
            query = query.filter(user__profile__country=country)
        
        # Hole alle Scores sorted
        all_scores = list(query.values_list('score_total', flat=True).order_by('score_total'))
        
        if not all_scores:
            return {
                'percentile': None,
                'total_comparisons': 0,
                'better_than_percent': 0,
                'average_score': 0,
                'your_score': score_total,
            }
        
        # Berechne Percentile
        better_than_count = sum(1 for s in all_scores if s < score_total)
        total = len(all_scores)
        
        percentile = math.floor((better_than_count / total) * 100) if total > 0 else 0
        average_score = sum(all_scores) / total if total > 0 else 0
        
        return {
            'percentile': percentile,
            'total_comparisons': total,
            'better_than_percent': percentile,
            'average_score': round(average_score, 2),
            'your_score': score_total,
            'interpretation': cls._interpret_percentile(percentile),
        }
    
    @classmethod
    def _interpret_percentile(cls, percentile):
        """Interpretiere Percentile für User-Feedback."""
        if percentile is None:
            return "Nicht genug Daten"
        if percentile < 25:
            return "Sehr wenige RedFlags - Sehr gesunde Beziehung!"
        elif percentile < 50:
            return "Wenige RedFlags - Gute Beziehung"
        elif percentile < 75:
            return "Durchschnittlich - Einige Bereiche könnten verbessert werden"
        else:
            return "Viele RedFlags - Aufmerksamkeit erforderlich"
    
    @classmethod
    def get_age_group_statistics(cls):
        """
        Hole Durchschnitts-Scores für alle Altersgruppen.
        
        Premium Feature: "Durchschnitts-Score nach Altersgruppe"
        
        Returns:
            Liste von dicts mit Altersgruppen-Stats
        """
        from datetime import date
        today = date.today()
        
        stats = []
        
        for min_age, max_age, label in cls.AGE_GROUPS:
            min_birth_year = today.year - max_age
            max_birth_year = today.year - min_age
            
            group_analyses = Analysis.objects.filter(
                is_unlocked=True,
                user__profile__birthdate__year__gte=min_birth_year,
                user__profile__birthdate__year__lt=max_birth_year
            )
            
            count = group_analyses.count()
            if count > 0:
                avg_score = group_analyses.aggregate(Avg('score_total'))['score_total__avg']
                stats.append({
                    'age_group': label,
                    'min_age': min_age,
                    'max_age': max_age,
                    'avg_score': round(avg_score, 2) if avg_score else 0,
                    'count': count,
                })
        
        return stats
    
    @classmethod
    def get_regional_heatmap_data(cls):
        """
        Hole Regional-Daten für Heatmap.
        
        Premium Feature: "Heatmap nach Land"
        
        Returns:
            Liste von dicts mit Land-Stats
        """
        # Aggregiere nach Land
        country_stats = Analysis.objects.filter(
            is_unlocked=True,
            user__profile__country__isnull=False
        ).values('user__profile__country').annotate(
            avg_score=Avg('score_total'),
            count=Count('id')
        ).filter(count__gte=5)  # Mindestens 5 Analysen für Statistik
        
        results = []
        for stat in country_stats:
            results.append({
                'country': stat['user__profile__country'],
                'avg_score': round(stat['avg_score'], 2) if stat['avg_score'] else 0,
                'count': stat['count'],
            })
        
        return sorted(results, key=lambda x: x['avg_score'], reverse=True)
    
    @classmethod
    def get_category_heatmap_by_country(cls, category):
        """
        Hole Category-spezifische Scores nach Land.
        
        Args:
            category: Category Key (z.B. "communication", "trust")
        
        Returns:
            Liste von dicts mit Land und Category Score
        """
        country_stats = CategoryScore.objects.filter(
            category=category,
            analysis__is_unlocked=True,
            analysis__user__profile__country__isnull=False
        ).values('analysis__user__profile__country').annotate(
            avg_score=Avg('score'),
            count=Count('id')
        ).filter(count__gte=3)  # Mindestens 3 für Category
        
        results = []
        for stat in country_stats:
            results.append({
                'country': stat['analysis__user__profile__country'],
                'category': category,
                'avg_score': round(stat['avg_score'], 2) if stat['avg_score'] else 0,
                'count': stat['count'],
            })
        
        return sorted(results, key=lambda x: x['avg_score'], reverse=True)
    
    @classmethod
    def get_user_premium_insights(cls, analysis):
        """
        Generiere Premium Insights für eine Analyse.
        Nur für Premium Users.
        
        Returns:
            dict mit allen Premium Insights
        """
        user = analysis.user
        age_group = cls.get_user_age_group(user)
        country = user.profile.country if hasattr(user, 'profile') else None
        
        # Percentile Berechnung
        percentile_data = cls.calculate_percentile(
            analysis.score_total,
            age_group=age_group,
            country=country
        )
        
        # Altersgruppen-Vergleich
        age_stats = cls.get_age_group_statistics()
        
        # Regional Vergleich
        regional_stats = cls.get_regional_heatmap_data()
        
        return {
            'percentile': percentile_data,
            'age_group': age_group,
            'age_group_stats': age_stats,
            'regional_stats': regional_stats[:10],  # Top 10 Länder
            'country': country,
        }
