"""
VitalBite AI — Database Client & Session Manager
Handles Supabase client initialization, configuration checks, safe diagnostics,
and optional mock database wrapper using official Python Supabase SDK.
"""
import os
import time
import streamlit as st
from typing import Optional, Dict, Any, List

# Try importing official supabase-py SDK
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = Any

def get_config_val(key: str, default: str = "") -> str:
    """Safely retrieves a configuration setting from environment variables or Streamlit secrets."""
    env_val = os.getenv(key)
    if env_val is not None and env_val.strip() != "":
        return env_val.strip()
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val != "":
                return val
    except Exception:
        pass
    return default

def is_placeholder_credential(url: str, key: str) -> bool:
    """Checks if Supabase credentials are template placeholders."""
    if not url or not key:
        return True
    placeholders = ["your-project", "your_supabase", "your_gemini", "your_usda", "example.com", "YOUR_"]
    return any(p in url.lower() for p in placeholders) or any(p in key.lower() for p in placeholders)

def is_mock_db_allowed() -> bool:
    """Checks if mock DB mode is explicitly enabled via VITALBITE_ALLOW_MOCK_DB env or secrets."""
    val = get_config_val("VITALBITE_ALLOW_MOCK_DB", "false").lower()
    return val in ("true", "1", "yes")

def get_supabase_credentials() -> tuple[str, str]:
    """
    Retrieves SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_PUBLISHABLE_KEY) safely.
    NEVER uses or exposes service role keys in ordinary application configuration.
    """
    url = get_config_val("SUPABASE_URL", "")
    key = get_config_val("SUPABASE_ANON_KEY", "") or get_config_val("SUPABASE_PUBLISHABLE_KEY", "")
    return url, key

class SupabaseManager:
    """Singleton wrapper for official Python Supabase Client with connection diagnostics."""
    _instance: Optional[Client] = None
    _use_mock: bool = False
    _last_diagnostic: Dict[str, Any] = {}
    _diagnostic_timestamp: float = 0.0
    _DIAGNOSTIC_CACHE_TTL: float = 300.0  # 5 minute cache to protect API limits

    @classmethod
    def get_detailed_diagnostics(cls, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Evaluates Supabase configuration, SDK presence, and connectivity safely.
        Never prints or exposes raw key values or database secrets.
        """
        now = time.time()
        if not force_refresh and cls._last_diagnostic and (now - cls._diagnostic_timestamp < cls._DIAGNOSTIC_CACHE_TTL):
            return cls._last_diagnostic

        diag = {
            "sdk_available": SUPABASE_AVAILABLE,
            "url_configured": False,
            "key_configured": False,
            "status": "CONFIG_MISSING",
            "safe_message": "Supabase credentials are not configured in secrets.toml or .env."
        }

        if not SUPABASE_AVAILABLE:
            diag["status"] = "SDK_UNAVAILABLE"
            diag["safe_message"] = "Official Python Supabase SDK ('supabase' package) is not installed."
            cls._last_diagnostic = diag
            cls._diagnostic_timestamp = now
            return diag

        url, key = get_supabase_credentials()

        if not url and not key:
            diag["status"] = "CONFIG_MISSING"
            diag["safe_message"] = "SUPABASE_URL and SUPABASE_ANON_KEY are missing from environment/secrets."
            cls._last_diagnostic = diag
            cls._diagnostic_timestamp = now
            return diag

        if is_placeholder_credential(url, key):
            diag["status"] = "CONFIG_PLACEHOLDER"
            diag["safe_message"] = "Supabase configuration contains placeholder values (e.g. 'your-project-id')."
            cls._last_diagnostic = diag
            cls._diagnostic_timestamp = now
            return diag

        diag["url_configured"] = bool(url)
        diag["key_configured"] = bool(key)

        # Test basic endpoint connectivity
        try:
            temp_client = create_client(url, key)
            # Perform a lightweight metadata query to test table existence & RLS
            res = temp_client.table("profiles").select("id").limit(1).execute()
            diag["status"] = "READY"
            diag["safe_message"] = "Supabase database connection established and profiles table verified."
        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["401", "403", "jwt", "unauthorized", "invalid api key", "invalid_claim"]):
                diag["status"] = "AUTH_FAILED"
                diag["safe_message"] = "Supabase authentication failed. Please verify your SUPABASE_ANON_KEY or SUPABASE_PUBLISHABLE_KEY."
            elif any(term in err_str for term in ["relation", "does not exist", "pgrst204", "pgrst301", "404", "table"]):
                diag["status"] = "TABLE_MISSING"
                diag["safe_message"] = "Supabase connected successfully, but database tables (schema.sql) have not been created yet."
            elif "42501" in err_str or "permission denied" in err_str:
                diag["status"] = "READY"  # Connection & RLS are working as expected for unauthenticated queries
                diag["safe_message"] = "Supabase connected successfully (Row Level Security active)."
            else:
                diag["status"] = "NETWORK_ERROR"
                diag["safe_message"] = "Unable to connect to Supabase endpoint. Please check your network connection and SUPABASE_URL."

        cls._last_diagnostic = diag
        cls._diagnostic_timestamp = now
        return diag

    @classmethod
    def has_valid_credentials(cls) -> bool:
        """Returns True if valid non-placeholder Supabase credentials exist."""
        if cls.is_mock_mode():
            return True
        url, key = get_supabase_credentials()
        return bool(url and key and not is_placeholder_credential(url, key) and SUPABASE_AVAILABLE)

    @classmethod
    def get_client(cls) -> Optional[Client]:
        """
        Initializes and returns the official Python Supabase client.
        Applies user session access token if available to respect RLS policies.
        Never throws unhandled exceptions when credentials are missing; returns None gracefully.
        """
        if cls._use_mock:
            return None

        if is_mock_db_allowed():
            cls._use_mock = True
            return None

        url, key = get_supabase_credentials()

        if not url or not key or is_placeholder_credential(url, key) or not SUPABASE_AVAILABLE:
            return None

        try:
            if cls._instance is None:
                cls._instance = create_client(url, key)
                cls._use_mock = False

            # Attach session access token if available in Streamlit session state for RLS
            token = st.session_state.get("vitalbite_auth_access_token")
            if token and cls._instance and hasattr(cls._instance, "postgrest"):
                try:
                    cls._instance.postgrest.auth(token)
                except Exception:
                    pass

            return cls._instance
        except Exception as e:
            print(f"[SupabaseManager] Failed to connect to Supabase: {e}")
            return None

    @classmethod
    def is_mock_mode(cls) -> bool:
        """Returns True if the application is running in explicit mock DB mode."""
        if cls._use_mock:
            return True
        if cls._instance is None and is_mock_db_allowed():
            cls._use_mock = True
            return True
        return cls._use_mock

# Global in-memory mock store for local dev when VITALBITE_ALLOW_MOCK_DB=true
MOCK_STORE: Dict[str, Any] = {
    "profiles": {},
    "chat_sessions": {},
    "chat_messages": {},
    "symptom_assessments": {},
    "diet_plans": {},
    "documents": {},
    "health_metrics": {},
    "reports": {}
}
