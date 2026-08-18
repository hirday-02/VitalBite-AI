"""
VitalBite AI — Source-Grounded Nutrition Data Service
Queries database-sourced datasets (ICMR-NIN Indian Food Tables & USDA FoodData Central).
Explicitly avoids AI hallucinations by returning structured, data-attributed nutrition objects.
"""
import os
import json
import requests
import streamlit as st
from typing import Optional, Dict, Any, List

def get_usda_api_key() -> str:
    try:
        if hasattr(st, "secrets") and "USDA_FDC_API_KEY" in st.secrets:
            return str(st.secrets["USDA_FDC_API_KEY"])
    except Exception:
        pass
    return os.getenv("USDA_FDC_API_KEY", "DEMO_KEY")

class NutritionService:
    _icmr_dataset: Optional[Dict[str, Any]] = None

    @classmethod
    def _load_icmr_dataset(cls) -> Dict[str, Any]:
        if cls._icmr_dataset is not None:
            return cls._icmr_dataset

        dataset_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "icmr_nin_foods.json")
        try:
            if os.path.exists(dataset_path):
                with open(dataset_path, "r", encoding="utf-8") as f:
                    cls._icmr_dataset = json.load(f)
                    return cls._icmr_dataset
        except Exception as e:
            print(f"[NutritionService] Error loading ICMR dataset: {e}")
        
        cls._icmr_dataset = {"foods": [], "dataset_info": {}}
        return cls._icmr_dataset

    @classmethod
    def search_food(cls, query: str) -> Dict[str, Any]:
        """
        Searches ICMR-NIN dataset first for Indian foods, then falls back to USDA API.
        Returns a source-grounded match result or an explicit non-match status.
        """
        query_clean = query.strip().lower()
        if not query_clean:
            return {
                "matched": False,
                "query": query,
                "message": "Please provide a valid food item to search."
            }

        # 1. Search ICMR-NIN Reference Dataset
        icmr_data = cls._load_icmr_dataset()
        for food in icmr_data.get("foods", []):
            name_match = query_clean in food["name"].lower()
            alias_match = any(query_clean in alias.lower() for alias in food.get("aliases", []))
            if name_match or alias_match:
                return {
                    "matched": True,
                    "query": query,
                    "food_item": food["name"],
                    "serving_size": food["serving_size"],
                    "calories_kcal": food["calories_kcal"],
                    "protein_g": food["protein_g"],
                    "carbs_g": food["carbs_g"],
                    "fat_g": food["fat_g"],
                    "fiber_g": food.get("fiber_g", 0.0),
                    "calcium_mg": food.get("calcium_mg", 0),
                    "source": food.get("source", "ICMR-NIN IFCT"),
                    "ref_id": food.get("ref_id", "ICMR-IFCT"),
                    "category": food.get("category", "General Food"),
                    "confidence": "Database-Sourced Match",
                    "disclaimer": "Nutrition information is based on available source data and may vary by food variety, preparation method, brand, serving size, and measurement."
                }

        # 2. Search USDA FoodData Central API
        usda_res = cls._search_usda_api(query_clean)
        if usda_res.get("matched"):
            return usda_res

        # 3. Non-Match Handling
        return {
            "matched": False,
            "query": query,
            "message": f"I couldn't confidently match '{query}' to a database-sourced record, so I won't estimate its nutritional values.",
            "disclaimer": "VitalBite AI strictly relies on database-sourced nutrition records to prevent inaccurate calorie or macronutrient hallucinations."
        }

    @classmethod
    def _search_usda_api(cls, query: str) -> Dict[str, Any]:
        """Queries USDA FoodData Central REST API."""
        api_key = get_usda_api_key()
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query}&pageSize=1"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                foods = data.get("foods", [])
                if foods:
                    first = foods[0]
                    nutrients = {n.get("nutrientName", "").lower(): n.get("value", 0.0) for n in first.get("foodNutrients", [])}
                    
                    calories = nutrients.get("energy", nutrients.get("energy (kcal)", 0.0))
                    protein = nutrients.get("protein", 0.0)
                    carbs = nutrients.get("carbohydrate, by difference", 0.0)
                    fat = nutrients.get("total lipid (fat)", 0.0)
                    fiber = nutrients.get("fiber, total dietary", 0.0)

                    return {
                        "matched": True,
                        "query": query,
                        "food_item": first.get("description", query.capitalize()),
                        "serving_size": "100g",
                        "calories_kcal": round(calories, 1),
                        "protein_g": round(protein, 1),
                        "carbs_g": round(carbs, 1),
                        "fat_g": round(fat, 1),
                        "fiber_g": round(fiber, 1),
                        "source": "USDA FoodData Central API",
                        "category": first.get("foodCategory", "USDA Reference Food"),
                        "confidence": "Database-Sourced Match",
                        "disclaimer": "Nutritional data retrieved from USDA FoodData Central. Serving values are normalized per 100g."
                    }
        except Exception as e:
            print(f"[NutritionService] USDA API error: {e}")

        return {"matched": False}

    @classmethod
    def get_food_swaps(cls, original_food: str, swap_preference: str = "High Protein") -> List[Dict[str, Any]]:
        """Provides database-sourced food substitution recommendations."""
        icmr_data = cls._load_icmr_dataset().get("foods", [])
        swaps = []
        
        orig_clean = original_food.lower()
        pref_clean = swap_preference.lower()

        for item in icmr_data:
            if orig_clean in item["name"].lower():
                continue
            
            if "protein" in pref_clean and item.get("protein_g", 0) >= 8.0:
                swaps.append(item)
            elif "vegetarian" in pref_clean and item.get("category") in ["Dairy & Milk Products", "Pulses & Legumes", "Fermented Foods"]:
                swaps.append(item)
            elif "low carb" in pref_clean and item.get("carbs_g", 100) <= 10.0:
                swaps.append(item)

        return swaps[:3] if swaps else icmr_data[:3]
