"""
VitalBite AI — Main Streamlit Application Entrypoint & Page Router
Personalized, multi-user, privacy-aware digital health & nutrition AI platform.
"""
import streamlit as st

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="VitalBite AI — Health & Nutrition Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.custom_css import inject_custom_css
from services.auth_service import AuthService
from database.repositories import ProfileRepository

# Import UI Components
from components.auth_ui import render_auth_page
from components.dashboard_ui import render_dashboard
from components.profile_ui import render_profile_tab
from components.chat_ui import render_chat_tab
from components.symptom_ui import render_symptom_tab
from components.diet_ui import render_diet_tab
from components.insights_ui import render_insights_tab
from components.history_ui import render_history_tab
from components.documents_ui import render_documents_tab
from components.settings_ui import render_settings_tab

def main():
    # Inject Custom Light Theme & Frosted Glassmorphism CSS
    inject_custom_css()

    # Check Authentication
    if not AuthService.is_authenticated():
        render_auth_page()
        return

    user_id = AuthService.get_current_user_id()
    if not user_id:
        render_auth_page()
        return

    profile = ProfileRepository.get_profile(user_id) or {}
    user_name = profile.get("name") or "Alex Rivera"

    # Top Application Header Bar matching Reference UI
    st.html(f"""
    <div class="vitalbite-header-bar">
        <div class="vitalbite-logo-box">
            <div class="vitalbite-emblem">VB</div>
            <div>
                <h1 class="vitalbite-brand-name">VitalBite AI</h1>
            </div>
        </div>
        <div class="vitalbite-chip-group">
            <span class="vitalbite-chip-beta">BETA</span>
            <span class="vitalbite-chip-assistant">Healthcare SaaS</span>
            <div class="vitalbite-user-pill">
                <span style="font-size: 0.95rem;">👤</span> {user_name}
            </div>
        </div>
    </div>
    """)

    # Unified Navigation Session State
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = "Dashboard"

    def set_nav_tab(tab_name: str):
        st.session_state["nav_selection"] = tab_name
        st.rerun()

    # Sidebar Navigation Menu
    with st.sidebar:
        st.html("""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding-bottom: 0.85rem; border-bottom: 1px solid rgba(186, 230, 253, 0.45); margin-bottom: 0.85rem;">
            <div class="vitalbite-emblem" style="width: 36px; height: 36px; font-size: 1.05rem;">VB</div>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #0F172A; letter-spacing: -0.02em;">VitalBite AI</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">Health & Nutrition SaaS</div>
            </div>
        </div>
        """)

        nav_options = [
            "Dashboard",
            "Profile",
            "Health AI",
            "Symptoms",
            "Nutrition",
            "Insights",
            "History",
            "Documents",
            "Settings"
        ]

        icons = {
            "Dashboard": "📊",
            "Profile": "👤",
            "Health AI": "💬",
            "Symptoms": "⚡",
            "Nutrition": "🥗",
            "Insights": "📈",
            "History": "🕒",
            "Documents": "📄",
            "Settings": "⚙️"
        }

        # Deterministic single-click navigation
        st.radio(
            "Navigation Menu",
            options=nav_options,
            format_func=lambda x: f"{icons.get(x, '')} {x}",
            key="nav_selection",
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            AuthService.sign_out()
            st.rerun()

    # Route Active Tab
    active_tab = st.session_state["nav_selection"]

    if active_tab == "Dashboard":
        render_dashboard(user_id, set_nav_tab)
    elif active_tab == "Profile":
        render_profile_tab(user_id)
    elif active_tab == "Health AI":
        render_chat_tab(user_id)
    elif active_tab == "Symptoms":
        render_symptom_tab(user_id)
    elif active_tab == "Nutrition":
        render_diet_tab(user_id)
    elif active_tab == "Insights":
        render_insights_tab(user_id)
    elif active_tab == "History":
        render_history_tab(user_id)
    elif active_tab == "Documents":
        render_documents_tab(user_id)
    elif active_tab == "Settings":
        render_settings_tab(user_id)

    # Clean, Unobtrusive Footer Medical Disclaimer
    st.html("""
    <div style="margin-top: 2.5rem; text-align: center; border-top: 1px solid rgba(186, 230, 253, 0.45); padding-top: 1.25rem; color: #64748B; font-size: 0.78rem; line-height: 1.5;">
        <b>VitalBite AI — Beta</b> | Educational & Informational Health Guidance | Not a Medical Prescription or Clinical Diagnostic Tool<br>
        For acute medical emergencies in India, immediately dial <b>112</b> or contact your local hospital emergency room.
    </div>
    """)

if __name__ == "__main__":
    main()
