import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
import streamlit as st

def generate_dashboard(reviews, sentiment_data, fake_score):
    """
    Generates and displays the Review Analytics Dashboard in Streamlit.
    """
    if not reviews:
        st.warning("No reviews available for analysis.")
        return

    st.markdown("### 📊 Review Analytics Dashboard")
    
    # 1. Sentiment Distribution (Pie Chart)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        counts = sentiment_data.get("sentiment_counts", {})
        labels = list(counts.keys())
        sizes = list(counts.values())
        colors = ['#66b3ff', '#ff9999', '#99ff99'] # Blue, Red, Greenish

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)

    # 2. Review Length Distribution
    with col2:
        st.subheader("Review Length Distribution")
        review_lens = [len(r.split()) for r in reviews]
        fig2, ax2 = plt.subplots()
        sns.histplot(review_lens, kde=True, ax=ax2, color="skyblue")
        ax2.set_xlabel("Word Count")
        ax2.set_ylabel("Frequency")
        st.pyplot(fig2)

    # 3. Word Cloud
    st.subheader("☁️ Word Cloud (Common Terms)")
    text = " ".join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.imshow(wordcloud, interpolation='bilinear')
    ax3.axis("off")
    st.pyplot(fig3)

    # 4. Fake Review Indicators
    st.markdown("---")
    st.subheader("🕵️ Fake Review Analysis")
    st.metric(label="Probability of Fake Reviews", value=f"{fake_score}%", delta="-High Risk" if fake_score > 50 else "Low Risk")
    
    # 5. Top Praise vs. Complaints (simple keyword extraction)
    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("👍 Top Praise Keywords (Simulated)")
        st.write("• quality, great, love, value, fast")
    
    with col4:
        st.subheader("👎 Top Complaints (Simulated)")
        st.write("• broke, cheap, stopped, customer service")

