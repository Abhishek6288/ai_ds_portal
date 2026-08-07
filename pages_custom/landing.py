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
    # --- INJECT CUSTOM RESPONSIVE CSS ---
    st.markdown("""
        <style>
            /* Custom Responsive Styles */
            .hero-card {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.7));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 2rem 1.5rem;
                text-align: center;
                backdrop-filter: blur(12px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 1.5rem;
            }
            .hero-title {
                background: linear-gradient(135deg, #38bdf8, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: clamp(2rem, 5vw, 3rem);
                font-weight: 800;
                letter-spacing: -0.5px;
                margin-bottom: 0.5rem;
            }
            .event-badge {
                display: inline-block;
                background: rgba(139, 92, 246, 0.2);
                border: 1px solid rgba(168, 85, 247, 0.4);
                color: #c084fc;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
            }
            .login-container {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 1.25rem;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            }
            /* Responsive layout tweak for mobile */
            @media (max-width: 768px) {
                .hero-card { padding: 1.5rem 1rem; }
                .stTabs [data-baseweb="tab-list"] { gap: 4px; }
            }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO HEADER ---
    st.markdown("""
        <div class="hero-card">
            <span class="event-badge">Official Academic Portal</span>
            <h1 class="hero-title">Department of AI & Data Science</h1>
            <p style="color: #94a3b8; font-size: 1.1rem; max-width: 650px; margin: 0 auto;">
                Empowering future intelligence with real-time quizzes, competitive hackathons, and interactive analytics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- MAIN RESPONSIVE GRID (Mobile First: Login comes right at the top on phones) ---
    col_access, col_content = st.columns([1.1, 1.4], gap="large")

    # --- RIGHT COLUMN ON DESKTOP / TOP ON MOBILE: PORTAL ACCESS ---
    with col_access:
        st.subheader("🔑 Portal Access")
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Tabs for Auth
        tab_login, tab_register, tab_qr = st.tabs(["🔑 Login", "📝 Student Register", "📱 Mobile QR"])

        # --- LOGIN TAB ---
        with tab_login:
            st.caption("Access point for Students & Faculty members.")
            with st.form("login_form"):
                identifier = st.text_input("Username, Email or Roll No", placeholder="e.g. 21AI001 or prof@dept.edu")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Sign In to Portal", use_container_width=True)

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
                        st.warning("Please fill in all fields.")

        # --- STUDENT REGISTRATION TAB ---
        with tab_register:
            st.caption("🔒 Registration is **restricted to Students**. Faculty accounts are issued by System Admins.")
            with st.form("registration_form", clear_on_submit=True):
                reg_username = st.text_input("Username / Roll No", placeholder="e.g. 21AI001")
                reg_email = st.text_input("Email Address", placeholder="student@example.com")
                reg_password = st.text_input("Password", type="password", placeholder="••••••••")
                reg_confirm_pass = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                # Hardcoded strictly to Student role
                submit_reg = st.form_submit_button("Create Student Account", use_container_width=True)
                
                if submit_reg:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Please fill out all required fields.")
                    elif reg_password != reg_confirm_pass:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        success, msg = register_user(reg_username, reg_email, reg_password, role="Student")
                        if success:
                            st.success("🎉 Account created successfully! Please sign in.")
                        else:
                            st.error(msg)

        # --- QR CODE TAB ---
        with tab_qr:
            st.write("Scan to open on mobile browser:")
            qr_img = generate_qr("https://ai-ds-portal.university.edu/login")
            st.image(qr_img, width=180, caption="Quick Link QR")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- LEFT COLUMN ON DESKTOP / BOTTOM ON MOBILE: HIGHLIGHTS & ANNOUNCEMENTS ---
    with col_content:
        st.subheader("🔥 Active Events")
        
        st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.6); border-left: 4px solid #a855f7; padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem;">
                <span class="event-badge">LIVE NOW</span>
                <h3 style="color: #f8fafc; margin: 0.4rem 0;">National AI & ML Speed Hackathon 2026</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0.8rem;">
                    Test your skills in Generative AI, Deep Learning optimization, and complex SQL data transformations under strict time limits.
                </p>
                <div style="display: flex; gap: 15px; color: #38bdf8; font-weight: 600; font-size: 0.85rem; flex-wrap: wrap;">
                    <span>⏱️ Duration: 120 Mins</span>
                    <span>🎯 30 MCQs + 2 Code Puzzles</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.subheader("📢 Department Notices")
        st.info("📌 **Mid-Semester Data Science Sprint** starts Friday at 10:00 AM IST. Update your profiles prior to session launch.")
        st.warning("⚠️ Proctoring Active: Tab-switching during quizzes triggers alerts on the Academic Integrity Dashboard.")

    # --- STATS ROW AT BOTTOM ---
    st.markdown("---")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric(label="Active Participants", value="1,240+", delta="+18% this month")
    with col_s2:
        st.metric(label="Quizzes Completed", value="8,520", delta="+340 this week")
    with col_s3:
        st.metric(label="Submissions", value="4,105", delta="89% Pass Rate")
    with col_s4:
        st.metric(label="Certificates", value="980", delta="Verified QR")