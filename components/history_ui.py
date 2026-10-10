"""
VitalBite AI — History & Downloadable Reports UI Component
Categorized consultation history viewer with ReportLab PDF export and individual deletion actions.
"""
import streamlit as st
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository
from services.report_service import ReportService
from utils.icons import get_svg_icon

def render_history_tab(user_id: str):
    history_svg = get_svg_icon("history", color="#0284C7", size=22)

    st.html(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em; display: flex; align-items: center; gap: 0.5rem;">
            {history_svg} Consultation & Health History
        </h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Review previous conversations, symptom assessments, diet plans, and download PDF summaries.</p>
    </div>
    """)

    profile = ProfileRepository.get_profile(user_id) or {}
    user_name = profile.get("name") or "Alex Rivera"

    h_tab1, h_tab2, h_tab3 = st.tabs(["Symptom Assessments", "Diet Plans", "Chat Threads"])

    # 1. SYMPTOM ASSESSMENTS HISTORY
    with h_tab1:
        assessments = SymptomRepository.list_assessments(user_id)
        if not assessments:
            st.info("No recorded symptom assessments yet.")
        else:
            for idx, item in enumerate(assessments):
                title = f"Assessment ({item.get('created_at', '')[:10]}): {item.get('symptoms', '')[:40]}..."
                with st.expander(title):
                    st.write(f"**Symptoms:** {item.get('symptoms')}")
                    st.write(f"**Duration:** {item.get('duration') or 'Not specified'} | **Severity:** {item.get('severity') or 'Not specified'}/10")
                    st.markdown("---")
                    st.markdown(item.get("analysis", ""))

                    col_pdf, col_del = st.columns([3, 1])
                    with col_pdf:
                        pdf_bytes = ReportService.generate_pdf_report(
                            title="Symptom Assessment Summary",
                            report_type="symptom_assessment",
                            content_text=f"SYMPTOMS REPORTED:\n{item.get('symptoms')}\nDuration: {item.get('duration')}\nSeverity: {item.get('severity')}/10\n\nASSESSMENT DETAILS:\n{item.get('analysis')}",
                            user_name=user_name,
                            profile=profile
                        )
                        st.download_button(
                            "Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"vitalbite_symptom_report_{item.get('id', '')[:8]}.pdf",
                            mime="application/pdf",
                            key=f"dl_sym_{idx}"
                        )
                    with col_del:
                        if st.button("Delete Entry", key=f"del_sym_{idx}"):
                            SymptomRepository.delete_assessment(user_id, item["id"])
                            st.success("Entry deleted.")
                            st.rerun()

    # 2. DIET PLANS HISTORY
    with h_tab2:
        plans = DietRepository.list_plans(user_id)
        if not plans:
            st.info("No saved diet plans yet.")
        else:
            for idx, item in enumerate(plans):
                title = f"Diet Plan ({item.get('created_at', '')[:10]}): {item.get('goal')} ({item.get('diet_type')})"
                with st.expander(title):
                    st.write(f"**Goal:** {item.get('goal')} | **Diet Type:** {item.get('diet_type')}")
                    st.markdown("---")
                    st.markdown(item.get("plan_text", ""))

                    col_pdf, col_del = st.columns([3, 1])
                    with col_pdf:
                        pdf_bytes = ReportService.generate_pdf_report(
                            title=f"7-Day Diet Plan — {item.get('goal')}",
                            report_type="diet_plan",
                            content_text=item.get("plan_text", ""),
                            user_name=user_name,
                            profile=profile
                        )
                        st.download_button(
                            "Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"vitalbite_diet_plan_{item.get('id', '')[:8]}.pdf",
                            mime="application/pdf",
                            key=f"dl_diet_{idx}"
                        )
                    with col_del:
                        if st.button("Delete Plan", key=f"del_diet_{idx}"):
                            DietRepository.delete_plan(user_id, item["id"])
                            st.success("Plan deleted.")
                            st.rerun()

    # 3. CHAT THREADS HISTORY
    with h_tab3:
        sessions = ChatRepository.list_sessions(user_id)
        if not sessions:
            st.info("No chat threads recorded.")
        else:
            for idx, sess in enumerate(sessions):
                title = f"Chat Thread: {sess.get('title')} ({sess.get('created_at', '')[:10]})"
                with st.expander(title):
                    msgs = ChatRepository.get_messages(user_id, sess["id"])
                    for m in msgs:
                        st.markdown(f"**{'User' if m.get('sender') == 'user' else 'VitalBite AI'}:** {m.get('message')}")

                    if st.button("Delete Chat Thread", key=f"del_sess_{idx}"):
                        ChatRepository.delete_session(user_id, sess["id"])
                        st.success("Thread deleted.")
                        st.rerun()
