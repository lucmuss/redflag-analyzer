"""
Unit Tests for Score Calculator
Tests the core scoring algorithm and edge cases
"""
import pytest
from app.services.score_calculator import ScoreCalculator
from app.models.analysis import QuestionResponse, CategoryScores


class TestScoreCalculator:
    """Test suite for ScoreCalculator"""
    
    def test_calculate_factor_min_value(self):
        """Test factor calculation with minimum response value (1)"""
        factor = ScoreCalculator.calculate_factor(1)
        assert factor == 0.0, "Response value 1 should result in factor 0.0"
    
    def test_calculate_factor_max_value(self):
        """Test factor calculation with maximum response value (5)"""
        factor = ScoreCalculator.calculate_factor(5)
        assert factor == 10.0, "Response value 5 should result in factor 10.0"
    
    def test_calculate_factor_middle_value(self):
        """Test factor calculation with middle response value (3)"""
        factor = ScoreCalculator.calculate_factor(3)
        assert factor == 5.0, "Response value 3 should result in factor 5.0"
    
    def test_calculate_factor_progression(self):
        """Test factor calculation progression (1-5)"""
        expected = [0.0, 2.5, 5.0, 7.5, 10.0]
        for response_value in range(1, 6):
            factor = ScoreCalculator.calculate_factor(response_value)
            assert factor == expected[response_value - 1], \
                f"Response {response_value} should give factor {expected[response_value - 1]}"
    
    def test_calculate_factor_out_of_range_high(self):
        """Test factor calculation with value > 5 (should clamp to 5)"""
        factor = ScoreCalculator.calculate_factor(10)
        assert factor == 10.0, "Out of range values should be clamped to max (5 -> 10.0)"
    
    def test_calculate_factor_out_of_range_low(self):
        """Test factor calculation with value < 1 (should clamp to 1)"""
        factor = ScoreCalculator.calculate_factor(0)
        assert factor == 0.0, "Out of range values should be clamped to min (1 -> 0.0)"
    
    def test_calculate_weighted_score_simple(self):
        """Test weighted score calculation with simple example"""
        responses = [
            QuestionResponse(key="q1", value=5),  # factor=10, weight=4 -> 40
            QuestionResponse(key="q2", value=1),  # factor=0,  weight=2 -> 0
        ]
        weights = {"q1": 4, "q2": 2}
        
        # Expected: (40 + 0) / (4 + 2) = 40 / 6 = 6.67
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert abs(score - 6.67) < 0.01, f"Expected ~6.67, got {score}"
    
    def test_calculate_weighted_score_all_ones(self):
        """Test weighted score when all responses are 1 (no red flags)"""
        responses = [
            QuestionResponse(key="q1", value=1),
            QuestionResponse(key="q2", value=1),
            QuestionResponse(key="q3", value=1),
        ]
        weights = {"q1": 3, "q2": 3, "q3": 3}
        
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert score == 0.0, "All response value 1 should give score 0.0"
    
    def test_calculate_weighted_score_all_fives(self):
        """Test weighted score when all responses are 5 (maximum red flags)"""
        responses = [
            QuestionResponse(key="q1", value=5),
            QuestionResponse(key="q2", value=5),
            QuestionResponse(key="q3", value=5),
        ]
        weights = {"q1": 3, "q2": 3, "q3": 3}
        
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert score == 10.0, "All response value 5 should give score 10.0"
    
    def test_calculate_weighted_score_mixed_weights(self):
        """Test weighted score with different weights"""
        responses = [
            QuestionResponse(key="high_weight", value=5),   # factor=10, weight=5 -> 50
            QuestionResponse(key="low_weight", value=5),    # factor=10, weight=1 -> 10
        ]
        weights = {"high_weight": 5, "low_weight": 1}
        
        # Expected: (50 + 10) / (5 + 1) = 60 / 6 = 10.0
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert score == 10.0, f"Expected 10.0, got {score}"
    
    def test_calculate_weighted_score_default_weight(self):
        """Test that missing weights default to 3"""
        responses = [
            QuestionResponse(key="unknown_key", value=3),  # factor=5, default_weight=3 -> 15
        ]
        weights = {}  # No weights defined
        
        # Expected: (5 * 3) / 3 = 5.0
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert score == 5.0, f"Expected 5.0 with default weight, got {score}"
    
    def test_calculate_weighted_score_empty_responses(self):
        """Test edge case: empty responses list"""
        responses = []
        weights = {}
        
        score = ScoreCalculator.calculate_weighted_score(responses, weights)
        assert score == 0.0, "Empty responses should return 0.0"
    
    def test_calculate_category_scores(self):
        """Test category score calculation"""
        responses = [
            QuestionResponse(key="trust1", value=5),
            QuestionResponse(key="trust2", value=3),
            QuestionResponse(key="behavior1", value=4),
            QuestionResponse(key="values1", value=2),
        ]
        
        weights = {
            "trust1": 5,
            "trust2": 3,
            "behavior1": 4,
            "values1": 2,
        }
        
        question_categories = {
            "trust1": "TRUST",
            "trust2": "TRUST",
            "behavior1": "BEHAVIOR",
            "values1": "VALUES",
        }
        
        category_scores = ScoreCalculator.calculate_category_scores(
            responses, weights, question_categories
        )
        
        assert isinstance(category_scores, CategoryScores)
        
        # Trust: (10*5 + 5*3) / (5+3) = 65/8 = 8.125 -> 8.12
        assert abs(category_scores.TRUST - 8.12) < 0.01
        
        # Behavior: (7.5*4) / 4 = 7.5
        assert abs(category_scores.BEHAVIOR - 7.5) < 0.01
        
        # Values: (2.5*2) / 2 = 2.5
        assert abs(category_scores.VALUES - 2.5) < 0.01
        
        # Dynamics: No responses -> 0.0
        assert category_scores.DYNAMICS == 0.0
    
    def test_calculate_top_red_flags(self):
        """Test top red flags calculation"""
        responses = [
            QuestionResponse(key="flag1", value=5),  # impact = 10 * 5 = 50
            QuestionResponse(key="flag2", value=4),  # impact = 7.5 * 3 = 22.5
            QuestionResponse(key="flag3", value=3),  # impact = 5 * 2 = 10
            QuestionResponse(key="flag4", value=5),  # impact = 10 * 4 = 40
        ]
        
        weights = {
            "flag1": 5,
            "flag2": 3,
            "flag3": 2,
            "flag4": 4,
        }
        
        top_flags = ScoreCalculator.calculate_top_red_flags(responses, weights, limit=3)
        
        assert len(top_flags) == 3, "Should return top 3 flags"
        assert top_flags[0]["key"] == "flag1", "Highest impact should be first"
        assert top_flags[0]["impact"] == 50.0
        assert top_flags[1]["key"] == "flag4"
        assert top_flags[1]["impact"] == 40.0
        assert top_flags[2]["key"] == "flag2"
        assert abs(top_flags[2]["impact"] - 22.5) < 0.01
    
    def test_calculate_full_analysis(self):
        """Test full analysis calculation (integration test)"""
        responses = [
            QuestionResponse(key="trust1", value=5),
            QuestionResponse(key="behavior1", value=3),
            QuestionResponse(key="values1", value=4),
        ]
        
        weights = {
            "trust1": 5,
            "behavior1": 3,
            "values1": 4,
        }
        
        question_categories = {
            "trust1": "TRUST",
            "behavior1": "BEHAVIOR",
            "values1": "VALUES",
        }
        
        total_score, category_scores, top_red_flags = ScoreCalculator.calculate_full_analysis(
            responses, weights, question_categories
        )
        
        # Verify total score
        # (10*5 + 5*3 + 7.5*4) / (5+3+4) = (50+15+30) / 12 = 95/12 = 7.92
        assert abs(total_score - 7.92) < 0.01, f"Expected ~7.92, got {total_score}"
        
        # Verify category scores exist
        assert isinstance(category_scores, CategoryScores)
        assert category_scores.TRUST == 10.0  # (10*5)/5
        assert category_scores.BEHAVIOR == 5.0  # (5*3)/3
        assert abs(category_scores.VALUES - 7.5) < 0.01  # (7.5*4)/4
        assert category_scores.DYNAMICS == 0.0  # No responses
        
        # Verify top red flags
        assert len(top_red_flags) > 0
        assert top_red_flags[0]["key"] == "trust1"  # Highest impact


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
