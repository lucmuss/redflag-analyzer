"""
User Models
Pydantic models for user data validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserProfile(BaseModel):
    """User profile information"""
    age: Optional[int] = Field(None, ge=18, le=120, description="User age")
    country: Optional[str] = Field(None, max_length=2, description="ISO country code (DE, US, etc.)")
    gender: Optional[str] = Field(None, description="User gender")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 28,
                "country": "DE",
                "gender": "male"
            }
        }


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 chars)")
    
    @validator("password")
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123"
            }
        }


class UserUpdate(BaseModel):
    """Model for user profile updates"""
    profile: Optional[UserProfile] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile": {
                    "age": 30,
                    "country": "DE",
                    "gender": "male"
                }
            }
        }


class User(UserBase):
    """User model for API responses (without sensitive data)"""
    id: str = Field(alias="_id", description="User ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: bool = Field(default=False, description="Email verification status")
    profile: Optional[UserProfile] = None
    credits: int = Field(default=1, ge=0, description="Available analysis credits")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "created_at": "2024-01-15T10:00:00",
                "is_verified": True,
                "credits": 3,
                "profile": {
                    "age": 28,
                    "country": "DE",
                    "gender": "male"
                }
            }
        }


class UserInDB(User):
    """User model as stored in database (includes password hash)"""
    password_hash: str = Field(..., description="Hashed password")


class TokenData(BaseModel):
    """JWT token payload data"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
