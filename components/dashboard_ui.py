"""
VitalBite AI — Dashboard UI Component
Personal Health Command Center with profile summary, SVG metric gauges, recent activity,
and quick action cards matching Reference Screen 2.
"""
import streamlit as st
from typing import Dict, Any, Optional
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository
from services.health_service import HealthService
from services.auth_service import AuthService
from utils.custom_css import render_bmi_gauge_html, render_completeness_donut_html

def render_dashboard(user_id: str, set_nav_callback):
    is_demo = AuthService.is_demo_mode()
    user_info = AuthService.get_current_user() or {}
    profile = ProfileRepository.get_profile(user_id) or {}
    name = profile.get("name") or user_info.get("user_metadata", {}).get("full_name") or ("Alex Rivera" if is_demo else "User")

    # 1. Main Greeting Banner
    st.html(f"""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="color: #0F172A; font-size: 1.95rem; font-weight: 800; margin-bottom: 0.25rem; letter-spacing: -0.025em;">Welcome back, {name} 👋</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Here's your personalized health & wellness overview.</p>
    </div>
    """)

    if is_demo:
        st.html("""
        <div class="med-card" style="background: rgba(245, 243, 255, 0.92); border: 1px solid rgba(196, 181, 253, 0.8); padding: 0.85rem 1.25rem; margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <div>
                    <span style="font-weight: 800; color: #7E22CE; font-size: 0.92rem;">✨ Demo Mode Active:</span>
                    <span style="font-size: 0.86rem; color: #5B21B6; margin-left: 0.35rem;">
                        Pre-populated with fictional sample records (Alex Rivera, 28y, Recomposition). Test diet planning, symptom checking, or health insights freely!
                    </span>
                </div>
            </div>
        </div>
        """)

    # 2. Top Metric Cards (BMI, Profile Completeness, Consultation Records)
    col1, col2, col3 = st.columns(3)

    height_cm = float(profile.get("height_cm") or 0)
    weight_kg = float(profile.get("weight_kg") or 0)
    bmi_info = HealthService.calculate_bmi(height_cm, weight_kg)
    completeness = HealthService.get_profile_completeness(profile)

    with col1:
        if bmi_info:
            gauge_html = render_bmi_gauge_html(bmi_info['bmi'], bmi_info['category'], bmi_info['color'])
            st.html(f"""
            <div class="med-card">
                <div class="med-card-subtitle">BODY MASS INDEX (BMI)</div>
                {gauge_html}
            </div>
            """)
        else:
            st.html("""
            <div class="med-card">
                <div class="med-card-subtitle">BODY MASS INDEX (BMI)</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 1.6rem; font-weight: 800; color: #64748B;">--</div>
                        <div style="font-size: 0.82rem; color: #64748B;">Enter height & weight in Profile</div>
                    </div>
                    <div style="font-size: 2rem; opacity: 0.35;">⚖️</div>
                </div>
            </div>
            """)

    with col2:
        donut_html = render_completeness_donut_html(
            completeness['percentage'],
            completeness['completed_count'],
            completeness['total_count']
        )
        st.html(f"""
        <div class="med-card">
            <div class="med-card-subtitle">PROFILE COMPLETENESS</div>
            {donut_html}
        </div>
        """)

    with col3:
        sessions = ChatRepository.list_sessions(user_id)
        assessments = SymptomRepository.list_assessments(user_id)
        plans = DietRepository.list_plans(user_id)
        total_actions = len(sessions) + len(assessments) + len(plans)
        st.html(f"""
        <div class="med-card">
            <div class="med-card-subtitle">CONSULTATION RECORDS</div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-size: 2.1rem; font-weight: 800; color: #0284C7; line-height: 1.1; letter-spacing: -0.02em;">{total_actions}</div>
                    <div style="font-size: 0.84rem; color: #475569; font-weight: 600; margin-top: 0.25rem;">Chats, Symptoms & Diets</div>
                </div>
                <div style="font-size: 1.6rem; display: flex; gap: 0.35rem;">💬🩺🥗</div>
            </div>
        </div>
        """)

    # 3. Quick Action Cards
    st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800; margin-top: 0.85rem; margin-bottom: 0.75rem; letter-spacing: -0.015em;'>Quick Actions</h3>")

    act_col1, act_col2, act_col3, act_col4 = st.columns(4)
    with act_col1:
        if st.button("💬 Ask Health AI\n\nAI health assistant", use_container_width=True, key="qa_chat"):
            set_nav_callback("Health AI")
    with act_col2:
        if st.button("⚡ Check Symptoms\n\nGuided triage", use_container_width=True, key="qa_symptom"):
            set_nav_callback("Symptoms")
    with act_col3:
        if st.button("🥗 Build Diet Plan\n\n7-day meal plan", use_container_width=True, key="qa_diet"):
            set_nav_callback("Nutrition")
    with act_col4:
        if st.button("📄 Scan Report\n\nDocument interpreter", use_container_width=True, key="qa_doc"):
            set_nav_callback("Documents")

    # 4. Structured Health Profile Overview Card
    st.html(f"""
    <div class="med-card" style="margin-top: 1.25rem;">
        <div class="med-card-title">👤 Health Profile Overview</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.1rem; margin-top: 0.65rem;">
            <div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Age</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('age') or 'Not specified'}</div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-top: 0.75rem;">Blood Type</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('blood_type') or 'Not specified'}</div>
            </div>
            <div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Gender</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('gender') or 'Not specified'}</div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-top: 0.75rem;">Dietary Preference</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('dietary_preference') or 'Vegetarian'}</div>
            </div>
            <div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Height</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('height_cm') or '?'} cm</div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-top: 0.75rem;">Allergies</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0284C7;">{profile.get('allergies') or 'None'}</div>
            </div>
            <div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Weight</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{profile.get('weight_kg') or '?'} kg</div>
                <div style="font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase; margin-top: 0.75rem;">Conditions</div>
                <div style="font-size: 1rem; font-weight: 700; color: #0284C7;">{profile.get('conditions') or 'None'}</div>
            </div>
        </div>
    </div>
    """)

    # 5. Recent Activity Timeline
    st.html("<h3 style='color: #0F172A; font-size: 1.15rem; font-weight: 800; margin-top: 1.35rem; margin-bottom: 0.75rem; letter-spacing: -0.015em;'>Recent Activity</h3>")
    if not assessments and not plans and not sessions:
        st.info("No recent consultation history. Click one of the quick actions above to start!")
    else:
        if len(assessments) > 0:
            latest_s = assessments[0]
            st.html(f"""
            <div class="med-card" style="padding: 0.95rem 1.25rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #0284C7; font-size: 0.92rem;">⚡ Symptom Check: {latest_s.get('symptoms', '')[:45]}...</span>
                    <span style="font-size: 0.8rem; color: #64748B; font-weight: 500;">{latest_s.get('created_at', '')[:10]}</span>
                </div>
            </div>
            """)

        if len(plans) > 0:
            latest_p = plans[0]
            st.html(f"""
            <div class="med-card" style="padding: 0.95rem 1.25rem; margin-bottom: 0.65rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #059669; font-size: 0.92rem;">🥗 Diet Plan: {latest_p.get('goal', '')} ({latest_p.get('diet_type', '')})</span>
                    <span style="font-size: 0.8rem; color: #64748B; font-weight: 500;">{latest_p.get('created_at', '')[:10]}</span>
                </div>
            </div>
            """)

    # 6. Persistent Medical Disclaimer Notice
    st.html("""
    <div class="disclaimer-box">
        📌 <b>Medical Disclaimer:</b> VitalBite AI is an early beta health assistant designed for general educational purposes only. It is not a licensed physician, medical diagnostic tool, or substitute for professional healthcare evaluation.
    </div>
    """)
