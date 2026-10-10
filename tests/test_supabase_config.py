"""
VitalBite AI — Supabase Configuration & Diagnostics Test Suite
Verifies safe credential retrieval, diagnostic status categorization, placeholder detection,
and resilience when credentials or database tables are unavailable.
"""
import os
import unittest
from unittest.mock import patch
from database.client import SupabaseManager, get_supabase_credentials, is_placeholder_credential

class TestSupabaseConfig(unittest.TestCase):
    def setUp(self):
        # Reset diagnostic cache
        SupabaseManager._last_diagnostic = {}
        SupabaseManager._diagnostic_timestamp = 0.0
        SupabaseManager._instance = None
        SupabaseManager._use_mock = False

    def test_01_is_placeholder_credential(self):
        self.assertTrue(is_placeholder_credential("", ""))
        self.assertTrue(is_placeholder_credential("https://your-project.supabase.co", "sb_secret_123"))
        self.assertTrue(is_placeholder_credential("https://xyz.supabase.co", "your_supabase_anon_key_here"))
        self.assertFalse(is_placeholder_credential("https://abcxyz.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.validtoken"))

    def test_02_publishable_key_fallback(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "", "SUPABASE_PUBLISHABLE_KEY": "sbp_publishable_key_123"}, clear=True):
            url, key = get_supabase_credentials()
            self.assertEqual(url, "https://test.supabase.co")
            self.assertEqual(key, "sbp_publishable_key_123")

    def test_03_diagnostic_config_missing(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": ""}, clear=True):
            with patch("database.client.get_config_val", return_value=""):
                diag = SupabaseManager.get_detailed_diagnostics(force_refresh=True)
                self.assertEqual(diag["status"], "CONFIG_MISSING")
                self.assertIn("missing", diag["safe_message"].lower())

    def test_04_diagnostic_config_placeholder(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "https://your-project-id.supabase.co", "SUPABASE_ANON_KEY": "your_supabase_anon_key_here"}, clear=True):
            diag = SupabaseManager.get_detailed_diagnostics(force_refresh=True)
            self.assertEqual(diag["status"], "CONFIG_PLACEHOLDER")
            self.assertIn("placeholder", diag["safe_message"].lower())

    def test_05_client_graceful_none_on_missing_credentials(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": ""}, clear=True):
            with patch("database.client.get_config_val", return_value=""):
                client = SupabaseManager.get_client()
                self.assertIsNone(client)

if __name__ == "__main__":
    unittest.main()
