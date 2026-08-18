"""
VitalBite AI — Document & Report Scanner UI Component
Upload and analyze health documents, lab report excerpts, or medical notes with AI interpretation matching Reference Screen 6.
"""
import streamlit as st
from services.ai_service import AIService, build_document_analysis_prompt

def render_documents_tab(user_id: str):
    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">📄 Document Center & Scanner</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Upload or paste lab reports, prescriptions, or health notes to receive plain-English AI explanations.</p>
    </div>
    """)

    # Document Cards Overview matching Reference Screen 6
    st.html("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="med-card" style="padding: 1rem 1.15rem; margin: 0;">
            <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">📑</div>
            <div style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">Health Report</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.15rem;">Type: AI Consultation</div>
        </div>
        <div class="med-card" style="padding: 1rem 1.15rem; margin: 0;">
            <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">🥗</div>
            <div style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">Diet Plan</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.15rem;">Type: Nutrition Plan</div>
        </div>
        <div class="med-card" style="padding: 1rem 1.15rem; margin: 0;">
            <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">🩺</div>
            <div style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">Lab Report</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.15rem;">Type: Diagnostic Excerpt</div>
        </div>
        <div class="med-card" style="padding: 1rem 1.15rem; margin: 0;">
            <div style="font-size: 1.5rem; margin-bottom: 0.35rem;">📄</div>
            <div style="font-weight: 800; color: #0F172A; font-size: 0.95rem;">Generated PDF</div>
            <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.15rem;">Type: Export Record</div>
        </div>
    </div>
    """)

    st.html("<h3 style='color: #0F172A; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.65rem;'>Scan New Health Document</h3>")
    uploaded_file = st.file_uploader("Upload Health Document (Text or PDF excerpt)", type=["txt", "pdf", "md"])

    doc_text_input = st.text_area(
        "Or paste document text / lab report excerpt directly:",
        placeholder="e.g. Complete Blood Count (CBC) Result: Hemoglobin 13.5 g/dL, Fasting Blood Sugar 95 mg/dL...",
        height=130
    )

    st.markdown("<div style='margin-top: 0.85rem;'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("📄 Scan & Analyze Document", use_container_width=True)

    if analyze_btn:
        final_text = ""

        if uploaded_file is not None:
            try:
                bytes_data = uploaded_file.read()
                final_text = bytes_data.decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"Error reading file: {e}")
                return
        elif doc_text_input.strip():
            final_text = doc_text_input.strip()

        if not final_text:
            st.error("Please upload a file or paste document text before running analysis.")
            return

        with st.spinner("Analyzing document terms and medical values..."):
            prompt, sys_prompt = build_document_analysis_prompt(final_text[:4000])
            analysis = AIService.generate_response(prompt, sys_prompt)

        st.html("<h3 style='color: #0284C7; font-weight: 800; margin-top: 1.5rem; margin-bottom: 0.75rem;'>AI-Assisted Interpretation</h3>")
        
        if analysis.startswith("SERVICE_UNAVAILABLE:"):
            st.html(f"""
            <div class="error-card">
                <div class="error-card-title">⚠️ AI Service Notice</div>
                <div style="font-size: 0.88rem;">{analysis.replace("SERVICE_UNAVAILABLE:", "").strip()}</div>
            </div>
            """)
        else:
            st.markdown(analysis)

        st.html("""
        <div class="disclaimer-box">
            ⚠️ <b>Important Notice:</b> AI-assisted document interpretation is provided for educational clarification only. It is not an official laboratory diagnostics report or prescription interpretation. Please present your physical documents to your attending doctor.
        </div>
        """)
