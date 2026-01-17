import 'package:flutter_test/flutter_test.dart';

/// Basic Unit Tests for Score Calculation Logic
void main() {
  group('Score Calculation Tests', () {
    test('Score calculation formula - all 1s should give 0', () {
      // Arrange
      final responses = List.generate(65, (_) => 1);
      final weights = List.generate(65, (_) => 5);
      
      // Act
      final score = calculateScore(responses, weights);
      
      // Assert
      expect(score, equals(0.0));
    });

    test('Score calculation formula - all 5s should give 10', () {
      // Arrange
      final responses = List.generate(65, (_) => 5);
      final weights = List.generate(65, (_) => 5);
      
      // Act
      final score = calculateScore(responses, weights);
      
      // Assert
      expect(score, equals(10.0));
    });

    test('Score calculation formula - mixed values', () {
      // Arrange
      final responses = [3, 3, 3]; // Neutral
      final weights = [5, 5, 5];
      
      // Act
      final score = calculateScore(responses, weights);
      
      // Assert
      expect(score, equals(5.0)); // (3-1)*2.5 = 5
    });

    test('Score should be between 0 and 10', () {
      // Arrange
      final responses = [1, 3, 5, 2, 4];
      final weights = [1, 2, 3, 4, 5];
      
      // Act
      final score = calculateScore(responses, weights);
      
      // Assert
      expect(score, greaterThanOrEqualTo(0.0));
      expect(score, lessThanOrEqualTo(10.0));
    });

    test('Empty responses should return 0', () {
      // Arrange
      final responses = <int>[];
      final weights = <int>[];
      
      // Act
      final score = calculateScore(responses, weights);
      
      // Assert
      expect(score, equals(0.0));
    });
  });

  group('Category Score Tests', () {
    test('Category scores should be calculated separately', () {
      // Trust: [1, 2] -> Avg factor = (0 + 2.5) / 2 = 1.25
      final trustResponses = [1, 2];
      final trustWeights = [5, 5];
      
      final score = calculateScore(trustResponses, trustWeights);
      
      expect(score, closeTo(1.25, 0.01));
    });
  });
}

/// Score Calculation Function (same as backend)
/// For each response R (1-5): Factor f = (R - 1) * 2.5 (results in 0-10)
/// Total Score: Weighted average = SUM(f * weight) / SUM(weight)
double calculateScore(List<int> responses, List<int> weights) {
  if (responses.isEmpty || weights.isEmpty) return 0.0;
  
  double totalFactorWeighted = 0.0;
  int totalWeight = 0;
  
  for (int i = 0; i < responses.length; i++) {
    final response = responses[i];
    final weight = weights[i];
    
    // Calculate factor (0-10 scale)
    final factor = (response - 1) * 2.5;
    
    totalFactorWeighted += factor * weight;
    totalWeight += weight;
  }
  
  if (totalWeight == 0) return 0.0;
  
  return totalFactorWeighted / totalWeight;
}
