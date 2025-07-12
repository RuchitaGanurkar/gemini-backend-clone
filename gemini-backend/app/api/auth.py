from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserSignup, SendOTP, VerifyOTP, ChangePassword, UserResponse, Token
from app.core.security import create_access_token, get_password_hash, verify_password
from app.services.otp_service import otp_service
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.mobile_number == user_data.mobile_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists"
        )
    
    # Create new user
    user = User(
        mobile_number=user_data.mobile_number,
        name=user_data.name,
        email=user_data.email
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/send-otp")
def send_otp(otp_data: SendOTP, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.mobile_number == otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate and return OTP (in real implementation, this would be sent via SMS)
    otp = otp_service.generate_otp(otp_data.mobile_number)
    
    return {
        "message": "OTP sent successfully",
        "otp": otp,  # In production, remove this line
        "mobile_number": otp_data.mobile_number
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(otp_data: VerifyOTP, db: Session = Depends(get_db)):
    # Verify OTP
    if not otp_service.verify_otp(otp_data.mobile_number, otp_data.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Get user
    user = db.query(User).filter(User.mobile_number == otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(otp_data: SendOTP, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.mobile_number == otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate and return OTP for password reset
    otp = otp_service.generate_otp(f"reset:{otp_data.mobile_number}")
    
    return {
        "message": "Password reset OTP sent successfully",
        "otp": otp,  # In production, remove this line
        "mobile_number": otp_data.mobile_number
    }

@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify old password if it exists
    if current_user.password_hash and not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
