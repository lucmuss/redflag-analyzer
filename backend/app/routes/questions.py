"""
Questions Routes
Endpoints for fetching questions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.question import Question
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=List[Question])
async def get_all_questions(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all questions
    
    Returns all 65 questions with their keys, categories, and default weights.
    Question texts (DE/EN) are stored in the Flutter app for i18n.
    
    Questions are grouped by category:
    - TRUST: Trust and reliability issues
    - BEHAVIOR: Behavioral patterns
    - VALUES: Core values and beliefs
    - DYNAMICS: Relationship dynamics
    """
    try:
        # Fetch all questions from database
        cursor = db.questions.find({})
        questions_docs = await cursor.to_list(length=100)
        
        # Convert to Question models
        questions = []
        for doc in questions_docs:
            questions.append(Question(
                _id=str(doc["_id"]),
                key=doc["key"],
                category=doc["category"],
                default_weight=doc.get("default_weight", 3)
            ))
        
        logger.info(f"Retrieved {len(questions)} questions")
        return questions
    
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch questions"
        )


@router.get("/{question_key}", response_model=Question)
async def get_question_by_key(
    question_key: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a specific question by its key
    
    - **question_key**: Unique question identifier (e.g., "father_absence")
    """
    try:
        doc = await db.questions.find_one({"key": question_key})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with key '{question_key}' not found"
            )
        
        return Question(
            _id=str(doc["_id"]),
            key=doc["key"],
            category=doc["category"],
            default_weight=doc.get("default_weight", 3)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching question {question_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch question"
        )


@router.get("/category/{category}", response_model=List[Question])
async def get_questions_by_category(
    category: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all questions for a specific category
    
    - **category**: TRUST, BEHAVIOR, VALUES, or DYNAMICS
    """
    # Validate category
    valid_categories = ["TRUST", "BEHAVIOR", "VALUES", "DYNAMICS"]
    if category.upper() not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    try:
        cursor = db.questions.find({"category": category.upper()})
        questions_docs = await cursor.to_list(length=100)
        
        questions = []
        for doc in questions_docs:
            questions.append(Question(
                _id=str(doc["_id"]),
                key=doc["key"],
                category=doc["category"],
                default_weight=doc.get("default_weight", 3)
            ))
        
        logger.info(f"Retrieved {len(questions)} questions for category {category}")
        return questions
    
    except Exception as e:
        logger.error(f"Error fetching questions for category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch questions"
        )
