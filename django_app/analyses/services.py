"""
Service Layer für Score-Berechnungen
Trennung von Business Logic und Models (Fat Models, aber komplexe Logik in Services)
"""
from typing import Dict, List
from decimal import Decimal


class ScoreCalculator:
    """
    Service für Score-Berechnung.
    Entkoppelt Berechnungslogik vom Model.
    """
    
    def __init__(self, responses: List[Dict], weights: Dict[str, int]):
        """
        Args:
            responses: List von {"key": str, "value": int}
            weights: Dict von {key: weight}
        """
        self.responses = responses
        self.weights = weights
    
    def calculate_total_score(self) -> Decimal:
        """
        Berechne Gesamt-Score (0-10).
        Formula: Durchschnitt von (value * weight) / max_possible_weight
        """
        if not self.responses:
            return Decimal('0.00')
        
        total_weighted_sum = 0
        max_possible = 0
        
        for response in self.responses:
            key = response['key']
            value = response['value']  # 1-5
            weight = self.weights.get(key, 3)  # Default 3
            
            total_weighted_sum += value * weight
            max_possible += 5 * weight  # Max value is 5
        
        if max_possible == 0:
            return Decimal('0.00')
        
        # Normalisiere auf 0-10 Skala
        score = (total_weighted_sum / max_possible) * 10
        return Decimal(str(round(score, 2)))
    
    def calculate_category_scores(self) -> Dict[str, Decimal]:
        """
        Berechne Scores pro Kategorie.
        Returns: {"TRUST": 5.2, "BEHAVIOR": 7.8, ...}
        """
        from questionnaire.models import Question
        
        # Gruppiere responses nach Kategorie
        category_responses = {
            'TRUST': [],
            'BEHAVIOR': [],
            'VALUES': [],
            'DYNAMICS': []
        }
        
        # Hole Question-Kategorien aus DB
        questions = Question.objects.filter(
            key__in=[r['key'] for r in self.responses]
        ).values('key', 'category')
        
        key_to_category = {q['key']: q['category'] for q in questions}
        
        for response in self.responses:
            key = response['key']
            category = key_to_category.get(key)
            if category:
                category_responses[category].append(response)
        
        # Berechne Score für jede Kategorie
        category_scores = {}
        for category, responses in category_responses.items():
            if responses:
                calc = ScoreCalculator(responses, self.weights)
                category_scores[category] = calc.calculate_total_score()
            else:
                category_scores[category] = Decimal('0.00')
        
        return category_scores
    
    @staticmethod
    def create_weight_snapshot(user=None, questions=None) -> Dict[str, int]:
        """
        Erstelle Snapshot der aktuellen Gewichte.
        Verwendet User-spezifische Gewichte falls vorhanden, sonst default_weight.
        
        Args:
            user: User-Objekt (optional). Wenn vorhanden, werden personalisierte Gewichte verwendet.
            questions: Question QuerySet (optional)
        
        Returns:
            Dict mit {question_key: weight}
        """
        from questionnaire.models import Question, WeightResponse
        
        if questions is None:
            questions = Question.objects.filter(is_active=True)
        
        # Hole User-spezifische Gewichte falls User vorhanden
        if user:
            user_weights = WeightResponse.get_user_weights(user)
            # Verwende user_weights falls vorhanden, sonst default_weight
            return {
                q.key: user_weights.get(q.key, q.default_weight) 
                for q in questions
            }
        
        # Fallback: Verwende default_weights
        return {q.key: q.default_weight for q in questions}
