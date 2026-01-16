"""
Analysis Models
Pydantic models for analysis data validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
from .question import QuestionCategory


class QuestionResponse(BaseModel):
    """Individual question response"""
    key: str = Field(..., description="Question key")
    value: int = Field(..., ge=1, le=5, description="Response value (1-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "key": "father_absence",
                "value": 4
            }
        }


class CategoryScores(BaseModel):
    """Scores grouped by category"""
    TRUST: float = Field(..., ge=0, le=10, description="Trust category score")
    BEHAVIOR: float = Field(..., ge=0, le=10, description="Behavior category score")
    VALUES: float = Field(..., ge=0, le=10, description="Values category score")
    DYNAMICS: float = Field(..., ge=0, le=10, description="Dynamics category score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "TRUST": 5.1,
                "BEHAVIOR": 7.8,
                "VALUES": 6.0,
                "DYNAMICS": 5.9
            }
        }


class AnalysisCreate(BaseModel):
    """Model for creating a new analysis"""
    responses: List[QuestionResponse] = Field(..., min_length=1, max_length=65, description="Question responses")
    
    @validator("responses")
    def validate_unique_keys(cls, v):
        """Ensure no duplicate question keys"""
        keys = [r.key for r in v]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate question keys found in responses")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "responses": [
                    {"key": "father_absence", "value": 4},
                    {"key": "bad_father_relationship", "value": 2},
                    {"key": "feminist_blames_men", "value": 5}
                ]
            }
        }


class AnalysisBase(BaseModel):
    """Base analysis model"""
    user_id: str = Field(..., description="User ID who created the analysis")
    is_unlocked: bool = Field(default=False, description="Whether analysis is unlocked (paid)")
    responses: List[QuestionResponse] = Field(..., description="Question responses")
    snapshot_weights: Dict[str, int] = Field(..., description="Snapshot of weights used at analysis time")
    score_total: float = Field(..., ge=0, le=10, description="Total weighted score (0-10)")
    category_scores: CategoryScores = Field(..., description="Scores per category")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class Analysis(AnalysisBase):
    """Analysis model for API responses"""
    id: str = Field(alias="_id", description="Analysis ID")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "is_unlocked": True,
                "responses": [
                    {"key": "father_absence", "value": 4},
                    {"key": "bad_father_relationship", "value": 2}
                ],
                "snapshot_weights": {
                    "father_absence": 5,
                    "bad_father_relationship": 4
                },
                "score_total": 6.23,
                "category_scores": {
                    "TRUST": 5.1,
                    "BEHAVIOR": 7.8,
                    "VALUES": 6.0,
                    "DYNAMICS": 5.9
                },
                "created_at": "2024-01-15T12:00:00"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis results (may be locked)"""
    id: str = Field(alias="_id", description="Analysis ID")
    is_unlocked: bool = Field(..., description="Whether analysis is unlocked")
    created_at: datetime = Field(..., description="Creation timestamp")
    score_total: Optional[float] = Field(None, description="Total score (only if unlocked)")
    category_scores: Optional[CategoryScores] = Field(None, description="Category scores (only if unlocked)")
    top_red_flags: Optional[List[Dict[str, any]]] = Field(None, description="Top 5 red flags (only if unlocked)")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "is_unlocked": True,
                "created_at": "2024-01-15T12:00:00",
                "score_total": 6.23,
                "category_scores": {
                    "TRUST": 5.1,
                    "BEHAVIOR": 7.8,
                    "VALUES": 6.0,
                    "DYNAMICS": 5.9
                },
                "top_red_flags": [
                    {"key": "feminist_blames_men", "impact": 12.5},
                    {"key": "high_bodycount", "impact": 10.0}
                ]
            }
        }


class UnlockAnalysisRequest(BaseModel):
    """Request to unlock an analysis"""
    analysis_id: str = Field(..., description="Analysis ID to unlock")
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": "507f1f77bcf86cd799439011"
            }
        }
