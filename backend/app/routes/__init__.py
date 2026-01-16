"""
API Routes
"""
from .auth import router as auth_router
from .questions import router as questions_router
from .analyses import router as analyses_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "questions_router",
    "analyses_router",
    "users_router",
]
