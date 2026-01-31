from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db, Conversation
from app.schemas.chat import AnalyticsResponse, ConversationHistory
from app.services.analytics_service import AnalyticsService
from typing import List

router = APIRouter()

@router.get("/analytics/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get main dashboard analytics"""
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_dashboard_stats()
    return AnalyticsResponse(**stats)

@router.get("/analytics/conversations")
async def get_all_conversations(
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of all conversations with optional filtering"""
    query = db.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": conv.id,
            "session_id": conv.session_id,
            "customer_name": conv.customer_name,
            "status": conv.status,
            "escalated": conv.escalated,
            "average_sentiment": conv.average_sentiment,
            "created_at": conv.created_at.isoformat()
        }
        for conv in conversations
    ]

@router.get("/analytics/sentiment-trends")
async def get_sentiment_trends(db: Session = Depends(get_db)):
    """Get sentiment trends over time"""
    analytics_service = AnalyticsService(db)
    trends = analytics_service.get_sentiment_over_time()
    return {"trends": trends}