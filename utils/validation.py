"""
VitalBite AI — Input Validation Helper
Validates age, height, weight, email, and user input fields without shaming users.
"""
from typing import Optional

def validate_age(age_str: str) -> tuple[bool, Optional[int], str]:
    if not age_str or not age_str.strip():
        return True, None, ""
    try:
        val = int(age_str.strip())
        if 0 <= val <= 130:
            return True, val, ""
        return False, None, "Age must be between 0 and 130."
    except ValueError:
        return False, None, "Please enter age as a valid number."

def validate_height(height_str: str) -> tuple[bool, Optional[float], str]:
    if not height_str or not height_str.strip():
        return True, None, ""
    try:
        val = float(height_str.strip())
        if 30.0 <= val <= 280.0:
            return True, round(val, 1), ""
        return False, None, "Height must be between 30 cm and 280 cm."
    except ValueError:
        return False, None, "Please enter height as a valid number (in cm)."

def validate_weight(weight_str: str) -> tuple[bool, Optional[float], str]:
    if not weight_str or not weight_str.strip():
        return True, None, ""
    try:
        val = float(weight_str.strip())
        if 2.0 <= val <= 450.0:
            return True, round(val, 1), ""
        return False, None, "Weight must be between 2 kg and 450 kg."
    except ValueError:
        return False, None, "Please enter weight as a valid number (in kg)."
