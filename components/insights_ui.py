"""
VitalBite AI — Health Insights Component
Data-grounded health metrics and metabolic estimates derived strictly from user-provided data.
"""
import streamlit as st
from database.repositories import ProfileRepository
from services.health_service import HealthService
from utils.custom_css import render_bmi_gauge_html

def render_insights_tab(user_id: str):
    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">📈 Health Insights</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Understand your health and nutrition trends derived objectively from your verified profile.</p>
    </div>
    """)

    profile = ProfileRepository.get_profile(user_id) or {}

    height_cm = float(profile.get("height_cm") or 0)
    weight_kg = float(profile.get("weight_kg") or 0)
    age = int(profile.get("age") or 0)
    gender = profile.get("gender") or "Male"

    if not height_cm or not weight_kg:
        st.info("⚠️ Height and Weight are required in your Profile to compute metabolic & BMI insights.")
        return

    # Metric Cards Grid matching Reference Screen 5
    col1, col2, col3 = st.columns(3)

    bmi_info = HealthService.calculate_bmi(height_cm, weight_kg)
    bmr_val = HealthService.calculate_bmr(height_cm, weight_kg, age, gender) if age else None
    tdee_val = HealthService.calculate_tdee(bmr_val) if bmr_val else None

    with col1:
        if bmi_info:
            gauge_html = render_bmi_gauge_html(bmi_info['bmi'], bmi_info['category'], bmi_info['color'])
            st.html(f"""
            <div class="med-card">
                <div class="med-card-subtitle">BMI STATUS</div>
                {gauge_html}
            </div>
            """)
        else:
            st.html("""
            <div class="med-card">
                <div class="med-card-subtitle">BMI STATUS</div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #64748B;">N/A</div>
            </div>
            """)

    with col2:
        st.html(f"""
        <div class="med-card">
            <div class="med-card-subtitle">ESTIMATED BMR</div>
            <div style="font-size: 2.1rem; font-weight: 800; color: #0284C7; line-height: 1.1; letter-spacing: -0.02em;">
                {int(bmr_val) if bmr_val else 'N/A'} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">kcal/day</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem; font-weight: 500;">Basal Metabolic Rate (Mifflin-St Jeor)</div>
        </div>
        """)

    with col3:
        st.html(f"""
        <div class="med-card">
            <div class="med-card-subtitle">ESTIMATED TDEE</div>
            <div style="font-size: 2.1rem; font-weight: 800; color: #059669; line-height: 1.1; letter-spacing: -0.02em;">
                {int(tdee_val) if tdee_val else 'N/A'} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">kcal/day</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748B; margin-top: 0.25rem; font-weight: 500;">Total Energy (Moderate Activity)</div>
        </div>
        """)

    # Detailed Metric Explanations Card
    st.html("""
    <div class="med-card" style="margin-top: 1.25rem;">
        <div class="med-card-title">💡 Metric Definitions & Evidence Basis</div>
        <ul style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin-top: 0.4rem; padding-left: 1.2rem;">
            <li><b style="color: #0F172A;">Body Mass Index (BMI):</b> Standard international reference metric calculated as weight (kg) / height (m²). Used strictly as a general screening reference.</li>
            <li><b style="color: #0F172A;">Basal Metabolic Rate (BMR):</b> Estimated daily calories expended at rest for essential biological maintenance (Mifflin-St Jeor equation).</li>
            <li><b style="color: #0F172A;">Total Daily Energy Expenditure (TDEE):</b> Estimated total daily calorie burn factoring in baseline metabolism and moderate activity.</li>
        </ul>
        <div class="disclaimer-box" style="margin-top: 1rem;">
            📌 <b>Data-Grounded Principle:</b> VitalBite AI strictly displays metrics based on user-provided height, weight, and age. We never invent blood pressure, pulse, or blood glucose numbers.
        </div>
    </div>
    """)
