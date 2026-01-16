"""
Question Models
Pydantic models for question data validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class QuestionCategory(str, Enum):
    """Question categories for grouping"""
    TRUST = "TRUST"
    BEHAVIOR = "BEHAVIOR"
    VALUES = "VALUES"
    DYNAMICS = "DYNAMICS"


class QuestionBase(BaseModel):
    """Base question model"""
    key: str = Field(..., description="Unique question identifier (snake_case)")
    category: QuestionCategory = Field(..., description="Question category")
    default_weight: int = Field(default=3, ge=1, le=5, description="Default importance weight (1-5)")
    
    class Config:
        use_enum_values = True


class QuestionCreate(QuestionBase):
    """Model for creating new questions"""
    pass


class Question(QuestionBase):
    """Question model for API responses"""
    id: str = Field(alias="_id", description="Question ID")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "key": "father_absence",
                "category": "DYNAMICS",
                "default_weight": 5
            }
        }


class QuestionWithText(Question):
    """Question model with localized text (from Flutter app)"""
    text_de: Optional[str] = Field(None, description="German question text")
    text_en: Optional[str] = Field(None, description="English question text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "key": "father_absence",
                "category": "DYNAMICS",
                "default_weight": 5,
                "text_de": "Sie ist zum größten Teil in ihrem Leben ohne biologischen Vater aufgewachsen.",
                "text_en": "She grew up mostly without her biological father."
            }
        }
