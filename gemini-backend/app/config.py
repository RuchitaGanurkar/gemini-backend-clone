from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Redis
    redis_url: str
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    # Stripe
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str
    
    # Gemini
    gemini_api_key: str
    
    # Rate Limiting
    basic_daily_limit: int = 5
    pro_daily_limit: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()
