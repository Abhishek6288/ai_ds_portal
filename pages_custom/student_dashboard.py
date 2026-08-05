import streamlit as st
import pandas as pd
from database.connection import fetch_data
from modules.analytics import build_radar_performance_chart

def render():
    st.title("🎓 Student Dashboard")
    
    # 1. Safely retrieve user data from session state with fallbacks
    user = st.session_state.get("user", {})
    student_id = user.get("id", None)
    username = user.get("username", "Student")
    email = user.get("email", "")
    
    # Dynamic profile details (falling back to user data or defaults)
    full_name = user.get("full_name", username)
    roll_number = user.get("roll_number", "DS2026-001")
    dept_name = user.get("dept_name", "AI & Data Science")
    academic_year = user.get("academic_year", "3")

    # --- WELCOME CARD ---
    st.markdown(f"""
        <div class="glass-card" style="display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; margin-bottom: 2rem;">
            <div>
                <h2 style="color: #f8fafc; margin: 0;">Welcome back, {full_name} 👋</h2>
                <p style="color: #94a3b8; margin: 5px 0 0 0;">
                    Roll No: <b style="color:#06b6d4">{roll_number}</b> | Department: <b style="color:#8b5cf6">{dept_name}</b> | Year: <b>Year {academic_year}</b>
                </p>
            </div>
            <div style="background: rgba(139, 92, 246, 0.2); border: 1px solid #8b5cf6; padding: 8px 18px; border-radius: 20px; color: #c084fc; font-weight: bold;">
                Status: Active
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- METRICS & BADGES ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overall Score", "84.5%", delta="+2.3%")
    with m2:
        st.metric("Department Rank", "#4", delta="Top 5%")
    with m3:
        st.metric("Quizzes Completed", "12")
    with m4:
        st.metric("Certificates Earned", "3")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN CONTENT LAYOUT ---
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("📚 Topic-Wise Mastery")
        categories = ["Python", "SQL", "Data Science", "Machine Learning", "Deep Learning", "GenAI"]
        scores = [90, 85, 78, 88, 65, 92]  # Demo competency scores
        
        # Render Radar Chart from analytics engine
        try:
            fig = build_radar_performance_chart(categories, scores)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning("Unable to render Radar Chart. Please ensure Plotly is installed.")

        st.subheader("🏅 Achievement Badges")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <span style="font-size: 2rem;">⚡</span>
                    <h4 style="margin: 5px 0; color: #f8fafc;">Fast Solver</h4>
                    <caption style="color:#94a3b8;">Finished Quiz under 5 mins</caption>
                </div>
            """, unsafe_allow_html=True)
        with b2:
            st.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <span style="font-size: 2rem;">🎯</span>
                    <h4 style="margin: 5px 0; color: #f8fafc;">Bullseye</h4>
                    <caption style="color:#94a3b8;">100% Accuracy in SQL</caption>
                </div>
            """, unsafe_allow_html=True)
        with b3:
            st.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <span style="font-size: 2rem;">🔥</span>
                    <h4 style="margin: 5px 0; color: #f8fafc;">Streak Master</h4>
                    <caption style="color:#94a3b8;">5 consecutive events</caption>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.subheader("⚡ Available Activities")
        
        # Sample Active Event Card
        st.markdown("""
            <div class="glass-card" style="margin-bottom: 1rem;">
                <h4 style="color:#06b6d4; margin: 0 0 5px 0;">Python & ML Sprint Quiz</h4>
                <p style="color:#94a3b8; font-size:0.85rem; margin-bottom: 10px;">15 Questions | 20 Minutes</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quiz Now 🚀", use_container_width=True):
            st.info("Navigate to 'Quiz Portal' from the sidebar menu to begin!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📜 Recent Certificates")
        
        # Fetch certificates safely using MySQL %s parameter placeholders
        if student_id:
            certs_df = fetch_data("SELECT * FROM certificates WHERE student_id = %s", (student_id,))
            if certs_df is not None and not certs_df.empty:
                for idx, c in certs_df.iterrows():
                    st.write(f"🎓 **{c.get('cert_type', 'Certificate')}** - Event ID: {c.get('event_id', 'N/A')}")
            else:
                st.caption("No certificates issued yet. Complete a quiz to earn your first certificate!")
        else:
            st.caption("Log in as a registered student to view issued certificates.")
3
