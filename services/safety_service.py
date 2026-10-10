"""
VitalBite AI — Medical Safety & Emergency Triage Service
Multi-layer safety escalation system combining rule-based red-flag detection and contextual safety prompts.
Presents immediate emergency guidance for Indian emergency contacts (112).
"""
import re
from typing import Dict, Any, List

# Core red-flag trigger keywords for rapid safety escalation
EMERGENCY_KEYWORDS = [
    r"chest pain", r"severe pain in chest", r"heart attack",
    r"difficulty breathing", r"cannot breathe", r"shortness of breath", r"gasping",
    r"unconscious", r"passed out", r"fainted", r"unresponsive",
    r"stroke", r"facial drooping", r"slurred speech", r"arm weakness", r"sudden numbness",
    r"severe bleeding", r"uncontrolled bleeding", r"gushing blood",
    r"seizure", r"convulsions", r"fits",
    r"anaphylaxis", r"severe allergic reaction", r"swollen throat",
    r"suicide", r"self harm", r"end my life", r"overdose"
]

class SafetyService:
    @staticmethod
    def evaluate_emergency(text: str) -> Dict[str, Any]:
        """
        Multi-layered emergency evaluation.
        Combines deterministic regex safety scanning with safety triage guidance.
        """
        clean_text = text.lower()

        matched_triggers: List[str] = []
        for kw_pattern in EMERGENCY_KEYWORDS:
            if re.search(kw_pattern, clean_text):
                matched_triggers.append(kw_pattern.replace(r"\b", "").replace(r"\r", ""))

        is_high_risk = len(matched_triggers) > 0

        return {
            "is_emergency": is_high_risk,
            "triggers": matched_triggers,
            "primary_number": "112",
            "country": "India",
            "guidance_title": "POSSIBLE MEDICAL EMERGENCY DETECTED",
            "message": (
                "Your description contains symptoms that may require immediate emergency medical care. "
                "Do NOT wait for an AI response. Please seek immediate professional medical assistance or go to the nearest hospital."
            ),
            "action_steps": [
                "Call 112 immediately (India Emergency Contact)",
                "Go to the nearest emergency room or hospital",
                "Contact a trusted family member or neighbor",
                "Do not attempt to self-treat severe or sudden acute symptoms"
            ],
            "disclaimer": "VitalBite AI is an educational assistant and is NOT equipped to handle or evaluate medical emergencies."
        }
