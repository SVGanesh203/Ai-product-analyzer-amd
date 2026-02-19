from transformers import pipeline
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch

# Check for GPU (CUDA or ROCm)
device = 0 if torch.cuda.is_available() else -1
print(f"NLP Module: Using device {'GPU' if device == 0 else 'CPU'}")

# Initialize Transformers Pipeline (fingers crossed for compatible environment)
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=device)
    transformers_available = True
except Exception as e:
    print(f"Transformers pipeline failed to initialize: {e}")
    transformers_available = False

vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(reviews):
    """
    Analyzes sentiment of a list of reviews.
    Returns a dictionary with overall sentiment and detailed breakdown.
    """
    if not reviews:
        return {
            "overall_score": 0.0,
            "sentiment_counts": {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0},
            "reviews_analyzed": 0,
            "inference_time": 0.0,
            "device": "GPU" if device == 0 else "CPU"
        }

    start_time = time.time()
    results = []
    
    # Use Transformers if available and robust enough
    if transformers_available:
        try:
             # Truncate to 512 tokens to avoid errors with some models
            truncated_reviews = [review[:2000] for review in reviews] 
            results = sentiment_pipeline(truncated_reviews)
        except Exception as e:
             print(f"Transformer inference failed, falling back to VADER: {e}")
             results = [] # Trigger fallback

    # Fallback to VADER if Transformers unavailable or failed
    if not results:
        for review in reviews:
            score = vader_analyzer.polarity_scores(review)
            if score['compound'] >= 0.05:
                results.append({"label": "POSITIVE", "score": score['compound']})
            elif score['compound'] <= -0.05:
                results.append({"label": "NEGATIVE", "score": abs(score['compound'])})
            else:
                 results.append({"label": "NEUTRAL", "score": 1.0 - abs(score['compound'])}) # simple proxy

    end_time = time.time()
    inference_time = end_time - start_time

    # Aggregation
    sentiment_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
    total_score = 0.0
    
    for res in results:
        label = res['label'].upper() # Ensure uppercase
        if label not in sentiment_counts:
             # Map transformer output (e.g., 'LABEL_1') if necessary, though distilbert uses POSITIVE/NEGATIVE
             if 'POSITIVE' in label or 'LABEL_1' in label: label = 'POSITIVE'
             elif 'NEGATIVE' in label or 'LABEL_0' in label: label = 'NEGATIVE'
             else: label = 'NEUTRAL'
        
        sentiment_counts[label] += 1
        # Normalize score to 0-1 range for simple averaging, where POS=1, NEG=0
        if label == 'POSITIVE':
            total_score += res['score']
        elif label == 'NEGATIVE':
            total_score += (1 - res['score']) # Invert for specific logic if needed, but simple count is often better
        else:
            total_score += 0.5 

    # Normalize overall score components
    positive_ratio = sentiment_counts['POSITIVE'] / len(reviews) if reviews else 0
    
    return {
        "overall_score": positive_ratio * 10, # 0-10 scale
        "sentiment_counts": sentiment_counts,
        "reviews_analyzed": len(reviews),
        "inference_time": inference_time,
        "device": "GPU" if device == 0 else "CPU"
    }
