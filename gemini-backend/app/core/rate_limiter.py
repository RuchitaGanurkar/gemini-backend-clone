from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, SubscriptionTier
from app.config import settings

def check_rate_limit(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    today = datetime.utcnow().date()
    
    # Reset counter if it's a new day
    if not user.last_message_date or user.last_message_date.date() != today:
        user.daily_message_count = 0
        user.last_message_date = datetime.utcnow()
        db.commit()
    
    # Check limits based on subscription tier
    if user.subscription_tier == SubscriptionTier.BASIC:
        return user.daily_message_count < settings.basic_daily_limit
    elif user.subscription_tier == SubscriptionTier.PRO:
        return user.daily_message_count < settings.pro_daily_limit
    
    return False

def increment_message_count(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.daily_message_count += 1
        user.last_message_date = datetime.utcnow()
        db.commit()
