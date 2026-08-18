"""
VitalBite AI — Automated Test Suite Runner (Standard Library)
Runs unit tests for multi-user isolation, profile completeness, AI diagnostics, source-grounded nutrition, and emergency safety triage.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest

# Import test cases
from tests.test_auth_isolation import test_profile_isolation, test_symptom_isolation, test_chat_isolation, test_diet_isolation
from tests.test_profile_completeness import (
    test_profile_completeness_none,
    test_profile_completeness_empty,
    test_profile_completeness_partial,
    test_profile_completeness_full,
    test_profile_completeness_explicit_none_strings
)
from tests.test_ai_diagnostics import TestAIDiagnostics
from tests.test_diet_planner import TestDietPlanner
from tests.test_nutrition import test_icmr_paneer_lookup, test_icmr_roti_lookup, test_unknown_food_lookup
from tests.test_safety import test_chest_pain_emergency_trigger, test_stroke_symptoms_trigger, test_mild_symptom_no_emergency

class VitalBiteTestSuite(unittest.TestCase):
    def test_01_profile_isolation(self):
        test_profile_isolation()

    def test_01b_profile_completeness_none(self):
        test_profile_completeness_none()

    def test_01c_profile_completeness_empty(self):
        test_profile_completeness_empty()

    def test_01d_profile_completeness_partial(self):
        test_profile_completeness_partial()

    def test_01e_profile_completeness_full(self):
        test_profile_completeness_full()

    def test_01f_profile_completeness_explicit_none(self):
        test_profile_completeness_explicit_none_strings()

    def test_02_symptom_isolation(self):
        test_symptom_isolation()

    def test_02b_chat_isolation(self):
        test_chat_isolation()

    def test_02c_diet_isolation(self):
        test_diet_isolation()

    def test_03_paneer_lookup(self):
        test_icmr_paneer_lookup()

    def test_04_roti_lookup(self):
        test_icmr_roti_lookup()

    def test_05_unknown_food_lookup(self):
        test_unknown_food_lookup()

    def test_06_chest_pain_trigger(self):
        test_chest_pain_emergency_trigger()

    def test_07_stroke_trigger(self):
        test_stroke_symptoms_trigger()

    def test_08_mild_symptom_no_emergency(self):
        test_mild_symptom_no_emergency()

def main():
    print("Running VitalBite AI Automated Verification Suite...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(VitalBiteTestSuite))
    suite.addTests(loader.loadTestsFromTestCase(TestAIDiagnostics))
    suite.addTests(loader.loadTestsFromTestCase(TestDietPlanner))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    main()
