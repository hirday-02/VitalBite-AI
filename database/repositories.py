"""
VitalBite AI — Database Repositories
Data Access Objects enforcing multi-user data isolation and zero-database Demo Mode containment.
"""
import uuid
import streamlit as st
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from database.client import SupabaseManager, MOCK_STORE
from services.demo_service import (
    DEMO_USER_ID,
    get_default_demo_profile,
    get_default_demo_chat_sessions,
    get_default_demo_chat_messages,
    get_default_demo_symptom_assessments,
    get_default_demo_diet_plans
)

SESSION_DEMO_DATA_KEY = "vitalbite_demo_store"

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _get_demo_store() -> Dict[str, Any]:
    """Retrieves or initializes the session-scoped in-memory demo store."""
    if SESSION_DEMO_DATA_KEY not in st.session_state:
        st.session_state[SESSION_DEMO_DATA_KEY] = {
            "profile": get_default_demo_profile(),
            "chat_sessions": get_default_demo_chat_sessions(),
            "chat_messages": get_default_demo_chat_messages(),
            "symptom_assessments": get_default_demo_symptom_assessments(),
            "diet_plans": get_default_demo_diet_plans(),
            "documents": []
        }
    return st.session_state[SESSION_DEMO_DATA_KEY]

class ProfileRepository:
    @staticmethod
    def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
        if user_id == DEMO_USER_ID:
            return _get_demo_store().get("profile")

        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["profiles"].get(user_id)
        
        client = SupabaseManager.get_client()
        if not client:
            return None
        
        try:
            res = client.table("profiles").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            print(f"[ProfileRepository] get_profile error: {e}")
        return None

    @staticmethod
    def upsert_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        profile_data["id"] = user_id
        profile_data["updated_at"] = _now_iso()
        
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            existing = store.get("profile", {})
            existing.update(profile_data)
            store["profile"] = existing
            return existing

        if SupabaseManager.is_mock_mode():
            existing = MOCK_STORE["profiles"].get(user_id, {})
            existing.update(profile_data)
            MOCK_STORE["profiles"][user_id] = existing
            return existing

        client = SupabaseManager.get_client()
        if not client:
            return profile_data

        try:
            res = client.table("profiles").upsert(profile_data).execute()
            return res.data[0] if res.data else profile_data
        except Exception as e:
            print(f"[ProfileRepository] upsert_profile error: {e}")
            return profile_data

class ChatRepository:
    @staticmethod
    def get_or_create_session(user_id: str, session_id: Optional[str] = None, title: str = "New Conversation") -> Dict[str, Any]:
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            sessions = store.get("chat_sessions", [])
            if session_id:
                for s in sessions:
                    if s.get("id") == session_id:
                        return s
            new_id = session_id or f"demo_sess_{len(sessions) + 1}"
            sess = {
                "id": new_id,
                "user_id": DEMO_USER_ID,
                "title": title,
                "created_at": _now_iso(),
                "updated_at": _now_iso()
            }
            sessions.insert(0, sess)
            store["chat_sessions"] = sessions
            return sess

        if SupabaseManager.is_mock_mode():
            if session_id and session_id in MOCK_STORE["chat_sessions"]:
                return MOCK_STORE["chat_sessions"][session_id]
            
            new_id = session_id or str(uuid.uuid4())
            sess = {
                "id": new_id,
                "user_id": user_id,
                "title": title,
                "created_at": _now_iso(),
                "updated_at": _now_iso()
            }
            MOCK_STORE["chat_sessions"][new_id] = sess
            return sess

        client = SupabaseManager.get_client()
        if not client:
            return {"id": str(uuid.uuid4()), "user_id": user_id, "title": title}

        try:
            if session_id:
                res = client.table("chat_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
                if res.data:
                    return res.data[0]

            new_sess = {
                "user_id": user_id,
                "title": title
            }
            res = client.table("chat_sessions").insert(new_sess).execute()
            return res.data[0]
        except Exception as e:
            print(f"[ChatRepository] get_or_create_session error: {e}")
            return {"id": str(uuid.uuid4()), "user_id": user_id, "title": title}

    @staticmethod
    def list_sessions(user_id: str) -> List[Dict[str, Any]]:
        if user_id == DEMO_USER_ID:
            return _get_demo_store().get("chat_sessions", [])

        if SupabaseManager.is_mock_mode():
            return [s for s in MOCK_STORE["chat_sessions"].values() if s.get("user_id") == user_id]

        client = SupabaseManager.get_client()
        if not client:
            return []

        try:
            res = client.table("chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[ChatRepository] list_sessions error: {e}")
            return []

    @staticmethod
    def add_message(user_id: str, session_id: str, sender: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_obj = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": user_id,
            "sender": sender,
            "message": message,
            "metadata": metadata or {},
            "created_at": _now_iso()
        }
        
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            msg_map = store.get("chat_messages", {})
            if session_id not in msg_map:
                msg_map[session_id] = []
            msg_map[session_id].append(msg_obj)
            store["chat_messages"] = msg_map
            return msg_obj

        if SupabaseManager.is_mock_mode():
            if session_id not in MOCK_STORE["chat_messages"]:
                MOCK_STORE["chat_messages"][session_id] = []
            MOCK_STORE["chat_messages"][session_id].append(msg_obj)
            return msg_obj

        client = SupabaseManager.get_client()
        if not client:
            return msg_obj

        try:
            res = client.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user_id,
                "sender": sender,
                "message": message,
                "metadata": metadata or {}
            }).execute()
            
            client.table("chat_sessions").update({"updated_at": _now_iso()}).eq("id", session_id).execute()
            return res.data[0] if res.data else msg_obj
        except Exception as e:
            print(f"[ChatRepository] add_message error: {e}")
            return msg_obj

    @staticmethod
    def get_messages(user_id: str, session_id: str) -> List[Dict[str, Any]]:
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            return store.get("chat_messages", {}).get(session_id, [])

        if SupabaseManager.is_mock_mode():
            msgs = MOCK_STORE["chat_messages"].get(session_id, [])
            return [m for m in msgs if m.get("user_id") == user_id]

        client = SupabaseManager.get_client()
        if not client:
            return []

        try:
            res = client.table("chat_messages").select("*").eq("session_id", session_id).eq("user_id", user_id).order("created_at", desc=False).execute()
            return res.data or []
        except Exception as e:
            print(f"[ChatRepository] get_messages error: {e}")
            return []

    @staticmethod
    def delete_session(user_id: str, session_id: str) -> bool:
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            store["chat_sessions"] = [s for s in store.get("chat_sessions", []) if s.get("id") != session_id]
            if session_id in store.get("chat_messages", {}):
                del store["chat_messages"][session_id]
            return True

        if SupabaseManager.is_mock_mode():
            if session_id in MOCK_STORE["chat_sessions"] and MOCK_STORE["chat_sessions"][session_id].get("user_id") == user_id:
                del MOCK_STORE["chat_sessions"][session_id]
                if session_id in MOCK_STORE["chat_messages"]:
                    del MOCK_STORE["chat_messages"][session_id]
                return True
            return False

        client = SupabaseManager.get_client()
        if not client:
            return False

        try:
            client.table("chat_sessions").delete().eq("id", session_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[ChatRepository] delete_session error: {e}")
            return False

class SymptomRepository:
    @staticmethod
    def save_assessment(user_id: str, symptoms: str, duration: str, severity: str, analysis: str, is_emergency: bool = False) -> Dict[str, Any]:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "symptoms": symptoms,
            "duration": duration,
            "severity": severity,
            "analysis": analysis,
            "is_emergency": is_emergency,
            "created_at": _now_iso()
        }
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            assessments = store.get("symptom_assessments", [])
            assessments.insert(0, data)
            store["symptom_assessments"] = assessments
            return data

        if SupabaseManager.is_mock_mode():
            if user_id not in MOCK_STORE["symptom_assessments"]:
                MOCK_STORE["symptom_assessments"][user_id] = []
            MOCK_STORE["symptom_assessments"][user_id].append(data)
            return data

        client = SupabaseManager.get_client()
        if not client:
            return data

        try:
            res = client.table("symptom_assessments").insert({
                "user_id": user_id,
                "symptoms": symptoms,
                "duration": duration,
                "severity": severity,
                "analysis": analysis,
                "is_emergency": is_emergency
            }).execute()
            return res.data[0] if res.data else data
        except Exception as e:
            print(f"[SymptomRepository] save_assessment error: {e}")
            return data

    @staticmethod
    def list_assessments(user_id: str) -> List[Dict[str, Any]]:
        if user_id == DEMO_USER_ID:
            return _get_demo_store().get("symptom_assessments", [])

        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["symptom_assessments"].get(user_id, [])

        client = SupabaseManager.get_client()
        if not client:
            return []

        try:
            res = client.table("symptom_assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[SymptomRepository] list_assessments error: {e}")
            return []

    @staticmethod
    def delete_assessment(user_id: str, assessment_id: str) -> bool:
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            store["symptom_assessments"] = [x for x in store.get("symptom_assessments", []) if x.get("id") != assessment_id]
            return True

        if SupabaseManager.is_mock_mode():
            items = MOCK_STORE["symptom_assessments"].get(user_id, [])
            MOCK_STORE["symptom_assessments"][user_id] = [x for x in items if x.get("id") != assessment_id]
            return True

        client = SupabaseManager.get_client()
        if not client:
            return False

        try:
            client.table("symptom_assessments").delete().eq("id", assessment_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[SymptomRepository] delete_assessment error: {e}")
            return False

class DietRepository:
    @staticmethod
    def save_plan(user_id: str, goal: str, diet_type: str, plan_text: str, structured_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "goal": goal,
            "diet_type": diet_type,
            "plan_text": plan_text,
            "structured_data": structured_data or {},
            "created_at": _now_iso()
        }
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            plans = store.get("diet_plans", [])
            plans.insert(0, data)
            store["diet_plans"] = plans
            return data

        if SupabaseManager.is_mock_mode():
            if user_id not in MOCK_STORE["diet_plans"]:
                MOCK_STORE["diet_plans"][user_id] = []
            MOCK_STORE["diet_plans"][user_id].append(data)
            return data

        client = SupabaseManager.get_client()
        if not client:
            return data

        try:
            res = client.table("diet_plans").insert({
                "user_id": user_id,
                "goal": goal,
                "diet_type": diet_type,
                "plan_text": plan_text,
                "structured_data": structured_data or {}
            }).execute()
            return res.data[0] if res.data else data
        except Exception as e:
            print(f"[DietRepository] save_plan error: {e}")
            return data

    @staticmethod
    def list_plans(user_id: str) -> List[Dict[str, Any]]:
        if user_id == DEMO_USER_ID:
            return _get_demo_store().get("diet_plans", [])

        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["diet_plans"].get(user_id, [])

        client = SupabaseManager.get_client()
        if not client:
            return []

        try:
            res = client.table("diet_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[DietRepository] list_plans error: {e}")
            return []

    @staticmethod
    def delete_plan(user_id: str, plan_id: str) -> bool:
        if user_id == DEMO_USER_ID:
            store = _get_demo_store()
            store["diet_plans"] = [x for x in store.get("diet_plans", []) if x.get("id") != plan_id]
            return True

        if SupabaseManager.is_mock_mode():
            items = MOCK_STORE["diet_plans"].get(user_id, [])
            MOCK_STORE["diet_plans"][user_id] = [x for x in items if x.get("id") != plan_id]
            return True

        client = SupabaseManager.get_client()
        if not client:
            return False

        try:
            client.table("diet_plans").delete().eq("id", plan_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[DietRepository] delete_plan error: {e}")
            return False

class AccountRepository:
    @staticmethod
    def delete_all_user_data(user_id: str) -> bool:
        """Permanently deletes or purges all data belonging to the specified user."""
        if user_id == DEMO_USER_ID:
            st.session_state.pop(SESSION_DEMO_DATA_KEY, None)
            return True

        if SupabaseManager.is_mock_mode():
            MOCK_STORE["profiles"].pop(user_id, None)
            MOCK_STORE["symptom_assessments"].pop(user_id, None)
            MOCK_STORE["diet_plans"].pop(user_id, None)
            MOCK_STORE["documents"].pop(user_id, None)
            MOCK_STORE["health_metrics"].pop(user_id, None)
            MOCK_STORE["reports"].pop(user_id, None)
            sess_to_del = [sid for sid, s in MOCK_STORE["chat_sessions"].items() if s.get("user_id") == user_id]
            for sid in sess_to_del:
                MOCK_STORE["chat_sessions"].pop(sid, None)
                MOCK_STORE["chat_messages"].pop(sid, None)
            return True

        client = SupabaseManager.get_client()
        if not client:
            return False

        try:
            client.table("profiles").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"[AccountRepository] delete_all_user_data error: {e}")
            return False
