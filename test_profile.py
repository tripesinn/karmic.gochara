from app_common import _enrich_profile_with_natal

profile = {
    "name": "Test",
    "year": 1990, "month": 1, "day": 1,
    "hour": 12, "minute": 0,
    "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"
}

natal = {
    "Ascendant": {"display": "Ascendant Vierge 15°0'"},
    "Lune ☽": {"display": "Lune Sagittaire 20°0'", "lon": 260.0},
    "Soleil ☀": {"display": "Soleil Capricorne 10°0'"}
}

enriched = _enrich_profile_with_natal(profile, natal)
print(enriched.get("planets_info"))
