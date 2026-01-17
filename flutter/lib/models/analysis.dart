import 'package:equatable/equatable.dart';
import 'question.dart';

/// Category Scores
class CategoryScores extends Equatable {
  final double trust;
  final double behavior;
  final double values;
  final double dynamics;

  const CategoryScores({
    required this.trust,
    required this.behavior,
    required this.values,
    required this.dynamics,
  });

  factory CategoryScores.fromJson(Map<String, dynamic> json) {
    return CategoryScores(
      trust: (json['TRUST'] as num).toDouble(),
      behavior: (json['BEHAVIOR'] as num).toDouble(),
      values: (json['VALUES'] as num).toDouble(),
      dynamics: (json['DYNAMICS'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'TRUST': trust,
      'BEHAVIOR': behavior,
      'VALUES': values,
      'DYNAMICS': dynamics,
    };
  }

  @override
  List<Object> get props => [trust, behavior, values, dynamics];
}

/// Red Flag Item
class RedFlag extends Equatable {
  final String key;
  final int responseValue;
  final int weight;
  final double impact;

  const RedFlag({
    required this.key,
    required this.responseValue,
    required this.weight,
    required this.impact,
  });

  factory RedFlag.fromJson(Map<String, dynamic> json) {
    return RedFlag(
      key: json['key'] as String,
      responseValue: json['response_value'] as int,
      weight: json['weight'] as int,
      impact: (json['impact'] as num).toDouble(),
    );
  }

  @override
  List<Object> get props => [key, responseValue, weight, impact];
}

/// Analysis Model
class Analysis extends Equatable {
  final String id;
  final bool isUnlocked;
  final DateTime createdAt;
  final double? scoreTotal;
  final CategoryScores? categoryScores;
  final List<RedFlag>? topRedFlags;

  const Analysis({
    required this.id,
    required this.isUnlocked,
    required this.createdAt,
    this.scoreTotal,
    this.categoryScores,
    this.topRedFlags,
  });

  factory Analysis.fromJson(Map<String, dynamic> json) {
    return Analysis(
      id: json['_id'] as String,
      isUnlocked: json['is_unlocked'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
      scoreTotal: json['score_total'] != null 
          ? (json['score_total'] as num).toDouble()
          : null,
      categoryScores: json['category_scores'] != null
          ? CategoryScores.fromJson(json['category_scores'] as Map<String, dynamic>)
          : null,
      topRedFlags: json['top_red_flags'] != null
          ? (json['top_red_flags'] as List)
              .map((e) => RedFlag.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  bool get hasData => isUnlocked && scoreTotal != null;

  @override
  List<Object?> get props => [
        id,
        isUnlocked,
        createdAt,
        scoreTotal,
        categoryScores,
        topRedFlags,
      ];
}

/// Analysis Create Request
class AnalysisCreateRequest {
  final List<QuestionResponse> responses;

  const AnalysisCreateRequest({required this.responses});

  Map<String, dynamic> toJson() {
    return {
      'responses': responses.map((r) => r.toJson()).toList(),
    };
  }
}
