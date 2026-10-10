"""
VitalBite AI — Demo Mode Data & Fallback Intelligence Service
Provides rich, realistic fictional health profiles, pre-populated consultation records,
7-day meal plans, and fallback AI reasoning when external APIs or databases are not configured.
"""
from typing import Dict, Any, List, Optional

DEMO_USER_ID = "demo_user_vitalbite"

def get_default_demo_profile() -> Dict[str, Any]:
    """Returns a realistic, strictly fictional demonstration health profile."""
    return {
        "id": DEMO_USER_ID,
        "name": "Harsh Singh",
        "age": 22,
        "gender": "Male",
        "height_cm": 182,
        "weight_kg": 74.5,
        "blood_type": "O+",
        "dietary_preference": "Vegetarian",
        "allergies": "None",
        "conditions": "None",
        "medications": "None",
        "fitness_goal": "Body Recomposition",
        "activity_level": "moderate",
        "training_frequency": "4–5 days/week (Consistent Training)",
        "training_type": "Strength Training",
        "updated_at": "2026-08-18T10:00:00Z"
    }

def get_default_demo_chat_sessions() -> List[Dict[str, Any]]:
    """Returns sample conversation threads for demonstration."""
    return [
        {
            "id": "demo_sess_1",
            "user_id": DEMO_USER_ID,
            "title": "Gym Training & Nutrition Strategy",
            "created_at": "2026-08-16T14:30:00Z",
            "updated_at": "2026-08-16T14:35:00Z"
        },
        {
            "id": "demo_sess_2",
            "user_id": DEMO_USER_ID,
            "title": "Hydration & Sleep Recovery",
            "created_at": "2026-08-17T09:15:00Z",
            "updated_at": "2026-08-17T09:20:00Z"
        }
    ]

def get_default_demo_chat_messages() -> Dict[str, List[Dict[str, Any]]]:
    """Returns initial demo messages for demo chat threads."""
    return {
        "demo_sess_1": [
            {
                "id": "demo_msg_1",
                "session_id": "demo_sess_1",
                "user_id": DEMO_USER_ID,
                "sender": "user",
                "message": "I recently started going to the gym 4 days a week for body recomposition. What are the key pillars for steady progress?",
                "created_at": "2026-08-16T14:30:00Z"
            },
            {
                "id": "demo_msg_2",
                "session_id": "demo_sess_1",
                "user_id": DEMO_USER_ID,
                "sender": "assistant",
                "message": """Great initiative! Body recomposition (building lean muscle while managing body fat) is achievable through consistent lifestyle habits. Here are the core evidence-based pillars:

1. **Progressive Overload**: Gradually increase resistance, repetitions, or improve form over time to stimulate muscle adaptation.
2. **Protein Optimization**: Aim for roughly 1.6–2.0g of protein per kg of body weight distributed across 3–5 balanced meals.
3. **Calorie Balance**: Maintain a slight caloric deficit (10–15%) or eat at maintenance on training days.
4. **Rest & Recovery**: Muscle protein synthesis occurs during rest. Prioritize 7–9 hours of quality sleep.
5. **Hydration**: Drink 2.5–3.5 liters of water daily to support metabolic function and workout stamina.

*VitalBite AI is currently in beta testing. Information provided is for general educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical advice.*""",
                "created_at": "2026-08-16T14:31:00Z"
            }
        ],
        "demo_sess_2": [
            {
                "id": "demo_msg_3",
                "session_id": "demo_sess_2",
                "user_id": DEMO_USER_ID,
                "sender": "user",
                "message": "How does sleep affect my metabolism and muscle recovery?",
                "created_at": "2026-08-17T09:15:00Z"
            },
            {
                "id": "demo_msg_4",
                "session_id": "demo_sess_2",
                "user_id": DEMO_USER_ID,
                "sender": "assistant",
                "message": """Sleep is critical for both metabolic regulation and cellular repair:

- **Hormonal Balance**: Sleep regulates ghrelin (hunger hormone) and leptin (satiety hormone). Sleep deprivation increases cravings for calorie-dense carbohydrates.
- **Growth Hormone Release**: Deep slow-wave sleep is when the body releases human growth hormone (HGH), crucial for tissue repair and muscle protein synthesis.
- **Cortisol Management**: Inadequate sleep elevates cortisol, which can accelerate muscle breakdown and impair insulin sensitivity.

*Aim for a consistent sleep schedule and minimize blue light exposure 60 minutes before bed.*

*VitalBite AI is currently in beta testing. Educational guidance on sleep hygiene and recovery.*""",
                "created_at": "2026-08-17T09:16:00Z"
            }
        ]
    }

def get_default_demo_symptom_assessments() -> List[Dict[str, Any]]:
    """Returns sample symptom check history for demonstration."""
    return [
        {
            "id": "demo_sym_1",
            "user_id": DEMO_USER_ID,
            "symptoms": "Mild tension headache after 8 hours of computer work and low water intake",
            "duration": "4 hours",
            "severity": "3",
            "analysis": """## **Possible Considerations** (Educational Only)
- **Tension Headache**: Commonly triggered by prolonged screen time, eye strain, neck posture, or mild dehydration.
- **Dehydration**: Inadequate fluid intake can reduce blood volume and trigger cranial muscle tension.

## **Safe Self-Care & Monitoring**
- Drink 500–750ml of room temperature water immediately.
- Take a 15-minute break from digital screens. Apply a cool compress to the forehead.
- Practice gentle neck stretches and shoulder rolls.

## **When to Seek Professional Medical Care**
- Sudden "thunderclap" severe headache intensity.
- Headache accompanied by fever, stiff neck, confusion, vision changes, or numbness.

## **Important Disclaimer**
VitalBite AI is an educational assistant and cannot provide a medical diagnosis. Consult a healthcare provider if headaches persist.""",
            "is_emergency": False,
            "created_at": "2026-08-15T16:00:00Z"
        }
    ]

def get_default_demo_diet_plans() -> List[Dict[str, Any]]:
    """Returns sample diet plan history for demonstration."""
    return [
        {
            "id": "demo_diet_1",
            "user_id": DEMO_USER_ID,
            "goal": "Body Recomposition",
            "diet_type": "Vegetarian",
            "plan_text": """Goal: Body Recomposition (Vegetarian)
Target Daily Intake: ~2350 kcal | Protein: ~140g | Carbs: ~260g | Fat: ~65g

Optimized Daily Schedule:
- Breakfast: Oats with Toned Milk, Almonds & Banana (450 kcal, 18g P)
- Mid-Morning: Whey Protein Isolate Scoop in Water (120 kcal, 24g P)
- Lunch: Paneer Sabzi, 2 Whole Wheat Rotis, Yellow Dal & Cucumber Salad (720 kcal, 42g P)
- Evening Snack: Roasted Chana & Green Tea (210 kcal, 11g P)
- Dinner: Soya Chunk Curry, Brown Rice & Mixed Vegetable Salad (650 kcal, 45g P)

Nutritional Data Source: Verified ICMR-NIN IFCT 2017 & USDA Food Composition Tables.""",
            "created_at": "2026-08-17T12:00:00Z"
        }
    ]

def get_fallback_ai_response(
    prompt: str,
    user_name: str = "User",
    is_demo: bool = True,
    profile: Optional[Dict[str, Any]] = None
) -> str:
    """
    Provides intelligent, evidence-based health guidance when Gemini API is unavailable.
    Never assumes hardcoded user identity ('Alex Rivera') unless verified in user profile.
    Uses deterministic calculations when complete profile parameters are available.
    """
    p_lower = prompt.lower()

    # Clean display name
    clean_name = user_name if user_name and user_name != "Alex" else "there"
    if is_demo and (not user_name or user_name == "User"):
        clean_name = "there"

    if any(w in p_lower for w in ["gym", "workout", "muscle", "strength", "progress", "exercise", "lift", "training", "diet", "meal plan", "meal", "weekly plan", "7-day", "7 day", "menu", "plan for", "protein", "calorie", "nutrition", "eat", "food", "carb", "fat", "supplement", "macro"]):
        # Check if profile has sufficient metrics for deterministic calculation
        has_metrics = bool(profile and profile.get("age") and profile.get("height_cm") and profile.get("weight_kg"))

        if has_metrics:
            from services.diet_planner_service import DietPlannerService
            goal = profile.get("fitness_goal") or "General Fitness"
            targets = DietPlannerService.calculate_nutrition_targets(
                profile=profile,
                fitness_goal=goal,
                activity_level=profile.get("activity_level", "moderate")
            )
            return f"""### Gym & Goal-Aligned Nutrition Strategy

Welcome! Starting a gym routine is an excellent step toward strength, metabolic resilience, and body composition.

#### Verified Target Estimates (Based on Saved Profile)
- **Primary Goal**: {goal}
- **Basal Metabolic Rate (BMR)**: ~{targets['bmr']} kcal/day
- **Total Daily Energy Expenditure (TDEE)**: ~{targets['tdee']} kcal/day
- **Target Calories**: ~{targets['target_calories']} kcal/day
- **Protein Target**: ~{targets['protein_g']}g/day (1.6–2.0g/kg body weight)
- **Carbohydrates / Fats**: ~{targets['carbs_g']}g carbs / ~{targets['fat_g']}g fat

#### Key Beginner Principles
1. **Progressive Overload**: Focus on multi-joint compound movements (squats, deadlifts, presses, rows). Gradually increase load or improve form over time.
2. **Protein Distribution**: Spread your protein across 3–4 balanced meals using verified whole foods (Paneer, Tofu, Legumes, Eggs, or Lean Poultry).
3. **Rest & Recovery**: Aim for 7–9 hours of sleep nightly to support muscle protein synthesis.

#### Interactive 7-Day Meal Plan
For a complete, day-by-day 7-day meal plan with exact food portioning and allergen exclusions, head over to the **7-Day Diet Planner** tab in VitalBite AI!

*VitalBite AI is in beta testing. Information provided is for general educational and informational purposes only.*"""
        else:
            return f"""### Gym & Fitness Nutrition Guidance

Starting a gym routine is a fantastic decision for long-term health, strength, and energy!

#### Core Beginner Pillars
1. **Progressive Resistance Training**: Start with 3–4 days of compound exercises (squats, rows, chest presses). Focus on proper form before adding heavy weights.
2. **Protein Optimization**: Aim for roughly 1.6 to 2.0g of protein per kg of body weight to support muscle recovery.
3. **Calorie Balance & Hydration**: Align your caloric intake with your primary goal and drink 2.5–3.5L of water daily.
4. **Recovery & Sleep**: Prioritize 7–9 hours of quality sleep to support muscle protein synthesis.

#### Help Us Personalize Your Exact Targets
To calculate your specific daily calorie, protein, carbohydrate, and fat numbers deterministically, could you share:
1. **Primary Goal**: Muscle Gain, Fat Loss, or Body Recomposition?
2. **Demographics**: Your current age, height, and weight (or save them in your **Health Profile** tab).
3. **Dietary Preference**: Vegetarian, Vegan, Non-Vegetarian, or specific food allergies?

#### Ready for a Complete 7-Day Meal Plan?
Once your profile is set, navigate to the **7-Day Diet Planner** tab to generate a custom 7-day meal plan using verified ICMR-NIN & USDA nutritional records.

*VitalBite AI is in beta testing. Information provided is for general educational purposes only.*"""

    elif any(w in p_lower for w in ["sleep", "stress", "tired", "energy", "fatigue", "recovery"]):
        return f"""### Rest, Sleep & Recovery Optimization

Optimizing rest is foundational for immune resilience, mental clarity, and physical recovery:

- **Circadian Consistency**: Go to bed and wake up at consistent times every day.
- **Sleep Hygiene**: Keep the bedroom cool, dark, and quiet. Avoid blue-light screens 60 minutes before bed.
- **Caffeine Curfew**: Limit caffeine consumption at least 8 hours before sleeping.
- **Active Relaxation**: Incorporate 10–15 minutes of light stretching or breathwork to down-regulate the nervous system.

*VitalBite AI is currently in beta testing. If persistent fatigue or sleep issues continue, please consult a physician.*"""

    else:
        return f"""### Health & Wellness Guidance

Thank you for your inquiry, {clean_name}!

When managing everyday health and wellness, consider the following evidence-based foundations:
1. **Balanced Nutrition**: Prioritize whole, minimally processed foods, adequate dietary protein, and colorful vegetables.
2. **Regular Movement**: Aim for at least 150 minutes of moderate aerobic activity or 3–4 strength sessions weekly.
3. **Rest & Recovery**: Ensure 7–9 hours of sleep nightly and manage lifestyle stressors.
4. **Hydration & Consistency**: Maintain steady daily hydration (2.5–3.5L daily) and monitor how your body responds.

*VitalBite AI is currently in beta testing. Information provided is for general educational and informational purposes only. Please consult a qualified healthcare professional for medical concerns.*"""

def get_fallback_symptom_assessment(symptoms: str, duration: str, severity: str) -> str:
    """Generates structured, safe symptom assessment when Gemini is offline."""
    return f"""## **Possible Considerations** (Educational Only)
- **General Symptom Response**: The symptoms described (*"{symptoms[:60]}..."*) are commonly associated with environmental factors, minor viral strains, muscle strain, fatigue, or stress.
- **Contextual Factors**: Duration (*{duration or 'recent'}*) and moderate severity rating (*{severity or '4'}/10*) suggest monitoring progression closely.

## **Safe Self-Care & Monitoring**
- Ensure adequate rest, hydration, and gentle nutrition.
- Avoid strenuous physical exertion until symptoms resolve.
- Monitor temperature and note any new or worsening signs.

## **When to Seek Professional Medical Care**
- Symptoms that worsen rapidly or fail to improve after several days.
- Appearance of red-flag symptoms such as high persistent fever, severe pain, breathing difficulty, or chest discomfort.

## **Important Disclaimer**
VitalBite AI is currently in beta testing. This information is for educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical care. Consult a qualified healthcare professional for medical evaluation."""
