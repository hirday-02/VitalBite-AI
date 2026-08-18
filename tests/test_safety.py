"""
VitalBite AI — Emergency Safety Unit Tests
Verifies multi-layer red-flag detection and 112 emergency contact escalation.
"""
from services.safety_service import SafetyService

def test_chest_pain_emergency_trigger():
    res = SafetyService.evaluate_emergency("I have severe crushing chest pain radiating down my left arm")
    assert res["is_emergency"] is True
    assert res["primary_number"] == "112"
    assert "chest pain" in res["triggers"]

def test_stroke_symptoms_trigger():
    res = SafetyService.evaluate_emergency("My face is drooping on one side and I have slurred speech")
    assert res["is_emergency"] is True
    assert res["primary_number"] == "112"

def test_mild_symptom_no_emergency():
    res = SafetyService.evaluate_emergency("I have a slight headache and a mild runny nose")
    assert res["is_emergency"] is False
