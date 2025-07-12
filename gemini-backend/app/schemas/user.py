from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.user import SubscriptionTier

class UserSignup(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    name: Optional[str] = None
    email: Optional[str] = None

class SendOTP(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')

class VerifyOTP(BaseModel):
    mobile_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp: str = Field(..., min_length=4, max_length=6)

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    mobile_number: str
    name: Optional[str]
    email: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_active: bool
    daily_message_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
