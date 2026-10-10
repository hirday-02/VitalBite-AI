"""
VitalBite AI — Authentication & Session Service
Wraps Supabase Auth API to manage User Identity securely in Streamlit,
with first-class support for isolated, safe, zero-credential Demo Mode.
"""
import streamlit as st
from typing import Optional, Dict, Any
from database.client import SupabaseManager
from services.demo_service import (
    DEMO_USER_ID,
    get_default_demo_profile,
    get_default_demo_chat_sessions,
    get_default_demo_chat_messages,
    get_default_demo_symptom_assessments,
    get_default_demo_diet_plans
)

SESSION_USER_KEY = "vitalbite_authenticated_user"
SESSION_TOKEN_KEY = "vitalbite_auth_access_token"
SESSION_DEMO_KEY = "vitalbite_is_demo_mode"
SESSION_DEMO_DATA_KEY = "vitalbite_demo_store"

class AuthService:
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """
        Retrieves the authenticated user dict from Streamlit session state.
        Returns None if no user is signed in.
        """
        return st.session_state.get(SESSION_USER_KEY, None)

    @staticmethod
    def get_current_user_id() -> Optional[str]:
        """
        Returns the verified user ID of the currently signed-in user.
        Crucial for data isolation: NEVER trust frontend user_id params.
        """
        user = AuthService.get_current_user()
        if user:
            return user.get("id")
        return None

    @staticmethod
    def is_authenticated() -> bool:
        """Returns True if a user session (real or demo) is active."""
        return AuthService.get_current_user_id() is not None

    @staticmethod
    def is_demo_mode() -> bool:
        """Returns True if the current active session is Demo Mode."""
        user_id = AuthService.get_current_user_id()
        return bool(st.session_state.get(SESSION_DEMO_KEY, False) or user_id == DEMO_USER_ID)

    @staticmethod
    def start_demo_mode():
        """
        Initializes an isolated, zero-credential Demo Session with realistic fictional data.
        Does NOT write to Supabase or touch real user accounts.
        """
        demo_user = {
            "id": DEMO_USER_ID,
            "email": "Harsh.Singh@example.com",
            "user_metadata": {
                "full_name": "Harsh Singh",
                "is_demo": True
            }
        }
        st.session_state[SESSION_USER_KEY] = demo_user
        st.session_state[SESSION_TOKEN_KEY] = "demo-access-token"
        st.session_state[SESSION_DEMO_KEY] = True

        # Pre-populate isolated in-memory demo store
        st.session_state[SESSION_DEMO_DATA_KEY] = {
            "profile": get_default_demo_profile(),
            "chat_sessions": get_default_demo_chat_sessions(),
            "chat_messages": get_default_demo_chat_messages(),
            "symptom_assessments": get_default_demo_symptom_assessments(),
            "diet_plans": get_default_demo_diet_plans(),
            "documents": []
        }
        st.session_state["nav_selection"] = "Dashboard"

    @staticmethod
    def exit_demo_mode():
        """Exits Demo Mode, wipes demo in-memory data, and redirects to the sign-in screen."""
        st.session_state.pop(SESSION_USER_KEY, None)
        st.session_state.pop(SESSION_TOKEN_KEY, None)
        st.session_state.pop(SESSION_DEMO_KEY, None)
        st.session_state.pop(SESSION_DEMO_DATA_KEY, None)
        st.session_state["nav_selection"] = "Dashboard"
        
        # Clear UI state keys
        for k in list(st.session_state.keys()):
            if k.startswith("vitalbite_") or k.startswith("chk_food_") or k.startswith("active_"):
                st.session_state.pop(k, None)

    @staticmethod
    def sign_in_email(email: str, password: str) -> tuple[bool, str]:
        """Signs in a user with email and password via Supabase Auth."""
        if SupabaseManager.is_mock_mode():
            # Mock authentication for local development testing
            mock_id = f"mock-user-{hash(email) % 10000}"
            user_obj = {
                "id": mock_id,
                "email": email,
                "user_metadata": {"full_name": email.split("@")[0].capitalize()}
            }
            st.session_state[SESSION_USER_KEY] = user_obj
            st.session_state[SESSION_TOKEN_KEY] = "mock-token-xyz"
            st.session_state[SESSION_DEMO_KEY] = False
            return True, "Signed in successfully (Mock Mode)."

        client = SupabaseManager.get_client()
        if not client:
            return False, "Supabase authentication is not configured on this server. Please use 'Explore Demo' or configure SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets."

        try:
            res = client.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                user_obj = {
                    "id": res.user.id,
                    "email": res.user.email,
                    "user_metadata": res.user.user_metadata or {}
                }
                st.session_state[SESSION_USER_KEY] = user_obj
                st.session_state[SESSION_TOKEN_KEY] = res.session.access_token if res.session else ""
                st.session_state[SESSION_DEMO_KEY] = False
                return True, "Successfully logged in."
            return False, "Invalid email or password."
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    @staticmethod
    def sign_up_email(email: str, password: str, full_name: str) -> tuple[bool, str]:
        """Registers a new user with email, password, and full name."""
        if SupabaseManager.is_mock_mode():
            mock_id = f"mock-user-{hash(email) % 10000}"
            user_obj = {
                "id": mock_id,
                "email": email,
                "user_metadata": {"full_name": full_name}
            }
            st.session_state[SESSION_USER_KEY] = user_obj
            st.session_state[SESSION_TOKEN_KEY] = "mock-token-xyz"
            st.session_state[SESSION_DEMO_KEY] = False
            return True, "Account created successfully (Mock Mode)."

        client = SupabaseManager.get_client()
        if not client:
            return False, "Supabase authentication is not configured on this server. Please use 'Explore Demo' or configure SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets."

        try:
            res = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": full_name}
                }
            })
            if res.user:
                user_obj = {
                    "id": res.user.id,
                    "email": res.user.email,
                    "user_metadata": res.user.user_metadata or {}
                }
                st.session_state[SESSION_USER_KEY] = user_obj
                st.session_state[SESSION_TOKEN_KEY] = res.session.access_token if res.session else ""
                st.session_state[SESSION_DEMO_KEY] = False
                return True, "Account created successfully!"
            return False, "Registration failed. Please check your details."
        except Exception as e:
            return False, f"Sign-up error: {str(e)}"

    @staticmethod
    def reset_password(email: str) -> tuple[bool, str]:
        """Triggers password reset email via Supabase Auth."""
        if SupabaseManager.is_mock_mode():
            return True, "Password reset instructions sent (Mock Mode)."

        client = SupabaseManager.get_client()
        if not client:
            return False, "Supabase authentication is not configured on this server. Please use 'Explore Demo' or configure SUPABASE_URL and SUPABASE_ANON_KEY in Streamlit secrets."

        try:
            client.auth.reset_password_for_email(email)
            return True, "Password reset instructions sent to your email."
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"

    @staticmethod
    def sign_out():
        """Logs out the user and clears Streamlit session state."""
        client = SupabaseManager.get_client()
        if client and not SupabaseManager.is_mock_mode() and not AuthService.is_demo_mode():
            try:
                client.auth.sign_out()
            except Exception as e:
                print(f"[AuthService] Sign-out warning: {e}")

        # Clear session keys
        st.session_state.pop(SESSION_USER_KEY, None)
        st.session_state.pop(SESSION_TOKEN_KEY, None)
        st.session_state.pop(SESSION_DEMO_KEY, None)
        st.session_state.pop(SESSION_DEMO_DATA_KEY, None)
        st.session_state["nav_selection"] = "Dashboard"

        # Clear UI cache states
        for k in list(st.session_state.keys()):
            if k.startswith("vitalbite_") or k.startswith("chk_food_") or k.startswith("active_"):
                st.session_state.pop(k, None)
