import sys
import os
import streamlit as st
import qrcode
from io import BytesIO

# Ensure root path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import authentication functions from modules package
from modules.auth import authenticate_user, register_user

def generate_qr(data: str) -> BytesIO:
    """Generates an in-memory QR code image stream."""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#8b5cf6", back_color="#0f172a")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def render():
    # --- HERO BANNER & HEADER ---
    st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem; margin-bottom: 2rem;">
            <h1 style="background: linear-gradient(135deg, #06b6d4, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem;">
                Department of AI & Data Science
            </h1>
            <p style="color: #94a3b8; font-size: 1.2rem; max-width: 700px; margin: 0 auto 1.5rem auto;">
                Empowering future intelligence through real-time quizzes, hackathons, coding challenges, and interactive analytics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- STATS ROW ---
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric(label="Active Participants", value="1,240+", delta="+18% this month")
    with col_s2:
        st.metric(label="Quizzes Completed", value="8,520", delta="+340 this week")
    with col_s3:
        st.metric(label="Coding Submissions", value="4,105", delta="89% Pass Rate")
    with col_s4:
        st.metric(label="Certificates Issued", value="980", delta="Verified QR")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN CONTENT GRID ---
    left_col, right_col = st.columns([1.6, 1])

    with left_col:
        st.subheader("🔥 Highlighted Event")
        
        # Event Glass Banner
        st.markdown("""
            <div class="glass-card" style="border-left: 5px solid #8b5cf6; padding: 1.5rem; margin-bottom: 1.5rem;">
                <span style="background: rgba(139, 92, 246, 0.2); color: #c084fc; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">ACTIVE NOW</span>
                <h2 style="color: #f8fafc; margin: 0.5rem 0;">National AI & ML Speed Hackathon 2026</h2>
                <p style="color: #94a3b8;">Test your skills in Generative AI, Deep Learning optimization, and complex SQL data transformations under tight time constraints.</p>
                <div style="display: flex; gap: 20px; color: #06b6d4; font-weight: 600; font-size: 0.95rem;">
                    <span>⏱️ Duration: 120 Mins</span>
                    <span>🎯 Questions: 30 MCQs + 2 Puzzles</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("📢 Faculty Announcements")
        st.info("📌 **Mid-Semester Data Science Sprint** begins this Friday at 10:00 AM IST. Make sure your roll numbers are updated.")
        st.warning("⚠️ Full-screen exiting or tab switching during active quizzes will be flagged in the Academic Integrity Dashboard.")

    with right_col:
        st.subheader("🔑 Portal Access")
        
        # Auth Tabs
        tab_login, tab_register, tab_qr = st.tabs(["🔑 Login", "📝 Student Register", "📱 Mobile QR"])

        # --- LOGIN TAB ---
        with tab_login:
            st.caption("Students and Faculty log in with assigned credentials.")
            with st.form("login_form"):
                identifier = st.text_input("Username, Email or Roll No", placeholder="e.g., 21AI001 or faculty@dept.edu")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Access Portal", use_container_width=True)

                if submit:
                    if identifier and password:
                        user_info, msg = authenticate_user(identifier, password)
                        
                        if user_info:
                            st.session_state.user = user_info
                            st.session_state.role = user_info['role']
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter both login identifier and password.")

        # --- STUDENT REGISTRATION TAB ---
        with tab_register:
            st.caption("🔒 Registration is restricted to **Students only**. Faculty accounts are pre-provisioned by system administrators.")
            with st.form("registration_form", clear_on_submit=True):
                reg_username = st.text_input("Username / Roll No", placeholder="e.g. 21AI001")
                reg_email = st.text_input("Email Address", placeholder="student@dept.edu")
                reg_password = st.text_input("Password", type="password")
                reg_confirm_pass = st.text_input("Confirm Password", type="password")
                
                # Role selection dropdown removed to enforce Student role
                submit_reg = st.form_submit_button("Create Student Account", use_container_width=True)
                
                if submit_reg:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Please complete all required fields.")
                    elif reg_password != reg_confirm_pass:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.warning("Password must be at least 6 characters long.")
                    else:
                        # Hardcoded "Student" role to prevent unauthorized faculty registration
                        success, msg = register_user(reg_username, reg_email, reg_password, role="Student")
                        if success:
                            st.success("🎉 Student account created! You can now log in.")
                        else:
                            st.error(msg)

        # --- QR CODE TAB ---
        with tab_qr:
            st.write("Scan to access portal on mobile:")
            qr_img = generate_qr("https://ai-ds-portal.university.edu/login")
            st.image(qr_img, width=200, caption="Quick Mobile Entry Point")