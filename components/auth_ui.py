"""
VitalBite AI — Authentication UI Component
Renders clean, frosted glassmorphic login, registration, password reset, and one-click Demo Mode exploration.
"""
import streamlit as st
from services.auth_service import AuthService

def render_auth_page():
    st.html("""
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 18px; background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%); font-weight: 800; font-size: 1.8rem; color: #FFFFFF; box-shadow: 0 8px 24px rgba(14, 165, 233, 0.35); margin-bottom: 0.85rem;">
            VB
        </div>
        <h1 style="color: #0F172A; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.35rem; letter-spacing: -0.03em;">VitalBite AI</h1>
        <p style="color: #475569; font-size: 1.05rem; margin-bottom: 0.65rem; font-weight: 500;">Your intelligent companion for everyday health & nutrition.</p>
        <span class="vitalbite-chip-beta" style="font-size: 0.8rem; padding: 0.3rem 0.85rem;">BETA</span>
    </div>
    """)

    col1, col_center, col3 = st.columns([1, 1.85, 1])

    with col_center:
        st.html("""
        <div class="med-card" style="padding: 1.5rem 1.85rem; border-radius: 22px;">
            <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">Welcome to VitalBite AI</div>
            <div style="font-size: 0.84rem; color: #64748B; margin-bottom: 1.25rem;">Sign in to access your private health command center, or explore Demo Mode instantly.</div>
        """)

        tab_login, tab_signup, tab_reset = st.tabs(["🔒 Sign In", "📝 Create Account", "🔑 Reset Password"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="name@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

                if submitted:
                    if not email or not password:
                        st.error("Please provide both email and password.")
                    else:
                        success, msg = AuthService.sign_in_email(email, password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with tab_signup:
            with st.form("signup_form"):
                full_name = st.text_input("Full Name", placeholder="e.g. Alex Rivera")
                email_up = st.text_input("Email Address", placeholder="name@example.com")
                password_up = st.text_input("Password (min 6 chars)", type="password")
                password_confirm = st.text_input("Confirm Password", type="password")
                submitted_up = st.form_submit_button("Create Account", use_container_width=True)

                if submitted_up:
                    if not email_up or not password_up:
                        st.error("Please fill in all required fields.")
                    elif password_up != password_confirm:
                        st.error("Passwords do not match.")
                    elif len(password_up) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success, msg = AuthService.sign_up_email(email_up, password_up, full_name)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with tab_reset:
            with st.form("reset_form"):
                email_res = st.text_input("Enter your account email", placeholder="name@example.com")
                submitted_res = st.form_submit_button("Send Password Reset Email", use_container_width=True)

                if submitted_res:
                    if not email_res:
                        st.error("Please provide your email address.")
                    else:
                        success, msg = AuthService.reset_password(email_res)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

        # Dedicated Demo Mode Entry Card (Prominent yet secondary)
        st.markdown("<div style='margin-top: 1.5rem; border-top: 1px solid rgba(186, 230, 253, 0.6); padding-top: 1.25rem;'></div>", unsafe_allow_html=True)
        st.html("""
        <div style="text-align: center; margin-bottom: 0.65rem;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">OR EXPLORE WITHOUT SIGNING IN</span>
        </div>
        """)

        if st.button("✨ Explore Demo", use_container_width=True, key="btn_explore_demo"):
            AuthService.start_demo_mode()
            st.rerun()

        st.html("""
        <div style="text-align: center; font-size: 0.78rem; color: #64748B; margin-top: 0.4rem; font-weight: 500;">
            Demo Mode — Explore VitalBite AI with sample data. Demo data is temporary and not saved.
        </div>
        """)

        st.html("</div>")

    # Medical Disclaimer Notice
    st.html("""
    <div class="disclaimer-box" style="max-width: 620px; margin: 1.5rem auto 0 auto; text-align: center;">
        📌 <b>VitalBite AI is currently in beta.</b> Information provided is for general educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical advice.
    </div>
    """)
