"""
VitalBite AI — Database Repositories
Data Access Objects enforcing multi-user data isolation.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from database.client import SupabaseManager, MOCK_STORE

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class ProfileRepository:
    @staticmethod
    def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["profiles"].get(user_id)
        
        client = SupabaseManager.get_client()
        if not client:
            return None
        
        res = client.table("profiles").select("*").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    @staticmethod
    def upsert_profile(user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        profile_data["id"] = user_id
        profile_data["updated_at"] = _now_iso()
        
        if SupabaseManager.is_mock_mode():
            existing = MOCK_STORE["profiles"].get(user_id, {})
            existing.update(profile_data)
            MOCK_STORE["profiles"][user_id] = existing
            return existing

        client = SupabaseManager.get_client()
        if not client:
            raise RuntimeError("Database client unavailable.")

        res = client.table("profiles").upsert(profile_data).execute()
        return res.data[0] if res.data else profile_data

class ChatRepository:
    @staticmethod
    def get_or_create_session(user_id: str, session_id: Optional[str] = None, title: str = "New Conversation") -> Dict[str, Any]:
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
        if session_id:
            res = client.table("chat_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
            if res.data:
                return res.data[0]

        # Create new session
        new_sess = {
            "user_id": user_id,
            "title": title
        }
        res = client.table("chat_sessions").insert(new_sess).execute()
        return res.data[0]

    @staticmethod
    def list_sessions(user_id: str) -> List[Dict[str, Any]]:
        if SupabaseManager.is_mock_mode():
            return [s for s in MOCK_STORE["chat_sessions"].values() if s.get("user_id") == user_id]

        client = SupabaseManager.get_client()
        res = client.table("chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
        return res.data or []

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
        
        if SupabaseManager.is_mock_mode():
            if session_id not in MOCK_STORE["chat_messages"]:
                MOCK_STORE["chat_messages"][session_id] = []
            MOCK_STORE["chat_messages"][session_id].append(msg_obj)
            return msg_obj

        client = SupabaseManager.get_client()
        res = client.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "sender": sender,
            "message": message,
            "metadata": metadata or {}
        }).execute()
        
        # Touch session updated_at
        client.table("chat_sessions").update({"updated_at": _now_iso()}).eq("id", session_id).execute()
        return res.data[0] if res.data else msg_obj

    @staticmethod
    def get_messages(user_id: str, session_id: str) -> List[Dict[str, Any]]:
        if SupabaseManager.is_mock_mode():
            msgs = MOCK_STORE["chat_messages"].get(session_id, [])
            return [m for m in msgs if m.get("user_id") == user_id]

        client = SupabaseManager.get_client()
        res = client.table("chat_messages").select("*").eq("session_id", session_id).eq("user_id", user_id).order("created_at", desc=False).execute()
        return res.data or []

    @staticmethod
    def delete_session(user_id: str, session_id: str) -> bool:
        if SupabaseManager.is_mock_mode():
            if session_id in MOCK_STORE["chat_sessions"] and MOCK_STORE["chat_sessions"][session_id].get("user_id") == user_id:
                del MOCK_STORE["chat_sessions"][session_id]
                if session_id in MOCK_STORE["chat_messages"]:
                    del MOCK_STORE["chat_messages"][session_id]
                return True
            return False

        client = SupabaseManager.get_client()
        client.table("chat_sessions").delete().eq("id", session_id).eq("user_id", user_id).execute()
        return True

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
        if SupabaseManager.is_mock_mode():
            if user_id not in MOCK_STORE["symptom_assessments"]:
                MOCK_STORE["symptom_assessments"][user_id] = []
            MOCK_STORE["symptom_assessments"][user_id].append(data)
            return data

        client = SupabaseManager.get_client()
        res = client.table("symptom_assessments").insert({
            "user_id": user_id,
            "symptoms": symptoms,
            "duration": duration,
            "severity": severity,
            "analysis": analysis,
            "is_emergency": is_emergency
        }).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def list_assessments(user_id: str) -> List[Dict[str, Any]]:
        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["symptom_assessments"].get(user_id, [])

        client = SupabaseManager.get_client()
        res = client.table("symptom_assessments").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data or []

    @staticmethod
    def delete_assessment(user_id: str, assessment_id: str) -> bool:
        if SupabaseManager.is_mock_mode():
            items = MOCK_STORE["symptom_assessments"].get(user_id, [])
            MOCK_STORE["symptom_assessments"][user_id] = [x for x in items if x.get("id") != assessment_id]
            return True

        client = SupabaseManager.get_client()
        client.table("symptom_assessments").delete().eq("id", assessment_id).eq("user_id", user_id).execute()
        return True

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
        if SupabaseManager.is_mock_mode():
            if user_id not in MOCK_STORE["diet_plans"]:
                MOCK_STORE["diet_plans"][user_id] = []
            MOCK_STORE["diet_plans"][user_id].append(data)
            return data

        client = SupabaseManager.get_client()
        res = client.table("diet_plans").insert({
            "user_id": user_id,
            "goal": goal,
            "diet_type": diet_type,
            "plan_text": plan_text,
            "structured_data": structured_data or {}
        }).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def list_plans(user_id: str) -> List[Dict[str, Any]]:
        if SupabaseManager.is_mock_mode():
            return MOCK_STORE["diet_plans"].get(user_id, [])

        client = SupabaseManager.get_client()
        res = client.table("diet_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return res.data or []

    @staticmethod
    def delete_plan(user_id: str, plan_id: str) -> bool:
        if SupabaseManager.is_mock_mode():
            items = MOCK_STORE["diet_plans"].get(user_id, [])
            MOCK_STORE["diet_plans"][user_id] = [x for x in items if x.get("id") != plan_id]
            return True

        client = SupabaseManager.get_client()
        client.table("diet_plans").delete().eq("id", plan_id).eq("user_id", user_id).execute()
        return True

class AccountRepository:
    @staticmethod
    def delete_all_user_data(user_id: str) -> bool:
        """Permanently deletes or purges all data belonging to the specified user."""
        if SupabaseManager.is_mock_mode():
            MOCK_STORE["profiles"].pop(user_id, None)
            MOCK_STORE["symptom_assessments"].pop(user_id, None)
            MOCK_STORE["diet_plans"].pop(user_id, None)
            MOCK_STORE["documents"].pop(user_id, None)
            MOCK_STORE["health_metrics"].pop(user_id, None)
            MOCK_STORE["reports"].pop(user_id, None)
            # Remove chat sessions and messages
            sess_to_del = [sid for sid, s in MOCK_STORE["chat_sessions"].items() if s.get("user_id") == user_id]
            for sid in sess_to_del:
                MOCK_STORE["chat_sessions"].pop(sid, None)
                MOCK_STORE["chat_messages"].pop(sid, None)
            return True

        client = SupabaseManager.get_client()
        if not client:
            return False

        # Deleting profile will cascade to all user-owned tables via foreign keys
        client.table("profiles").delete().eq("id", user_id).execute()
        return True
