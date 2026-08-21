import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import fetch_data

def render():
    st.title("📊 Analytics Dashboard")
    
    # Fetch all quiz attempt data joined with users
    query = """
        SELECT u.username, q.quiz_title, q.percentage, q.attempted_at 
        FROM quiz_attempts q
        JOIN users u ON q.user_id = u.id;
    """
    df = fetch_data(query)

    if df is not None and not df.empty:
        # Create two columns for the top summary charts
        col1, col2 = st.columns(2)

        # 1. Top Rankers Chart (Top 5)
        with col1:
            st.subheader("🏆 Top Performers (Podium)")
            top_rankers = df.groupby('username')['percentage'].max().nlargest(5).reset_index()
            top_rankers['username'] = top_rankers['username'].astype(str)
            top_rankers = top_rankers.sort_values('percentage', ascending=True)

            fig1 = px.bar(
                top_rankers, 
                x='percentage', 
                y='username', 
                orientation='h',
                color='percentage', 
                color_continuous_scale='Blues',
                title="Highest Scores Achieved"
            )
            fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title="Percentage (%)", yaxis_title="Username")
            st.plotly_chart(fig1, use_container_width=True)

        # 2. Participation Chart
        with col2:
            st.subheader("👥 Participation Trends")
            df['date'] = pd.to_datetime(df['attempted_at']).dt.date
            participation = df.groupby('date').size().reset_index(name='count')
            
            fig2 = px.area(
                participation, 
                x='date', 
                y='count', 
                title="Daily Quiz Attempts", 
                markers=True
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Stats Metric Section
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Attempts", len(df))
        m2.metric("Unique Participants", df['username'].nunique())
        m3.metric("Avg Score", f"{df['percentage'].mean():.1f}%")

        # 3. Comprehensive Filterable Leaderboard Table for All Users
        st.markdown("---")
        st.subheader("📋 Complete Student Leaderboard & Performance Table")

        # Aggregate user performance data for the table
        user_summary = df.groupby('username').agg(
            total_quizzes=('quiz_title', 'count'),
            highest_score=('percentage', 'max'),
            average_score=('percentage', 'mean'),
            last_attempt=('attempted_at', 'max')
        ).reset_index()

        user_summary['average_score'] = user_summary['average_score'].round(1)

        # Search bar filter
        search_query = st.text_input("🔍 Search student by username:", "")
        
        if search_query:
            user_summary = user_summary[user_summary['username'].str.contains(search_query, case=False, na=False)]

        # Display interactive dataframe that faculty can sort
        st.dataframe(
            user_summary.sort_values(by='highest_score', ascending=False),
            column_config={
                "username": "Username",
                "total_quizzes": "Quizzes Taken",
                "highest_score": "Highest Score (%)",
                "average_score": "Average Score (%)",
                "last_attempt": "Last Attempt Date"
            },
            hide_index=True,
            use_container_width=True
        )
        
    else:
        st.info("No data yet. Get students to take their first quiz!")