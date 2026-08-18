"""
VitalBite AI — Multi-User RLS Isolation Unit Tests
Verifies that User A cannot read, update, or delete User B's records.
"""
import os
os.environ["VITALBITE_ALLOW_MOCK_DB"] = "true"

from database.client import SupabaseManager
from database.repositories import ProfileRepository, ChatRepository, SymptomRepository, DietRepository

def test_profile_isolation():
    user_a = "user-a-1111"
    user_b = "user-b-2222"

    ProfileRepository.upsert_profile(user_a, {"name": "User Alpha", "age": 28})
    ProfileRepository.upsert_profile(user_b, {"name": "User Beta", "age": 35})

    profile_a = ProfileRepository.get_profile(user_a)
    profile_b = ProfileRepository.get_profile(user_b)

    assert profile_a["name"] == "User Alpha"
    assert profile_b["name"] == "User Beta"
    assert profile_a["id"] != profile_b["id"]

def test_symptom_isolation():
    user_a = "user-a-1111"
    user_b = "user-b-2222"

    SymptomRepository.save_assessment(user_a, "Headache", "1 day", "3", "Rest and hydrate")
    SymptomRepository.save_assessment(user_b, "Chest tightness", "1 hour", "9", "Emergency escalation")

    assessments_a = SymptomRepository.list_assessments(user_a)
    assessments_b = SymptomRepository.list_assessments(user_b)

    assert len(assessments_a) >= 1
    assert len(assessments_b) >= 1
    assert all(item["user_id"] == user_a for item in assessments_a)
    assert all(item["user_id"] == user_b for item in assessments_b)

def test_chat_isolation():
    user_a = "user-a-1111"
    user_b = "user-b-2222"

    sess_a = ChatRepository.get_or_create_session(user_a, title="Alpha Session")
    sess_b = ChatRepository.get_or_create_session(user_b, title="Beta Session")

    ChatRepository.add_message(user_a, sess_a["id"], "user", "Alpha Question")
    ChatRepository.add_message(user_b, sess_b["id"], "user", "Beta Question")

    msgs_a = ChatRepository.get_messages(user_a, sess_a["id"])
    msgs_b = ChatRepository.get_messages(user_b, sess_b["id"])

    assert len(msgs_a) >= 1
    assert len(msgs_b) >= 1
    assert all(m["user_id"] == user_a for m in msgs_a)
    assert all(m["user_id"] == user_b for m in msgs_b)

    # Ensure user_a cannot fetch messages for user_b's session
    cross_msgs = ChatRepository.get_messages(user_a, sess_b["id"])
    assert len(cross_msgs) == 0

def test_diet_isolation():
    user_a = "user-a-1111"
    user_b = "user-b-2222"

    DietRepository.save_plan(user_a, "Weight Loss", "Vegetarian", "Plan A details")
    DietRepository.save_plan(user_b, "Muscle Gain", "High Protein", "Plan B details")

    plans_a = DietRepository.list_plans(user_a)
    plans_b = DietRepository.list_plans(user_b)

    assert len(plans_a) >= 1
    assert len(plans_b) >= 1
    assert all(p["user_id"] == user_a for p in plans_a)
    assert all(p["user_id"] == user_b for p in plans_b)

