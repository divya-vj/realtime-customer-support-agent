from sqlalchemy.orm import Session
from app.models.database import Conversation, Message
from datetime import datetime

class ChatService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_conversation(self, session_id: str, customer_name: str = None):
        """Get existing conversation or create new one"""
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
        """Save a message to database"""
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
        
        # Update conversation average sentiment
        if sentiment_score is not None and role == "user":
            self.update_conversation_sentiment(conversation.id)
        
        return message
    
    def update_conversation_sentiment(self, conversation_id: int):
        """Calculate and update average sentiment for conversation"""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "user",
            Message.sentiment_score.isnot(None)
        ).all()
        
        if messages:
            avg_sentiment = sum(m.sentiment_score for m in messages) / len(messages)
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            conversation.average_sentiment = avg_sentiment
            self.db.commit()
    
    def escalate_conversation(self, session_id: str):
        """Mark conversation as escalated"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if conversation:
            conversation.escalated = True
            conversation.status = "escalated"
            self.db.commit()
    
    def resolve_conversation(self, session_id: str):
        """Mark conversation as resolved"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if conversation:
            conversation.status = "resolved"
            self.db.commit()
    
    def get_conversation_history(self, session_id: str):
        """Get all messages for a conversation"""
        messages = self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        return messages
    
    def should_escalate(self, sentiment_score: float, conversation_id: int):
        """Determine if conversation should be escalated"""
        # Escalate if very negative sentiment
        if sentiment_score < -0.5:
            return True
        
        # Check conversation history
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        ).order_by(Message.timestamp.desc()).limit(3).all()
        
        # Escalate if last 3 messages are all negative
        if len(messages) >= 3:
            recent_sentiments = [m.sentiment_score for m in messages if m.sentiment_score]
            if all(s < -0.3 for s in recent_sentiments):
                return True
        
        return False