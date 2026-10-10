"""
VitalBite AI — Symptom Assessment UI Component
Guided medical questionnaire with emergency 112 triage escalation, structured analysis,
and resilient Demo Mode fallback evaluations.
"""
import streamlit as st
from database.repositories import ProfileRepository, SymptomRepository
from services.ai_service import AIService, build_symptom_assessment_prompt
from services.auth_service import AuthService
from services.safety_service import SafetyService
from services.demo_service import get_fallback_symptom_assessment
from utils.icons import get_svg_icon

def render_symptom_tab(user_id: str):
    is_demo = AuthService.is_demo_mode()
    symptom_svg = get_svg_icon("symptom", color="#0D9488", size=22)
    emergency_svg = get_svg_icon("emergency", color="#DC2626", size=20)
    alert_svg = get_svg_icon("alert", color="#DC2626", size=16)

    st.html(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em; display: flex; align-items: center; gap: 0.5rem;">
            {symptom_svg} Guided Symptom Assessment
        </h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Describe what you are experiencing to receive structured health information and safe triage guidance.</p>
    </div>
    """)

    profile = ProfileRepository.get_profile(user_id) or {}
    user_name = profile.get("name") or ("Alex" if is_demo else "User")

    with st.form("symptom_form"):
        st.html("<h4 style='color: #0284C7; font-weight: 800; font-size: 1.05rem; margin-bottom: 0.5rem;'>Describe Your Current Symptoms</h4>")
        symptoms_text = st.text_area(
            "What symptoms are you experiencing?",
            placeholder="e.g. Mild headache, low-grade fever, sore throat when swallowing",
            height=110,
            label_visibility="collapsed"
        )

        col_d, col_s = st.columns(2)
        with col_d:
            st.html("<div style='font-size: 0.84rem; color: #1E293B; font-weight: 700; margin-bottom: 0.25rem;'>Duration</div>")
            duration_str = st.text_input("Duration", placeholder="e.g. 2 days, 1 week", label_visibility="collapsed")
        with col_s:
            st.html("<div style='font-size: 0.84rem; color: #1E293B; font-weight: 700; margin-bottom: 0.25rem;'>Severity Rating (1 - 10)</div>")
            severity_str = st.select_slider(
                "Severity Rating",
                options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                value="3" if is_demo else "4",
                label_visibility="collapsed"
            )

        st.markdown("<div style='margin-top: 0.85rem;'></div>", unsafe_allow_html=True)
        submit_symptoms = st.form_submit_button("Run Guided Assessment", use_container_width=True)

    if submit_symptoms:
        if not symptoms_text.strip():
            st.error("Please describe your symptoms before requesting an assessment.")
            return

        # 1. Multi-layer Emergency Safety Check
        safety_eval = SafetyService.evaluate_emergency(symptoms_text)
        is_high_severity = int(severity_str) >= 9

        if safety_eval["is_emergency"] or is_high_severity:
            # UNMISTAKABLE EMERGENCY OVERRIDE
            st.html(f"""
            <div class="emergency-overlay">
                <div style="font-size: 1.25rem; font-weight: 800; color: #DC2626; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.5rem;">
                    {emergency_svg} EMERGENCY ALERT — URGENT MEDICAL EVALUATION REQUIRED
                </div>
                <div style="font-size: 0.95rem; color: #991B1B; line-height: 1.5; margin-bottom: 1rem; font-weight: 500;">
                    Your reported symptoms (or high severity rating) indicate potential emergency warning signs.<br>
                    <b>Do NOT wait or rely solely on AI guidance for severe symptoms.</b>
                </div>
                <a href="tel:{safety_eval.get('primary_number', '112')}" class="emergency-btn">
                    CALL {safety_eval.get('primary_number', '112')} IMMEDIATELY
                </a>
            </div>
            """)

        # 2. AI Assessment Generation
        with st.spinner("VitalBite AI is reviewing health context against evidence guidelines..."):
            prompt, sys_prompt = build_symptom_assessment_prompt(symptoms_text, duration_str, severity_str, profile)
            analysis_result = AIService.generate_response(
                prompt=prompt,
                system_instruction=sys_prompt,
                is_demo=is_demo,
                user_name=user_name
            )

            # If Gemini service returned unavailable and we're in demo mode, use the structured fallback
            if analysis_result.startswith("SERVICE_UNAVAILABLE:") and is_demo:
                analysis_result = get_fallback_symptom_assessment(symptoms_text, duration_str, severity_str)

        # Save to database repository (session-scoped if in demo mode)
        SymptomRepository.save_assessment(
            user_id=user_id,
            symptoms=symptoms_text,
            duration=duration_str,
            severity=severity_str,
            analysis=analysis_result,
            is_emergency=safety_eval["is_emergency"] or is_high_severity
        )

        st.html("<h3 style='color: #0284C7; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.75rem;'>Informational Assessment Results</h3>")
        
        if analysis_result.startswith("SERVICE_UNAVAILABLE:"):
            st.html(f"""
            <div class="error-card">
                <div class="error-card-title">{alert_svg} AI Service Notice</div>
                <div style="font-size: 0.88rem;">{analysis_result.replace("SERVICE_UNAVAILABLE:", "").strip()}</div>
            </div>
            """)
        else:
            st.markdown(analysis_result)

        st.html("""
        <div class="disclaimer-box">
            <b>Important Notice:</b> VitalBite AI is currently in beta testing. This assessment is for educational purposes only and cannot diagnose a medical condition. If symptoms worsen, persist, or cause concern, please consult a qualified healthcare professional.
        </div>
        """)
