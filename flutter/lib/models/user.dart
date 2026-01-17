import 'package:equatable/equatable.dart';

/// User Model
class User extends Equatable {
  final String id;
  final String email;
  final int credits;
  final UserProfile? profile;
  final DateTime createdAt;
  final bool isVerified;

  const User({
    required this.id,
    required this.email,
    required this.credits,
    this.profile,
    required this.createdAt,
    this.isVerified = false,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['_id'] as String,
      email: json['email'] as String,
      credits: json['credits'] as int? ?? 0,
      profile: json['profile'] != null
          ? UserProfile.fromJson(json['profile'] as Map<String, dynamic>)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      isVerified: json['is_verified'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      '_id': id,
      'email': email,
      'credits': credits,
      'profile': profile?.toJson(),
      'created_at': createdAt.toIso8601String(),
      'is_verified': isVerified,
    };
  }

  User copyWith({
    String? id,
    String? email,
    int? credits,
    UserProfile? profile,
    DateTime? createdAt,
    bool? isVerified,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      credits: credits ?? this.credits,
      profile: profile ?? this.profile,
      createdAt: createdAt ?? this.createdAt,
      isVerified: isVerified ?? this.isVerified,
    );
  }

  @override
  List<Object?> get props => [id, email, credits, profile, createdAt, isVerified];
}

/// User Profile
class UserProfile extends Equatable {
  final int? age;
  final String? country;
  final String? gender;

  const UserProfile({
    this.age,
    this.country,
    this.gender,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      age: json['age'] as int?,
      country: json['country'] as String?,
      gender: json['gender'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'age': age,
      'country': country,
      'gender': gender,
    };
  }

  @override
  List<Object?> get props => [age, country, gender];
}

/// Auth Response with Token
class AuthResponse extends Equatable {
  final String accessToken;
  final String tokenType;

  const AuthResponse({
    required this.accessToken,
    this.tokenType = 'bearer',
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
    );
  }

  @override
  List<Object> get props => [accessToken, tokenType];
}
