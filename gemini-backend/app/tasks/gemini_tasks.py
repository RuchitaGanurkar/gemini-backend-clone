from celery import Celery
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.chatroom import Message, MessageType
from app.services.gemini_service import gemini_service
from app.config import settings

celery_app = Celery(
    "gemini_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

@celery_app.task
def process_gemini_message(chatroom_id: int, user_message: str):
    db = SessionLocal()
    try:
        # Generate AI response
        ai_response = gemini_service.generate_response(user_message)
        
        # Save AI response to database
        ai_message = Message(
            chatroom_id=chatroom_id,
            content=ai_response,
            message_type=MessageType.ASSISTANT
        )
        db.add(ai_message)
        db.commit()
        
        return {"status": "success", "response": ai_response}
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
