import 'package:equatable/equatable.dart';

/// Question Category
enum QuestionCategory {
  trust('TRUST'),
  behavior('BEHAVIOR'),
  valuesCategory('VALUES'),  // Renamed from 'values' (reserved word)
  dynamics('DYNAMICS');

  final String value;
  const QuestionCategory(this.value);

  static QuestionCategory fromString(String value) {
    return QuestionCategory.values.firstWhere(
      (e) => e.value == value.toUpperCase(),
      orElse: () => QuestionCategory.trust,
    );
  }
}

/// Question Model
class Question extends Equatable {
  final String id;
  final String key;
  final QuestionCategory category;
  final int defaultWeight;

  const Question({
    required this.id,
    required this.key,
    required this.category,
    this.defaultWeight = 3,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['_id'] as String,
      key: json['key'] as String,
      category: QuestionCategory.fromString(json['category'] as String),
      defaultWeight: json['default_weight'] as int? ?? 3,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      '_id': id,
      'key': key,
      'category': category.value,
      'default_weight': defaultWeight,
    };
  }

  @override
  List<Object> get props => [id, key, category, defaultWeight];
}

/// Question Response (user's answer to a question)
class QuestionResponse extends Equatable {
  final String key;
  final int value; // 1-5

  const QuestionResponse({
    required this.key,
    required this.value,
  });

  factory QuestionResponse.fromJson(Map<String, dynamic> json) {
    return QuestionResponse(
      key: json['key'] as String,
      value: json['value'] as int,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'key': key,
      'value': value,
    };
  }

  @override
  List<Object> get props => [key, value];
}
