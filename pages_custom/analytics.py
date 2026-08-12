import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import fetch_data

def render():
    st.title("📊 Analytics Dashboard")
    
    # Fetch data (same as your leaderboard logic)
    query = """
        SELECT u.username, q.quiz_title, q.percentage, q.attempted_at 
        FROM quiz_attempts q
        JOIN users u ON q.user_id = u.id;
    """
    df = fetch_data(query)

    if df is not None and not df.empty:
        # Create two columns for the dashboard
        col1, col2 = st.columns(2)

        # 1. Top Rankers Chart
        with col1:
            st.subheader("🏆 Top Performers")
            # Get the top 5 students based on max percentage
            top_rankers = df.groupby('username')['percentage'].max().nlargest(5).reset_index()
            fig1 = px.bar(top_rankers, x='username', y='percentage', color='percentage', 
                          color_continuous_scale='Blues', title="Highest Scores Achieved")
            st.plotly_chart(fig1, use_container_width=True)

        # 2. Participation Chart
        with col2:
            st.subheader("👥 Participation Trends")
            df['date'] = pd.to_datetime(df['attempted_at']).dt.date
            participation = df.groupby('date').size().reset_index(name='count')
            fig2 = px.area(participation, x='date', y='count', 
                           title="Daily Quiz Attempts", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

        # Stats Metric Section
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Attempts", len(df))
        m2.metric("Unique Participants", df['username'].nunique())
        m3.metric("Avg Score", f"{df['percentage'].mean():.1f}%")
        
    else:
        st.info("No data yet. Get students to take their first quiz!")