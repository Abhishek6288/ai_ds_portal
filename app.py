import sys
import os

# Force Python to recognize the root project folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from streamlit_option_menu import option_menu

# 1. Configuration & Page Setup (Call ONLY ONCE)
st.set_page_config(
    page_title="AI & DS Activity Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom CSS
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/css/style.css")

# 3. Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None  # 'Student', 'Faculty', or None

# 4. Dynamic Sidebar & Navigation Menu
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 10px 0;'>
            <h2 style='color: #8b5cf6; margin:0;'>⚡ AI & DS PORTAL</h2>
            <p style='color: #94a3b8; font-size: 0.85rem;'>Department of Data Science</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.user:
        user = st.session_state.user
        st.write(f"👤 **{user.get('username', 'User')}** ({st.session_state.role})")
        st.markdown("---")

    # Build menu options dynamically
    if st.session_state.user is None:
        menu_options = ["Home"]
        icons = ["house"]
    else:
        if st.session_state.role == "Student":
            menu_options = ["Dashboard", "Quiz Portal"]
            icons = ["person-badge", "pencil-square"]
        elif st.session_state.role == "Faculty":
            menu_options = ["Dashboard", "Faculty Admin", "Integrity Monitor", "Leaderboard", "Analytics"]
            icons = ["person-badge", "gear", "shield-exclamation", "trophy", "bar-chart"]
        else:
            menu_options = ["Home"]
            icons = ["house"]

    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=icons,
        default_index=0,
        styles={
            "container": {"padding": "5px!important", "background-color": "transparent"},
            "icon": {"color": "#06b6d4", "font-size": "18px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "2px", "--hover-color": "rgba(139, 92, 246, 0.2)"},
            "nav-link-selected": {"background-color": "#8b5cf6", "font-weight": "600"},
        }
    )

    if st.session_state.user:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.role = None
            st.rerun()

# 5. Route Handling Logic
if selected == "Home":
    if st.session_state.user is not None:
        import pages_custom.student_dashboard as student_dashboard
        student_dashboard.render()
    else:
        import pages_custom.landing as landing
        landing.render()

elif selected == "Dashboard":
    if st.session_state.role == "Student":
        import pages_custom.student_dashboard as student_dashboard
        student_dashboard.render()
    elif st.session_state.role == "Faculty":
        st.title("👨‍🏫 Faculty Overview Dashboard")
        st.info("Welcome to the faculty portal. Use the sidebar tabs to manage quizzes, view the leaderboard, or check analytics.")

elif selected == "Faculty Admin" and st.session_state.role == "Faculty":
    import pages_custom.faculty_admin as faculty_admin
    faculty_admin.render()

elif selected == "Integrity Monitor" and st.session_state.role == "Faculty":
    # Optional placeholder if you decide to implement it later
    st.title("🛡️ Academic Integrity Monitor")
    st.info("Proctoring and tab-switch logs will appear here.")

elif selected == "Quiz Portal" and st.session_state.role == "Student":
    import pages_custom.quiz_module as quiz_module
    quiz_module.render()

elif selected == "Leaderboard" and st.session_state.role == "Faculty":
    import pages_custom.live_leaderboard as leaderboard
    leaderboard.render()

elif selected == "Analytics" and st.session_state.role == "Faculty":
    import pages_custom.analytics as analytics
    analytics.render()

else:
    import pages_custom.landing as landing
    landing.render()