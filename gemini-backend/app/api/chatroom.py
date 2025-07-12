from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.chatroom import Chatroom, Message, MessageType
from app.models.user import User
from app.schemas.chatroom import ChatroomCreate, ChatroomResponse, ChatroomDetailResponse, MessageSend, MessageResponse
from app.middleware.auth_middleware import get_current_user
from app.core.cache import cache
from app.core.rate_limiter import check_rate_limit, increment_message_count
from app.tasks.gemini_tasks import process_gemini_message

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])

@router.post("", response_model=ChatroomResponse)
def create_chatroom(
    chatroom_data: ChatroomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatroom = Chatroom(
        title=chatroom_data.title,
        description=chatroom_data.description,
        owner_id=current_user.id
    )
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    
    # Clear cache for user's chatrooms
    cache.delete(f"chatrooms:user:{current_user.id}")
    
    return chatroom

@router.get("", response_model=List[ChatroomResponse])
def get_user_chatrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check cache first
    cache_key = f"chatrooms:user:{current_user.id}"
    cached_chatrooms = cache.get(cache_key)
    
    if cached_chatrooms:
        return cached_chatrooms
    
    # Query database
    chatrooms = db.query(Chatroom).filter(Chatroom.owner_id == current_user.id).all()
    chatroom_list = [ChatroomResponse.from_orm(chatroom) for chatroom in chatrooms]
    
    # Cache for 5 minutes (300 seconds)
    cache.set(cache_key, [chatroom.dict() for chatroom in chatroom_list], ttl=300)
    
    return chatroom_list

@router.get("/{chatroom_id}", response_model=ChatroomDetailResponse)
def get_chatroom_detail(
    chatroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.owner_id == current_user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Get messages for this chatroom
    messages = db.query(Message).filter(Message.chatroom_id == chatroom_id).all()
    
    return ChatroomDetailResponse(
        **chatroom.__dict__,
        messages=[MessageResponse.from_orm(msg) for msg in messages]
    )

@router.post("/{chatroom_id}/message", response_model=MessageResponse)
def send_message(
    chatroom_id: int,
    message_data: MessageSend,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if chatroom exists and belongs to user
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.owner_id == current_user.id
    ).first()
    
    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )
    
    # Check rate limit
    if not check_rate_limit(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily message limit exceeded. Upgrade to Pro for unlimited messages."
        )
    
    # Save user message
    user_message = Message(
        chatroom_id=chatroom_id,
        content=message_data.content,
        message_type=MessageType.USER
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Increment message count
    increment_message_count(db, current_user.id)
    
    # Process AI response asynchronously
    background_tasks.add_task(
        process_gemini_message.delay,
        chatroom_id,
        message_data.content
    )
    
    return user_message
