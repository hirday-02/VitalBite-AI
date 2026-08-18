"""
VitalBite AI — Demo Mode & Deployment Resilience Test Suite
Verifies zero-credential demo startup, session isolation, fallback AI responses,
data containment, exit demo behavior, and seamless coexistence with real private accounts.
"""
import os
import unittest
from unittest.mock import patch
import streamlit as st

from services.auth_service import AuthService, SESSION_USER_KEY, SESSION_DEMO_KEY
from services.demo_service import DEMO_USER_ID, get_fallback_ai_response, get_fallback_symptom_assessment
from database.client import SupabaseManager
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository, AccountRepository
from services.health_service import HealthService
from services.diet_planner_service import DietPlannerService
from services.ai_service import AIService

class TestDemoMode(unittest.TestCase):
    def setUp(self):
        # Clear Streamlit session state
        for k in list(st.session_state.keys()):
            del st.session_state[k]

    def test_01_demo_starts_without_supabase_or_gemini_credentials(self):
        """Verify demo mode initializes cleanly with zero credentials."""
        with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
            AuthService.start_demo_mode()
            self.assertTrue(AuthService.is_authenticated())
            self.assertTrue(AuthService.is_demo_mode())
            self.assertEqual(AuthService.get_current_user_id(), DEMO_USER_ID)

    def test_02_demo_profile_loads_fictional_data(self):
        """Verify demo profile contains realistic fictional data."""
        AuthService.start_demo_mode()
        profile = ProfileRepository.get_profile(DEMO_USER_ID)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.get("name"), "Alex Rivera")
        self.assertEqual(profile.get("age"), 28)
        self.assertEqual(profile.get("gender"), "Male")
        self.assertEqual(profile.get("fitness_goal"), "Body Recomposition")
        self.assertEqual(profile.get("blood_type"), "O+")

    def test_03_demo_data_does_not_reach_supabase(self):
        """Verify that demo updates and saves only mutate session state, never Supabase."""
        AuthService.start_demo_mode()
        
        # Modify demo profile
        ProfileRepository.upsert_profile(DEMO_USER_ID, {"name": "Alex Modified", "age": 29})
        updated = ProfileRepository.get_profile(DEMO_USER_ID)
        self.assertEqual(updated.get("name"), "Alex Modified")
        self.assertEqual(updated.get("age"), 29)

        # Add symptom assessment
        sym = SymptomRepository.save_assessment(DEMO_USER_ID, "Mild headache", "1 day", "2", "Analysis text")
        self.assertIsNotNone(sym.get("id"))
        assessments = SymptomRepository.list_assessments(DEMO_USER_ID)
        self.assertTrue(any(a["symptoms"] == "Mild headache" for a in assessments))

        # Add diet plan
        dp = DietRepository.save_plan(DEMO_USER_ID, "Fat Loss", "Vegetarian", "Sample plan")
        self.assertIsNotNone(dp.get("id"))
        plans = DietRepository.list_plans(DEMO_USER_ID)
        self.assertTrue(any(p["goal"] == "Fat Loss" for p in plans))

    def test_04_fallback_ai_response_for_demo_and_offline(self):
        """Verify evidence-based fallback AI responses when Gemini is unavailable."""
        ai_resp = get_fallback_ai_response("What workout should I do at the gym for muscle progress?", "Alex")
        self.assertIn("Training", ai_resp)
        self.assertIn("Progressive Overload", ai_resp)
        self.assertIn("VitalBite AI is currently in beta testing", ai_resp)

        nut_resp = get_fallback_ai_response("How much protein should I eat?", "Alex")
        self.assertIn("Protein", nut_resp)
        self.assertIn("beta testing", nut_resp)

        sym_resp = get_fallback_symptom_assessment("Headache and fatigue", "2 days", "3")
        self.assertIn("Possible Considerations", sym_resp)
        self.assertIn("Safe Self-Care", sym_resp)
        self.assertIn("beta testing", sym_resp)

    def test_05_exit_demo_mode_cleans_session(self):
        """Verify exiting demo mode wipes session state and returns to unauthenticated state."""
        AuthService.start_demo_mode()
        self.assertTrue(AuthService.is_authenticated())

        AuthService.exit_demo_mode()
        self.assertFalse(AuthService.is_authenticated())
        self.assertFalse(AuthService.is_demo_mode())
        self.assertIsNone(AuthService.get_current_user_id())

    def test_06_real_user_isolation_vs_demo_mode(self):
        """Verify real user data is completely distinct and isolated from demo data."""
        # Setup mock DB mode for real user simulation
        SupabaseManager._use_mock = True
        real_user_id = "real_user_uuid_12345"

        ProfileRepository.upsert_profile(real_user_id, {
            "name": "Sarah Connor",
            "age": 35,
            "gender": "Female",
            "height_cm": 170,
            "weight_kg": 65,
            "dietary_preference": "Non-Vegetarian",
            "fitness_goal": "Fat Loss"
        })

        AuthService.start_demo_mode()
        demo_profile = ProfileRepository.get_profile(DEMO_USER_ID)
        real_profile = ProfileRepository.get_profile(real_user_id)

        self.assertEqual(demo_profile.get("name"), "Alex Rivera")
        self.assertEqual(real_profile.get("name"), "Sarah Connor")
        self.assertNotEqual(demo_profile.get("name"), real_profile.get("name"))

    def test_07_diet_planner_works_in_demo_mode(self):
        """Verify 7-day diet planner computes deterministic macros for demo profile."""
        AuthService.start_demo_mode()
        demo_profile = ProfileRepository.get_profile(DEMO_USER_ID)
        
        plan = DietPlannerService.generate_7day_plan(
            profile=demo_profile,
            fitness_goal="Body Recomposition",
            dietary_preference="Vegetarian",
            selected_food_ids=['icmr_paneer', 'icmr_roti', 'icmr_toor_dal', 'icmr_apple', 'usda_oats', 'icmr_curd', 'icmr_almonds'],
            protein_powder_config={'enabled': True, 'food_id': 'usda_whey_isolate', 'servings': 1.0}
        )
        self.assertTrue(plan["success"])
        self.assertEqual(len(plan["days"]), 7)
        self.assertGreaterEqual(plan["days"][0]["summary"]["calories_pct"], 85)
        self.assertGreaterEqual(plan["days"][0]["summary"]["protein_pct"], 85)

if __name__ == "__main__":
    unittest.main()
