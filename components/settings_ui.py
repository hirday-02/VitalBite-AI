"""
VitalBite AI — Settings & Account Management UI Component
Account info, Preferences, Data Export (JSON/CSV), Danger Zone Account Deletion for real users,
and seamless Exit Demo controls for demonstration users.
"""
import json
import pandas as pd
import streamlit as st
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository, AccountRepository
from services.auth_service import AuthService

def render_settings_tab(user_id: str):
    is_demo = AuthService.is_demo_mode()

    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">⚙️ Settings & Privacy Controls</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Manage your account details, privacy controls, data export, and session settings.</p>
    </div>
    """)

    user_info = AuthService.get_current_user() or {}
    profile = ProfileRepository.get_profile(user_id) or {}

    s_tab1, s_tab2, s_tab3, s_tab4 = st.tabs([
        "👤 Account",
        "🔒 Privacy & AI",
        "📦 Data Export",
        "🚪 Session & Actions" if is_demo else "⚠️ Danger Zone"
    ])

    # 1. ACCOUNT DETAILS
    with s_tab1:
        st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800; margin-bottom: 0.75rem;'>Account Overview</h3>")
        if is_demo:
            st.html("""
            <div class="med-card" style="border-left: 4px solid #7E22CE;">
                <div style="font-weight: 800; color: #7E22CE; font-size: 1.05rem;">✨ Demo Mode Active</div>
                <div style="font-size: 0.88rem; color: #475569; margin-top: 0.35rem; line-height: 1.5;">
                    You are currently exploring VitalBite AI in <b>Demo Mode</b> using sample data.
                    No personal data is collected or saved to the production database.
                </div>
            </div>
            """)
        
        st.write(f"**Email:** {user_info.get('email', 'alex.rivera@example.com' if is_demo else 'N/A')}")
        st.write(f"**User ID:** `{user_id}`")
        st.write(f"**Name:** {profile.get('name') or ('Alex Rivera' if is_demo else 'Not specified')}")

        st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
        if is_demo:
            if st.button("🚪 Exit Demo Mode", use_container_width=True, key="btn_settings_exit_demo_top"):
                AuthService.exit_demo_mode()
                st.rerun()
        else:
            if st.button("🚪 Sign Out", use_container_width=True, key="btn_settings_signout"):
                AuthService.sign_out()
                st.rerun()

    # 2. PRIVACY & AI CONTROLS
    with s_tab2:
        st.html("""
        <div class="med-card">
            <div class="med-card-title">🔒 Data Privacy & Security Architecture</div>
            <ul style="color: #475569; font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                <li><b style="color: #0F172A;">PostgreSQL Row Level Security (RLS):</b> In production mode, all your health profiles, chats, symptom checks, and diet plans are strictly isolated by <code>user_id</code>. User A can never access User B's records.</li>
                <li><b style="color: #0F172A;">Demo Mode Isolation:</b> Demo records exist strictly in local session memory. Zero demo interactions are written to Supabase.</li>
                <li><b style="color: #0F172A;">AI Data Policy:</b> Prompts sent to Google Gemini contain relevant health context (age, allergies, symptoms) to provide tailored responses. We do not use your private records for model training.</li>
                <li><b style="color: #0F172A;">Zero Secrets Exposure:</b> Authentication and database connections strictly use public client credentials. Service role credentials are never exposed client-side.</li>
            </ul>
        </div>
        """)

    # 3. DATA EXPORT
    with s_tab3:
        st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800;'>Export Personal Data Backup</h3>")
        st.caption("Download a complete copy of profile details, symptom checks, diet plans, and chat logs in JSON or CSV format.")

        assessments = SymptomRepository.list_assessments(user_id)
        plans = DietRepository.list_plans(user_id)
        sessions = ChatRepository.list_sessions(user_id)

        export_obj = {
            "user_id": user_id,
            "mode": "Demo Mode" if is_demo else "Authenticated User",
            "profile": profile,
            "symptom_assessments": assessments,
            "diet_plans": plans,
            "chat_sessions": sessions
        }

        json_bytes = json.dumps(export_obj, indent=2).encode("utf-8")
        st.download_button(
            "📥 Download Complete Data Backup (JSON)",
            data=json_bytes,
            file_name="vitalbite_demo_data_export.json" if is_demo else "vitalbite_my_data_export.json",
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

    # 4. DANGER ZONE / SESSION EXIT
    with s_tab4:
        if is_demo:
            st.html("""
            <div class="med-card" style="border-left: 4px solid #0284C7;">
                <div style="font-size: 1.15rem; font-weight: 800; color: #0284C7; margin-bottom: 0.35rem;">
                    ✨ Demo Session Management
                </div>
                <div style="font-size: 0.9rem; color: #475569; line-height: 1.5; margin-bottom: 1rem;">
                    Demo Mode is temporary. Any edits made to the demo profile or generated diet plans will be cleared when you exit.
                </div>
            </div>
            """)
            if st.button("🚪 Exit Demo Mode & Return to Sign In", use_container_width=True, key="btn_settings_exit_demo_bottom"):
                AuthService.exit_demo_mode()
                st.rerun()
        else:
            st.html("""
            <div class="emergency-overlay" style="border-color: #EF4444; background: rgba(254, 242, 242, 0.95);">
                <div style="font-size: 1.15rem; font-weight: 800; color: #DC2626; margin-bottom: 0.4rem;">
                    ⚠️ Permanent Account Deletion
                </div>
                <div style="font-size: 0.9rem; color: #991B1B; line-height: 1.5; margin-bottom: 0.85rem;">
                    Deleting your account will permanently erase your profile, all consultation threads, symptom records, diet plans, and associated metrics from the database. This action is <b>irreversible</b>.
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
