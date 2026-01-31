from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.chat import ChatMessage, ChatResponse, MessageDetail
from app.services.chat_service import ChatService
from typing import List

router = APIRouter()

# Placeholder functions - Person 1 will replace these
async def get_llm_response(message: str, history: list) -> str:
    return "This is a placeholder AI response. Person 1 will integrate the actual LLM here."

async def analyze_sentiment(message: str) -> tuple:
    # Simple keyword-based placeholder
    negative_words = ["bad", "terrible", "awful", "angry", "frustrated", "unacceptable"]
    positive_words = ["good", "great", "excellent", "thank", "perfect"]
    
    message_lower = message.lower()
    if any(word in message_lower for word in negative_words):
        return (-0.6, "negative")
    elif any(word in message_lower for word in positive_words):
        return (0.6, "positive")
    return (0.0, "neutral")

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage, db: Session = Depends(get_db)):
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
    chat_service = ChatService(db)
    messages = chat_service.get_conversation_history(session_id)
    return messages

@router.post("/chat/resolve/{session_id}")
async def resolve_conversation(session_id: str, db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    chat_service.resolve_conversation(session_id)
    return {"status": "resolved"}