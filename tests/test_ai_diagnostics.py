"""
VitalBite AI — AI Service & Diagnostics Test Suite
Verifies safe internal diagnostic states, placeholder detection, error handling, and model discovery.
"""
import os
import unittest
from unittest.mock import patch
from services.ai_service import AIService, is_valid_gemini_key, get_gemini_api_key

class TestAIDiagnostics(unittest.TestCase):
    def setUp(self):
        # Reset cached configuration state
        AIService._configured = False
        AIService._available_models = []
        AIService._client = None
        AIService._last_diagnostic = {}
        AIService._diagnostic_timestamp = 0.0

    def test_01_is_valid_gemini_key(self):
        self.assertFalse(is_valid_gemini_key(""))
        self.assertFalse(is_valid_gemini_key("   "))
        self.assertFalse(is_valid_gemini_key("your_gemini_api_key_here"))
        self.assertFalse(is_valid_gemini_key("YOUR_GEMINI_API_KEY"))
        self.assertFalse(is_valid_gemini_key("your_api_key"))
        self.assertTrue(is_valid_gemini_key("AIzaSyD-valid-mock-key-12345"))

    def test_02_diagnostic_config_missing(self):
        with patch("services.ai_service.get_gemini_api_key", return_value=""):
            with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
                with patch("services.ai_service.os.path.exists", return_value=False):
                    status = AIService.get_diagnostic_status()
                    self.assertIn(status, ["CONFIG_MISSING", "CONFIG_PLACEHOLDER"])

    def test_03_diagnostic_config_placeholder(self):
        with patch("services.ai_service.get_gemini_api_key", return_value=""):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "your_gemini_api_key_here"}, clear=False):
                status = AIService.get_diagnostic_status()
                self.assertEqual(status, "CONFIG_PLACEHOLDER")

    def test_04_offline_generate_response_contract(self):
        with patch("services.ai_service.get_gemini_api_key", return_value=""):
            with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
                with patch("services.ai_service.os.path.exists", return_value=False):
                    AIService._configured = False
                    AIService._client = None
                    resp = AIService.generate_response("Test prompt")
                    self.assertTrue(resp.startswith("SERVICE_UNAVAILABLE:"))

if __name__ == "__main__":
    unittest.main()
