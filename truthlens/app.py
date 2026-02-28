import streamlit as st
import time
import pandas as pd
from core import scraping, nlp, fake_review, pricing, vision, scoring, dashboard, utils

# Page Config
st.set_page_config(
    page_title="TruthLens - AMD AI Product Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium" look
st.markdown("""
<style>
    /* Global Settings & Typography */
     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* Primary Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2), 0 2px 4px -1px rgba(239, 68, 68, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.3), 0 4px 6px -2px rgba(239, 68, 68, 0.15);
        color: white;
        border: none;
    }
    
    /* Metric Cards Customization */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] h1 {
        color: #EF4444;
        font-weight: 800;
        font-size: 2rem;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #cbd5e1;
    }
    .stTextArea>div>div>textarea {
        border-radius: 6px;
        border: 1px solid #cbd5e1;
    }
    
    /* Warning/Info/Success Boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center; color: #EF4444; margin-bottom: 0;'>🔍 TruthLens</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #64748b; font-weight: 600; margin-top: -10px;'>AI-Powered Product Analysis</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# Inputs
input_method = st.sidebar.radio("Input Method", ["Product Link", "Manual Entry"])
product_url = ""
product_name = ""
product_price = 0.0
reviews_text = ""
specs_text = ""
image_file = None

def clear_search():
    st.session_state["product_url_input"] = ""
    if 'scraped_data' in st.session_state:
        del st.session_state['scraped_data']

if input_method == "Product Link":
    # Use a key to allow programmatic clearing
    product_url = st.sidebar.text_input("Enter Product URL (Amazon/Flipkart)", key="product_url_input")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Fetch Details", use_container_width=True):
            if product_url:
                with st.spinner("Scraping..."):
                    data = scraping.scrape_product(product_url)
                    if data and "error" not in data:
                        st.session_state['scraped_data'] = data
                        st.rerun()
                    else:
                        st.error("Failed to scrape.")
            else:
                st.sidebar.warning("Enter URL.")
    
    with col2:
        st.button("Clear URL", on_click=clear_search, use_container_width=True)

    # Load from cache if available
    if 'scraped_data' in st.session_state:
         data = st.session_state['scraped_data']
         product_name = st.text_input("Product Name", value=data.get("title"))
         product_price = st.number_input("Price", value=float(data.get("price")), min_value=0.0)
         reviews_text = st.text_area("Reviews", value="\n".join(data.get("reviews", [])), height=150)

elif input_method == "Manual Entry":
    product_name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Electronics", "Laptop", "Smartphone", "Home", "Other"])
    product_price = st.number_input("Price", min_value=0.0)
    reviews_text = st.text_area("Paste Reviews (one per line)", height=150)

specs_text = st.text_area("Product Specs (Optional)")
image_file = st.file_uploader("Upload Product Image (Optional)", type=["jpg", "png", "jpeg"])


# Analyze Button
if st.button("🚀 ANALYZE PRODUCT"):
    if not reviews_text and not product_url:
        st.error("Please provide reviews or a product link.")
    else:
        st.markdown("---")
        
        # 1. Run Analysis
        reviews_list = [r.strip() for r in reviews_text.split('\n') if r.strip()]
        
        with st.spinner("Analyzing Sentiment (NLP)..."):
            sentiment_res = nlp.analyze_sentiment(reviews_list)
        
        with st.spinner("Detecting Fake Reviews..."):
            fake_res = fake_review.detect_fake_reviews(reviews_list)
            
        with st.spinner("Analyzing Pricing..."):
             # Default category if not selected
            cat = "Electronics" if input_method == "Product Link" else category
            price_res = pricing.price_fairness(product_price, cat, specs_text)
            
        with st.spinner("Analyzing Visuals..."):
            img_bytes = image_file.read() if image_file else None
            vision_res = vision.analyze_image(img_bytes)

        # Calculate Overall Score
        overall_score = scoring.calculate_overall_score(
            sentiment_res['overall_score'],
            fake_res['fake_score'],
            price_res['label'],
            vision_res.get('quality_score', 0)
        )

        # 2. Display Results
        st.title(f"Analysis Result: {product_name}")
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Quality Score", f"{overall_score}/10")
        col2.metric("Sentiment Score", f"{round(sentiment_res['overall_score'], 1)}/10")
        col3.metric("Fake Review Prob", f"{fake_res['fake_score']}%", delta_color="inverse")
        col4.metric("Price Fairness", price_res['label'], f"{round(price_res['score'], 1)}%")

        # Second Row
        col5, col6, col7 = st.columns(3)
        col5.metric("Durability Risk", "Low") # Placeholder/Hardcoded for now as per scoring.py limit
        col6.metric("Image Quality", f"{vision_res.get('quality_score', 0)}/10")
        col7.metric("Sustainability Score", "7/10") # Placeholder

        # 3. AMD Performance Section
        st.markdown("### ⚡ AMD Hardware Optimization")
        perf_col1, perf_col2 = st.columns(2)
        with perf_col1:
            st.info(f"Inference Device: **{sentiment_res['device']}**")
        with perf_col2:
            st.success(f"Inference Time: **{round(sentiment_res['inference_time'], 4)} seconds**")
        
        if sentiment_res['device'] == 'GPU':
             st.caption("🚀 ROCm Acceleration Active! Performance boosted.")

        # 4. Visual Dashboard
        dashboard.generate_dashboard(reviews_list, sentiment_res, fake_res['fake_score'])

        # 5. Comparison / Alternatives
        st.markdown("---")
        st.subheader("💡 Suggested Alternatives")
        st.write("Based on your analysis, here are similar products with better scores:")
        st.info("• Placeholder Alternative A (Score: 9.2)\n• Placeholder Alternative B (Score: 8.8)")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by TruthLens Team | Powered by AMD ROCm")
