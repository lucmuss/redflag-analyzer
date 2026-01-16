"""
Users Routes
Endpoints for user profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.user import User, UserUpdate
from app.routes.auth import get_current_user_dependency
from app.services.auth_service import AuthService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get current user's full profile
    
    Returns user data including email, credits, and profile details
    """
    return current_user


@router.put("/me", response_model=User)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update current user's profile
    
    - **profile**: Profile data (age, country, gender)
    
    Example: {"profile": {"age": 30, "country": "DE", "gender": "male"}}
    """
    auth_service = AuthService(db)
    
    try:
        # Update profile
        if user_update.profile:
            success = await auth_service.update_user_profile(
                user_id=current_user.id,
                profile_data=user_update.profile.dict(exclude_none=True)
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update profile"
                )
        
        # Fetch updated user
        updated_user = await auth_service.get_user_by_id(current_user.id)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Profile updated for user {current_user.id}")
        
        # Return user without password_hash
        return User(
            _id=str(updated_user.id),
            email=updated_user.email,
            created_at=updated_user.created_at,
            is_verified=updated_user.is_verified,
            profile=updated_user.profile,
            credits=updated_user.credits
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
