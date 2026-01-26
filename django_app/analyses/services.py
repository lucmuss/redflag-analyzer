"""
Service Layer für Score-Berechnungen
DYNAMISCH: Verwendet Question.calculated_weight (wird automatisch aktualisiert)
"""
from typing import Dict, List
from decimal import Decimal


class ScoreCalculator:
    """
    Service für Score-Berechnung.
    DYNAMISCH: Holt Gewichte direkt aus Question.calculated_weight
    """
    
    def __init__(self, responses: List[Dict]):
        """
        Args:
            responses: List von {"key": str, "value": int}
        """
        self.responses = responses
        # Hole aktuelle calculated_weights DYNAMISCH aus DB
        self.weights = self._get_current_weights()
    
    def _get_current_weights(self) -> Dict[str, float]:
        """
        Holt aktuelle calculated_weights aus Question Model.
        DYNAMISCH: Gewichte werden immer frisch aus DB geladen.
        """
        from questionnaire.models import Question
        
        questions = Question.objects.filter(is_active=True)
        return {q.key: q.calculated_weight for q in questions}
    
    def calculate_total_score(self) -> Decimal:
        """
        Berechne Gesamt-Score (0-5).
        Formula: Gewichtete Summe normalisiert auf 0-5 Skala
        
        Berechnung:
        1. Gewichtete Summe = Σ(Bewertung × Calculated Weight)
        2. Max mögliche Summe = Σ(5 × Calculated Weight) 
        3. Score = (Gewichtete Summe / Max mögliche Summe) × 5
        """
        if not self.responses:
            return Decimal('0.00')
        
        total_weighted_sum = 0
        max_possible = 0
        
        for response in self.responses:
            key = response['key']
            value = response['value']  # 1-5 (Bewertung aus Fragebogen)
            weight = self.weights.get(key, 5.0)  # Calculated Weight aus Question
            
            # Gewichtete Summe: Bewertung × Calculated Weight
            total_weighted_sum += value * weight
            
            # Max mögliche Summe: 5 (max Bewertung) × Calculated Weight
            max_possible += 5 * weight
        
        if max_possible == 0:
            return Decimal('0.00')
        
        # Normalisiere auf 0-5 Skala
        score = (total_weighted_sum / max_possible) * 5
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
                calc = ScoreCalculator(responses)
                category_scores[category] = calc.calculate_total_score()
            else:
                category_scores[category] = Decimal('0.00')
        
        return category_scores
