import sys

sys.path.append("/Users/jero87/karmic.gochara")
from ai_interpret import get_hook_natal

user_data = {
    "name": "TestUser",
    "chandra_lagna_sign": "Aries",
    "ketu_house": 4,
    "chiron_house": 6,
    "porte_visible_sign": "Libra",
    "lilith_house": 12,
    "ketu_nakshatra": "Ashvini",
    "rahu_nakshatra": "Chitra",
    "chiron_nakshatra": "Swati",
    "user_provider": "local"
}

try:
    print("Testing get_hook_natal...")
    res1 = get_hook_natal(user_data, lang="fr")
    print("\nResult 1:")
    print(res1)
    
    print("\nTesting get_hook_natal (again for originality)...")
    res2 = get_hook_natal(user_data, lang="fr")
    print("\nResult 2:")
    print(res2)

except Exception as e:
    print("Error:", e)
