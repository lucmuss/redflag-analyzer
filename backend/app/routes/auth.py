"""
Authentication Routes
Endpoints for user registration and login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.models.user import UserCreate, User, LoginRequest, Token
from app.services.auth_service import AuthService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters, must contain letters and digits
    
    Returns the created user with 1 free credit
    """
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.register_user(user_data)
        
        # Return user without password_hash
        return User(
            _id=str(user.id),
            email=user.email,
            created_at=user.created_at,
            is_verified=user.is_verified,
            profile=user.profile,
            credits=user.credits
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login with email and password
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT access token valid for 60 minutes
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    token = await auth_service.create_access_token_for_user(user)
    
    return token


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Get current authenticated user info
    
    Requires valid JWT token in Authorization header
    """
    return current_user


# Dependency for protected routes
async def get_current_user_dependency(
    db: AsyncIOMotorDatabase = Depends(get_database),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    from app.utils.security import decode_access_token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Decode token
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    # Get user from database
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(token_data.email)
    
    if user is None:
        raise credentials_exception
    
    # Return user without password_hash
    return User(
        _id=str(user.id),
        email=user.email,
        created_at=user.created_at,
        is_verified=user.is_verified,
        profile=user.profile,
        credits=user.credits
    )


# OAuth2 scheme for token extraction
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
