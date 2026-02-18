import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# Simple training data for demonstration (in a real app, load a pre-trained model)
# 0 = Real, 1 = Fake
TRAIN_REVIEWS = [
    "This product is amazing! Best thing ever bought.", 1,
    "Terrible quality, broke after one use.", 0,
    "I received this product for free in exchange for a review.", 1,
    "Decent product for the price, works as expected.", 0,
    "Five stars! Highly recommended!", 1,
    "Total scam, do not buy.", 0,
    "Great value, fast shipping.", 1,
    "The material feels initially good but wears out quickly.", 0,
    "Wow! Incredible! Life changing!", 1,
    "Okay, serves its purpose.", 0
]

def train_dummy_model():
    texts = TRAIN_REVIEWS[0::2]
    labels = TRAIN_REVIEWS[1::2]
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    model = LogisticRegression()
    model.fit(X, labels)
    return model, vectorizer

# Initialize model (lazy loading ideally, but simple here)
model, vectorizer = train_dummy_model()

def detect_fake_reviews(reviews):
    """
    Analyzes reviews for signs of being fake/spam.
    Returns a probability score (0-100%) and a list of flagged reviews.
    """
    if not reviews:
        return {"fake_score": 0, "flagged_reviews": []}

    # Heuristic checks
    suspicious_patterns = [
        r"highly recommend",
        r"best product ever",
        r"received for free",
        r"exchange for a review",
        r"wow",
        r"amazing",
        r"five stars"
    ]
    
    flagged = []
    heuristic_count = 0
    
    for review in reviews:
        # Check repetitive patterns or over-enthusiasm
        if any(re.search(p, review.lower()) for p in suspicious_patterns):
            heuristic_count += 1
            flagged.append(review)
        
        # Check length (very short reviews can be suspicious)
        if len(review.split()) < 5:
            heuristic_count += 0.5 # Weight less

    # TF-IDF + Model Prediction (Soft voting)
    try:
        X_test = vectorizer.transform(reviews)
        probs = model.predict_proba(X_test)[:, 1] # Probability of being fake
        avg_model_prob = np.mean(probs)
    except:
        avg_model_prob = 0.0

    # Combine scores
    heuristic_score = (heuristic_count / len(reviews)) * 100
    final_score = (heuristic_score * 0.6) + (avg_model_prob * 100 * 0.4)
    
    return {
        "fake_score": min(100, round(final_score, 2)),
        "flagged_count": len(flagged),
        "total_reviews": len(reviews)
    }
