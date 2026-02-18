from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db, Message
from app.schemas.chat import ChatMessage, ChatResponse, MessageDetail
from app.services.chat_service import ChatService
from app.services.sentiment import analyze_sentiment as ai_sentiment
from typing import List
import random

router = APIRouter()

async def get_llm_response(message: str, history: list) -> str:
    """Smart mock responses for demo"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your AI support assistant. How can I help you today?"
    
    # Order-related
    if any(word in message_lower for word in ['order', 'delivery', 'shipping', 'package']):
        return "I'd be happy to help with your order! Could you please provide your order number so I can look into this for you?"
    
    # Frustrated/angry sentiment
    if any(word in message_lower for word in ['frustrated', 'angry', 'upset', 'annoyed', 'terrible']):
        return "I completely understand your frustration, and I sincerely apologize for the inconvenience. Let me escalate this to a senior agent who can resolve this immediately. In the meantime, can you share more details about the issue?"
    
    # Refund/return
    if any(word in message_lower for word in ['refund', 'return', 'money back', 'cancel']):
        return "I can definitely help you with that. Our return policy allows refunds within 30 days. Would you like me to start the refund process for you? I'll need your order number to proceed."
    
    # Account issues
    if any(word in message_lower for word in ['account', 'login', 'password', 'sign in']):
        return "I can help you with your account! Have you tried resetting your password? I can send you a password reset link to your registered email address."
    
    # Payment issues
    if any(word in message_lower for word in ['payment', 'charge', 'credit card', 'billing']):
        return "Let me help you resolve this payment issue. Could you clarify what specific problem you're experiencing? I can check your billing details and transaction history."
    
    # Product questions
    if any(word in message_lower for word in ['product', 'item', 'quality', 'size', 'color']):
        return "I'd be happy to provide more information about our products! Which specific item are you interested in? I can share details about features, specifications, and availability."
    
    # Thanks/positive
    if any(word in message_lower for word in ['thank', 'thanks', 'appreciate', 'great', 'awesome']):
        return "You're very welcome! I'm glad I could help. Is there anything else I can assist you with today?"
    
    # Help/general
    if any(word in message_lower for word in ['help', 'support', 'assist', 'question']):
        return "I'm here to help! I can assist with orders, returns, account issues, product information, and more. What would you like help with?"
    
    # Default fallback responses
    fallbacks = [
        "I understand your concern. Could you provide a bit more detail so I can assist you better?",
        "Thank you for reaching out! Let me help you with that. Can you share more information about your issue?",
        "I'm here to help resolve this for you. Could you elaborate on what you're experiencing?",
        "I appreciate you contacting us. To better assist you, could you provide more details about your situation?"
    ]
    
    return random.choice(fallbacks)

async def analyze_sentiment(message: str) -> tuple:
    """Call sentiment analysis"""
    result = ai_sentiment(message)

    mood = result["mood"]
    confidence = result["confidence"]

    if mood == "positive":
        score = confidence
    elif mood == "negative":
        score = -confidence
    else:
        score = 0.0

    return (score, mood)

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage, db: Session = Depends(get_db)):
    """Handle chat message and return AI response"""

    chat_service = ChatService(db)

    conversation = chat_service.get_or_create_conversation(
        chat_message.session_id,
        chat_message.customer_name
    )

    sentiment_score, sentiment_label = await analyze_sentiment(chat_message.message)

    chat_service.save_message(
        session_id=chat_message.session_id,
        role="user",
        content=chat_message.message,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label
    )

    history = chat_service.get_conversation_history(chat_message.session_id)
    history_list = [{"role": m.role, "content": m.content} for m in history]

    ai_response = await get_llm_response(chat_message.message, history_list)

    chat_service.save_message(
        session_id=chat_message.session_id,
        role="assistant",
        content=ai_response
    )

    should_escalate = chat_service.should_escalate(sentiment_score, conversation.id)

    if should_escalate:
        chat_service.escalate_conversation(chat_message.session_id)

    return ChatResponse(
        response=ai_response,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        should_escalate=should_escalate,
        session_id=chat_message.session_id
    )

@router.get("/chat/history/{session_id}", response_model=List[MessageDetail])
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get conversation history"""
    chat_service = ChatService(db)
    messages = chat_service.get_conversation_history(session_id)
    return messages

@router.post("/chat/resolve/{session_id}")
async def resolve_conversation(session_id: str, db: Session = Depends(get_db)):
    """Mark conversation as resolved"""
    chat_service = ChatService(db)
    chat_service.resolve_conversation(session_id)
    return {"status": "resolved"}

@router.post("/chat/update-sentiment/{session_id}")
async def update_conversation_sentiment(session_id: str, db: Session = Depends(get_db)):
    """Force update conversation sentiment"""
    chat_service = ChatService(db)
    conversation = chat_service.get_or_create_conversation(session_id)
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id,
        Message.role == "user",
        Message.sentiment_score.isnot(None)
    ).all()

    if messages:
        avg = sum(m.sentiment_score for m in messages) / len(messages)
        conversation.average_sentiment = avg
        db.commit()
        return {"sentiment": avg, "message_count": len(messages)}

    return {"sentiment": None, "message_count": 0}
