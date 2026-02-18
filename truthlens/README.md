# TruthLens - AMD AI Product Analyzer

TruthLens is a Streamlit-based web application that uses AI to analyze products from e-commerce links or manual input. It provides comprehensive insights, including sentiment analysis, fake review detection, price fairness, and durability assessments.

## Features

- **Product Analysis**: Analyze products via URL (Amazon/Flipkart) or manual text entry.
- **Sentiment Analysis**: Uses HuggingFace Transformers (with VADER fallback) to determine review sentiment.
- **Fake Review Detection**: Identifies potential fake reviews using heuristics and machine learning.
- **Price Fairness**: Evaluates if a product is overpriced based on specs and category.
- **Visual Dashboard**: Interactive charts for sentiment, word clouds, and more.
- **AMD Optimization**: Benchmarks inference performance on CPU vs. GPU (if available).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd truthlens
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python -m streamlit run truthlens/app.py
    ```

## AMD Optimization

This application includes a performance benchmark section that compares inference times between CPU and GPU (if an AMD GPU with ROCm support is detected).

## Ethical Note

This tool scrapes public product data for analysis purposes. Please respect website terms of service and use responsibly.
