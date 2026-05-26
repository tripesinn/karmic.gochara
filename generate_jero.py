import sys
import json
from datetime import date
from ai_interpret import get_hook_natal, stream_ai, get_synthesis
from astro_calc import calculate_transits

# Jero's profile
user = {
    "user_provider": "local", 
    "user_key": "dummy", 
    "user_model": "mlx-community/phi-4-4bit", 
    "name": "Jero", 
    "pseudo": "jero",
    "email": "jero@example.com",
    "lang": "fr",
    "year": 1987,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "lat": 48.8566,
    "lon": 2.3522,
    "tz": "Europe/Paris",
    "city": "Paris, France",
    "chandra_lagna_sign": "Cancer", 
    "ketu_house": 12, 
    "chiron_house": 4, 
    "porte_visible_sign": "Lion", 
    "lilith_house": 8, 
    "ketu_nakshatra": "Ashlesha", 
    "rahu_nakshatra": "Shravana", 
    "chiron_nakshatra": "Magha"
}

# Calculate Transits for today
today = date.today()
transit_loc = {"city": "Paris", "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"}
natal = {
    "name": user["name"],
    "year": user["year"],
    "month": user["month"],
    "day": user["day"],
    "hour": user["hour"],
    "minute": user["minute"],
    "lat": user["lat"],
    "lon": user["lon"],
    "tz": user["tz"],
    "city": user["city"],
}

print("Calculating transits...")
chart_data = calculate_transits(natal, transit_loc, today.year, today.month, today.day, 12, 0)

print("Generating Natal Hook...")
hook_natal = get_hook_natal(user)

print("Generating Synthesis...")
try:
    synthesis = get_synthesis(chart_data, user, lang="fr")
except Exception as e:
    synthesis = f"Erreur Synthèse: {e}"

# Writing to markdown file
with open("synthesis_jero.md", "w") as f:
    f.write(f"# Résultats Phi-4 pour Jero\n\n")
    f.write(f"## Hook Natal\n{hook_natal}\n\n")
    f.write(f"## Synthèse Complète\n{synthesis}\n\n")

print("Done. Wrote to synthesis_jero.md")
