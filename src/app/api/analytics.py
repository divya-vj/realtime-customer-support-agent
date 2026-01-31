from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db, Conversation
from app.schemas.chat import AnalyticsResponse, ConversationHistory
from app.services.analytics_service import AnalyticsService
from typing import List

router = APIRouter()

@router.get("/analytics/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_dashboard_stats()
    return AnalyticsResponse(**stats)

@router.get("/analytics/conversations", response_model=List[ConversationHistory])
async def get_all_conversations(
    status: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.order_by(Conversation.created_at.desc()).limit(limit).all()
    
    return conversations