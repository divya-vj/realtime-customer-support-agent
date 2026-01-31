from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of input text and return mood + confidence score.
    """
    polarity = TextBlob(text).sentiment.polarity
    
    if polarity > 0.2:
        mood = "positive"
    elif polarity < -0.2:
        mood = "negative"
    else:
        mood = "neutral"
    
    return {
        "mood": mood,
        "confidence": round(abs(polarity), 2)
    }