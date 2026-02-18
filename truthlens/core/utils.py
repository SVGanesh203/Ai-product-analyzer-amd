import re

def clean_text(text):
    """
    Cleans text by removing extra whitespace and special characters.
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_price(price_str):
    """
    Formats price string to float.
    Handles currency symbols and commas.
    """
    if not price_str:
        return 0.0
    # Remove currency symbols and commas
    price_clean = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(price_clean)
    except ValueError:
        return 0.0
