import requests
from bs4 import BeautifulSoup
import random
import time
from .utils import clean_text, format_price

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
    }

def scrape_amazon(url):
    """
    Scrapes product details from Amazon.
    Returns a dictionary with title, price, ratings, and reviews.
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Title
        title_elem = soup.find("span", {"id": "productTitle"})
        title = clean_text(title_elem.text) if title_elem else "Unknown Product"

        # Price
        price_elem = soup.find("span", {"class": "a-price-whole"})
        price_fraction = soup.find("span", {"class": "a-price-fraction"})
        price = "0.0"
        if price_elem:
            price = price_elem.text
            if price_fraction:
                price += "." + price_fraction.text
        
        # Ratings
        rating_elem = soup.find("span", {"class": "a-icon-alt"})
        rating = rating_elem.text.split(" ")[0] if rating_elem else "0.0"

        # Reviews (Basic extraction from the main page)
        reviews = []
        review_blocks = soup.find_all("div", {"data-hook": "review"})
        for block in review_blocks:
            review_text_elem = block.find("span", {"data-hook": "review-body"})
            if review_text_elem:
                reviews.append(clean_text(review_text_elem.text))

        return {
            "title": title,
            "price": format_price(price),
            "rating": rating,
            "reviews": reviews,
            "source": "Amazon"
        }

    except Exception as e:
        print(f"Error scraping Amazon: {e}")
        return None

def scrape_flipkart(url):
    """
    Scrapes product details from Flipkart.
    Returns a dictionary with title, price, ratings, and reviews.
    """
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Title
        title_elem = soup.find("span", {"class": "B_NuCI"})
        title = clean_text(title_elem.text) if title_elem else "Unknown Product"

        # Price
        price_elem = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
        price = price_elem.text if price_elem else "0.0"

        # Ratings
        rating_elem = soup.find("div", {"class": "_3LWZlK"})
        rating = rating_elem.text if rating_elem else "0.0"

        # Reviews
        reviews = []
        review_blocks = soup.find_all("div", {"class": "t-ZTKy"})
        for block in review_blocks:
             # Expand 'READ MORE' if present (Flipkart often hides full text)
            review_text = block.text.replace("READ MORE", "").strip()
            reviews.append(clean_text(review_text))

        return {
            "title": title,
            "price": format_price(price),
            "rating": rating,
            "reviews": reviews,
            "source": "Flipkart"
        }

    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
        return None

def scrape_product(url):
    """
    Main scraping function that dispatches to specific scrapers based on URL.
    """
    if "amazon" in url.lower():
        return scrape_amazon(url)
    elif "flipkart" in url.lower():
        return scrape_flipkart(url)
    else:
        return {"error": "Unsupported URL or scraping failed."}
