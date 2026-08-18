"""
VitalBite AI — Profile Completeness Data Contract Unit Tests
Verifies that HealthService.get_profile_completeness consistently returns
completed_count, total_count, percentage, and missing_fields across all inputs.
"""
from services.health_service import HealthService

def test_profile_completeness_none():
    res = HealthService.get_profile_completeness(None)
    assert res["completed_count"] == 0
    assert res["total_count"] == 9
    assert res["percentage"] == 0
    assert len(res["missing_fields"]) == 9

def test_profile_completeness_empty():
    res = HealthService.get_profile_completeness({})
    assert res["completed_count"] == 0
    assert res["total_count"] == 9
    assert res["percentage"] == 0
    assert len(res["missing_fields"]) == 9

def test_profile_completeness_partial():
    profile = {
        "name": "Jane Doe",
        "age": 30,
        "gender": "Female",
        "height_cm": 165.0,
        "weight_kg": 60.0
    }
    res = HealthService.get_profile_completeness(profile)
    assert res["completed_count"] == 5
    assert res["total_count"] == 9
    assert res["percentage"] == 56
    assert "Blood Type" in res["missing_fields"]

def test_profile_completeness_full():
    profile = {
        "name": "Jane Doe",
        "age": 30,
        "gender": "Female",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "blood_type": "O+",
        "allergies": "Peanuts",
        "conditions": "Asthma",
        "medications": "Albuterol"
    }
    res = HealthService.get_profile_completeness(profile)
    assert res["completed_count"] == 9
    assert res["total_count"] == 9
    assert res["percentage"] == 100
    assert len(res["missing_fields"]) == 0

def test_profile_completeness_explicit_none_strings():
    profile = {
        "name": "Jane Doe",
        "age": 30,
        "gender": "Female",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "blood_type": "O+",
        "allergies": "None",
        "conditions": "None",
        "medications": "None"
    }
    res = HealthService.get_profile_completeness(profile)
    assert res["completed_count"] == 9
    assert res["total_count"] == 9
    assert res["percentage"] == 100
    assert len(res["missing_fields"]) == 0
