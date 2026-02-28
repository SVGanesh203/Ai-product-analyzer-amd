import plotly.express as px
from wordcloud import WordCloud
import pandas as pd
import streamlit as st

def generate_dashboard(reviews, sentiment_data, fake_score):
    """
    Generates and displays the Review Analytics Dashboard in Streamlit interactively.
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
        
        if labels and sizes:
            fig1 = px.pie(
                names=labels, 
                values=sizes,
                color_discrete_sequence=['#66b3ff', '#ff9999', '#99ff99']
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No sentiment data available.")

    # 2. Review Length Distribution
    with col2:
        st.subheader("Review Length Distribution")
        review_lens = [len(r.split()) for r in reviews]
        df_lens = pd.DataFrame({'Word Count': review_lens})
        
        fig2 = px.histogram(
            df_lens, 
            x='Word Count', 
            nbins=20,
            marginal='box',
            color_discrete_sequence=['skyblue']
        )
        fig2.update_layout(yaxis_title="Frequency")
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Word Cloud
    st.subheader("☁️ Word Cloud (Common Terms)")
    text = " ".join(reviews)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # Plotly doesn't natively support word clouds easily without complex scatters.
    # Displaying as a native Streamlit image is the cleanest way.
    st.image(wordcloud.to_array(), use_container_width=True)

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

