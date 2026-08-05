import streamlit as st
import pandas as pd
from database.connection import fetch_data

def safe_query_df(query):
    """Safely converts fetch_data results into a valid pandas DataFrame."""
    try:
        res = fetch_data(query)
        if isinstance(res, pd.DataFrame):
            return res
        elif isinstance(res, (list, tuple, dict)):
            return pd.DataFrame(res)
    except Exception:
        pass
    return pd.DataFrame()

def get_analytics_summary():
    """Fetches high-level metrics across all students and events from MySQL."""
    total_users_df = safe_query_df("SELECT COUNT(*) AS total FROM users WHERE role = 'Student'")
    total_results_df = safe_query_df("SELECT COUNT(*) AS total, AVG(score) as avg_score FROM student_results")
    total_events_df = safe_query_df("SELECT COUNT(*) AS total FROM events")

    # Safely extract total_students
    if not total_users_df.empty and 'total' in total_users_df.columns:
        total_students = int(total_users_df.iloc[0]['total']) if pd.notna(total_users_df.iloc[0]['total']) else 0
    else:
        total_students = 0

    # Safely extract total_submissions and avg_score
    if not total_results_df.empty:
        tot_val = total_results_df.iloc[0].get('total', 0)
        avg_val = total_results_df.iloc[0].get('avg_score', 0.0)
        
        total_submissions = int(tot_val) if pd.notna(tot_val) else 0
        avg_score = float(avg_val) if pd.notna(avg_val) else 0.0
    else:
        total_submissions = 0
        avg_score = 0.0

    # Safely extract total_events
    if not total_events_df.empty and 'total' in total_events_df.columns:
        total_events = int(total_events_df.iloc[0]['total']) if pd.notna(total_events_df.iloc[0]['total']) else 0
    else:
        total_events = 0

    return {
        "students": total_students,
        "submissions": total_submissions,
        "avg_score": round(avg_score, 1),
        "events": total_events
    }

def get_event_performance():
    """Fetches score breakdown grouped by event type."""
    query = """
        SELECT 
            e.title AS 'Event Title',
            e.event_type AS 'Type',
            COUNT(r.id) AS 'Submissions',
            ROUND(AVG(r.score), 1) AS 'Average Score',
            MAX(r.score) AS 'Highest Score'
        FROM events e
        LEFT JOIN student_results r ON e.id = r.event_id
        GROUP BY e.id, e.title, e.event_type
        ORDER BY Submissions DESC
    """
    return safe_query_df(query)

def render():
    st.title("📈 Department Analytics Hub")
    st.write("Real-time performance analytics, participation rates, and event outcomes across the AI & DS department.")

    # Refresh Control
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    # --- TOP LEVEL METRICS ---
    metrics = get_analytics_summary()
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Registered Students", value=metrics["students"])
    with m2:
        st.metric(label="Active Events", value=metrics["events"])
    with m3:
        st.metric(label="Total Submissions", value=metrics["submissions"])
    with m4:
        st.metric(label="Avg Quiz Score", value=f"{metrics['avg_score']} pts")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- DETAILED EVENT ANALYTICS ---
    st.subheader("📊 Event Performance Breakdown")
    
    df_events = get_event_performance()

    if df_events.empty:
        st.info("ℹ️ No event analytics available yet. Check back once students begin completing activities.")
        return

    # Render table and chart side by side
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.write("**Submissions per Event**")
        if "Submissions" in df_events.columns and df_events["Submissions"].sum() > 0:
            chart_df = df_events.set_index("Event Title")[["Submissions"]]
            st.bar_chart(chart_df)
        else:
            st.caption("No submission chart data available yet.")

    with col_table:
        st.write("**Event Summaries**")
        st.dataframe(
            df_events,
            use_container_width=True,
            hide_index=True
        )