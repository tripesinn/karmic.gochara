import sys
import os
sys.path.append('.')
from ai_interpret import _build_natal_context, generate_ai

profile = {
    "name": "Jero",
    "year": 1987, "month": 5, "day": 25,
    "hour": 12, "minute": 0,
    "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris", "city": "Paris",
    "planets": {
        "Sun": {"sign": "Taurus", "house": 10},
        "Moon": {"sign": "Virgo", "house": 2}
    }
}
try:
    natal_ctx = _build_natal_context(profile)
    print("Ctx built:", natal_ctx)
    user_params = {"user_provider": None, "user_key": None, "user_model": None}
    system = "Test system"
    prompt = "Test prompt"
    content = generate_ai(system, prompt, user=user_params, max_tokens=1024)
    print("Content:", content)
except Exception as e:
    import traceback
    traceback.print_exc()
