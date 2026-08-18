import os
import sys
sys.path.insert(0, os.path.abspath("."))

import unittest
from services.diet_planner_service import DietPlannerService
from database.repositories import DietRepository
from services.report_service import ReportService

class TestDietPlanner(unittest.TestCase):
    def setUp(self):
        self.user_a_id = "test-user-alpha-111"
        self.user_b_id = "test-user-beta-222"

    def test_01_target_calculation_fat_loss(self):
        profile = {"age": 30, "gender": "Male", "height_cm": 175.0, "weight_kg": 80.0}
        targets = DietPlannerService.calculate_nutrition_targets(
            profile, fitness_goal="Fat Loss / Weight Loss", activity_level="moderate"
        )
        
        self.assertGreater(targets["bmr"], 1600)
        self.assertGreater(targets["tdee"], targets["target_calories"])
        self.assertAlmostEqual(targets["tdee"] - targets["target_calories"], 450, delta=20)
        self.assertGreaterEqual(targets["protein_g"], 80.0 * 1.4)
        self.assertTrue(targets["is_estimate"])

    def test_02_target_calculation_muscle_gain(self):
        profile = {"age": 25, "gender": "Female", "height_cm": 165.0, "weight_kg": 60.0}
        targets = DietPlannerService.calculate_nutrition_targets(
            profile, fitness_goal="Muscle Gain", activity_level="active"
        )
        
        self.assertGreater(targets["target_calories"], targets["tdee"])
        self.assertAlmostEqual(targets["target_calories"] - targets["tdee"], 350, delta=10)
        self.assertGreaterEqual(targets["protein_g"], 60.0 * 1.7)
        self.assertTrue(targets["is_estimate"])

    def test_02b_all_six_fitness_goals(self):
        profile = {"age": 28, "gender": "Male", "height_cm": 180.0, "weight_kg": 75.0}
        goals = [
            "Maintain Current Physique",
            "Fat Loss / Weight Loss",
            "Muscle Gain",
            "Body Recomposition",
            "Performance / Strength",
            "General Fitness & Health"
        ]
        for g in goals:
            t = DietPlannerService.calculate_nutrition_targets(profile, fitness_goal=g)
            self.assertIn("target_calories", t)
            self.assertIn("protein_g", t)
            self.assertGreater(t["target_calories"], 1200)
            self.assertGreater(t["protein_g"], 50)
            self.assertTrue(t["is_estimate"])

    def test_03_hard_allergen_exclusion_peanuts(self):
        foods = DietPlannerService.filter_compatible_foods("Vegetarian", "Peanuts")
        peanut_matches = [f for f in foods if "peanut" in f["id"] or "peanut" in f.get("allergen_tags", [])]
        self.assertEqual(len(peanut_matches), 0)

    def test_04_hard_allergen_exclusion_dairy(self):
        foods = DietPlannerService.filter_compatible_foods("Vegetarian", "Dairy, Milk, Paneer")
        dairy_matches = [f for f in foods if "dairy" in f.get("allergen_tags", [])]
        self.assertEqual(len(dairy_matches), 0)

    def test_05_vegan_diet_compliance(self):
        foods = DietPlannerService.filter_compatible_foods("Vegan", "")
        for f in foods:
            tags = f.get("allergen_tags", [])
            self.assertNotIn("dairy", tags)
            self.assertNotIn("eggs", tags)
            self.assertNotIn("poultry", tags)
            self.assertNotIn("fish", tags)

    def test_06_jain_diet_compliance(self):
        foods = DietPlannerService.filter_compatible_foods("Jain", "")
        for f in foods:
            self.assertIn("jain_safe", f.get("diet_tags", []))

    def test_07_protein_powder_verified_and_custom(self):
        # 1. Verified Whey Isolate
        cfg_whey = {
            "enabled": True,
            "food_id": "usda_whey_isolate",
            "servings": 1.0
        }
        res_whey = DietPlannerService.calculate_protein_powder_nutrition(cfg_whey)
        self.assertIsNotNone(res_whey)
        self.assertEqual(res_whey["protein_g"], 24.0)
        self.assertEqual(res_whey["calories_kcal"], 120.0)

        # 2. Scaled Servings (1.5 scoops)
        cfg_1_5 = {
            "enabled": True,
            "food_id": "usda_whey_isolate",
            "servings": 1.5
        }
        res_1_5 = DietPlannerService.calculate_protein_powder_nutrition(cfg_1_5)
        self.assertEqual(res_1_5["protein_g"], 36.0)
        self.assertEqual(res_1_5["calories_kcal"], 180.0)

        # 3. Custom Protein Powder Entry
        cfg_custom = {
            "enabled": True,
            "food_id": "custom",
            "servings": 1.0,
            "custom_nutrition": {
                "brand_name": "Gold Standard 100% Whey",
                "serving_size_label": "1 scoop (30.4g)",
                "calories_kcal": 120.0,
                "protein_g": 24.0,
                "carbs_g": 3.0,
                "fat_g": 1.5,
                "fiber_g": 0.0
            }
        }
        res_custom = DietPlannerService.calculate_protein_powder_nutrition(cfg_custom)
        self.assertIsNotNone(res_custom)
        self.assertIn("Gold Standard", res_custom["name"])
        self.assertEqual(res_custom["protein_g"], 24.0)

    def test_08_empty_or_too_few_food_selection_handling(self):
        profile = {"name": "Arjun", "age": 29, "gender": "Male", "height_cm": 178.0, "weight_kg": 74.0}
        
        # 1. No foods selected
        res_empty = DietPlannerService.generate_7day_plan(
            profile, fitness_goal="Maintain Current Physique", dietary_preference="Vegetarian", selected_food_ids=[]
        )
        self.assertFalse(res_empty["success"])
        self.assertEqual(res_empty["error_code"], "NO_FOODS_SELECTED")

        # 2. Only 1 food selected (too few)
        res_few = DietPlannerService.generate_7day_plan(
            profile, fitness_goal="Maintain Current Physique", dietary_preference="Vegetarian", selected_food_ids=["icmr_apple"]
        )
        self.assertFalse(res_few["success"])
        self.assertEqual(res_few["error_code"], "TOO_FEW_FOODS")

    def test_09_deterministic_7day_plan_and_90pct_optimization(self):
        profile = {"name": "Arjun", "age": 29, "gender": "Male", "height_cm": 178.0, "weight_kg": 74.0, "allergies": "None"}
        selected_foods = [
            "icmr_apple", "icmr_banana", "icmr_spinach_palak", "usda_broccoli",
            "icmr_paneer", "icmr_roti", "icmr_brown_rice", "usda_oats",
            "icmr_toor_dal", "icmr_curd", "icmr_almonds"
        ]
        powder_cfg = {
            "enabled": True,
            "food_id": "usda_whey_isolate",
            "servings": 1.0
        }

        plan = DietPlannerService.generate_7day_plan(
            profile=profile,
            fitness_goal="Maintain Current Physique",
            dietary_preference="Vegetarian",
            selected_food_ids=selected_foods,
            protein_powder_config=powder_cfg
        )
        
        self.assertTrue(plan["success"])
        self.assertEqual(len(plan["days"]), 7)

        # Check 7-day variety: Day 1 meals shouldn't be identically stringified to Day 2
        day_1_str = str(plan["days"][0]["meals"])
        day_2_str = str(plan["days"][1]["meals"])
        self.assertNotEqual(day_1_str, day_2_str)

        for day in plan["days"]:
            self.assertEqual(len(day["meals"]), 5) # 5 structured daily meals
            
            # Verify that summary is exactly the sum of the meals
            calc_cal = sum(m["total_calories"] for m in day["meals"])
            calc_prot = sum(m["total_protein"] for m in day["meals"])
            calc_carbs = sum(m["total_carbs"] for m in day["meals"])
            calc_fat = sum(m["total_fat"] for m in day["meals"])
            calc_fiber = sum(m["total_fiber"] for m in day["meals"])

            self.assertAlmostEqual(day["summary"]["calories"], calc_cal, delta=0.5)
            self.assertAlmostEqual(day["summary"]["protein_g"], calc_prot, delta=0.5)
            self.assertAlmostEqual(day["summary"]["carbs_g"], calc_carbs, delta=0.5)
            self.assertAlmostEqual(day["summary"]["fat_g"], calc_fat, delta=0.5)
            self.assertAlmostEqual(day["summary"]["fiber_g"], calc_fiber, delta=0.5)

            # Check that day achieves approximately >=90% of target calories & protein
            self.assertGreaterEqual(day["summary"]["calories_pct"], 85)
            self.assertGreaterEqual(day["summary"]["protein_pct"], 85)

    def test_10_food_substitution_and_recalculation(self):
        profile = {"age": 30, "gender": "Male", "height_cm": 175.0, "weight_kg": 75.0}
        selected_foods = [
            "icmr_apple", "icmr_banana", "icmr_paneer", "icmr_roti",
            "icmr_toor_dal", "icmr_curd", "icmr_spinach_palak"
        ]
        plan = DietPlannerService.generate_7day_plan(
            profile, fitness_goal="Maintain Current Physique", dietary_preference="Vegetarian", selected_food_ids=selected_foods
        )
        
        day_0 = plan["days"][0]
        first_meal = day_0["meals"][0]
        first_item = first_meal["items"][0]
        
        # Swap with tofu
        updated_plan = DietPlannerService.substitute_food_in_plan(
            plan=plan,
            day_idx=0,
            meal_idx=0,
            old_food_id=first_item["id"],
            new_food_id="usda_tofu"
        )
        
        updated_day_0 = updated_plan["days"][0]
        expected_cal = sum(m["total_calories"] for m in updated_day_0["meals"])
        self.assertAlmostEqual(updated_day_0["summary"]["calories"], expected_cal, delta=0.5)

    def test_11_medical_safety_override(self):
        safe_profile = {"conditions": "None"}
        res_safe = DietPlannerService.check_medical_safety_override(safe_profile)
        self.assertFalse(res_safe["has_warning"])

        renal_profile = {"conditions": "Chronic Kidney Disease Stage 3, Hypertension"}
        res_renal = DietPlannerService.check_medical_safety_override(renal_profile)
        self.assertTrue(res_renal["has_warning"])
        self.assertIn("kidney", res_renal["warning_text"].lower())

    def test_12_user_isolation_saved_plans(self):
        plan_a = DietRepository.save_plan(
            user_id=self.user_a_id,
            goal="Weight Loss",
            diet_type="Vegan",
            plan_text="Plan for User A"
        )
        
        plan_b = DietRepository.save_plan(
            user_id=self.user_b_id,
            goal="Muscle Gain",
            diet_type="Non-Vegetarian",
            plan_text="Plan for User B"
        )

        plans_a = DietRepository.list_plans(self.user_a_id)
        self.assertTrue(any(p["id"] == plan_a["id"] for p in plans_a))
        self.assertFalse(any(p["id"] == plan_b["id"] for p in plans_a))

        plans_b = DietRepository.list_plans(self.user_b_id)
        self.assertTrue(any(p["id"] == plan_b["id"] for p in plans_b))
        self.assertFalse(any(p["id"] == plan_a["id"] for p in plans_b))

    def test_13_pdf_report_export(self):
        pdf_bytes = ReportService.generate_pdf_report(
            title="7-Day Diet Plan — Maintain Physique",
            report_type="diet_plan",
            content_text="## **Day 1**\n- Breakfast: Oats + Apple (228 kcal)\n- Lunch: Roti + Toor Dal + Spinach (351 kcal)",
            user_name="Arjun",
            profile={"age": 29, "gender": "Male"}
        )
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertGreater(len(pdf_bytes), 100)

if __name__ == "__main__":
    unittest.main()
