from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Conversation, Message
from collections import Counter
import json

class AnalyticsService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self):
        """Get overall dashboard statistics"""
        
        # Total conversations
        total_conversations = self.db.query(Conversation).count()
        
        # Resolved conversations
        resolved_conversations = self.db.query(Conversation).filter(
            Conversation.status == "resolved"
        ).count()
        
        # Escalated conversations
        escalated_conversations = self.db.query(Conversation).filter(
            Conversation.escalated == True
        ).count()
        
        # Calculate resolution rate
        resolution_rate = (resolved_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        # Average sentiment
        avg_sentiment_result = self.db.query(
            func.avg(Conversation.average_sentiment)
        ).filter(Conversation.average_sentiment.isnot(None)).scalar()
        
        average_sentiment = float(avg_sentiment_result) if avg_sentiment_result else 0
        
        # Sentiment distribution
        sentiment_distribution = self.get_sentiment_distribution()
        
        # Common issues
        common_issues = self.get_common_issues()
        
        return {
            "total_conversations": total_conversations,
            "resolved_conversations": resolved_conversations,
            "escalated_conversations": escalated_conversations,
            "resolution_rate": round(resolution_rate, 2),
            "average_sentiment": round(average_sentiment, 3),
            "sentiment_distribution": sentiment_distribution,
            "common_issues": common_issues
        }
    
    def get_sentiment_distribution(self):
        """Get distribution of sentiments"""
        messages = self.db.query(Message).filter(
            Message.sentiment_label.isnot(None),
            Message.role == "user"
        ).all()
        
        if not messages:
            return {"positive": 0, "neutral": 0, "negative": 0}
        
        sentiment_counts = Counter(m.sentiment_label for m in messages)
        total = len(messages)
        
        return {
            "positive": round(sentiment_counts.get("positive", 0) / total * 100, 1),
            "neutral": round(sentiment_counts.get("neutral", 0) / total * 100, 1),
            "negative": round(sentiment_counts.get("negative", 0) / total * 100, 1)
        }
    
    def get_common_issues(self, limit=5):
        """Extract common issues from user messages"""
        messages = self.db.query(Message).filter(
            Message.role == "user"
        ).all()
        
        # Keywords to look for
        issue_keywords = {
            "password": ["password", "login", "access", "sign in"],
            "order": ["order", "delivery", "shipping", "track"],
            "refund": ["refund", "return", "money back"],
            "account": ["account", "profile", "settings"],
            "payment": ["payment", "charge", "billing", "card"],
            "technical": ["error", "bug", "not working", "broken"]
        }
        
        issue_counts = Counter()
        
        for message in messages:
            content_lower = message.content.lower()
            for issue, keywords in issue_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    issue_counts[issue] += 1
        
        # Get top issues
        common_issues = [issue for issue, count in issue_counts.most_common(limit)]
        
        return common_issues if common_issues else ["No data yet"]
    
    def get_sentiment_over_time(self):
        """Get sentiment trends over time"""
        results = self.db.query(
            func.date(Message.timestamp).label('date'),
            func.avg(Message.sentiment_score).label('avg_sentiment')
        ).filter(
            Message.sentiment_score.isnot(None),
            Message.role == "user"
        ).group_by(
            func.date(Message.timestamp)
        ).order_by('date').all()
        
        return [
            {
                "date": str(r.date),
                "sentiment": round(float(r.avg_sentiment), 3)
            }
            for r in results
        ]