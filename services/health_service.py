"""
VitalBite AI — Health Metrics & Analytics Service
Calculates standard objective health metrics (BMI, BMR, TDEE, Profile Completeness).
Strictly avoids age-risk heuristics or pseudoscientific health rules.
"""
from typing import Dict, Any, Optional

class HealthService:
    @staticmethod
    def calculate_bmi(height_cm: float, weight_kg: float) -> Optional[Dict[str, Any]]:
        """
        Calculates Body Mass Index (BMI).
        Presents result strictly as a general population reference metric, NOT a medical diagnosis.
        """
        if not height_cm or not weight_kg or height_cm <= 0 or weight_kg <= 0:
            return None

        height_m = height_cm / 100.0
        bmi_val = round(weight_kg / (height_m * height_m), 1)

        category = "Normal weight"
        color = "#059669"  # Soft emerald
        description = "Your BMI falls within the standard normal reference range."

        if bmi_val < 18.5:
            category = "Underweight"
            color = "#D97706"  # Amber
            description = "Your BMI is below the standard reference range. Ensure adequate nutrient intake."
        elif 25.0 <= bmi_val < 30.0:
            category = "Overweight"
            color = "#D97706"
            description = "Your BMI is slightly above the standard reference range."
        elif bmi_val >= 30.0:
            category = "Obesity"
            color = "#DC2626"  # Red
            description = "Your BMI falls in the elevated reference range. Consider discussing balanced wellness with a doctor."

        return {
            "bmi": bmi_val,
            "category": category,
            "color": color,
            "description": description,
            "disclaimer": "BMI is a simple screening tool based on height and weight. It does not account for muscle mass, bone density, or individual body composition."
        }

    @staticmethod
    def calculate_bmr(height_cm: float, weight_kg: float, age: int, gender: str = "Male") -> Optional[float]:
        """Calculates Basal Metabolic Rate (BMR) using Mifflin-St Jeor equation."""
        if not height_cm or not weight_kg or not age:
            return None

        is_male = gender.lower() == "male"
        s = 5 if is_male else -161
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + s
        return round(bmr, 0)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
        """Calculates Total Daily Energy Expenditure (TDEE)."""
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        mult = multipliers.get(activity_level.lower(), 1.55)
        return round(bmr * mult, 0)

    @staticmethod
    def get_profile_completeness(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates health profile completion percentage based on provided fields."""
        fields = [
            ("name", "Name"),
            ("age", "Age"),
            ("gender", "Gender"),
            ("height_cm", "Height"),
            ("weight_kg", "Weight"),
            ("blood_type", "Blood Type"),
            ("allergies", "Allergies"),
            ("conditions", "Chronic Conditions"),
            ("medications", "Current Medications")
        ]
        
        if not profile:
            return {
                "percentage": 0,
                "completed_count": 0,
                "total_count": len(fields),
                "missing_fields": [label for _, label in fields]
            }

        completed = 0
        missing = []
        for key, label in fields:
            val = profile.get(key)
            if val is not None and str(val).strip() != "":
                completed += 1
            else:
                missing.append(label)

        pct = round((completed / len(fields)) * 100)
        return {
            "percentage": pct,
            "completed_count": completed,
            "total_count": len(fields),
            "missing_fields": missing
        }
