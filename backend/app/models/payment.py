"""
Payment Models
Pydantic models for payment and credit transactions
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Credit transaction types"""
    SIGNUP_BONUS = "signup_bonus"  # Initial free credit
    PURCHASE = "purchase"  # IAP or Stripe purchase
    UNLOCK_ANALYSIS = "unlock_analysis"  # Spend credit to unlock
    REFUND = "refund"  # Credit refund
    ADMIN_ADJUSTMENT = "admin_adjustment"  # Manual adjustment


class CreditTransaction(BaseModel):
    """Credit transaction record"""
    id: str = Field(alias="_id", description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    type: TransactionType = Field(..., description="Transaction type")
    amount: int = Field(..., description="Credit amount (+/-)")
    balance_after: int = Field(..., ge=0, description="Credit balance after transaction")
    description: Optional[str] = Field(None, description="Transaction description")
    metadata: Optional[dict] = Field(None, description="Additional metadata (e.g., analysis_id, payment_id)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "type": "purchase",
                "amount": 1,
                "balance_after": 3,
                "description": "Purchased 1 analysis credit",
                "metadata": {
                    "payment_id": "pi_1234567890",
                    "amount_paid": 5.00,
                    "currency": "EUR"
                },
                "created_at": "2024-01-15T12:00:00"
            }
        }


class PurchaseCreditsRequest(BaseModel):
    """Request to purchase credits"""
    quantity: int = Field(default=1, ge=1, le=10, description="Number of credits to purchase")
    payment_method: str = Field(default="stripe", description="Payment method (stripe, iap_apple, iap_google)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 1,
                "payment_method": "stripe"
            }
        }


class StripeWebhookPayload(BaseModel):
    """Stripe webhook payload"""
    event_type: str = Field(..., description="Stripe event type")
    payment_intent_id: str = Field(..., description="Payment intent ID")
    customer_email: Optional[str] = Field(None, description="Customer email")
    amount: float = Field(..., description="Amount paid")
    currency: str = Field(default="eur", description="Currency code")
    metadata: Optional[dict] = Field(None, description="Custom metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "payment_intent.succeeded",
                "payment_intent_id": "pi_1234567890",
                "customer_email": "user@example.com",
                "amount": 5.00,
                "currency": "eur",
                "metadata": {
                    "user_id": "507f1f77bcf86cd799439012",
                    "quantity": 1
                }
            }
        }
