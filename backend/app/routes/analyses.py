"""
Analysis Routes
Endpoints for creating and managing relationship analyses
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.analysis import AnalysisCreate, Analysis, AnalysisResponse, UnlockAnalysisRequest
from app.models.user import User
from app.routes.auth import get_current_user_dependency
from app.services.score_calculator import ScoreCalculator
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new relationship analysis
    
    - **responses**: List of question responses (1-65 questions)
    
    The analysis will be created but locked (is_unlocked=False) until user unlocks it with a credit.
    First-time users have 1 free credit from signup bonus.
    """
    try:
        # Fetch all questions to get categories and weights
        questions_cursor = db.questions.find({})
        questions_docs = await questions_cursor.to_list(length=100)
        
        # Build lookup dicts
        question_categories = {doc["key"]: doc["category"] for doc in questions_docs}
        default_weights = {doc["key"]: doc.get("default_weight", 3) for doc in questions_docs}
        
        # TODO: In future, use user-specific or community-aggregated weights
        # For now, use default weights from questions
        snapshot_weights = default_weights.copy()
        
        # Calculate scores using ScoreCalculator
        total_score, category_scores, top_red_flags = ScoreCalculator.calculate_full_analysis(
            responses=analysis_data.responses,
            weights=snapshot_weights,
            question_categories=question_categories
        )
        
        # Create analysis document
        analysis_doc = {
            "user_id": current_user.id,
            "is_unlocked": False,  # Locked by default
            "responses": [r.dict() for r in analysis_data.responses],
            "snapshot_weights": snapshot_weights,
            "score_total": total_score,
            "category_scores": category_scores.dict(),
            "top_red_flags": top_red_flags,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.analyses.insert_one(analysis_doc)
        analysis_id = str(result.inserted_id)
        
        logger.info(f"Analysis created: {analysis_id} for user {current_user.id}")
        
        # Return locked response (no scores visible)
        return AnalysisResponse(
            _id=analysis_id,
            is_unlocked=False,
            created_at=analysis_doc["created_at"],
            score_total=None,
            category_scores=None,
            top_red_flags=None
        )
    
    except Exception as e:
        logger.error(f"Error creating analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create analysis"
        )


@router.post("/{analysis_id}/unlock", response_model=AnalysisResponse)
async def unlock_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Unlock an analysis using 1 credit
    
    - **analysis_id**: ID of the analysis to unlock
    
    Requires 1 credit. After unlocking, full results including scores, 
    category breakdown, and top red flags are revealed.
    """
    try:
        # Fetch analysis
        analysis_doc = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
        
        if not analysis_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # Check ownership
        if analysis_doc["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to unlock this analysis"
            )
        
        # Check if already unlocked
        if analysis_doc.get("is_unlocked", False):
            logger.info(f"Analysis {analysis_id} already unlocked")
            # Return full data
            return _build_analysis_response(analysis_doc, unlocked=True)
        
        # Check user credits
        if current_user.credits < 1:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient credits. Purchase credits to unlock analysis."
            )
        
        # Deduct credit
        new_balance = current_user.credits - 1
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"credits": new_balance}}
        )
        
        # Unlock analysis
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": {"is_unlocked": True}}
        )
        
        # Log transaction
        await _log_credit_transaction(
            db=db,
            user_id=current_user.id,
            transaction_type="unlock_analysis",
            amount=-1,
            balance_after=new_balance,
            description=f"Unlocked analysis {analysis_id}",
            metadata={"analysis_id": analysis_id}
        )
        
        logger.info(f"Analysis {analysis_id} unlocked by user {current_user.id}. New balance: {new_balance}")
        
        # Return full data
        analysis_doc["is_unlocked"] = True
        return _build_analysis_response(analysis_doc, unlocked=True)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock analysis"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a specific analysis by ID
    
    Returns full data if unlocked, otherwise only metadata
    """
    try:
        analysis_doc = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
        
        if not analysis_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # Check ownership
        if analysis_doc["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this analysis"
            )
        
        is_unlocked = analysis_doc.get("is_unlocked", False)
        return _build_analysis_response(analysis_doc, unlocked=is_unlocked)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis"
        )


@router.get("", response_model=List[AnalysisResponse])
async def get_user_analyses(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = 10,
    skip: int = 0
):
    """
    Get all analyses for current user
    
    - **limit**: Maximum number of results (default: 10)
    - **skip**: Number of results to skip for pagination (default: 0)
    
    Returns analyses sorted by creation date (newest first)
    """
    try:
        cursor = db.analyses.find({"user_id": current_user.id}).sort("created_at", -1).skip(skip).limit(limit)
        analyses_docs = await cursor.to_list(length=limit)
        
        results = []
        for doc in analyses_docs:
            is_unlocked = doc.get("is_unlocked", False)
            results.append(_build_analysis_response(doc, unlocked=is_unlocked))
        
        logger.info(f"Retrieved {len(results)} analyses for user {current_user.id}")
        return results
    
    except Exception as e:
        logger.error(f"Error fetching user analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analyses"
        )


# Helper functions
def _build_analysis_response(analysis_doc: dict, unlocked: bool) -> AnalysisResponse:
    """Build AnalysisResponse from database document"""
    from app.models.analysis import CategoryScores
    
    if unlocked:
        return AnalysisResponse(
            _id=str(analysis_doc["_id"]),
            is_unlocked=True,
            created_at=analysis_doc["created_at"],
            score_total=analysis_doc.get("score_total"),
            category_scores=CategoryScores(**analysis_doc.get("category_scores", {})),
            top_red_flags=analysis_doc.get("top_red_flags")
        )
    else:
        return AnalysisResponse(
            _id=str(analysis_doc["_id"]),
            is_unlocked=False,
            created_at=analysis_doc["created_at"],
            score_total=None,
            category_scores=None,
            top_red_flags=None
        )


async def _log_credit_transaction(
    db: AsyncIOMotorDatabase,
    user_id: str,
    transaction_type: str,
    amount: int,
    balance_after: int,
    description: str,
    metadata: dict = None
):
    """Log a credit transaction"""
    transaction_doc = {
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "balance_after": balance_after,
        "description": description,
        "metadata": metadata or {},
        "created_at": datetime.utcnow()
    }
    
    await db.credit_transactions.insert_one(transaction_doc)
