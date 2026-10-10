"""
VitalBite AI — AI Responses & Identity Regression Test Suite
Verifies:
1. No hardcoded 'Alex Rivera' identity assumptions in AI responses or prompts.
2. Goal identification and progressive questioning when user asks for diet advice without complete profile.
3. Deterministic target calculations when complete profile parameters are available.
4. Meal plan redirection to the 7-Day Diet Planner.
5. Strict AI system prompt directives.
"""
import unittest
from services.ai_service import AIService, build_health_chat_prompt, HEALTH_ASSISTANT_SYSTEM_PROMPT
from services.demo_service import get_fallback_ai_response

class TestAIResponses(unittest.TestCase):
    def test_01_no_alex_rivera_identity_assumption_in_fallback(self):
        """Verify fallback AI responses never output 'Alex Rivera' for arbitrary users."""
        prompt = "I want to start gym. What diet should I take?"

        # Test with generic user name
        resp = get_fallback_ai_response(prompt=prompt, user_name="John Doe", is_demo=False)
        self.assertNotIn("Alex Rivera", resp)
        self.assertNotIn("Strategy for Alex Rivera", resp)

        # Test with empty user name in demo mode
        resp_demo = get_fallback_ai_response(prompt=prompt, user_name="User", is_demo=True)
        self.assertNotIn("Strategy for Alex Rivera", resp_demo)

    def test_02_progressive_questioning_when_profile_missing(self):
        """Verify missing profile leads to progressive questions and beginner principles."""
        prompt = "I want to start gym. What diet should I take?"
        empty_profile = {}

        resp = get_fallback_ai_response(prompt=prompt, user_name="User", is_demo=False, profile=empty_profile)

        # Must mention beginner principles
        self.assertIn("Progressive Resistance Training", resp)
        self.assertIn("Protein Optimization", resp)

        # Must ask progressive follow-up questions
        self.assertIn("Primary Goal", resp)
        self.assertIn("Demographics", resp)
        self.assertIn("Dietary Preference", resp)

    def test_03_deterministic_targets_when_profile_complete(self):
        """Verify complete profile metrics generate deterministic numbers using DietPlannerService math."""
        prompt = "I want to start gym. What diet should I take?"
        complete_profile = {
            "age": 28,
            "gender": "Male",
            "height_cm": 180,
            "weight_kg": 75,
            "fitness_goal": "Body Recomposition",
            "activity_level": "moderate"
        }

        resp = get_fallback_ai_response(prompt=prompt, user_name="Sarah", is_demo=False, profile=complete_profile)

        # Must contain verified calculated numbers
        self.assertIn("Verified Target Estimates", resp)
        self.assertIn("BMR", resp)
        self.assertIn("TDEE", resp)
        self.assertIn("Target Calories", resp)
        self.assertIn("Protein Target", resp)
        self.assertNotIn("Strategy for Alex Rivera", resp)

    def test_04_meal_plan_redirection(self):
        """Verify complete meal plan inquiries direct users to the 7-Day Diet Planner tab."""
        prompt = "Can you give me a complete 7-day meal plan?"
        resp = get_fallback_ai_response(prompt=prompt, user_name="User", is_demo=True)

        self.assertIn("7-Day Diet Planner", resp)

    def test_05_system_prompt_directives(self):
        """Verify system prompt contains mandatory directives on non-diagnostic, progressive questioning, and accuracy."""
        prompt_text, sys_instruction = build_health_chat_prompt(
            user_message="I want to start gym. What diet should I take?",
            profile={"name": "Jane", "age": 30},
            is_demo=False
        )

        self.assertIn("IDENTITY & CONTEXT SAFETY", sys_instruction)
        self.assertIn("GOAL IDENTIFICATION & PROGRESSIVE QUESTIONING", sys_instruction)
        self.assertIn("NUMERICAL & NUTRITIONAL ACCURACY", sys_instruction)
        self.assertIn("MEAL PLAN INTEGRATION", sys_instruction)
        self.assertIn("VERIFIED USER HEALTH CONTEXT", prompt_text)
        self.assertIn("Jane", prompt_text)

if __name__ == "__main__":
    unittest.main()
