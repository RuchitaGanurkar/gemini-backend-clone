from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
