import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x_grok_bot import generate_karmic_data, call_grok

load_dotenv()

user_data = {
    "month": 10,
    "day": 31,
    "year": 1974,
    "hour": 8,
    "minute": 25,
    "location": "Paris"
}

print("Génération du thème...")
prompt = generate_karmic_data(user_data)
print("Thème généré, appel API...")
response = call_grok(prompt)
print("\n=== RÉPONSE DE GROK ===")
print(response)
