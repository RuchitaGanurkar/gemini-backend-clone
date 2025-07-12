from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.chatroom import MessageType

class ChatroomCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ChatroomResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageSend(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    message_type: MessageType
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatroomDetailResponse(ChatroomResponse):
    messages: List[MessageResponse] = []
