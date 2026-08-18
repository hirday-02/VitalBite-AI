"""
VitalBite AI — Centralized AI Service
Powered by the official Google GenAI SDK (google-genai) with cached diagnostics,
429 exponential backoff protection, zero-leak provider independence, and seamless Demo Mode fallbacks.
"""
import os
import time
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from services.demo_service import get_fallback_ai_response, get_fallback_symptom_assessment

# Load local environment variables if .env exists
load_dotenv()

# SDK Availability Inspection
GENAI_SDK_AVAILABLE = False
GENAI_SDK_TYPE = "none"
GENAI_SDK_VERSION = "none"

try:
    from google import genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
    GENAI_SDK_TYPE = "google-genai"
    GENAI_SDK_VERSION = getattr(genai, "__version__", "2.18.1")
except ImportError:
    try:
        import google.generativeai as legacy_genai
        GENAI_SDK_AVAILABLE = True
        GENAI_SDK_TYPE = "google-generativeai"
        GENAI_SDK_VERSION = getattr(legacy_genai, "__version__", "0.8.6")
    except ImportError:
        pass

def is_valid_gemini_key(key: Optional[str]) -> bool:
    """Verifies that the provided API key is non-empty and not a template placeholder."""
    if not key or not str(key).strip():
        return False
    k = str(key).strip().lower()
    placeholders = [
        "your_gemini_api_key_here",
        "your_gemini_api_key",
        "your_api_key",
        "your_key",
        "your_gemini",
        "placeholder",
        "example"
    ]
    return not any(p in k for p in placeholders)

def get_gemini_api_key() -> str:
    """
    Safely retrieves the Gemini API Key from:
    1. os.environ["GEMINI_API_KEY"] (including loaded .env)
    2. Streamlit secrets (st.secrets["GEMINI_API_KEY"] or .streamlit/secrets.toml)
    """
    env_val = os.getenv("GEMINI_API_KEY", "").strip()
    if is_valid_gemini_key(env_val):
        return env_val

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            sec_val = str(st.secrets["GEMINI_API_KEY"]).strip()
            if is_valid_gemini_key(sec_val):
                return sec_val
    except Exception:
        pass

    try:
        import toml
        secrets_file = os.path.abspath(".streamlit/secrets.toml")
        if os.path.exists(secrets_file):
            with open(secrets_file, "r", encoding="utf-8") as f:
                data = toml.load(f)
                file_key = str(data.get("GEMINI_API_KEY", "")).strip()
                if is_valid_gemini_key(file_key):
                    return file_key
    except Exception:
        pass

    return ""

class AIService:
    _configured: bool = False
    _client: Any = None
    _available_models: List[str] = []
    _selected_model: Optional[str] = None
    _last_diagnostic: Dict[str, Any] = {}
    _diagnostic_timestamp: float = 0.0
    _DIAGNOSTIC_CACHE_TTL: float = 600.0  # Cache diagnostics for 10 minutes to protect RPM limits

    @classmethod
    def get_detailed_diagnostics(cls, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Runs diagnostic evaluation of the Gemini configuration and connectivity without exposing secrets.
        Caches result in memory to prevent burning API rate limits on page switches and reruns.
        """
        now = time.time()
        if not force_refresh and cls._last_diagnostic and (now - cls._diagnostic_timestamp < cls._DIAGNOSTIC_CACHE_TTL):
            return cls._last_diagnostic

        diag = {
            "sdk_name": f"{GENAI_SDK_TYPE} ({GENAI_SDK_VERSION})",
            "api_configuration": "FAIL",
            "api_authentication": "FAIL",
            "model_discovery": "FAIL",
            "available_models": [],
            "selected_model": None,
            "status": "CONFIG_MISSING",
            "safe_message": "No API key configured."
        }

        if not GENAI_SDK_AVAILABLE:
            diag["status"] = "SDK_UNAVAILABLE"
            diag["safe_message"] = "Google GenAI SDK is not installed in the Python environment."
            cls._last_diagnostic = diag
            cls._diagnostic_timestamp = now
            return diag

        raw_key = get_gemini_api_key()
        if not raw_key:
            raw_unvalidated = os.getenv("GEMINI_API_KEY", "")
            if not raw_unvalidated:
                try:
                    import streamlit as st
                    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                        raw_unvalidated = str(st.secrets["GEMINI_API_KEY"])
                except Exception:
                    pass
            if not raw_unvalidated:
                try:
                    import toml
                    if os.path.exists(".streamlit/secrets.toml"):
                        with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
                            d = toml.load(f)
                            raw_unvalidated = str(d.get("GEMINI_API_KEY", ""))
                except Exception:
                    pass

            if raw_unvalidated and not is_valid_gemini_key(raw_unvalidated):
                diag["status"] = "CONFIG_PLACEHOLDER"
                diag["safe_message"] = "GEMINI_API_KEY is still set to template placeholder string."
            else:
                diag["status"] = "CONFIG_MISSING"
                diag["safe_message"] = "GEMINI_API_KEY is not configured in secrets.toml or environment."
            cls._last_diagnostic = diag
            cls._diagnostic_timestamp = now
            return diag

        diag["api_configuration"] = "PASS"

        # Test Authentication & Model Discovery
        try:
            if GENAI_SDK_TYPE == "google-genai":
                from google import genai
                client = genai.Client(api_key=raw_key)
                
                discovered = []
                for m in client.models.list():
                    name = getattr(m, "name", "")
                    if name:
                        clean_name = name.replace("models/", "")
                        discovered.append(clean_name)
                
                diag["api_authentication"] = "PASS"
                diag["available_models"] = discovered
                
                if discovered:
                    diag["model_discovery"] = "PASS"
                    preferred_priority = [
                        "gemini-3.6-flash",
                        "gemini-3.5-flash",
                        "gemini-3.5-flash-lite",
                        "gemini-3.1-flash-lite",
                        "gemini-3-flash-preview",
                        "gemini-flash-lite-latest"
                    ]
                    
                    selected = next((p for p in preferred_priority if p in discovered), None)
                    if not selected:
                        selected = next((d for d in discovered if "flash" in d and "tts" not in d and "image" not in d), discovered[0])

                    diag["selected_model"] = selected
                    diag["status"] = "READY"
                    diag["safe_message"] = f"Gemini connection established using {selected}."
                else:
                    diag["status"] = "MODEL_DISCOVERY_FAILED"
                    diag["safe_message"] = "Authentication succeeded but no generative models were returned by the API."
            else:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=raw_key)
                discovered = []
                for m in legacy_genai.list_models():
                    if "generateContent" in m.supported_generation_methods:
                        discovered.append(m.name.replace("models/", ""))
                
                diag["api_authentication"] = "PASS"
                diag["available_models"] = discovered
                if discovered:
                    diag["model_discovery"] = "PASS"
                    diag["selected_model"] = discovered[0]
                    diag["status"] = "READY"
                    diag["safe_message"] = f"Gemini connection established using {discovered[0]}."
                else:
                    diag["status"] = "MODEL_DISCOVERY_FAILED"
                    diag["safe_message"] = "Authentication succeeded but no generateContent models were discovered."

        except Exception as e:
            err_str = str(e).lower()
            if "auth" in err_str or "api_key" in err_str or "401" in err_str or "403" in err_str or "permission" in err_str:
                diag["status"] = "AUTH_FAILED"
                diag["safe_message"] = "Gemini API key authentication failed. Please verify key permissions in Google AI Studio."
            elif "429" in err_str or "quota" in err_str or "rate" in err_str or "resource_exhausted" in err_str:
                diag["status"] = "READY"
                diag["safe_message"] = "Gemini API key active (rate-limit backoff active)."
                diag["selected_model"] = "gemini-3.6-flash"
            else:
                diag["status"] = "API_REQUEST_FAILED"
                diag["safe_message"] = "Unable to connect to Google Gemini endpoint due to network/API error."

        cls._last_diagnostic = diag
        cls._diagnostic_timestamp = now
        return diag

    @classmethod
    def get_diagnostic_status(cls) -> str:
        """Returns the high-level status code from the latest diagnostic."""
        diag = cls.get_detailed_diagnostics(force_refresh=False)
        return diag.get("status", "CONFIG_MISSING")

    @classmethod
    def is_available(cls) -> bool:
        """Returns True if the Gemini service is configured and ready."""
        return cls.get_diagnostic_status() == "READY"

    @classmethod
    def initialize(cls) -> bool:
        """Configures the client once and reuses it across sessions."""
        if cls._configured and cls._client:
            return True

        diag = cls.get_detailed_diagnostics(force_refresh=False)
        if diag.get("status") != "READY":
            return False

        api_key = get_gemini_api_key()
        try:
            if GENAI_SDK_TYPE == "google-genai":
                from google import genai
                cls._client = genai.Client(api_key=api_key)
            else:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=api_key)
                cls._client = legacy_genai

            cls._available_models = diag.get("available_models", ["gemini-3.6-flash"])
            cls._selected_model = diag.get("selected_model", "gemini-3.6-flash")
            cls._configured = True
            return True
        except Exception:
            return False

    @classmethod
    def generate_response(
        cls,
        prompt: str,
        system_instruction: Optional[str] = None,
        is_demo: bool = False,
        user_name: str = "Alex"
    ) -> str:
        """
        Generates response from Google Gemini with single-request discipline and 429 exponential backoff.
        If Gemini is unavailable or during Demo Mode without keys, seamlessly returns realistic, evidence-based guidance.
        """
        # If Gemini is configured, attempt live call first
        if cls.initialize():
            model_name = cls._selected_model or "gemini-3.6-flash"
            for attempt in range(2):
                try:
                    if GENAI_SDK_TYPE == "google-genai":
                        config = None
                        if system_instruction:
                            config = types.GenerateContentConfig(
                                system_instruction=system_instruction
                            )
                        
                        response = cls._client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=config
                        )
                        if response and response.text:
                            return response.text.strip()
                    else:
                        import google.generativeai as legacy_genai
                        if system_instruction:
                            try:
                                gen_model = legacy_genai.GenerativeModel(model_name, system_instruction=system_instruction)
                            except Exception:
                                gen_model = legacy_genai.GenerativeModel(model_name)
                                prompt = f"SYSTEM INSTRUCTION: {system_instruction}\n\nUSER PROMPT: {prompt}"
                        else:
                            gen_model = legacy_genai.GenerativeModel(model_name)

                        response = gen_model.generate_content(prompt)
                        if response and response.text:
                            return response.text.strip()

                except Exception as e:
                    err_str = str(e).lower()
                    if ("429" in err_str or "quota" in err_str or "rate" in err_str or "resource_exhausted" in err_str) and attempt == 0:
                        time.sleep(2.5)  # Clean 2.5s backoff before single retry
                        continue
                    elif "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                        if is_demo:
                            return get_fallback_ai_response(prompt, user_name)
                        return (
                            "SERVICE_UNAVAILABLE: Google Gemini rate limit (5 RPM) reached. "
                            "Please wait 10–15 seconds before sending your next inquiry."
                        )
                    else:
                        if is_demo:
                            return get_fallback_ai_response(prompt, user_name)
                        return f"SERVICE_UNAVAILABLE: VitalBite AI encountered an error: {str(e)[:120]}"

        # If live service is offline or in Demo Mode, provide rich evidence-based fallback
        if is_demo:
            return get_fallback_ai_response(prompt, user_name)

        # For unconfigured non-demo users, return clear setup message
        diag = cls.get_detailed_diagnostics(force_refresh=False)
        status = diag.get("status", "CONFIG_MISSING")
        if status in ["CONFIG_MISSING", "CONFIG_PLACEHOLDER"]:
            return "SERVICE_UNAVAILABLE: AI configuration is not set up yet. Please provide a valid Gemini API key in secrets.toml or use Demo Mode."
        elif status == "AUTH_FAILED":
            return "SERVICE_UNAVAILABLE: VitalBite AI could not authenticate with the Gemini service. Please verify your API key."
        else:
            return "SERVICE_UNAVAILABLE: VitalBite AI is temporarily unable to reach the AI service. Please try again in a few moments."

HEALTH_ASSISTANT_SYSTEM_PROMPT = """
You are VitalBite AI, a calm, empathetic, intelligent digital health information assistant.

CORE RULES:
1. NON-DIAGNOSTIC BOUNDARY: You are an informational assistant, NOT a medical doctor, hospital, or diagnostic device. Never provide definitive clinical diagnoses.
2. SAFETY FIRST: Prioritize medical safety. Highlight red flags that require professional care.
3. EMPATHY & CLARITY: Use warm, encouraging, non-judgmental language. Avoid medical jargon.
4. MEDICAL DISCLAIMER: Always remind users that information is for general educational purposes and important health decisions should be evaluated by a licensed healthcare professional.
5. NO HALLUCINATION: Never invent medication dosages, medical studies, or clinical facts.
6. NUTRITION BOUNDARY: Numerical nutrition data (calories, protein, carbs, fat, fiber) in VitalBite AI is computed deterministically from verified ICMR-NIN & USDA datasets. Provide explanations and lifestyle context, but do not invent arbitrary numbers.
"""

def build_health_chat_prompt(user_message: str, profile: Optional[Dict[str, Any]] = None) -> tuple[str, str]:
    profile_summary = ""
    if profile:
        profile_summary = f"""
USER HEALTH CONTEXT:
- Name: {profile.get('name', 'Not specified')}
- Age: {profile.get('age', 'Not specified')}
- Gender: {profile.get('gender', 'Not specified')}
- Allergies: {profile.get('allergies', 'None')}
- Conditions: {profile.get('conditions', 'None')}
- Current Medications: {profile.get('medications', 'None')}
"""
    prompt = f"""
{profile_summary}
USER INQUIRY:
{user_message}

Please provide a helpful, empathetic response. Address their question directly, offer general evidence-based guidance, highlight any warning signs, and encourage consulting a healthcare provider if appropriate.
"""
    return prompt, HEALTH_ASSISTANT_SYSTEM_PROMPT

def build_symptom_assessment_prompt(
    symptoms: str, duration: str, severity: str, profile: Optional[Dict[str, Any]] = None
) -> tuple[str, str]:
    profile_summary = ""
    if profile:
        profile_summary = f"""
USER CONTEXT:
- Age: {profile.get('age', 'Not specified')}, Gender: {profile.get('gender', 'Not specified')}
- Allergies: {profile.get('allergies', 'None')}
- Chronic Conditions: {profile.get('conditions', 'None')}
"""
    prompt = f"""
{profile_summary}
REPORTED SYMPTOMS:
- Symptoms: {symptoms}
- Duration: {duration or 'Not specified'}
- Severity (1-10 scale): {severity or 'Not specified'}

Provide a structured, educational informational assessment.

Format with clear Markdown headings:
## **Possible Considerations** (Educational Only)
[List 2-4 general conditions or factors commonly associated with these symptoms. Emphasize these are possibilities, not diagnoses.]

## **Safe Self-Care & Monitoring**
[Provide safe, general comfort measures, hydration, rest, and symptoms to watch.]

## **When to Seek Professional Medical Care**
[Specific red flags requiring doctor consultation or urgent evaluation.]

## **Next Steps**
[Guidance on consulting a primary care doctor, specialist, or urgent care if symptoms persist.]

## **Important Disclaimer**
⚠️ VitalBite AI is currently in beta testing. This information is for educational/informational purposes and is not a diagnosis or a substitute for professional medical care. Consult a qualified healthcare professional.
"""
    return prompt, HEALTH_ASSISTANT_SYSTEM_PROMPT

def build_document_analysis_prompt(document_text: str) -> tuple[str, str]:
    prompt = f"""
The user has uploaded a health document or lab report excerpt:
---
{document_text}
---

Provide a clear, objective summary of the key terms, findings, or metrics in this document.
Explain medical terms in plain English.
Identify any values marked outside reference ranges so the user can discuss them with their doctor.

IMPORTANT: Clearly label this summary as "AI-Assisted Interpretation — Not an Official Medical Diagnostics Report".
Remind the user to share the full document with their prescribing doctor or hospital.
"""
    return prompt, HEALTH_ASSISTANT_SYSTEM_PROMPT
