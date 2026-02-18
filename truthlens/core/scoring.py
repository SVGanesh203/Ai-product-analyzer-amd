def calculate_overall_score(sentiment_score, fake_score, price_fairness_label, image_quality=0):
    """
    Calculates the final overall product score (0-10).
    Weights:
    - Sentiment: 50%
    - Fake Probability: -20% (Penalty)
    - Price Fairness: 20%
    - Image Quality: 10%
    """
    
    # 1. Sentiment Contribution (0-10 scale input) -> Max 5 points
    score = sentiment_score * 0.5
    
    # 2. Fake Review Penalty
    # If 100% fake probability, subtract 2 points.
    fake_penalty = (fake_score / 100.0) * 2.0
    score -= fake_penalty
    
    # 3. Price Fairness Bonus/Penalty
    if price_fairness_label == "Fair":
        score += 2.0
    elif price_fairness_label == "Undervalued":
        score += 2.5 # Bonus for good deal
    else: # Overpriced
        score += 1.0 # Smaller contribution
        
    # 4. Image Quality (0-10 scale input) -> Max 1 point
    score += (image_quality / 10.0) * 1.0
    
    # Clamp score to 0-10
    final_score = max(0.0, min(10.0, score))
    
    return round(final_score, 1)

def get_durability_risk(sentiment_data):
    """
    Estimates durability risk based on negative sentiment keywords.
    """
    negative_reviews = sentiment_data.get("negative_text", []) # Placeholder for actual access
    risk_score = 0
    keywords = ["broke", "stopped working", "quality", "cheap", "fell apart", "dead"]
    
    # Simple simulation if we don't have full text here yet.
    # In a real app, pass the full text specifically for this.
    return "Medium" # Default fallback for now
