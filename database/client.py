"""
VitalBite AI — Database Client & Session Manager
Handles Supabase client initialization, configuration checks, and optional mock database wrapper.
Guarantees resilience on Streamlit Cloud when credentials are not yet configured.
"""
import os
import streamlit as st
from typing import Optional, Dict, Any, List

# Try importing supabase-py
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
    """Retrieves SUPABASE_URL and SUPABASE_ANON_KEY safely. NEVER uses service role key."""
    url = get_config_val("SUPABASE_URL", "")
    key = get_config_val("SUPABASE_ANON_KEY", "")
    return url, key

class SupabaseManager:
    """Singleton wrapper for Supabase Client."""
    _instance: Optional[Client] = None
    _use_mock: bool = False

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
        Initializes and returns the Supabase client.
        Never throws unhandled exceptions when credentials are missing; returns None gracefully.
        """
        if cls._use_mock:
            return None

        if cls._instance is not None:
            return cls._instance

        # Handle explicit mock DB mode
        if is_mock_db_allowed():
            cls._use_mock = True
            return None

        url, key = get_supabase_credentials()

        # Handle missing or placeholder credentials in production mode gracefully
        if not url or not key or is_placeholder_credential(url, key) or not SUPABASE_AVAILABLE:
            return None

        try:
            cls._instance = create_client(url, key)
            cls._use_mock = False
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
