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

        # Title Selectors
        title_selectors = [
            {"id": "productTitle"},
            {"id": "title"},
            {"class": "a-size-large product-title-word-break"}
        ]
        title = "Unknown Product"
        for selector in title_selectors:
            elem = soup.find("span", selector)
            if elem:
                title = clean_text(elem.text)
                break

        # Price Selectors (Amazon India often uses different styles)
        price = "0.0"
        price_selectors = [
            (".a-price-whole", ".a-price-fraction"),
            (".apexPriceToPay .a-offscreen", None),
            (".priceToPay .a-offscreen", None),
            ("#priceblock_ourprice", None),
            ("#priceblock_dealprice", None)
        ]
        
        for whole_sel, frac_sel in price_selectors:
            if whole_sel.startswith("#"):
                price_elem = soup.find("span", id=whole_sel[1:])
            else:
                # Handle complex selectors manually for speed
                if ".a-offscreen" in whole_sel:
                    parent_class = whole_sel.split(" ")[0][1:]
                    parent = soup.find("span", class_=parent_class)
                    price_elem = parent.find("span", class_="a-offscreen") if parent else None
                else:
                    price_elem = soup.find("span", class_=whole_sel[1:])
            
            if price_elem:
                price_text = price_elem.text.strip().replace(",", "")
                # Remove currency symbol if it's there
                price_text = price_text.replace("₹", "").replace("$", "").replace("Rs.", "").strip()
                
                if frac_sel:
                    frac_elem = soup.find("span", class_=frac_sel[1:])
                    if frac_elem:
                        price_text += "." + frac_elem.text.strip()
                
                price = price_text
                break
        
        # Ratings
        rating_elem = soup.select_one(".a-icon-alt")
        rating = rating_elem.text.split(" ")[0] if rating_elem else "0.0"

        # Reviews
        reviews = []
        # Try different review containers
        review_selectors = [
            ("div", {"data-hook": "review"}),
            ("div", {"id": "customer_review"}),
            ("span", {"data-hook": "review-body"})
        ]
        
        for tag, attr in review_selectors:
            review_blocks = soup.find_all(tag, attr)
            if review_blocks:
                for block in review_blocks:
                    # If it's the body directly
                    if attr.get("data-hook") == "review-body":
                        reviews.append(clean_text(block.text))
                    else:
                        review_text_elem = block.find("span", {"data-hook": "review-body"})
                        if review_text_elem:
                            reviews.append(clean_text(review_text_elem.text))
                if reviews: break

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
    # Note: Flipkart has strict anti-bot protection and blocks simple requests.
    # In a real-world scenario, you would use a Selenium/Playwright scraper with rotating proxies or a scraping API.
    # We are adding a simple fallback mechanism here to fetch basic data or return simulated data if blocked.
    try:
        # First attempt with requests
        response = requests.get(url, headers=get_headers(), timeout=10)
        
        # If successfully bypassed
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Title Selectors
            title_elem = soup.find("span", {"class": "B_NuCI"}) or soup.find("span", {"class": "VU-Z7x"})
            title = clean_text(title_elem.text) if title_elem else "Unknown Flipkart Product"

            # Price Selectors
            price_elem = soup.find("div", {"class": "_30jeq3 _16Jk6d"}) or soup.find("div", {"class": "Nx9bqj _4b5DiR"})
            price = price_elem.text if price_elem else "0.0"

            # Ratings
            rating_elem = soup.find("div", {"class": "_3LWZlK"}) or soup.find("div", {"class": "XqYvS8"})
            rating = rating_elem.text if rating_elem else "0.0"

            # Reviews
            reviews = []
            review_blocks = soup.find_all("div", {"class": "t-ZTKy"}) or soup.find_all("div", {"class": "Z_3_1W"})
            for block in review_blocks:
                review_text = block.text.replace("READ MORE", "").strip()
                reviews.append(clean_text(review_text))

            if title != "Unknown Flipkart Product":
                return {
                    "title": title,
                    "price": format_price(price),
                    "rating": rating,
                    "reviews": reviews,
                    "source": "Flipkart"
                }

        # Fallback if blocked (e.g., 403 Forbidden) or data not found
        print("Flipkart blocked the request. Using simulated/fallback data.")
        return {
            "title": "Flipkart Product (Simulated due to bot protection)",
            "price": "49999.00",
            "rating": "4.5",
            "reviews": [
                "Amazing product, totally worth the price!",
                "Good build quality but battery life could be better.",
                "Fast delivery by Flipkart and the product is genuine.",
                "Terrible customer service when I tried to return it.",
                "Best in this price segment."
            ],
            "source": "Flipkart (Fallback)"
        }

    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
        # Return fallback data on error
        return {
            "title": "Flipkart Product (Fallback due to error)",
            "price": "49999.00",
            "rating": "4.5",
            "reviews": [
                "Amazing product, totally worth the price!",
                "Good build quality but battery life could be better.",
                "Fast delivery by Flipkart and the product is genuine."
            ],
            "source": "Flipkart (Fallback)"
        }

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
