"""
Authentication Service
Handles user registration, login, and token management
"""
from typing import Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.models.user import UserCreate, UserInDB, Token, LoginRequest
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> UserInDB:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            UserInDB: Created user with hashed password
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = await self.db.users.find_one({"email": user_data.email})
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "is_verified": False,
            "profile": None,
            "credits": 1  # Initial free credit
        }
        
        # Insert into database
        result = await self.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        logger.info(f"New user registered: {user_data.email} (ID: {result.inserted_id})")
        
        # Log credit transaction
        await self._log_credit_transaction(
            user_id=str(result.inserted_id),
            transaction_type="signup_bonus",
            amount=1,
            balance_after=1,
            description="Welcome bonus - 1 free analysis"
        )
        
        return UserInDB(**user_doc)
    
    async def authenticate_user(self, login_data: LoginRequest) -> Optional[UserInDB]:
        """
        Authenticate user with email and password
        
        Args:
            login_data: Login credentials
            
        Returns:
            UserInDB if authentication successful, None otherwise
        """
        # Find user by email
        user_doc = await self.db.users.find_one({"email": login_data.email})
        
        if not user_doc:
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            return None
        
        # Verify password
        if not verify_password(login_data.password, user_doc["password_hash"]):
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            return None
        
        logger.info(f"Successful login: {login_data.email}")
        return UserInDB(**user_doc)
    
    async def create_access_token_for_user(self, user: UserInDB) -> Token:
        """
        Create JWT access token for authenticated user
        
        Args:
            user: Authenticated user
            
        Returns:
            Token: JWT access token
        """
        token_data = {
            "sub": user.email,
            "user_id": str(user.id)
        }
        
        access_token = create_access_token(token_data)
        
        return Token(access_token=access_token)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            UserInDB if found, None otherwise
        """
        user_doc = await self.db.users.find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            UserInDB if found, None otherwise
        """
        try:
            user_doc = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(**user_doc)
        except Exception as e:
            logger.error(f"Error fetching user by ID {user_id}: {e}")
        
        return None
    
    async def update_user_profile(self, user_id: str, profile_data: dict) -> bool:
        """
        Update user profile
        
        Args:
            user_id: User ID
            profile_data: Profile data to update
            
        Returns:
            bool: True if successful
        """
        try:
            result = await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile": profile_data}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Profile updated for user {user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
        
        return False
    
    async def _log_credit_transaction(
        self,
        user_id: str,
        transaction_type: str,
        amount: int,
        balance_after: int,
        description: str,
        metadata: Optional[dict] = None
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
        
        await self.db.credit_transactions.insert_one(transaction_doc)
