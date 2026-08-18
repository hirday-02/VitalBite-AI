"""
VitalBite AI — Source-Grounded Nutrition Unit Tests
Verifies that food lookups return database-sourced match results or explicit non-match disclosures.
"""
from services.nutrition_service import NutritionService

def test_icmr_paneer_lookup():
    res = NutritionService.search_food("paneer")
    assert res["matched"] is True
    assert "Paneer" in res["food_item"]
    assert res["calories_kcal"] > 0
    assert res["protein_g"] > 0
    assert "ICMR-NIN" in res["source"]

def test_icmr_roti_lookup():
    res = NutritionService.search_food("roti")
    assert res["matched"] is True
    assert res["calories_kcal"] > 0
    assert "ICMR-NIN" in res["source"]

def test_unknown_food_lookup():
    res = NutritionService.search_food("xyz_non_existent_dish_99")
    assert res["matched"] is False
    assert "couldn't confidently match" in res["message"]
