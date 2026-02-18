def price_fairness(price, category, specs_text=""):
    """
    Determines if a product is overpriced based on category averages and specs.
    Returns assessment label and fairness percentage.
    """
    # Baseline prices for categories (very simplified)
    category_baselines = {
        "Electronics": 500.0,
        "Laptop": 800.0,
        "Smartphone": 600.0,
        "Headphones": 150.0,
        "Home": 50.0,
        "Clothing": 30.0,
        "Other": 100.0
    }
    
    baseline = category_baselines.get(category, 100.0)
    
    # Adjust baseline based on keywords in specs (simplified logic)
    specs = specs_text.lower()
    if "pro" in specs or "premium" in specs or "high-end" in specs:
        baseline *= 1.5
    if "budget" in specs or "basic" in specs:
        baseline *= 0.7
        
    diff_percent = ((price - baseline) / baseline) * 100
    
    if diff_percent < -20:
        return {"label": "Undervalued", "score": diff_percent}
    elif -20 <= diff_percent <= 20:
        return {"label": "Fair", "score": diff_percent}
    else:
        return {"label": "Overpriced", "score": diff_percent}
