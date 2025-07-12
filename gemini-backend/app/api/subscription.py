from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, SubscriptionTier
from app.models.subscription import Subscription
from app.middleware.auth_middleware import get_current_user
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/subscribe", tags=["Subscription"])

@router.post("/pro")
def create_pro_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user already has a pro subscription
    if current_user.subscription_tier == SubscriptionTier.PRO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a Pro subscription"
        )
    
    # Create Stripe customer if not exists
    if not current_user.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email or f"{current_user.mobile_number}@example.com",
            mobile_number=current_user.mobile_number
        )
        current_user.stripe_customer_id = customer.id
        db.commit()
    
    # Create checkout session
    try:
        checkout_session = stripe_service.create_checkout_session(
            customer_id=current_user.stripe_customer_id,
            success_url="https://your-domain.com/success",
            cancel_url="https://your-domain.com/cancel"
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.get("/status")
def get_subscription_status(current_user: User = Depends(get_current_user)):
    return {
        "subscription_tier": current_user.subscription_tier,
        "subscription_active": current_user.subscription_active,
        "daily_message_count": current_user.daily_message_count,
        "daily_limit": 5 if current_user.subscription_tier == SubscriptionTier.BASIC else 1000
    }
