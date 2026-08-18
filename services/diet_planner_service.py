"""
VitalBite AI — Interactive 7-Day Personalized Diet & Fitness Nutrition Planner Service
Computes goal-aligned nutritional target estimates (educational/fitness reference), applies hard allergen exclusions,
incorporates verified protein powder supplements, optimizes realistic food portions toward >=90% targets,
and constructs 7-day meal plans with deterministic ICMR-NIN/USDA food data.
"""
import os
import json
import random
from typing import Dict, Any, List, Optional
from services.health_service import HealthService

HIGH_RISK_CONDITIONS = [
    "kidney", "renal", "ckd", "dialysis",
    "type 1 diabetes", "insulin",
    "cirrhosis", "liver failure",
    "heart failure", "chf",
    "chemotherapy", "cancer active",
    "celiac", "severe malabsorption"
]

class DietPlannerService:
    _foods_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def load_foods(cls) -> List[Dict[str, Any]]:
        """Loads verified food database from datasets/icmr_nin_foods.json."""
        if cls._foods_cache is not None:
            return cls._foods_cache

        dataset_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "icmr_nin_foods.json")
        try:
            if os.path.exists(dataset_path):
                with open(dataset_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls._foods_cache = data.get("foods", [])
                    return cls._foods_cache
        except Exception as e:
            print(f"[DietPlannerService] Error loading food dataset: {e}")
        
        cls._foods_cache = []
        return cls._foods_cache

    @classmethod
    def check_medical_safety_override(cls, profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Checks if user profile contains clinical conditions requiring specialized medical supervision.
        """
        if not profile:
            return {"has_warning": False, "warning_text": ""}

        conditions_str = str(profile.get("conditions", "")).lower()
        matched = [c for c in HIGH_RISK_CONDITIONS if c in conditions_str]

        if matched:
            return {
                "has_warning": True,
                "warning_text": (
                    f"⚠️ Medical Caution: Your profile notes medical considerations ({', '.join(matched)}). "
                    "Automated meal plans are for general educational reference and fitness estimation only. "
                    "Please consult your physician or registered clinical dietitian before modifying your diet."
                )
            }
        return {"has_warning": False, "warning_text": ""}

    @classmethod
    def calculate_nutrition_targets(
        cls,
        profile: Dict[str, Any],
        fitness_goal: str,
        activity_level: str = "moderate",
        training_frequency: str = "2-3 days/week",
        training_type: str = "Mixed Training"
    ) -> Dict[str, Any]:
        """
        Calculates daily calorie, protein, carbohydrate, fat, and fiber target estimates.
        IMPORTANT: These are fitness & nutritional estimates, NOT clinical prescriptions.
        """
        height_cm = float(profile.get("height_cm") or 170.0)
        weight_kg = float(profile.get("weight_kg") or 65.0)
        age = int(profile.get("age") or 30)
        gender = str(profile.get("gender") or "Male")

        bmr = HealthService.calculate_bmr(height_cm, weight_kg, age, gender) or 1500.0

        # Adjust activity level baseline based on training frequency
        freq_lower = training_frequency.lower()
        effective_act = activity_level.lower()
        if "6+" in freq_lower or "high volume" in freq_lower:
            effective_act = "very_active"
        elif "4-5" in freq_lower and effective_act in ["sedentary", "light"]:
            effective_act = "active"
        elif "2-3" in freq_lower and effective_act == "sedentary":
            effective_act = "moderate"

        tdee = HealthService.calculate_tdee(bmr, effective_act) or 2200.0
        goal_lower = fitness_goal.lower()

        # Fitness Goal Estimations (Safe bounds, no extreme deficits/surpluses)
        if "muscle gain" in goal_lower:
            # Calorie surplus + high protein
            target_calories = tdee + 350.0
            protein_g = round(weight_kg * 1.8, 1) # 1.8 g/kg
            fat_g = round((target_calories * 0.25) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 32.0
            goal_category = "Muscle Gain"
        elif "fat loss" in goal_lower or "weight loss" in goal_lower:
            # Calorie deficit with safe floor
            floor_cal = 1200.0 if gender.lower() == "female" else 1500.0
            target_calories = max(floor_cal, tdee - 450.0)
            protein_g = round(weight_kg * 1.5, 1) # Preserved protein during deficit
            fat_g = round((target_calories * 0.25) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 35.0
            goal_category = "Fat Loss / Calorie Deficit"
        elif "recomposition" in goal_lower:
            # Slight deficit to maintenance, elevated protein
            target_calories = max(1400.0, tdee - 150.0)
            protein_g = round(weight_kg * 1.7, 1)
            fat_g = round((target_calories * 0.26) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 32.0
            goal_category = "Body Recomposition"
        elif "performance" in goal_lower or "strength" in goal_lower:
            # Fueling surplus + robust protein
            target_calories = tdee + 250.0
            protein_g = round(weight_kg * 1.7, 1)
            fat_g = round((target_calories * 0.25) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 30.0
            goal_category = "Performance / Strength"
        elif "general fitness" in goal_lower or "energy" in goal_lower:
            # Maintenance calories + balanced macros
            target_calories = tdee
            protein_g = round(weight_kg * 1.3, 1)
            fat_g = round((target_calories * 0.28) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 30.0
            goal_category = "General Fitness & Health"
        else: # Maintain Current Physique
            target_calories = tdee
            protein_g = round(weight_kg * 1.3, 1)
            fat_g = round((target_calories * 0.28) / 9.0, 1)
            carbs_g = round((target_calories - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0, 1)
            fiber_g = 30.0
            goal_category = "Maintain Current Physique"

        return {
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "target_calories": round(target_calories, 0),
            "protein_g": round(protein_g, 1),
            "carbs_g": max(50.0, round(carbs_g, 1)),
            "fat_g": max(25.0, round(fat_g, 1)),
            "fiber_g": round(fiber_g, 1),
            "goal": fitness_goal,
            "goal_category": goal_category,
            "activity_level": activity_level,
            "training_frequency": training_frequency,
            "training_type": training_type,
            "is_estimate": True
        }

    @classmethod
    def filter_compatible_foods(
        cls, dietary_preference: str, allergies: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Applies hard exclusions for dietary preferences and allergens to all verified foods.
        """
        all_foods = cls.load_foods()
        pref_clean = dietary_preference.lower()
        allergies_clean = [a.strip().lower() for a in allergies.split(",") if a.strip() and a.strip().lower() != "none"]

        compatible = []
        for food in all_foods:
            diet_tags = food.get("diet_tags", [])
            allergen_tags = food.get("allergen_tags", [])

            # 1. Dietary Preference Hard Check
            if "vegan" in pref_clean:
                if "vegan" not in diet_tags:
                    continue
            elif "jain" in pref_clean:
                if "jain_safe" not in diet_tags:
                    continue
            elif "vegetarian" in pref_clean and "non" not in pref_clean and "egg" not in pref_clean:
                if "vegetarian" not in diet_tags:
                    continue
            elif "eggetarian" in pref_clean:
                if "eggetarian" not in diet_tags and "vegetarian" not in diet_tags:
                    continue

            # 2. Hard Allergen Exclusions
            is_allergic = False
            for user_allergy in allergies_clean:
                for tag in allergen_tags:
                    if user_allergy in tag or tag in user_allergy:
                        is_allergic = True
                        break
                # Check food name / aliases against allergy
                f_name = food.get("name", "").lower()
                if user_allergy in f_name or any(user_allergy in al.lower() for al in food.get("aliases", [])):
                    is_allergic = True
                if is_allergic:
                    break

            if is_allergic:
                continue

            compatible.append(food)

        return compatible

    @classmethod
    def get_food_categories_dict(
        cls, dietary_preference: str, allergies: str = ""
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Groups filtered compatible foods into UI-friendly category buckets."""
        compatible = cls.filter_compatible_foods(dietary_preference, allergies)
        categories = {
            "🍎 Fruits": [],
            "🥦 Vegetables": [],
            "🍗 Protein (Whole Foods)": [],
            "🍚 Grains & Cereals": [],
            "🥛 Dairy & Plant Milks": [],
            "🥜 Nuts & Seeds": [],
            "🫘 Legumes & Dals": [],
            "🍛 Indian Prepared Dishes": []
        }

        cat_mapping = {
            "Fruits": "🍎 Fruits",
            "Vegetables": "🥦 Vegetables",
            "Protein": "🍗 Protein (Whole Foods)",
            "Grains & Cereals": "🍚 Grains & Cereals",
            "Dairy & Plant Milks": "🥛 Dairy & Plant Milks",
            "Nuts & Seeds": "🥜 Nuts & Seeds",
            "Legumes & Dals": "🫘 Legumes & Dals",
            "Indian Prepared Dishes": "🍛 Indian Prepared Dishes"
        }

        for food in compatible:
            # Exclude supplement protein powders from the regular whole food protein category list
            if food.get("is_supplement", False):
                continue
            c = food.get("category", "")
            mapped_key = cat_mapping.get(c)
            if mapped_key and mapped_key in categories:
                categories[mapped_key].append(food)

        return categories

    @classmethod
    def get_protein_powder_options(
        cls, dietary_preference: str, allergies: str = ""
    ) -> List[Dict[str, Any]]:
        """Returns compatible verified protein powder supplement options."""
        compatible = cls.filter_compatible_foods(dietary_preference, allergies)
        return [f for f in compatible if f.get("is_supplement", False)]

    @classmethod
    def calculate_protein_powder_nutrition(
        cls,
        powder_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Deterministically calculates protein powder nutrition based on verified record or custom label.
        Capped at 2.0 servings maximum for nutritional realism and safety.
        """
        if not powder_config or not powder_config.get("enabled", False):
            return None

        servings = min(2.0, max(0.0, float(powder_config.get("servings", 0.0))))
        if servings <= 0:
            return None

        food_id = powder_config.get("food_id")
        if food_id == "custom":
            custom_data = powder_config.get("custom_nutrition", {})
            brand_name = custom_data.get("brand_name", "Custom Protein Powder")
            serving_size_label = custom_data.get("serving_size_label", "1 scoop (30g)")
            cal_per = float(custom_data.get("calories_kcal", 120.0))
            prot_per = float(custom_data.get("protein_g", 24.0))
            carbs_per = float(custom_data.get("carbs_g", 2.0))
            fat_per = float(custom_data.get("fat_g", 1.0))
            fiber_per = float(custom_data.get("fiber_g", 0.0))

            return {
                "id": "custom_protein_powder",
                "name": f"{brand_name} ({servings} scoop{'s' if servings != 1 else ''})",
                "brand_name": brand_name,
                "serving_size": f"{servings} scoop(s) ({serving_size_label})",
                "base_serving_size": serving_size_label,
                "servings": servings,
                "calories_kcal": round(cal_per * servings, 1),
                "protein_g": round(prot_per * servings, 1),
                "carbs_g": round(carbs_per * servings, 1),
                "fat_g": round(fat_per * servings, 1),
                "fiber_g": round(fiber_per * servings, 1),
                "source": "User-Entered Verified Product Label",
                "is_supplement": True
            }

        # Look up in verified database
        all_foods = {f["id"]: f for f in cls.load_foods()}
        base_item = all_foods.get(food_id)
        if not base_item:
            return None

        return {
            "id": base_item["id"],
            "name": f"{base_item['name']} ({servings} scoop{'s' if servings != 1 else ''})",
            "base_name": base_item["name"],
            "serving_size": f"{servings} scoop(s) (~{round(servings * 30)}g)",
            "base_serving_size": base_item["serving_size"],
            "servings": servings,
            "calories_kcal": round(float(base_item["calories_kcal"]) * servings, 1),
            "protein_g": round(float(base_item["protein_g"]) * servings, 1),
            "carbs_g": round(float(base_item["carbs_g"]) * servings, 1),
            "fat_g": round(float(base_item["fat_g"]) * servings, 1),
            "fiber_g": round(float(base_item.get("fiber_g", 0.0)) * servings, 1),
            "source": base_item.get("source", "Verified Dataset Record"),
            "ref_id": base_item.get("ref_id", "USDA-FDC"),
            "is_supplement": True
        }

    @classmethod
    def generate_7day_plan(
        cls,
        profile: Dict[str, Any],
        fitness_goal: str,
        dietary_preference: str,
        selected_food_ids: Optional[List[str]] = None,
        activity_level: str = "moderate",
        training_frequency: str = "2-3 days/week",
        training_type: str = "Mixed Training",
        protein_powder_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Constructs a structured 7-day meal plan optimizing daily totals toward >=90% of calculated targets.
        Strictly deterministic. If selected food pool is insufficient to construct a plan, returns an informative explanation.
        """
        targets = cls.calculate_nutrition_targets(
            profile=profile,
            fitness_goal=fitness_goal,
            activity_level=activity_level,
            training_frequency=training_frequency,
            training_type=training_type
        )
        allergies = profile.get("allergies", "")
        compatible_foods = cls.filter_compatible_foods(dietary_preference, allergies)
        compatible_dict = {f["id"]: f for f in compatible_foods}

        # 1. Evaluate User Food Selection
        if selected_food_ids:
            user_pool = [compatible_dict[fid] for fid in selected_food_ids if fid in compatible_dict]
        else:
            user_pool = []

        # Check if protein powder is configured
        powder_item = cls.calculate_protein_powder_nutrition(protein_powder_config or {})

        # Validation: User must explicitly select foods
        if not user_pool:
            return {
                "success": False,
                "error_code": "NO_FOODS_SELECTED",
                "message": (
                    "Please select the food items you enjoy from the categories above. "
                    "VitalBite AI constructs your personalized meal plan exclusively from your chosen foods."
                ),
                "targets": targets
            }

        # Minimum pool validation: need at least 3 distinct food items to build varied realistic daily meals
        if len(user_pool) < 3:
            return {
                "success": False,
                "error_code": "TOO_FEW_FOODS",
                "message": (
                    f"You have selected only {len(user_pool)} food item(s). "
                    "To construct a nutritionally balanced 7-day meal plan reaching approximately 90%+ of your daily targets, "
                    "please select at least 4 to 6 items across proteins, grains, vegetables, and fruits."
                ),
                "targets": targets
            }

        # Segregate pool by categories for realistic meal construction
        fruits = [f for f in user_pool if f.get("category") == "Fruits"]
        veggies = [f for f in user_pool if f.get("category") == "Vegetables"]
        proteins = [f for f in user_pool if f.get("category") in ["Protein", "Legumes & Dals"]]
        grains = [f for f in user_pool if f.get("category") in ["Grains & Cereals", "Indian Prepared Dishes"]]
        dairy_milks = [f for f in user_pool if f.get("category") == "Dairy & Plant Milks"]
        nuts_seeds = [f for f in user_pool if f.get("category") == "Nuts & Seeds"]

        # If user selected only items from 1 single group, alert them
        populated_groups = sum(1 for g in [fruits, veggies, proteins, grains, dairy_milks, nuts_seeds] if len(g) > 0)
        if populated_groups < 2 and not powder_item:
            return {
                "success": False,
                "error_code": "INSUFFICIENT_VARIETY",
                "message": (
                    "Your selected foods are from only a single food category. "
                    "For realistic 5-meal daily planning and to achieve your macronutrient targets, "
                    "please select foods from multiple categories (e.g. grains, proteins, vegetables, and fruits)."
                ),
                "targets": targets
            }

        # Build meal-specific candidate pools
        breakfast_grains = [f for f in user_pool if f.get("category") in ["Grains & Cereals", "Indian Prepared Dishes"]]
        breakfast_candidates = breakfast_grains or [f for f in user_pool if "breakfast" in f.get("meal_suitability", [])] or user_pool

        lunch_grains = [f for f in user_pool if f.get("category") in ["Grains & Cereals", "Indian Prepared Dishes"]] or user_pool
        dinner_grains = [f for f in user_pool if f.get("category") in ["Grains & Cereals", "Indian Prepared Dishes"]] or user_pool

        target_cal = targets["target_calories"]
        target_prot = targets["protein_g"]

        days = []
        for day_num in range(1, 8):
            rng = random.Random(day_num * 137 + len(user_pool) * 19)

            # 1. 🌅 Breakfast: Main breakfast dish/grain + accompaniment (dairy/protein) + fruit
            b_items = []
            b_main = rng.choice(breakfast_candidates)
            b_items.append(cls._clone_food_item(b_main, multiplier=1.0))
            
            b_acc_cands = [f for f in (dairy_milks + proteins) if f["id"] != b_main["id"]]
            if b_acc_cands:
                b_items.append(cls._clone_food_item(rng.choice(b_acc_cands), multiplier=1.0))
            
            if fruits:
                b_fruit = rng.choice([f for f in fruits if f["id"] != b_main["id"]] or fruits)
                b_items.append(cls._clone_food_item(b_fruit, multiplier=1.0))

            # 2. ☀️ Mid-Morning Snack: Protein supplement if enabled, or fruit/nuts/sprouts
            snack1_items = []
            if powder_item:
                snack1_items.append(dict(powder_item))
                if fruits:
                    snack1_items.append(cls._clone_food_item(rng.choice(fruits), multiplier=1.0))
            elif nuts_seeds:
                snack1_items.append(cls._clone_food_item(rng.choice(nuts_seeds), multiplier=1.0))
                if fruits:
                    snack1_items.append(cls._clone_food_item(rng.choice(fruits), multiplier=1.0))
            elif fruits:
                snack1_items.append(cls._clone_food_item(rng.choice(fruits), multiplier=1.0))
            else:
                snack1_items.append(cls._clone_food_item(rng.choice(user_pool), multiplier=1.0))

            # 3. 🍛 Lunch: Grain staple + Main Protein (Paneer/Chicken/Fish/Soya) + Dal + Vegetable
            l_items = []
            l_grain = rng.choice(lunch_grains)
            l_items.append(cls._clone_food_item(l_grain, multiplier=1.0))

            l_prot_cands = [f for f in (proteins + [f for f in user_pool if f.get("category") == "Legumes & Dals"]) if f["id"] != l_grain["id"]]
            if l_prot_cands:
                l_items.append(cls._clone_food_item(rng.choice(l_prot_cands), multiplier=1.0))
            
            # Second protein/dal if available
            l_dal_cands = [f for f in user_pool if f.get("category") == "Legumes & Dals" and f["id"] not in [it["id"] for it in l_items]]
            if l_dal_cands:
                l_items.append(cls._clone_food_item(rng.choice(l_dal_cands), multiplier=1.0))

            if veggies:
                l_veg = rng.choice([f for f in veggies if f["id"] not in [it["id"] for it in l_items]] or veggies)
                l_items.append(cls._clone_food_item(l_veg, multiplier=1.0))

            if dairy_milks and all(it.get("category") != "Dairy & Plant Milks" for it in l_items):
                l_items.append(cls._clone_food_item(rng.choice(dairy_milks), multiplier=1.0))

            # 4. ☕ Evening Snack: Chaas / Sprouts / Nuts / Fruit
            snack2_items = []
            snack2_cands = [f for f in (nuts_seeds + dairy_milks + [f for f in user_pool if "sprouts" in f["id"]]) if all(f["id"] != it["id"] for it in snack1_items)]
            if snack2_cands:
                snack2_items.append(cls._clone_food_item(rng.choice(snack2_cands), multiplier=1.0))
            elif fruits:
                snack2_items.append(cls._clone_food_item(rng.choice(fruits), multiplier=1.0))
            else:
                snack2_items.append(cls._clone_food_item(rng.choice(user_pool), multiplier=1.0))

            # 5. 🌙 Dinner: Grain/Dish + Main Dal/Protein Sabzi + Vegetable side
            d_items = []
            d_grain_cands = [f for f in dinner_grains if f["id"] != l_grain["id"]] or dinner_grains
            d_grain = rng.choice(d_grain_cands)
            d_items.append(cls._clone_food_item(d_grain, multiplier=1.0))

            d_prot_cands = [f for f in (proteins + [f for f in user_pool if f.get("category") == "Legumes & Dals"]) if f["id"] != d_grain["id"]]
            if d_prot_cands:
                d_items.append(cls._clone_food_item(rng.choice(d_prot_cands), multiplier=1.0))

            if veggies and all(it["id"] not in [v["id"] for v in veggies] for it in d_items):
                d_items.append(cls._clone_food_item(rng.choice(veggies), multiplier=1.0))

            # =========================================================================
            # Target Optimization Engine: Realistic Portion Scaling Toward >=90% Targets
            # =========================================================================
            all_day_items = b_items + snack1_items + l_items + snack2_items + d_items
            base_cal = sum(it.get("calories_kcal", 0.0) for it in all_day_items)

            if base_cal > 0:
                deficit_ratio = target_cal / base_cal
                if deficit_ratio > 1.02:
                    scale_mult = min(2.0, max(1.0, deficit_ratio * 1.15))
                    for it in all_day_items:
                        if it.get("is_supplement"):
                            continue
                        cat = it.get("category", "")
                        if cat in ["Grains & Cereals", "Legumes & Dals", "Protein", "Indian Prepared Dishes"]:
                            portion_mult = min(2.0, round(scale_mult, 1))
                            cls._apply_multiplier_to_item(it, portion_mult)
                        elif cat in ["Dairy & Plant Milks", "Nuts & Seeds"] and deficit_ratio >= 1.15:
                            cls._apply_multiplier_to_item(it, min(1.5, round(scale_mult * 0.9, 1)))

            # Package formatted meals
            meals = [
                cls._format_meal("🌅 Breakfast", b_items),
                cls._format_meal("☀️ Mid-Morning Snack", snack1_items),
                cls._format_meal("🍛 Lunch", l_items),
                cls._format_meal("☕ Evening Snack", snack2_items),
                cls._format_meal("🌙 Dinner", d_items)
            ]

            day_cal = sum(m["total_calories"] for m in meals)
            day_prot = sum(m["total_protein"] for m in meals)
            day_carbs = sum(m["total_carbs"] for m in meals)
            day_fat = sum(m["total_fat"] for m in meals)
            day_fiber = sum(m["total_fiber"] for m in meals)

            cal_pct = round((day_cal / max(1.0, target_cal)) * 100)
            prot_pct = round((day_prot / max(1.0, target_prot)) * 100)
            target_reached = (cal_pct >= 90 and prot_pct >= 88)

            days.append({
                "day_number": day_num,
                "day_name": f"Day {day_num}",
                "meals": meals,
                "summary": {
                    "calories": round(day_cal, 0),
                    "protein_g": round(day_prot, 1),
                    "carbs_g": round(day_carbs, 1),
                    "fat_g": round(day_fat, 1),
                    "fiber_g": round(day_fiber, 1),
                    "calories_pct": cal_pct,
                    "protein_pct": prot_pct,
                    "target_reached": target_reached
                }
            })

        # Evaluate overall plan 90% reach
        avg_cal_pct = sum(d["summary"]["calories_pct"] for d in days) // 7
        avg_prot_pct = sum(d["summary"]["protein_pct"] for d in days) // 7

        advice_message = ""
        if avg_cal_pct < 90 or avg_prot_pct < 90:
            advice_message = (
                f"Your selected foods achieve approximately {avg_cal_pct}% of your daily calorie target "
                f"and {avg_prot_pct}% of your protein target. To optimize closer to 90–100%, consider adding "
                "additional dense foods (such as dals, paneer, oats, nuts, or protein powder) to your selection."
            )

        return {
            "success": True,
            "goal": fitness_goal,
            "dietary_preference": dietary_preference,
            "targets": targets,
            "allergies_excluded": allergies or "None",
            "days": days,
            "protein_powder_included": powder_item is not None,
            "protein_powder_item": powder_item,
            "avg_cal_pct": avg_cal_pct,
            "avg_prot_pct": avg_prot_pct,
            "advice_message": advice_message,
            "disclaimer": (
                "VitalBite AI provides general educational and fitness nutrition estimations. "
                "It is not a clinical diagnosis or medical prescription. Consult a qualified healthcare professional "
                "or registered dietitian for individualized clinical nutrition advice."
            )
        }

    @staticmethod
    def _clone_food_item(food: Dict[str, Any], multiplier: float = 1.0) -> Dict[str, Any]:
        """Clones a food item dictionary with base value retention."""
        item = dict(food)
        item["base_calories_kcal"] = float(food.get("calories_kcal", 0.0))
        item["base_protein_g"] = float(food.get("protein_g", 0.0))
        item["base_carbs_g"] = float(food.get("carbs_g", 0.0))
        item["base_fat_g"] = float(food.get("fat_g", 0.0))
        item["base_fiber_g"] = float(food.get("fiber_g", 0.0))
        item["base_serving_size"] = str(food.get("serving_size", ""))
        DietPlannerService._apply_multiplier_to_item(item, multiplier)
        return item

    @staticmethod
    def _apply_multiplier_to_item(item: Dict[str, Any], multiplier: float):
        """Applies multiplier to an item's macro values and adjusts serving string."""
        orig_serving = item.get("base_serving_size", item.get("serving_size", ""))
        item["multiplier"] = multiplier
        if multiplier == 1.0:
            item["serving_size"] = orig_serving
        elif multiplier == 1.5:
            item["serving_size"] = f"1.5x portion ({orig_serving})"
        elif multiplier == 2.0:
            item["serving_size"] = f"Double portion / 2x ({orig_serving})"
        else:
            item["serving_size"] = f"{multiplier}x ({orig_serving})"

        base_c = item.get("base_calories_kcal", float(item.get("calories_kcal", 0.0)))
        base_p = item.get("base_protein_g", float(item.get("protein_g", 0.0)))
        base_carb = item.get("base_carbs_g", float(item.get("carbs_g", 0.0)))
        base_f = item.get("base_fat_g", float(item.get("fat_g", 0.0)))
        base_fib = item.get("base_fiber_g", float(item.get("fiber_g", 0.0)))

        item["calories_kcal"] = round(base_c * multiplier, 1)
        item["protein_g"] = round(base_p * multiplier, 1)
        item["carbs_g"] = round(base_carb * multiplier, 1)
        item["fat_g"] = round(base_f * multiplier, 1)
        item["fiber_g"] = round(base_fib * multiplier, 1)

    @classmethod
    def _format_meal(cls, meal_title: str, foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates items into a meal structure with verified totals."""
        cal = sum(f.get("calories_kcal", 0.0) for f in foods)
        prot = sum(f.get("protein_g", 0.0) for f in foods)
        carbs = sum(f.get("carbs_g", 0.0) for f in foods)
        fat = sum(f.get("fat_g", 0.0) for f in foods)
        fiber = sum(f.get("fiber_g", 0.0) for f in foods)

        return {
            "meal_name": meal_title,
            "items": foods,
            "total_calories": round(cal, 0),
            "total_protein": round(prot, 1),
            "total_carbs": round(carbs, 1),
            "total_fat": round(fat, 1),
            "total_fiber": round(fiber, 1),
            "sources": list(set(f.get("source", "ICMR-NIN IFCT") for f in foods))
        }

    @classmethod
    def substitute_food_in_plan(
        cls,
        plan: Dict[str, Any],
        day_idx: int,
        meal_idx: int,
        old_food_id: str,
        new_food_id: str
    ) -> Dict[str, Any]:
        """
        Replaces a food item within a meal and recalculates exact daily totals.
        """
        all_foods = {f["id"]: f for f in cls.load_foods()}
        new_food = all_foods.get(new_food_id)
        if not new_food:
            return plan

        try:
            day = plan["days"][day_idx]
            meal = day["meals"][meal_idx]
            updated_items = []
            for item in meal["items"]:
                if item["id"] == old_food_id:
                    # Inherit multiplier if applicable
                    mult = item.get("multiplier", 1.0)
                    cloned = cls._clone_food_item(new_food, mult)
                    updated_items.append(cloned)
                else:
                    updated_items.append(item)

            day["meals"][meal_idx] = cls._format_meal(meal["meal_name"], updated_items)

            # Recalculate day summary
            day_cal = sum(m["total_calories"] for m in day["meals"])
            day_prot = sum(m["total_protein"] for m in day["meals"])
            day_carbs = sum(m["total_carbs"] for m in day["meals"])
            day_fat = sum(m["total_fat"] for m in day["meals"])
            day_fiber = sum(m["total_fiber"] for m in day["meals"])

            target_cal = plan["targets"]["target_calories"]
            target_prot = plan["targets"]["protein_g"]
            cal_pct = round((day_cal / max(1.0, target_cal)) * 100)
            prot_pct = round((day_prot / max(1.0, target_prot)) * 100)

            day["summary"] = {
                "calories": round(day_cal, 0),
                "protein_g": round(day_prot, 1),
                "carbs_g": round(day_carbs, 1),
                "fat_g": round(day_fat, 1),
                "fiber_g": round(day_fiber, 1),
                "calories_pct": cal_pct,
                "protein_pct": prot_pct,
                "target_reached": (cal_pct >= 90 and prot_pct >= 88)
            }
        except Exception as e:
            print(f"[DietPlannerService] Substitution error: {e}")

        return plan
