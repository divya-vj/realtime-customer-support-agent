from sqlalchemy.orm import Session
from app.models.database import Conversation, Message
from datetime import datetime

class ChatService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(self, session_id: str, customer_name: str = None):
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                customer_name=customer_name,
                created_at=datetime.utcnow(),
                status="active"
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
        
        return conversation
    
    def save_message(self, session_id: str, role: str, content: str, 
                    sentiment_score: float = None, sentiment_label: str = None):
        conversation = self.get_or_create_conversation(session_id)
        
        message = Message(
            conversation_id=conversation.id,
            session_id=session_id,
            role=role,
            content=content,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(message)
        self.db.commit()
        return message