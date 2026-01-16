"""
Score Calculation Service
Implements the weighted average algorithm for red flag scoring
"""
from typing import List, Dict, Tuple
from app.models.analysis import QuestionResponse, CategoryScores
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScoreCalculator:
    """Service for calculating red flag scores"""
    
    @staticmethod
    def calculate_factor(response_value: int) -> float:
        """
        Convert response value (1-5) to factor (0-10)
        
        Formula: (response - 1) * 2.5
        
        Examples:
            1 → 0.0 (does not apply at all)
            2 → 2.5
            3 → 5.0 (neutral)
            4 → 7.5
            5 → 10.0 (fully applies)
        
        Args:
            response_value: User response (1-5)
            
        Returns:
            float: Calculated factor (0-10)
        """
        if response_value < 1 or response_value > 5:
            logger.warning(f"Response value {response_value} out of range, clamping to 1-5")
            response_value = max(1, min(5, response_value))
        
        return (response_value - 1) * 2.5
    
    @staticmethod
    def calculate_weighted_score(
        responses: List[QuestionResponse],
        weights: Dict[str, int]
    ) -> float:
        """
        Calculate weighted average score
        
        Formula: SUM(factor * weight) / SUM(weight)
        
        Args:
            responses: List of question responses
            weights: Dict of question_key -> weight (1-5)
            
        Returns:
            float: Weighted score (0-10)
        """
        if not responses:
            logger.warning("No responses provided for score calculation")
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0
        
        for response in responses:
            factor = ScoreCalculator.calculate_factor(response.value)
            weight = weights.get(response.key, 3)  # Default weight = 3 if not found
            
            weighted_sum += factor * weight
            total_weight += weight
        
        if total_weight == 0:
            logger.error("Total weight is zero - division by zero prevented")
            return 0.0
        
        score = weighted_sum / total_weight
        
        # Ensure score is within bounds
        score = max(0.0, min(10.0, score))
        
        return round(score, 2)
    
    @staticmethod
    def calculate_category_scores(
        responses: List[QuestionResponse],
        weights: Dict[str, int],
        question_categories: Dict[str, str]
    ) -> CategoryScores:
        """
        Calculate scores per category
        
        Args:
            responses: List of question responses
            weights: Dict of question_key -> weight
            question_categories: Dict of question_key -> category
            
        Returns:
            CategoryScores: Scores for each category
        """
        # Group responses by category
        category_responses: Dict[str, List[QuestionResponse]] = {
            "TRUST": [],
            "BEHAVIOR": [],
            "VALUES": [],
            "DYNAMICS": []
        }
        
        for response in responses:
            category = question_categories.get(response.key)
            if category and category in category_responses:
                category_responses[category].append(response)
        
        # Calculate score for each category
        scores = {}
        for category, cat_responses in category_responses.items():
            if cat_responses:
                scores[category] = ScoreCalculator.calculate_weighted_score(
                    cat_responses,
                    weights
                )
            else:
                scores[category] = 0.0
        
        return CategoryScores(**scores)
    
    @staticmethod
    def calculate_top_red_flags(
        responses: List[QuestionResponse],
        weights: Dict[str, int],
        limit: int = 5
    ) -> List[Dict[str, any]]:
        """
        Calculate top red flags by impact (factor * weight)
        
        Args:
            responses: List of question responses
            weights: Dict of question_key -> weight
            limit: Number of top red flags to return
            
        Returns:
            List of dicts with key and impact score
        """
        red_flags = []
        
        for response in responses:
            factor = ScoreCalculator.calculate_factor(response.value)
            weight = weights.get(response.key, 3)
            impact = factor * weight
            
            red_flags.append({
                "key": response.key,
                "response_value": response.value,
                "weight": weight,
                "impact": round(impact, 2)
            })
        
        # Sort by impact (descending) and take top N
        red_flags.sort(key=lambda x: x["impact"], reverse=True)
        
        return red_flags[:limit]
    
    @staticmethod
    def calculate_full_analysis(
        responses: List[QuestionResponse],
        weights: Dict[str, int],
        question_categories: Dict[str, str]
    ) -> Tuple[float, CategoryScores, List[Dict[str, any]]]:
        """
        Perform full analysis calculation
        
        Returns:
            Tuple of (total_score, category_scores, top_red_flags)
        """
        # Calculate total score
        total_score = ScoreCalculator.calculate_weighted_score(responses, weights)
        
        # Calculate category scores
        category_scores = ScoreCalculator.calculate_category_scores(
            responses,
            weights,
            question_categories
        )
        
        # Calculate top red flags
        top_red_flags = ScoreCalculator.calculate_top_red_flags(responses, weights)
        
        logger.info(f"Analysis complete: total_score={total_score}, categories={category_scores}")
        
        return total_score, category_scores, top_red_flags
