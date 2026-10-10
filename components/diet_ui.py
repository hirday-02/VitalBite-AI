"""
VitalBite AI — Interactive 7-Day Personalized Diet & Fitness Nutrition Component
Personalized 7-day meal planner with verified ICMR-NIN & USDA food databases, expandable food categories,
unselected-by-default food options, fitness & body goals, protein powder supplement module,
>=90% target optimization, daily macro achievement progress bars, interactive food swaps, plan saving, and PDF export.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from database.repositories import ProfileRepository, DietRepository
from services.health_service import HealthService
from services.nutrition_service import NutritionService
from services.diet_planner_service import DietPlannerService
from services.report_service import ReportService
from utils.custom_css import render_macro_progress_bar_html
from utils.icons import get_svg_icon

def render_diet_tab(user_id: str):
    nutrition_svg = get_svg_icon("nutrition", color="#059669", size=22)
    profile_svg = get_svg_icon("profile", color="#0284C7", size=18)
    alert_svg = get_svg_icon("alert", color="#DC2626", size=16)

    st.html(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.95rem; margin-bottom: 0.25rem; letter-spacing: -0.025em; display: flex; align-items: center; gap: 0.5rem;">
            {nutrition_svg} Personalized Diet Planner
        </h2>
        <p style="color: #475569; font-size: 0.95rem; margin: 0; font-weight: 500;">Build a nutrition plan around your goals, preferences, and verified food data from ICMR-NIN and USDA.</p>
    </div>
    """)

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "7-Day Interactive Diet Planner",
        "Database Food Lookup",
        "Food Substitutions"
    ])

    # =========================================================================
    # SUB-TAB 1: 7-DAY INTERACTIVE DIET PLANNER
    # =========================================================================
    with sub_tab1:
        profile = ProfileRepository.get_profile(user_id) or {}
        height_cm = float(profile.get("height_cm") or 0)
        weight_kg = float(profile.get("weight_kg") or 0)
        age = int(profile.get("age") or 0)
        gender = profile.get("gender") or "Male"
        allergies = profile.get("allergies") or "None"
        saved_diet_pref = profile.get("dietary_preference") or "Vegetarian"

        # 1. Profile Completeness Gate
        if not height_cm or not weight_kg or not age:
            st.html(f"""
            <div class="med-card" style="border-left: 4px solid #0284C7; margin-bottom: 1rem;">
                <div class="med-card-title">{profile_svg} Complete Profile Required for Personalized Planning</div>
                <p style="color: #475569; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.5rem;">
                    To calculate your personal metabolic expenditure (BMR & TDEE) and establish goal-aligned calorie and macronutrient targets, VitalBite AI requires your age, height, and weight.
                </p>
            </div>
            """)
            if st.button("Complete Health Profile", key="btn_goto_profile"):
                st.session_state["nav_selection"] = "Profile"
                st.rerun()
            return

        # 2. Medical Safety Override Warning
        safety_check = DietPlannerService.check_medical_safety_override(profile)
        if safety_check["has_warning"]:
            st.html(f"""
            <div class="emergency-overlay" style="border-color: #F59E0B; background: rgba(254, 243, 199, 0.95); margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 800; color: #B45309; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.4rem;">
                    {alert_svg} Clinical Supervision Recommended
                </div>
                <div style="font-size: 0.88rem; color: #92400E; line-height: 1.5;">
                    {safety_check['warning_text']}
                </div>
            </div>
            """)

        # 3. Compact User Profile Summary Bar
        bmi_info = HealthService.calculate_bmi(height_cm, weight_kg)
        bmi_str = f"{bmi_info['bmi']} ({bmi_info['category']})" if bmi_info else "N/A"
        st.html(f"""
        <div class="med-card" style="padding: 0.85rem 1.25rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.65rem;">
            <div style="display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.88rem; color: #475569; font-weight: 600;">
                <span><b>{profile.get('name', 'User')}</b> ({age}y, {gender})</span>
                <span>Height: <b>{height_cm} cm</b></span>
                <span>Weight: <b>{weight_kg} kg</b></span>
                <span>BMI: <b style="color: #0284C7;">{bmi_str}</b></span>
                <span>Allergies: <b style="color: #DC2626;">{allergies}</b></span>
            </div>
        </div>
        """)

        # 4. Two-Column Planner Input Configuration
        col_left, col_right = st.columns([1.15, 1.35])

        with col_left:
            st.html("<h3 style='color: #0F172A; font-size: 1.1rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -0.015em;'>1. Nutrition Goals</h3>")

            fitness_goals = [
                "Maintain Current Physique",
                "Fat Loss / Weight Loss",
                "Muscle Gain",
                "Body Recomposition",
                "Performance / Strength",
                "General Fitness & Health"
            ]
            selected_goal = st.selectbox("Primary Goal", fitness_goals, index=0)

            col_fg1, col_fg2 = st.columns(2)
            with col_fg1:
                training_freq_opts = [
                    "0–1 days/week (Light / Inactive)",
                    "2–3 days/week (Moderate Training)",
                    "4–5 days/week (Consistent Training)",
                    "6+ days/week (High Volume Athlete)"
                ]
                selected_freq = st.selectbox("Training Frequency", training_freq_opts, index=1)
            with col_fg2:
                training_type_opts = [
                    "Mixed Training",
                    "Strength Training",
                    "Bodybuilding / Hypertrophy",
                    "Cardio & Endurance",
                    "Sports & Athletics"
                ]
                selected_type = st.selectbox("Training Type", training_type_opts, index=0)

            diet_options = ["Vegetarian", "Non-Vegetarian", "Vegan", "Jain", "Eggetarian", "Low Carb"]
            diet_idx = diet_options.index(saved_diet_pref) if saved_diet_pref in diet_options else 0
            selected_diet = st.selectbox("Dietary Preference", diet_options, index=diet_idx)

            act_mapping = {
                "Sedentary (Desk job, little exercise)": "sedentary",
                "Light Activity (1-3 days/week)": "light",
                "Moderate Activity (3-5 days/week)": "moderate",
                "Active (6-7 days/week)": "active",
                "Very Active (Intense training)": "very_active"
            }
            act_label = st.selectbox("Daily Activity Level", list(act_mapping.keys()), index=2)
            act_val = act_mapping[act_label]

            # Live Target Calculation Preview Card
            targets = DietPlannerService.calculate_nutrition_targets(
                profile=profile,
                fitness_goal=selected_goal,
                activity_level=act_val,
                training_frequency=selected_freq,
                training_type=selected_type
            )
            st.html(f"""
            <div class="med-card" style="margin-top: 0.85rem; padding: 1rem 1.15rem;">
                <div class="med-card-subtitle">CALCULATED DAILY TARGET ESTIMATES</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 0.5rem; font-size: 0.88rem;">
                    <div>Target Calories: <b style="color: #0284C7; font-size: 1rem;">{int(targets['target_calories'])} kcal</b></div>
                    <div>Protein: <b style="color: #0284C7;">{targets['protein_g']} g</b></div>
                    <div>Carbs: <b style="color: #0F172A;">{targets['carbs_g']} g</b></div>
                    <div>Fat: <b style="color: #0F172A;">{targets['fat_g']} g</b></div>
                    <div>Fiber Target: <b style="color: #059669;">{targets['fiber_g']} g</b></div>
                    <div>Est. TDEE: <b style="color: #64748B;">{int(targets['tdee'])} kcal</b></div>
                </div>
                <div style="font-size: 0.74rem; color: #64748B; margin-top: 0.65rem;">
                    Note: Calorie and macro targets are educational fitness estimates, not medical prescriptions.
                </div>
            </div>
            """)

            # Dedicated Protein Powder Supplement Box
            st.html("<h3 style='color: #0F172A; font-size: 1.1rem; font-weight: 800; margin-top: 1.15rem; margin-bottom: 0.45rem;'>Protein Powder (Optional Supplement)</h3>")
            enable_protein_powder = st.checkbox("Include Protein Powder in Diet Plan", value=False, key="chk_enable_protein_powder")

            powder_config = {"enabled": enable_protein_powder}
            if enable_protein_powder:
                powder_choices = [
                    "Whey Protein Isolate (USDA Verified — 24g P / 120 kcal)",
                    "Whey Protein Concentrate (USDA Verified — 24g P / 130 kcal)",
                    "Plant Protein Blend (Pea & Rice — 24g P / 120 kcal)",
                    "Soy Protein Isolate (Verified — 25g P / 115 kcal)",
                    "Custom Protein Powder (Enter Nutrition Label Data)"
                ]
                chosen_powder_type = st.selectbox("Selected Selection", powder_choices, key="sel_powder_type")

                powder_serving_opts = [
                    "0.5 serving (Half Scoop)",
                    "1.0 serving (1 Scoop — Standard)",
                    "1.5 servings (1.5 Scoops)",
                    "2.0 servings (2 Scoops — Max Recommended)"
                ]
                chosen_serving_str = st.selectbox("Serving Control (Scoops)", powder_serving_opts, index=1, key="sel_powder_servings")
                servings_float = 0.5 if "0.5" in chosen_serving_str else (1.0 if "1.0" in chosen_serving_str else (1.5 if "1.5" in chosen_serving_str else 2.0))

                powder_id_map = {
                    "Whey Protein Isolate (USDA Verified — 24g P / 120 kcal)": "usda_whey_isolate",
                    "Whey Protein Concentrate (USDA Verified — 24g P / 130 kcal)": "usda_whey_concentrate",
                    "Plant Protein Blend (Pea & Rice — 24g P / 120 kcal)": "usda_plant_protein",
                    "Soy Protein Isolate (Verified — 25g P / 115 kcal)": "icmr_soya_protein_isolate",
                    "Custom Protein Powder (Enter Nutrition Label Data)": "custom"
                }
                mapped_fid = powder_id_map.get(chosen_powder_type, "usda_whey_isolate")

                custom_nut = {}
                if mapped_fid == "custom":
                    st.caption("Enter the exact nutrition facts from your product label (per 1 scoop):")
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        c_brand = st.text_input("Brand / Product Name", value="My Whey Protein", key="custom_powder_brand")
                        c_serving = st.text_input("Serving Size", value="1 scoop (30g)", key="custom_powder_serving")
                        c_cal = st.number_input("Calories (kcal)", min_value=10.0, max_value=400.0, value=120.0, step=5.0, key="custom_powder_cal")
                    with c_col2:
                        c_prot = st.number_input("Protein (g)", min_value=1.0, max_value=50.0, value=24.0, step=1.0, key="custom_powder_prot")
                        c_carbs = st.number_input("Carbs (g)", min_value=0.0, max_value=50.0, value=2.0, step=0.5, key="custom_powder_carbs")
                        c_fat = st.number_input("Fat (g)", min_value=0.0, max_value=20.0, value=1.0, step=0.5, key="custom_powder_fat")

                    custom_nut = {
                        "brand_name": c_brand.strip(),
                        "serving_size_label": c_serving.strip(),
                        "calories_kcal": c_cal,
                        "protein_g": c_prot,
                        "carbs_g": c_carbs,
                        "fat_g": c_fat,
                        "fiber_g": 0.0
                    }

                powder_config = {
                    "enabled": True,
                    "food_id": mapped_fid,
                    "servings": servings_float,
                    "custom_nutrition": custom_nut
                }

                # Live Powder Nutrition Preview
                powder_preview = DietPlannerService.calculate_protein_powder_nutrition(powder_config)
                if powder_preview:
                    st.html(f"""
                    <div style="background: rgba(240, 249, 255, 0.95); border: 1.5px solid rgba(186, 230, 253, 0.8); border-radius: 12px; padding: 0.75rem 1rem; margin-top: 0.5rem; font-size: 0.85rem;">
                        <div style="font-weight: 700; color: #0284C7;">Selected Supplement Contribution ({servings_float} scoop):</div>
                        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.35rem; color: #1E293B; font-weight: 600;">
                            <span>Calories: <b>{powder_preview['calories_kcal']} kcal</b></span>
                            <span>Protein: <b style="color: #059669;">{powder_preview['protein_g']} g</b></span>
                            <span>Carbs: <b>{powder_preview['carbs_g']} g</b></span>
                            <span>Fat: <b>{powder_preview['fat_g']} g</b></span>
                        </div>
                    </div>
                    """)

        with col_right:
            st.html("<h3 style='color: #0F172A; font-size: 1.1rem; font-weight: 800; margin-bottom: 0.25rem; letter-spacing: -0.015em;'>2. Food Preferences (Verified Databases)</h3>")
            st.caption("All food items start UNSELECTED by default. Select the foods you enjoy eating. Incompatible foods and allergens are automatically excluded.")

            categories = DietPlannerService.get_food_categories_dict(selected_diet, allergies)
            all_compat_ids = [f["id"] for cat_list in categories.values() for f in cat_list]

            # Session state store for explicit food selection
            state_key = f"diet_selected_food_set_{user_id}"
            if state_key not in st.session_state:
                st.session_state[state_key] = set()

            col_btn1, col_btn2, col_count = st.columns([1, 1, 1.5])
            with col_btn1:
                if st.button("Select All", use_container_width=True, key="btn_select_all_foods"):
                    st.session_state[state_key] = set(all_compat_ids)
                    for fid in all_compat_ids:
                        st.session_state[f"chk_food_{user_id}_{fid}"] = True
                    st.rerun()

            with col_btn2:
                if st.button("Clear All", use_container_width=True, key="btn_clear_all_foods"):
                    st.session_state[state_key] = set()
                    for fid in all_compat_ids:
                        st.session_state[f"chk_food_{user_id}_{fid}"] = False
                    st.rerun()

            with col_count:
                selected_count = len(st.session_state[state_key])
                st.html(f"""
                <div style="text-align: right; padding-top: 0.4rem; font-size: 0.86rem; font-weight: 700; color: #0284C7;">
                    Selected: {selected_count} / {len(all_compat_ids)} items
                </div>
                """)

            # Render 8 Category Accordions with Unselected-by-default Checkboxes
            for cat_name, food_list in categories.items():
                if not food_list:
                    continue

                cat_selected_count = sum(1 for f in food_list if f["id"] in st.session_state[state_key])
                expander_label = f"{cat_name} ({cat_selected_count}/{len(food_list)} selected)"

                with st.expander(expander_label, expanded=(cat_selected_count > 0)):
                    cols = st.columns(2)
                    for idx, food in enumerate(food_list):
                        fid = food["id"]
                        chk_key = f"chk_food_{user_id}_{fid}"
                        is_checked = fid in st.session_state[state_key]

                        with cols[idx % 2]:
                            cal_display = f"{int(food['calories_kcal'])} kcal"
                            prot_display = f"{food['protein_g']}g P"
                            label_str = f"{food['name']} ({cal_display}, {prot_display})"

                            val = st.checkbox(
                                label_str,
                                value=is_checked,
                                key=chk_key
                            )
                            if val:
                                st.session_state[state_key].add(fid)
                            else:
                                st.session_state[state_key].discard(fid)

            # Generate Plan Trigger Button
            st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
            gen_plan_btn = st.button("Generate 7-Day Personalized Meal Plan", use_container_width=True, key="btn_generate_7day_plan")

            if gen_plan_btn:
                chosen_food_ids = list(st.session_state[state_key])

                with st.spinner("VitalBite AI is constructing and optimizing your 7-day meal plan..."):
                    generated_plan = DietPlannerService.generate_7day_plan(
                        profile=profile,
                        fitness_goal=selected_goal,
                        dietary_preference=selected_diet,
                        selected_food_ids=chosen_food_ids,
                        activity_level=act_val,
                        training_frequency=selected_freq,
                        training_type=selected_type,
                        protein_powder_config=powder_config
                    )

                st.session_state[f"active_diet_plan_{user_id}"] = generated_plan

        # =========================================================================
        # 7-DAY MEAL PLAN DISPLAY SECTION
        # =========================================================================
        plan_data = st.session_state.get(f"active_diet_plan_{user_id}")

        if plan_data:
            if not plan_data.get("success"):
                st.html(f"""
                <div class="error-card" style="margin-top: 1.5rem;">
                    <div class="error-card-title">{alert_svg} Meal Plan Notice: {plan_data.get('error_code')}</div>
                    <div style="font-size: 0.9rem; line-height: 1.5;">{plan_data.get('message')}</div>
                </div>
                """)
            else:
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                st.html("""
                <div style="margin-bottom: 1.25rem;">
                    <h3 style="color: #0F172A; font-weight: 800; font-size: 1.6rem; margin-bottom: 0.25rem; letter-spacing: -0.02em;">Your 7-Day Personalized Plan</h3>
                    <p style="color: #475569; font-size: 0.92rem; margin: 0; font-weight: 500;">Deterministic ICMR-NIN & USDA nutritional calculations with meal replacements and target tracking.</p>
                </div>
                """)

                # Day Selector Tabs / Radio
                day_tabs = st.tabs([f"Day {i}" for i in range(1, 8)])

                for day_idx, tab in enumerate(day_tabs):
                    with tab:
                        day = plan_data["days"][day_idx]
                        summary = day["summary"]

                        # Top Day Summary Metrics
                        st.html(f"""
                        <div class="med-card" style="padding: 1rem 1.4rem; margin-bottom: 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
                                <div>
                                    <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">{day['day_name']} Overview</div>
                                    <div style="font-size: 0.84rem; color: #64748B; margin-top: 0.2rem;">
                                        Calories: <b>{summary['calories']} kcal</b> ({summary['calories_pct']}% of target) |
                                        Protein: <b style="color: #0284C7;">{summary['protein_g']}g</b> ({summary['protein_pct']}% of target)
                                    </div>
                                </div>
                                <div>
                                    <span style="background: {'rgba(13, 148, 136, 0.12)' if summary['target_reached'] else 'rgba(217, 119, 6, 0.12)'}; color: {'#0D9488' if summary['target_reached'] else '#D97706'}; font-weight: 800; font-size: 0.82rem; padding: 0.35rem 0.85rem; border-radius: 20px; border: 1px solid {'rgba(13, 148, 136, 0.3)' if summary['target_reached'] else 'rgba(217, 119, 6, 0.3)'};">
                                        {'Target Reached (≥90%)' if summary['target_reached'] else 'Optimized Plan'}
                                    </span>
                                </div>
                            </div>
                        </div>
                        """)

                        # Render 5 Meals for this Day
                        for meal_idx, meal in enumerate(day["meals"]):
                            with st.container():
                                item_names = " + ".join([it["name"] for it in meal["items"]])
                                item_details = ", ".join([f"{it['name']} ({it.get('serving_size', '1 serving')})" for it in meal["items"]])

                                st.html(f"""
                                <div class="meal-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                                        <div>
                                            <div style="font-weight: 800; color: #0F172A; font-size: 1.05rem;">{meal['meal_name']}</div>
                                            <div style="font-size: 0.92rem; color: #0284C7; font-weight: 700; margin-top: 0.25rem;">{item_names}</div>
                                            <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.2rem;">{item_details}</div>
                                        </div>
                                        <div style="text-align: right;">
                                            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">{meal['total_calories']} kcal</div>
                                            <div style="font-size: 0.8rem; color: #475569; font-weight: 600; margin-top: 0.15rem;">
                                                {meal['total_protein']}g P • {meal['total_carbs']}g C • {meal['total_fat']}g F
                                            </div>
                                            <div style="margin-top: 0.35rem;">
                                                <span style="background: rgba(13, 148, 136, 0.1); color: #0D9488; font-size: 0.72rem; font-weight: 700; padding: 0.15rem 0.55rem; border-radius: 6px; border: 1px solid rgba(13, 148, 136, 0.25);">
                                                    Verified Source
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """)

                        # Daily Target Achievement Progress Bars
                        st.html("<h4 style='color: #0F172A; font-weight: 800; font-size: 1rem; margin-top: 1.25rem; margin-bottom: 0.65rem;'>Daily Target Achievement</h4>")
                        t_cal = plan_data["targets"]["target_calories"]
                        t_prot = plan_data["targets"]["protein_g"]
                        t_carbs = plan_data["targets"]["carbs_g"]
                        t_fat = plan_data["targets"]["fat_g"]
                        t_fiber = plan_data["targets"]["fiber_g"]

                        st.html(f"""
                        <div class="med-card" style="padding: 1.15rem 1.4rem;">
                            {render_macro_progress_bar_html('Calories', summary['calories'], t_cal, 'kcal', '#0EA5E9')}
                            {render_macro_progress_bar_html('Protein', summary['protein_g'], t_prot, 'g', '#0284C7')}
                            {render_macro_progress_bar_html('Carbohydrates', summary['carbs_g'], t_carbs, 'g', '#0D9488')}
                            {render_macro_progress_bar_html('Fat', summary['fat_g'], t_fat, 'g', '#F59E0B')}
                            {render_macro_progress_bar_html('Dietary Fiber', summary['fiber_g'], t_fiber, 'g', '#10B981')}
                        </div>
                        """)

                # Save Plan and Export PDF Buttons
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                col_save, col_pdf = st.columns(2)

                with col_save:
                    if st.button("Save 7-Day Plan to My Account", use_container_width=True, key="btn_save_diet_plan"):
                        plan_summary_text = (
                            f"Goal: {plan_data['goal']} ({plan_data['dietary_preference']})\n"
                            f"Daily Calories: ~{plan_data['days'][0]['summary']['calories']} kcal | "
                            f"Protein: ~{plan_data['days'][0]['summary']['protein_g']}g"
                        )
                        DietRepository.save_plan(
                            user_id=user_id,
                            goal=plan_data["goal"],
                            diet_type=plan_data["dietary_preference"],
                            plan_text=plan_summary_text,
                            structured_data=plan_data
                        )
                        st.success("Plan saved to your Consultation & Health History!")

                with col_pdf:
                    pdf_report_bytes = ReportService.generate_pdf_report(
                        title=f"7-Day Personalized Nutrition Plan — {plan_data['goal']}",
                        report_type="diet_plan",
                        content_text=f"Primary Goal: {plan_data['goal']}\nDietary Preference: {plan_data['dietary_preference']}\nTarget Calories: {t_cal} kcal\nProtein Target: {t_prot}g\n\nDaily meal schedule generated deterministically from ICMR-NIN/USDA verified datasets.",
                        user_name=profile.get("name", "User"),
                        profile=profile
                    )
                    st.download_button(
                        "Export 7-Day Plan (PDF)",
                        data=pdf_report_bytes,
                        file_name=f"vitalbite_7day_diet_plan_{user_id[:8]}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="btn_download_diet_pdf"
                    )

    # =========================================================================
    # SUB-TAB 2: DATABASE FOOD LOOKUP
    # =========================================================================
    with sub_tab2:
        st.html("""
        <div style="margin-bottom: 1rem;">
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.2rem; margin-bottom: 0.25rem;">Verified Database Food Lookup</h3>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Search verified ICMR-NIN IFCT 2017 & USDA food nutrition records.</p>
        </div>
        """)

        food_search_query = st.text_input("Enter food name (e.g. Paneer, Roti, Chicken, Apple, Oats)", placeholder="Search verified food...")
        if food_search_query:
            food_info = NutritionService.search_food(food_search_query)
            if food_info["matched"]:
                st.html(f"""
                <div class="med-card" style="margin-top: 1rem; border-left: 4px solid #0284C7;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">{food_info.get('name') or food_info.get('food_name') or food_info.get('item') or 'Food item'}</div>
                        <span style="background: rgba(13, 148, 136, 0.12); color: #0D9488; font-size: 0.76rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 20px;">
                            {food_info.get('source', 'ICMR-NIN IFCT')}
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #64748B; margin-top: 0.25rem;">Serving Size: <b>{food_info.get('serving_size', '100g')}</b></div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.85rem; margin-top: 1rem;">
                        <div class="food-category-box">
                            <div style="font-size: 0.74rem; color: #64748B; font-weight: 700;">CALORIES</div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: #0284C7;">{food_info['calories_kcal']} <span style="font-size: 0.8rem;">kcal</span></div>
                        </div>
                        <div class="food-category-box">
                            <div style="font-size: 0.74rem; color: #64748B; font-weight: 700;">PROTEIN</div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: #059669;">{food_info['protein_g']} <span style="font-size: 0.8rem;">g</span></div>
                        </div>
                        <div class="food-category-box">
                            <div style="font-size: 0.74rem; color: #64748B; font-weight: 700;">CARBS</div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: #0F172A;">{food_info['carbs_g']} <span style="font-size: 0.8rem;">g</span></div>
                        </div>
                        <div class="food-category-box">
                            <div style="font-size: 0.74rem; color: #64748B; font-weight: 700;">FAT</div>
                            <div style="font-size: 1.2rem; font-weight: 800; color: #F59E0B;">{food_info['fat_g']} <span style="font-size: 0.8rem;">g</span></div>
                        </div>
                    </div>
                </div>
                """)
            else:
                st.info(f"'{food_search_query}' not found in the verified dataset. Try searching for common Indian or global staples like Roti, Paneer, Dal, Chicken, Rice, Apple, Almonds, Oats, or Curd.")

    # =========================================================================
    # SUB-TAB 3: FOOD SUBSTITUTIONS
    # =========================================================================
    with sub_tab3:
        st.html("""
        <div style="margin-bottom: 1rem;">
            <h3 style="color: #0F172A; font-weight: 800; font-size: 1.2rem; margin-bottom: 0.25rem;">Smart Food Substitutions</h3>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Discover equivalent nutritional swaps from verified food databases.</p>
        </div>
        """)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            swap_food = st.selectbox("Select Food to Replace", ["Paneer", "Roti", "White Rice", "Chicken Breast", "Milk (Cow's)", "Peanuts"])
        with col_s2:
            swap_goal = st.selectbox("Substitution Goal", ["High Protein", "Lower Calorie", "Lactose Free", "Gluten Free", "Vegan Alternative"])

        if swap_food:
            swaps = NutritionService.get_food_swaps(swap_food, swap_goal)
            if swaps:
                st.write(f"**Recommended alternatives for {swap_food} ({swap_goal}):**")
                for s in swaps:
                    st.html(f"""
                    <div class="med-card" style="padding: 0.85rem 1.15rem; margin-bottom: 0.65rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 700; color: #0284C7; font-size: 0.95rem;">{s['name']}</span>
                            <span style="font-size: 0.82rem; color: #64748B;">{s['calories_kcal']} kcal • {s['protein_g']}g Protein</span>
                        </div>
                    </div>
                    """)
            else:
                st.info("No direct swap matches found for this specific criteria.")
