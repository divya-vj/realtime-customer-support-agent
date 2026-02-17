from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db, Message
from app.schemas.chat import ChatMessage, ChatResponse, MessageDetail
from app.services.chat_service import ChatService
from app.services.sentiment import analyze_sentiment as ai_sentiment
from typing import List
import anthropic
import os

router = APIRouter()

async def get_llm_response(message: str, history: list) -> str:
    """Call Claude API for response"""
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        messages = []
        for h in history:
            if h["role"] in ["user", "assistant"]:
                messages.append({"role": h["role"], "content": h["content"]})
        
        if not messages or messages[-1]["role"] != "user":
            messages.append({"role": "user", "content": message})
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system="You are a helpful customer support agent. Be concise, empathetic, and professional. Help customers with their issues efficiently.",
            messages=messages
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return "I apologize, I'm having trouble connecting. Please try again."

async def analyze_sentiment(message: str) -> tuple:
    """Call Person 1's AI sentiment analysis"""
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
