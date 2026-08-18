"""
VitalBite AI — Health AI Chat UI Component
Conversational AI interface with session selector, personal profile context, clean message bubbles, and safety triage.
Supports seamless Demo Mode reasoning when Gemini is not configured.
"""
import streamlit as st
from typing import Dict, Any, Optional
from database.repositories import ProfileRepository, ChatRepository
from services.ai_service import AIService, build_health_chat_prompt
from services.auth_service import AuthService
from services.safety_service import SafetyService
from components.emergency_modal import render_emergency_banner

def render_chat_tab(user_id: str):
    is_demo = AuthService.is_demo_mode()

    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">💬 Personal Health AI</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Ask questions about health topics, wellness routines, or medical concepts in plain English.</p>
    </div>
    """)

    # Check diagnostic status
    diag = AIService.get_detailed_diagnostics(force_refresh=False)
    status = diag.get("status", "CONFIG_MISSING")

    if is_demo and status != "READY":
        st.html("""
        <div class="med-card" style="background: rgba(245, 243, 255, 0.9); border: 1px solid rgba(196, 181, 253, 0.8); padding: 0.85rem 1.15rem; margin-bottom: 1rem;">
            <div style="font-weight: 800; color: #7E22CE; font-size: 0.92rem;">✨ Demo Health AI Active</div>
            <div style="font-size: 0.82rem; color: #5B21B6; margin-top: 0.2rem;">
                Exploring Health AI with evidence-based demonstration responses. In production, live Google Gemini reasoning is active when an API key is configured.
            </div>
        </div>
        """)
    elif not is_demo and status != "READY":
        if status in ["CONFIG_MISSING", "CONFIG_PLACEHOLDER"]:
            msg = "AI configuration is not set up yet. Please add your <code>GEMINI_API_KEY</code> to <code>.streamlit/secrets.toml</code> or environment variables."
        elif status == "AUTH_FAILED":
            msg = "VitalBite AI could not authenticate with the Gemini service. Please verify your API key permissions in Google AI Studio."
        else:
            msg = "VitalBite AI is temporarily unable to reach the AI service. Please try again later."

        st.html(f"""
        <div class="error-card">
            <div class="error-card-title">🔌 AI Connection Notice</div>
            <div style="font-size: 0.88rem; line-height: 1.4;">
                {msg}
            </div>
        </div>
        """)

    profile = ProfileRepository.get_profile(user_id) or {}
    user_name = profile.get("name") or ("Alex" if is_demo else "User")

    # Conversation Selector Card
    sessions = ChatRepository.list_sessions(user_id)
    session_options = {s["id"]: s.get("title", "Conversation") for s in sessions}

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        if session_options:
            selected_session_id = st.selectbox(
                "Active Conversation Thread",
                options=list(session_options.keys()),
                format_func=lambda sid: f"💬 {session_options[sid]}",
                label_visibility="collapsed"
            )
        else:
            new_sess = ChatRepository.get_or_create_session(user_id, title="New Conversation")
            selected_session_id = new_sess["id"]
    with col_s2:
        if st.button("➕ New Chat", use_container_width=True):
            new_sess = ChatRepository.get_or_create_session(user_id, title=f"Conversation {len(sessions) + 1}")
            st.session_state["active_chat_session_id"] = new_sess["id"]
            st.rerun()

    if "active_chat_session_id" in st.session_state and st.session_state["active_chat_session_id"] in session_options:
        selected_session_id = st.session_state["active_chat_session_id"]

    # Load existing messages (filtering legacy error entries)
    raw_messages = ChatRepository.get_messages(user_id, selected_session_id)
    messages = [m for m in raw_messages if not m.get("message", "").startswith("SERVICE_UNAVAILABLE:")]

    # Initial Welcome message
    if not messages:
        welcome_text = (
            f"Hello {user_name}! I am your VitalBite AI health assistant. "
            "I can help explain health concepts, workout strategies, and offer evidence-based guidance tailored to your profile. "
            "How can I assist you today?"
        )
        ChatRepository.add_message(user_id, selected_session_id, "assistant", welcome_text)
        messages = ChatRepository.get_messages(user_id, selected_session_id)

    # Render message history
    for msg in messages:
        sender = msg.get("sender", "user")
        text = msg.get("message", "")
        with st.chat_message("user" if sender == "user" else "assistant"):
            st.markdown(text)

    # Chat Input
    user_input = st.chat_input("Ask VitalBite AI a health question...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        ChatRepository.add_message(user_id, selected_session_id, "user", user_input)

        # Multi-layer Emergency Safety Check
        safety_eval = SafetyService.evaluate_emergency(user_input)
        if safety_eval["is_emergency"]:
            render_emergency_banner(safety_eval)
            emergency_reply = (
                "🚨 **SAFETY ESCALATION**: Your query contains symptoms that may indicate a serious medical emergency. "
                f"Please call **{safety_eval['primary_number']}** or seek immediate emergency medical care now."
            )
            with st.chat_message("assistant"):
                st.markdown(emergency_reply)
            ChatRepository.add_message(user_id, selected_session_id, "assistant", emergency_reply)
        else:
            with st.chat_message("assistant"):
                with st.spinner("VitalBite AI is reviewing health context..."):
                    prompt, sys_prompt = build_health_chat_prompt(user_input, profile)
                    response_text = AIService.generate_response(
                        prompt=prompt,
                        system_instruction=sys_prompt,
                        is_demo=is_demo,
                        user_name=user_name
                    )
                    
                    if response_text.startswith("SERVICE_UNAVAILABLE:"):
                        st.html(f"""
                        <div class="error-card" style="margin: 0;">
                            <div class="error-card-title">⚠️ AI Service Notice</div>
                            <div style="font-size: 0.85rem;">{response_text.replace("SERVICE_UNAVAILABLE:", "").strip()}</div>
                        </div>
                        """)
                    else:
                        st.markdown(response_text)
                        st.html("""
                        <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.5rem;">
                            ⚠️ VitalBite AI is in beta testing. Informational response only. Not a medical diagnosis or prescription.
                        </div>
                        """)
                        ChatRepository.add_message(user_id, selected_session_id, "assistant", response_text)
