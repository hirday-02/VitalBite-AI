"""
VitalBite AI — Authentication & Session Service
Wraps Supabase Auth API to manage User Identity securely in Streamlit.
"""
import streamlit as st
from typing import Optional, Dict, Any
from database.client import SupabaseManager

SESSION_USER_KEY = "vitalbite_authenticated_user"
SESSION_TOKEN_KEY = "vitalbite_auth_access_token"

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
        """Returns True if a user session is active."""
        return AuthService.get_current_user_id() is not None

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
            return True, "Signed in successfully (Mock Mode)."

        client = SupabaseManager.get_client()
        if not client:
            return False, "Database connection unavailable."

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
            return True, "Account created successfully (Mock Mode)."

        client = SupabaseManager.get_client()
        if not client:
            return False, "Database connection unavailable."

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
            return False, "Database connection unavailable."

        try:
            client.auth.reset_password_for_email(email)
            return True, "Password reset instructions sent to your email."
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"

    @staticmethod
    def get_google_auth_url(redirect_url: str = "http://localhost:8501") -> Optional[str]:
        """Generates Google OAuth redirect URL using Supabase Auth."""
        if SupabaseManager.is_mock_mode():
            return None

        client = SupabaseManager.get_client()
        if not client:
            return None

        try:
            res = client.auth.get_oauth_sign_in_url({
                "provider": "google",
                "options": {"redirect_to": redirect_url}
            })
            return res.url if res else None
        except Exception as e:
            print(f"[AuthService] Google OAuth URL error: {e}")
            return None

    @staticmethod
    def sign_out():
        """Logs out the user and clears Streamlit session state."""
        client = SupabaseManager.get_client()
        if client and not SupabaseManager.is_mock_mode():
            try:
                client.auth.sign_out()
            except Exception as e:
                print(f"[AuthService] Sign-out warning: {e}")

        # Clear session keys
        st.session_state.pop(SESSION_USER_KEY, None)
        st.session_state.pop(SESSION_TOKEN_KEY, None)
        # Clear UI cache states
        for k in list(st.session_state.keys()):
            if k.startswith("vitalbite_"):
                st.session_state.pop(k, None)
