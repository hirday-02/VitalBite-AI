"""
VitalBite AI — Settings & Account Management UI Component
Account info, Preferences, Data Export (JSON/CSV), and Danger Zone Account Deletion.
"""
import json
import pandas as pd
import streamlit as st
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository, AccountRepository
from services.auth_service import AuthService

def render_settings_tab(user_id: str):
    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">⚙️ Settings & Privacy Controls</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Manage your account details, privacy controls, data export, and permanent data deletion.</p>
    </div>
    """)

    user_info = AuthService.get_current_user() or {}
    profile = ProfileRepository.get_profile(user_id) or {}

    s_tab1, s_tab2, s_tab3, s_tab4 = st.tabs(["👤 Account", "🔒 Privacy & AI", "📦 Data Export", "⚠️ Danger Zone"])

    # 1. ACCOUNT DETAILS
    with s_tab1:
        st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800; margin-bottom: 0.75rem;'>Account Overview</h3>")
        st.write(f"**Email:** {user_info.get('email', 'N/A')}")
        st.write(f"**User ID:** `{user_id}`")
        st.write(f"**Name:** {profile.get('name') or 'Not specified'}")

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            AuthService.sign_out()
            st.rerun()

    # 2. PRIVACY & AI CONTROLS
    with s_tab2:
        st.html("""
        <div class="med-card">
            <div class="med-card-title">🔒 Data Privacy & Security Architecture</div>
            <ul style="color: #475569; font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                <li><b style="color: #0F172A;">PostgreSQL Row Level Security (RLS):</b> All your health profiles, chats, symptom checks, and diet plans are isolated at the database level. User A can never access User B's data under any circumstance.</li>
                <li><b style="color: #0F172A;">AI Data Policy:</b> Prompts sent to Google Gemini contain relevant health context (age, allergies, symptoms) to provide tailored responses. We do not use your private records for model training.</li>
                <li><b style="color: #0F172A;">Zero Secrets Exposure:</b> Authentication and database connections strictly use public client credentials. Service role credentials are never exposed client-side.</li>
            </ul>
        </div>
        """)

    # 3. DATA EXPORT
    with s_tab3:
        st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800;'>Export Your Personal Data</h3>")
        st.caption("Download a complete copy of your profile, symptom checks, diet plans, and chat logs in JSON or CSV format.")

        assessments = SymptomRepository.list_assessments(user_id)
        plans = DietRepository.list_plans(user_id)
        sessions = ChatRepository.list_sessions(user_id)

        export_obj = {
            "user_id": user_id,
            "profile": profile,
            "symptom_assessments": assessments,
            "diet_plans": plans,
            "chat_sessions": sessions
        }

        json_bytes = json.dumps(export_obj, indent=2).encode("utf-8")
        st.download_button(
            "📥 Download Complete Data Backup (JSON)",
            data=json_bytes,
            file_name="vitalbite_my_data_export.json",
            mime="application/json",
            use_container_width=True
        )

        if assessments:
            df_sym = pd.DataFrame(assessments)
            csv_bytes = df_sym.to_csv(index=False).encode("utf-8")
            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
            st.download_button(
                "📊 Export Symptom Assessments (CSV)",
                data=csv_bytes,
                file_name="vitalbite_symptoms.csv",
                mime="text/csv",
                use_container_width=True
            )

    # 4. DANGER ZONE → ACCOUNT DELETION
    with s_tab4:
        st.html("""
        <div class="emergency-overlay" style="border-color: #EF4444; background: rgba(254, 242, 242, 0.95);">
            <div style="font-size: 1.15rem; font-weight: 800; color: #DC2626; margin-bottom: 0.4rem;">
                ⚠️ Permanent Account Deletion
            </div>
            <div style="font-size: 0.9rem; color: #991B1B; line-height: 1.5; margin-bottom: 0.85rem;">
                Deleting your account will permanently erase your profile, all consultation threads, symptom records, diet plans, and associated metrics. This action is <b>irreversible</b>.
            </div>
        </div>
        """)

        confirm_text = st.text_input("Type 'DELETE MY ACCOUNT' to confirm:", placeholder="DELETE MY ACCOUNT")
        delete_button = st.button("🔴 Permanently Delete Account", use_container_width=True)

        if delete_button:
            if confirm_text.strip() != "DELETE MY ACCOUNT":
                st.error("Please type 'DELETE MY ACCOUNT' exactly as shown to confirm deletion.")
            else:
                success = AccountRepository.delete_all_user_data(user_id)
                if success:
                    AuthService.sign_out()
                    st.success("Your account and all associated data have been permanently deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete account. Please try again.")
