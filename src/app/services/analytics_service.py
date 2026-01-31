from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Conversation, Message
from collections import Counter

class AnalyticsService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self):
        total_conversations = self.db.query(Conversation).count()
        
        resolved_conversations = self.db.query(Conversation).filter(
            Conversation.status == "resolved"
        ).count()
        
        escalated_conversations = self.db.query(Conversation).filter(
            Conversation.escalated == True
        ).count()
        
        resolution_rate = (resolved_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        avg_sentiment_result = self.db.query(
            func.avg(Conversation.average_sentiment)
        ).filter(Conversation.average_sentiment.isnot(None)).scalar()
        
        average_sentiment = float(avg_sentiment_result) if avg_sentiment_result else 0
        
        sentiment_distribution = self.get_sentiment_distribution()
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
        messages = self.db.query(Message).filter(
            Message.role == "user"
        ).all()
        
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
        
        common_issues = [issue for issue, count in issue_counts.most_common(limit)]
        
        return common_issues if common_issues else ["No data yet"]