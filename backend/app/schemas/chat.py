from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    session_id: str
    message: str
    customer_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sentiment_score: float
    sentiment_label: str
    should_escalate: bool
    session_id: str

class MessageDetail(BaseModel):
    id: int
    role: str
    content: str
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ConversationHistory(BaseModel):
    id: int
    session_id: str
    customer_name: Optional[str]
    created_at: datetime
    status: str
    escalated: bool
    average_sentiment: Optional[float]
    
    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    total_conversations: int
    resolved_conversations: int
    escalated_conversations: int
    resolution_rate: float
    average_sentiment: float
    sentiment_distribution: dict
    common_issues: List[str]