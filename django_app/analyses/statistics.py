"""
Statistics Service für Compare with Average
Berechnet Durchschnittswerte aus allen Analysen
"""
from django.db.models import Avg
from .models import Analysis, CategoryScore


class StatisticsService:
    """
    Service für statistische Vergleiche
    Fat Service Pattern: Komplexe Business Logic hier
    """
    
    @staticmethod
    def get_average_scores():
        """
        Berechnet Durchschnittswerte über alle Analysen
        
        Returns:
            dict: {
                'total': float,
                'by_category': {
                    'TRUST': float,
                    'BEHAVIOR': float,
                    'VALUES': float,
                    'DYNAMICS': float
                }
            }
        """
        # Durchschnittlicher Total Score
        avg_total = Analysis.objects.filter(is_unlocked=True).aggregate(
            avg=Avg('score_total')
        )['avg']
        avg_total = float(avg_total) if avg_total is not None else 0.0
        
        # Durchschnitt pro Kategorie
        categories = ['TRUST', 'BEHAVIOR', 'VALUES', 'DYNAMICS']
        by_category = {}
        
        for category in categories:
            avg = CategoryScore.objects.filter(category=category).aggregate(
                avg=Avg('score')
            )['avg']
            avg = float(avg) if avg is not None else 0.0
            by_category[category] = round(avg, 1)
        
        return {
            'total': round(avg_total, 1),
            'by_category': by_category
        }
    
    @staticmethod
    def compare_with_average(analysis):
        """
        Vergleicht eine Analyse mit dem Durchschnitt
        
        Args:
            analysis: Analysis Model Instance
            
        Returns:
            dict: {
                'user_total': float,
                'avg_total': float,
                'diff_total': float,
                'diff_total_percent': float,
                'better_than_average': bool,
                'categories': [
                    {
                        'name': str,
                        'user_score': float,
                        'avg_score': float,
                        'diff': float,
                        'diff_percent': float
                    }
                ]
            }
        """
        averages = StatisticsService.get_average_scores()
        
        # Total Vergleich
        user_total = float(analysis.score_total)
        avg_total = float(averages['total'])
        diff_total = user_total - avg_total
        diff_total_percent = ((diff_total / avg_total) * 100) if avg_total > 0 else 0
        
        # Kategorie Vergleiche
        category_comparisons = []
        category_scores = {cs.category: cs.score for cs in analysis.category_scores.all()}
        
        category_names = {
            'TRUST': '🤝 Vertrauen',
            'BEHAVIOR': '🎭 Verhalten', 
            'VALUES': '💎 Werte',
            'DYNAMICS': '⚡ Dynamik'
        }
        
        for category, avg_score in averages['by_category'].items():
            user_score = float(category_scores.get(category, 0))
            avg_score = float(avg_score)  # Konvertiere Decimal zu float
            diff = user_score - avg_score
            diff_percent = ((diff / avg_score) * 100) if avg_score > 0 else 0
            
            category_comparisons.append({
                'name': category_names.get(category, category),
                'category': category,
                'user_score': user_score,
                'avg_score': avg_score,
                'diff': round(diff, 1),
                'diff_percent': round(diff_percent, 1),
                'better_than_average': diff < 0  # Niedriger Score ist besser
            })
        
        return {
            'user_total': user_total,
            'avg_total': avg_total,
            'diff_total': round(diff_total, 1),
            'diff_total_percent': round(diff_total_percent, 1),
            'better_than_average': diff_total < 0,  # Niedriger = besser
            'categories': category_comparisons
        }
