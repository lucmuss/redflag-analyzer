"""
Trend-Analyse für User Score-Verlauf über Zeit
"""
from django.db.models import Avg, Count, Max, Min
from datetime import timedelta
from django.utils import timezone
from .models import Analysis
import logging

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """
    Service für Score Trends über Zeit.
    Analysiert wie sich Red Flag Scores eines Users entwickeln.
    """
    
    @staticmethod
    def get_user_score_trend(user, days=90):
        """
        Hole Score-Trend der letzten X Tage.
        Returns: Liste von {date, score, analysis_count} Dicts
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        analyses = Analysis.objects.filter(
            user=user,
            created_at__gte=cutoff_date,
            is_unlocked=True
        ).order_by('created_at').values('created_at', 'score_total')
        
        trend_data = []
        for analysis in analyses:
            trend_data.append({
                'date': analysis['created_at'].strftime('%Y-%m-%d'),
                'score': float(analysis['score_total']),
            })
        
        return trend_data
    
    @staticmethod
    def get_trend_statistics(user):
        """
        Berechne Trend-Statistiken für einen User.
        """
        analyses = Analysis.objects.filter(user=user, is_unlocked=True)
        
        if not analyses.exists():
            return None
        
        stats = analyses.aggregate(
            avg_score=Avg('score_total'),
            max_score=Max('score_total'),
            min_score=Min('score_total'),
            total_analyses=Count('id')
        )
        
        # Berechne Trend (Verbesserung oder Verschlechterung)
        latest_analyses = analyses.order_by('-created_at')[:3]
        earliest_analyses = analyses.order_by('created_at')[:3]
        
        if latest_analyses.exists() and earliest_analyses.exists():
            latest_avg = sum(a.score_total for a in latest_analyses) / len(latest_analyses)
            earliest_avg = sum(a.score_total for a in earliest_analyses) / len(earliest_analyses)
            
            trend_direction = float(latest_avg - earliest_avg)
            
            if trend_direction < -0.3:
                trend_text = "📉 Deutliche Verbesserung - Weniger Red Flags!"
                trend_class = "positive"
            elif trend_direction < -0.1:
                trend_text = "↘️ Leichte Verbesserung"
                trend_class = "positive"
            elif trend_direction > 0.3:
                trend_text = "📈 Achtung: Mehr Red Flags erkannt"
                trend_class = "negative"
            elif trend_direction > 0.1:
                trend_text = "↗️ Leichter Anstieg der Red Flags"
                trend_class = "negative"
            else:
                trend_text = "➡️ Stabil - Keine große Veränderung"
                trend_class = "neutral"
        else:
            trend_direction = 0
            trend_text = "➡️ Zu wenig Daten für Trend-Analyse"
            trend_class = "neutral"
        
        return {
            **stats,
            'avg_score': float(stats['avg_score']),
            'max_score': float(stats['max_score']),
            'min_score': float(stats['min_score']),
            'trend_direction': trend_direction,
            'trend_text': trend_text,
            'trend_class': trend_class,
        }
    
    @staticmethod
    def get_category_trends(user, category):
        """
        Hole Trend für eine spezifische Kategorie.
        """
        from .models import CategoryScore
        
        category_scores = CategoryScore.objects.filter(
            analysis__user=user,
            analysis__is_unlocked=True,
            category=category
        ).select_related('analysis').order_by('analysis__created_at')
        
        trend_data = []
        for cs in category_scores:
            trend_data.append({
                'date': cs.analysis.created_at.strftime('%Y-%m-%d'),
                'score': float(cs.score),
                'analysis_id': cs.analysis.id,
            })
        
        return trend_data
    
    @staticmethod
    def compare_with_previous_analysis(analysis):
        """
        Vergleiche aktuelle Analyse mit vorheriger vom selben User.
        """
        previous = Analysis.objects.filter(
            user=analysis.user,
            is_unlocked=True,
            created_at__lt=analysis.created_at
        ).order_by('-created_at').first()
        
        if not previous:
            return None
        
        score_diff = float(analysis.score_total - previous.score_total)
        
        # Vergleiche auch Category Scores
        from .models import CategoryScore
        category_comparisons = {}
        
        for cat in ['TRUST', 'BEHAVIOR', 'VALUES', 'DYNAMICS']:
            current_cat = CategoryScore.objects.filter(
                analysis=analysis, 
                category=cat
            ).first()
            previous_cat = CategoryScore.objects.filter(
                analysis=previous, 
                category=cat
            ).first()
            
            if current_cat and previous_cat:
                diff = float(current_cat.score - previous_cat.score)
                category_comparisons[cat] = {
                    'current': float(current_cat.score),
                    'previous': float(previous_cat.score),
                    'diff': diff,
                    'improved': diff < 0,
                }
        
        return {
            'previous_analysis': previous,
            'score_diff': score_diff,
            'improved': score_diff < 0,
            'category_comparisons': category_comparisons,
            'days_between': (analysis.created_at - previous.created_at).days,
        }
