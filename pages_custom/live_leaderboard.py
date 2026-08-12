import streamlit as st
import pandas as pd
from database.connection import fetch_data

def render():
    st.title("🏆 Live Leaderboard")
    st.caption("Real-time rankings sorted by highest accuracy and fastest completion tiebreakers.")
    st.markdown("---")

    # Fetch available quizzes for the dropdown filter
    quizzes_df = fetch_data("SELECT id, quiz_title FROM quizzes;")

    if quizzes_df is None or quizzes_df.empty:
        st.info("📌 No quizzes available to rank yet.")
        return

    # Create quiz filter options dictionary (Title -> ID)
    quiz_options = {row['quiz_title']: row['id'] for _, row in quizzes_df.iterrows()}
    
    # Add an "All Quizzes (Overall)" option at the very top if desired, or keep it per quiz
    selected_quiz_title = st.selectbox("🎯 Filter Leaderboard by Quiz", list(quiz_options.keys()))
    selected_quiz_id = quiz_options[selected_quiz_title]

    st.markdown("<br>", unsafe_allow_html=True)

    # SQL Query filtered by the selected quiz ID
    query = """
        SELECT 
            u.username AS student_name,
            q.quiz_title AS assessment,
            MAX(q.percentage) AS max_pct,
            MAX(q.score) AS max_score,
            q.max_score AS total_possible,
            MIN(q.created_at) AS first_achieved_at
        FROM quiz_attempts q
        JOIN users u ON q.user_id = u.id
        WHERE q.quiz_id = %s
        GROUP BY u.id, q.user_id, u.username, q.quiz_title, q.max_score
        ORDER BY 
            max_pct DESC, 
            max_score DESC, 
            first_achieved_at ASC;
    """

    try:
        raw_data = fetch_data(query, (selected_quiz_id,))
    except Exception as e:
        raw_data = None

    # Handle data format safely
    if isinstance(raw_data, pd.DataFrame):
        df = raw_data
    elif isinstance(raw_data, (list, tuple, dict)):
        df = pd.DataFrame(raw_data)
    else:
        df = pd.DataFrame()

    # Safely check if data exists
    if not df.empty:
        # Format columns for display
        df['Best Score (%)'] = df['max_pct'].apply(lambda x: f"{float(x):.1f}%")
        df['Points'] = df.apply(lambda row: f"{row['max_score']} / {row['total_possible']}", axis=1)
        df['Achieved At'] = pd.to_datetime(df['first_achieved_at']).dt.strftime('%b %d, %H:%M:%S')

        # Generate Rank Symbols
        ranks = []
        for index in range(len(df)):
            if index == 0:
                ranks.append("🥇 1st")
            elif index == 1:
                ranks.append("🥈 2nd")
            elif index == 2:
                ranks.append("🥉 3rd")
            else:
                ranks.append(f"#{index + 1}")
        
        df.insert(0, "Rank", ranks)

        # Podium Display Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="🥇 1st Place", 
                value=df.iloc[0]['student_name'], 
                delta=df.iloc[0]['Best Score (%)']
            )
        if len(df) >= 2:
            with col2:
                st.metric(
                    label="🥈 2nd Place", 
                    value=df.iloc[1]['student_name'], 
                    delta=df.iloc[1]['Best Score (%)']
                )
        if len(df) >= 3:
            with col3:
                st.metric(
                    label="🥉 3rd Place", 
                    value=df.iloc[2]['student_name'], 
                    delta=df.iloc[2]['Best Score (%)']
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Clean Table View
        display_df = df[[
            "Rank", 
            "student_name", 
            "assessment", 
            "Best Score (%)", 
            "Points", 
            "Achieved At"
        ]].rename(columns={
            "student_name": "Student Name",
            "assessment": "Quiz Title"
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"📭 No student submissions recorded for **{selected_quiz_title}** yet. Be the first to take it in the **Quiz Portal**!")