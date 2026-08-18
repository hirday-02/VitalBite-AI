"""
VitalBite AI — Health Profile UI Component
Allows users to create, view, and update their personal health profile with visual progress feedback.
"""
import streamlit as st
from database.repositories import ProfileRepository
from services.health_service import HealthService
from utils.validation import validate_age, validate_height, validate_weight
from utils.custom_css import render_completeness_donut_html

def render_profile_tab(user_id: str):
    st.html("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em;">👤 Personal Health Profile</h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Maintain your core health details so VitalBite AI can provide accurate, personalized guidance.</p>
    </div>
    """)

    existing = ProfileRepository.get_profile(user_id) or {}
    completeness = HealthService.get_profile_completeness(existing)

    # Top Visual Completion Header
    st.html(f"""
    <div class="med-card" style="margin-bottom: 1.5rem; padding: 1.2rem 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.85rem;">
            <div>
                <div class="med-card-subtitle">PROFILE COMPLETION STATUS</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">
                    {completeness['percentage']}% Completed ({completeness['completed_count']}/{completeness['total_count']} Fields)
                </div>
                <div style="font-size: 0.84rem; color: #64748B; margin-top: 0.25rem; font-weight: 500;">
                    {"All key health metrics provided!" if completeness['percentage'] == 100 else f"Missing: {', '.join(completeness['missing_fields'][:3])}"}
                </div>
            </div>
            {render_completeness_donut_html(completeness['percentage'], completeness['completed_count'], completeness['total_count'])}
        </div>
    </div>
    """)

    with st.form("profile_form"):
        # Section 1: Demographics
        st.html("<h4 style='color: #0284C7; font-weight: 800; font-size: 1.05rem; margin-bottom: 0.5rem;'>1. Personal Information</h4>")
        col_name, col_age, col_gender = st.columns(3)
        with col_name:
            name = st.text_input("Full Name", value=existing.get("name", ""))
        with col_age:
            age_input = st.text_input("Age", value=str(existing.get("age") or ""))
        with col_gender:
            gender_opts = ["Male", "Female", "Other", "Prefer not to say"]
            gender_idx = gender_opts.index(existing.get("gender")) if existing.get("gender") in gender_opts else 0
            gender = st.selectbox("Gender", gender_opts, index=gender_idx)

        # Section 2: Body Measurements
        st.html("<h4 style='color: #0284C7; font-weight: 800; font-size: 1.05rem; margin-top: 1.15rem; margin-bottom: 0.5rem;'>2. Body Measurements & Blood Group</h4>")
        col_h, col_w, col_b = st.columns(3)
        with col_h:
            height_input = st.text_input("Height (cm)", value=str(existing.get("height_cm") or ""))
        with col_w:
            weight_input = st.text_input("Weight (kg)", value=str(existing.get("weight_kg") or ""))
        with col_b:
            blood_opts = ["Select Blood Type", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            b_idx = blood_opts.index(existing.get("blood_type")) if existing.get("blood_type") in blood_opts else 0
            blood_type = st.selectbox("Blood Type", blood_opts, index=b_idx)

        # Section 3: Diet & Nutrition
        st.html("<h4 style='color: #0284C7; font-weight: 800; font-size: 1.05rem; margin-top: 1.15rem; margin-bottom: 0.5rem;'>3. Diet & Nutrition Preferences</h4>")
        diet_opts = ["Vegetarian", "Eggetarian", "Non-Vegetarian", "Vegan", "Jain", "Low Carb"]
        d_idx = diet_opts.index(existing.get("dietary_preference")) if existing.get("dietary_preference") in diet_opts else 0
        diet_pref = st.selectbox("Primary Dietary Preference", diet_opts, index=d_idx)

        # Section 4: Medical Considerations
        st.html("<h4 style='color: #0284C7; font-weight: 800; font-size: 1.05rem; margin-top: 1.15rem; margin-bottom: 0.5rem;'>4. Medical Considerations & History</h4>")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            allergies = st.text_input("Allergies (Type 'None' if zero)", value=existing.get("allergies", ""))
            conditions = st.text_input("Chronic Conditions (Type 'None' if zero)", value=existing.get("conditions", ""))
        with col_m2:
            medications = st.text_input("Current Medications (Type 'None' if zero)", value=existing.get("medications", ""))

        st.markdown("<div style='margin-top: 1.15rem;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("💾 Save Profile Details", use_container_width=True)

    if save_btn:
        valid_age, age_val, age_err = validate_age(age_input)
        valid_h, h_val, h_err = validate_height(height_input)
        valid_w, w_val, w_err = validate_weight(weight_input)

        if not valid_age:
            st.error(age_err)
            return
        if not valid_h:
            st.error(h_err)
            return
        if not valid_w:
            st.error(w_err)
            return

        payload = {
            "name": name.strip(),
            "age": age_val,
            "gender": gender,
            "height_cm": h_val,
            "weight_kg": w_val,
            "blood_type": "" if blood_type == "Select Blood Type" else blood_type,
            "allergies": allergies.strip(),
            "conditions": conditions.strip(),
            "medications": medications.strip(),
            "dietary_preference": diet_pref
        }

        try:
            ProfileRepository.upsert_profile(user_id, payload)
            st.success("Profile saved successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save profile: {e}")
