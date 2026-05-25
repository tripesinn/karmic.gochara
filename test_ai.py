import sys
from ai_interpret import generate_ai, stream_ai, get_hook_natal

user = {"user_provider": "local", "user_key": "dummy", "user_model": "mlx-community/phi-4-4bit", "name": "Jero", "lang": "fr", "chandra_lagna_sign": "Cancer", "ketu_house": 12, "chiron_house": 4, "porte_visible_sign": "Lion", "lilith_house": 8, "ketu_nakshatra": "Ashlesha", "rahu_nakshatra": "Shravana", "chiron_nakshatra": "Magha"}

print("--- Testing generate_ai ---")
try:
    res = generate_ai("Tu es Astro.", "Dis bonjour !", user)
    print(res)
except Exception as e:
    print(f"Erreur lors de generate_ai (le serveur vLLM est-il lancé sur le port 8000 ?) : {e}")

print("\n--- Testing stream_ai ---")
try:
    stream_res = list(stream_ai("Tu es Astro.", "Dis bonjour 2 !", user))
    print("".join(stream_res))
except Exception as e:
    print(f"Erreur lors de stream_ai : {e}")

print("\n--- Testing get_hook_natal ---")
try:
    hook = get_hook_natal(user)
    print(hook)
except Exception as e:
    print(f"Erreur lors de get_hook_natal : {e}")

