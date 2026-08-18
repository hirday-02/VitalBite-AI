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
        "name": "Alex Rivera",
        "age": 28,
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

⚠️ *VitalBite AI is currently in beta testing. Information provided is for general educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical advice.*""",
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

⚠️ *VitalBite AI is currently in beta testing. Educational guidance only.*""",
                "created_at": "2026-08-17T09:16:00Z"
            }
        ]
    }

def get_default_demo_symptom_assessments() -> List[Dict[str, Any]]:
    """Returns sample symptom assessments for demonstration."""
    return [
        {
            "id": "demo_sym_1",
            "user_id": DEMO_USER_ID,
            "symptoms": "Mild tension headache across forehead and slight neck stiffness after long screen time.",
            "duration": "2 days",
            "severity": "3",
            "is_emergency": False,
            "created_at": "2026-08-17T11:20:00Z",
            "analysis": """## **Possible Considerations** (Educational Only)
- **Tension-Type Headache**: Common, non-throbbing bilateral ache often linked to posture, eye strain, or stress.
- **Digital Eye Strain**: Prolonged screen exposure without visual breaks can cause frontal head discomfort.
- **Cervicogenic Strain**: Poor ergonomics or prolonged neck flexion while working.

## **Safe Self-Care & Monitoring**
- Practice the 20-20-20 rule (every 20 minutes, look at an object 20 feet away for 20 seconds).
- Maintain steady hydration (at least 2.5L water daily).
- Perform gentle neck and upper trapezius stretches.
- Ensure proper screen height at eye level.

## **When to Seek Professional Medical Care**
- Sudden onset "thunderclap" severe headache.
- Accompanying high fever, rash, confusion, or visual disturbances.
- Headache following head trauma or worsening progressively.

## **Important Disclaimer**
⚠️ VitalBite AI is an educational assistant and cannot provide a medical diagnosis. Please discuss persistent or worsening symptoms with a qualified healthcare professional."""
        }
    ]

def get_default_demo_diet_plans() -> List[Dict[str, Any]]:
    """Returns sample saved diet plan for demonstration."""
    return [
        {
            "id": "demo_plan_1",
            "user_id": DEMO_USER_ID,
            "goal": "Body Recomposition",
            "diet_type": "Vegetarian",
            "created_at": "2026-08-16T15:00:00Z",
            "plan_text": "Goal: Body Recomposition (Vegetarian)\nDaily Calories: ~2,150 kcal | Protein: ~135g\nStructured 5-meal schedule with verified ICMR-NIN & USDA food staples (Paneer, Roti, Dal, Oats, Whey Isolate, Curd, Almonds)."
        }
    ]

def get_fallback_ai_response(prompt: str, user_name: str = "Alex") -> str:
    """
    Provides intelligent, evidence-based health guidance when Gemini API is unavailable.
    Guarantees zero crashes and 100% compliance with beta disclaimers.
    """
    p_lower = prompt.lower()

    if any(w in p_lower for w in ["gym", "workout", "muscle", "strength", "progress", "exercise", "lift", "training"]):
        return f"""### 🏋️ Training & Nutrition Strategy for {user_name}

Here are the evidence-based principles for fitness progress and body recomposition:

1. **Consistent Resistance Training**:
   - Focus on compound multi-joint movements (squats, deadlifts, presses, rows).
   - Apply Progressive Overload (gradually increasing load, volume, or execution quality).
2. **Nutritional Foundation**:
   - Consume adequate daily protein (~1.6 to 2.0g per kg body weight).
   - Distribute protein across 3–5 balanced meals containing whole grains, vegetables, and quality fats.
3. **Recovery & Sleep**:
   - Target 7–9 hours of continuous sleep to support muscle protein synthesis and hormonal balance.
4. **Hydration**:
   - Drink 2.5 to 3.5 liters of water daily.

⚠️ *VitalBite AI is currently in beta testing. Information provided is for general educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical advice. Please consult a qualified healthcare professional or certified trainer before beginning new exercise programs.*"""

    elif any(w in p_lower for w in ["diet", "food", "protein", "calorie", "nutrition", "eat", "meal", "carb", "fat"]):
        return f"""### 🥗 Evidence-Based Nutrition Insights

Balanced nutrition supports energy, recovery, and long-term metabolic health:

- **Protein Distribution**: Incorporate high-quality protein sources (Paneer, Tofu, Legumes, Greek Yogurt, Whey, Eggs, or Lean Poultry) with each meal.
- **Complex Carbohydrates**: Prioritize whole grains, oats, brown rice, and millets for sustained glycogen replenishment and dietary fiber.
- **Essential Fats**: Include nuts, seeds, olive oil, and avocado to support endocrine and cardiovascular function.
- **Micronutrient Density**: Fill half your plate with colorful vegetables and leafy greens for essential vitamins and minerals.

⚠️ *VitalBite AI is currently in beta testing. Educational guidance only. Consult a registered dietitian for tailored medical nutrition therapy.*"""

    elif any(w in p_lower for w in ["sleep", "stress", "tired", "energy", "fatigue", "recovery"]):
        return f"""### 🌙 Rest, Sleep & Recovery Optimization

Optimizing rest is foundational for immune resilience, mental clarity, and physical recovery:

- **Circadian Consistency**: Go to bed and wake up at consistent times every day.
- **Sleep Hygiene**: Keep the bedroom cool, dark, and quiet. Avoid blue-light screens 60 minutes before bed.
- **Caffeine Curfew**: Limit caffeine consumption at least 8 hours before sleeping.
- **Active Relaxation**: Incorporate 10–15 minutes of light stretching or breathwork to down-regulate the nervous system.

⚠️ *VitalBite AI is currently in beta testing. If persistent fatigue or sleep issues continue, please consult a physician.*"""

    else:
        return f"""### 💡 Health & Wellness Guidance

Thank you for your question, {user_name}!

When managing everyday health and wellness, consider the following evidence-based foundations:
1. **Balanced Nutrition**: Prioritize whole, minimally processed foods, adequate dietary protein, and colorful vegetables.
2. **Regular Movement**: Aim for at least 150 minutes of moderate aerobic activity or 3–4 strength sessions weekly.
3. **Rest & Recovery**: Ensure 7–9 hours of sleep nightly and manage lifestyle stressors.
4. **Hydration & Consistency**: Maintain steady daily hydration and monitor how your body responds to routine changes.

⚠️ *VitalBite AI is currently in beta testing. Information provided is for general educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical advice. Please consult a qualified healthcare professional for medical concerns.*"""

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
⚠️ VitalBite AI is currently in beta testing. This information is for educational and informational purposes only and is not a diagnosis, prescription, or substitute for professional medical care. Consult a qualified healthcare professional for medical evaluation."""
