"""
VitalBite AI — Safe Gemini Diagnostics & Connectivity Inspector
Executes end-to-end authentication, dynamic model discovery, bare generation, system instructions,
and multi-turn chat validation without exposing API keys or secrets.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from services.ai_service import AIService, get_gemini_api_key, GENAI_SDK_TYPE, GENAI_SDK_VERSION
from google import genai
from google.genai import types

def run_gemini_diagnostics():
    print("==================================================")
    print("      VITALBITE AI — GEMINI DIAGNOSTICS REPORT     ")
    print("==================================================")

    diag = AIService.get_detailed_diagnostics()
    key_val = get_gemini_api_key()

    sdk_label = f"{GENAI_SDK_TYPE} {GENAI_SDK_VERSION}"
    print(f"Gemini SDK:          {sdk_label}")
    print(f"API configuration:   {diag.get('api_configuration')}")
    print(f"API authentication:  {diag.get('api_authentication')}")
    print(f"Model discovery:     {diag.get('model_discovery')}")
    print(f"Status:              {diag.get('status')}")
    
    selected_model = diag.get("selected_model")
    print(f"Selected model:      {selected_model or 'None'}")
    
    models = diag.get("available_models", [])
    if models:
        print(f"Available models:    {len(models)} discovered")
        preview = [m for m in models if "flash" in m][:5]
        for m in preview:
            print(f"  • {m}")

    print("==================================================")

    if diag.get("status") != "READY" or not key_val:
        print(f"Root cause:          {diag.get('safe_message')}")
        print("Bare generation:     SKIPPED")
        print("System instruction:  SKIPPED")
        print("Chat generation:     SKIPPED")
        print("Health AI end-to-end: FAIL")
        return False

    client = genai.Client(api_key=key_val)
    test_model = selected_model or "gemini-3.6-flash"

    # Step 1: Bare generation
    bare_ok = False
    try:
        resp1 = client.models.generate_content(
            model=test_model,
            contents="Reply with exactly: VitalBite Gemini bare test successful."
        )
        if resp1 and resp1.text:
            print("Bare generation:     PASS")
            bare_ok = True
        else:
            print("Bare generation:     FAIL (Empty response)")
    except Exception as e:
        print(f"Bare generation:     FAIL ({type(e).__name__}: {str(e)[:80]})")

    # Step 2: System instruction
    sys_ok = False
    try:
        config = types.GenerateContentConfig(
            system_instruction="You are a calm, empathetic health assistant."
        )
        resp2 = client.models.generate_content(
            model=test_model,
            contents="Reply with exactly: VitalBite system instruction test successful.",
            config=config
        )
        if resp2 and resp2.text:
            print("System instruction:  PASS")
            sys_ok = True
        else:
            print("System instruction:  FAIL (Empty response)")
    except Exception as e:
        print(f"System instruction:  FAIL ({type(e).__name__}: {str(e)[:80]})")

    # Step 3: Chat generation
    chat_ok = False
    try:
        chat = client.chats.create(model=test_model)
        resp3 = chat.send_message("Reply with exactly: VitalBite chat test successful.")
        if resp3 and resp3.text:
            print("Chat generation:     PASS")
            chat_ok = True
        else:
            print("Chat generation:     FAIL (Empty response)")
    except Exception as e:
        print(f"Chat generation:     FAIL ({type(e).__name__}: {str(e)[:80]})")

    # Step 4: Health AI Service Full Request
    ai_service_ok = False
    try:
        full_resp = AIService.generate_response(
            prompt="Give me three general tips for staying healthy.",
            system_instruction="You are VitalBite AI, an informational health assistant."
        )
        if full_resp and not full_resp.startswith("SERVICE_UNAVAILABLE:"):
            print("Health AI end-to-end: PASS")
            print(f"\nSample Response Excerpt:\n{full_resp[:180]}...")
            ai_service_ok = True
        else:
            print(f"Health AI end-to-end: FAIL ({full_resp})")
    except Exception as e:
        print(f"Health AI end-to-end: FAIL ({type(e).__name__}: {str(e)[:80]})")

    print("==================================================")
    all_passed = bare_ok and sys_ok and chat_ok and ai_service_ok
    if all_passed:
        print("FINAL STATUS: ALL TESTS PASSED (READY)")
    else:
        print("FINAL STATUS: SOME TESTS FAILED")
    return all_passed

if __name__ == "__main__":
    success = run_gemini_diagnostics()
    sys.exit(0 if success else 1)
