"""
app_common.py — Constantes et helpers partages entre tous les blueprints
"""
import os

# ── Constantes ──────────────────────────────────────────────────────────────
TRANSIT_LOC_DEFAULT = {
    "city": "Paris, France",
    "lat":  48.8566,
    "lon":  2.3522,
    "tz":   "Europe/Paris",
}

_SIGNS_FR = [
    "Bélier", "Taureau", "Gémeaux", "Cancer",
    "Lion", "Vierge", "Balance", "Scorpion",
    "Sagittaire", "Capricorne", "Verseau", "Poissons",
]

UNLIMITED_PSEUDOS = {"jero", "marie"}

# Store des paiements en attente d'activation de session (cas navigateur externe).
# Clé : pseudo en minuscule, valeur : {"plan": str, "time": float}
_pending_plan_updates: dict = {}


# ── Helpers ─────────────────────────────────────────────────────────────────

def _enrich_profile_with_natal(profile: dict, natal: dict) -> dict:
    """
    Enrichit le profil session avec les données du thème natal calculé,
    pour que get_synthesis() dispose de chandra_lagna_sign, ketu_sign, etc.
    natal = result["natal"] de calculate_transits().
    """
    def _sign(display: str) -> str:
        parts = (display or "").strip().split()
        return parts[1] if len(parts) >= 2 else ""

    def _deg(display: str) -> str:
        parts = (display or "").strip().split()
        return parts[2] if len(parts) >= 3 else ""

    def _house(planet_sign: str, asc_sign: str) -> str:
        if not asc_sign or asc_sign not in _SIGNS_FR or not planet_sign or planet_sign not in _SIGNS_FR:
            return ""
        asc_idx = _SIGNS_FR.index(asc_sign)
        p_idx = _SIGNS_FR.index(planet_sign)
        return str((p_idx - asc_idx) % 12 + 1)

    enriched = dict(profile)
    asc = natal.get("Ascendant") or natal.get("ASC ↑") or {}
    asc_sign = _sign(asc.get("display", ""))
    enriched["chandra_lagna_sign"] = asc_sign
    enriched["chandra_lagna_deg"]  = _deg(asc.get("display", ""))

    for key, s_field, h_field, nak_field in [
        ("Nœud Sud ☋",      "ketu_sign",            "ketu_house",            "ketu_nakshatra"),
        ("Nœud Nord ☊",     "rahu_sign",            "rahu_house",            "rahu_nakshatra"),
        ("Chiron ⚷",        "chiron_sign",          "chiron_house",          "chiron_nakshatra"),
        ("Lilith ⚸",        "lilith_sign",          "lilith_house",          "lilith_nakshatra"),
        ("Saturne ♄",       "saturn_sign",          "saturn_house",          None),
        ("Jupiter ♃",       "jupiter_sign",         "jupiter_house",         None),
        ("Porte Visible ⊙", "porte_visible_sign",   "porte_visible_house",   None),
        ("Porte Invisible ⊗","porte_invisible_sign", "porte_invisible_house", None),
    ]:
        p = natal.get(key) or {}
        p_sign = _sign(p.get("display", ""))
        enriched[s_field] = p_sign
        enriched[h_field] = _house(p_sign, asc_sign)
        if nak_field:
            enriched[nak_field] = p.get("nakshatra", "")

    enriched["porte_visible_deg"]   = _deg((natal.get("Porte Visible ⊙")  or {}).get("display", ""))
    enriched["porte_invisible_deg"] = _deg((natal.get("Porte Invisible ⊗") or {}).get("display", ""))

    moon = natal.get("Lune ☽") or {}
    moon_lon = moon.get("lon_raw") or moon.get("lon")
    if moon_lon is not None:
        enriched["moon_longitude_sid"]   = str(round(float(moon_lon), 6))
        enriched["chandra_lagna_degree"] = str(round(float(moon_lon) % 30, 6))
    else:
        enriched["moon_longitude_sid"]   = ""
        enriched["chandra_lagna_degree"] = ""

    # Ajout de tous les degrés planétaires pour la carte SVG et de planets_info pour l'UI
    planets_info = []
    for p_key in ["Lune ☽", "Soleil ☀", "Mercure ☿", "Vénus ♀", "Mars ♂",
                  "Jupiter ♃", "Saturne ♄", "Uranus ♅", "Neptune ♆", "Pluton ♇",
                  "Nœud Nord ☊", "Nœud Sud ☋", "Chiron ⚷", "Lilith ⚸",
                  "Porte Visible ⊙", "Porte Invisible ⊗"]:
        planet_name = p_key.split(" ")[0].lower()
        p_data = natal.get(p_key, {})
        display = p_data.get("display", "")
        p_sign = _sign(display)
        p_deg = _deg(display)
        enriched[f"{planet_name}_deg"] = p_deg
        
        if p_data:
            planets_info.append({
                "name": p_key.split(" ")[0],
                "sign": p_sign,
                "degree": p_deg.replace("°", ".").replace("′", ""), # Clean up for sorting if needed, but UI just adds °
                "house": _house(p_sign, asc_sign),
                "retrograde": p_data.get("retrograde", False)
            })
            
    # Fix degree format for frontend (frontend adds °)
    for p in planets_info:
        if p["degree"]:
            p["degree"] = p["degree"].replace("°", ".").replace("′", "")

    enriched["planets_info"] = planets_info

    # Ajout des informations de naissance formatées
    year = enriched.get("year", "")
    month = enriched.get("month", "")
    day = enriched.get("day", "")
    if year and month and day:
        enriched["birth_date"] = f"{int(day):02d}/{int(month):02d}/{year}"
    
    hour = enriched.get("hour", "")
    minute = enriched.get("minute", "")
    if hour != "" and minute != "":
        enriched["birth_time"] = f"{int(hour):02d}:{int(minute):02d}"
        
    city = enriched.get("city", "")
    if city:
        enriched["birth_location"] = city

    # On ajoute natal_positions pour l'interprétation immédiate
    # ATTENTION: à supprimer avant session storage pour limiter la taille du cookie (max 4KB)
    enriched["natal_positions"] = natal

    return enriched


def _fulfill_order(pseudo: str, plan: str, stripe_customer_id: str = ""):
    """Mise à jour du plan utilisateur après paiement Stripe réussi."""
    try:
        from profiles import upgrade_plan
        ok = upgrade_plan(pseudo, plan, stripe_customer_id=stripe_customer_id)
        if not ok:
            import logging
            logging.getLogger("app").warning("upgrade_plan a retourné False pour %s (utilisateur non trouvé dans le sheet)", pseudo)
    except Exception as e:
        import logging
        logging.getLogger("app").error("Erreur fulfill_order pour %s : %s", pseudo, e)


def get_hook_cta() -> dict:
    """
    Génère la CTA (Call-To-Action) qui accompagne le hook gratuit.
    Injectée à la fin du stream SSE pour créer tension → conversion.
    Retourne les deux langues pour que le JS choisisse selon document.lang.
    """
    MYPOS_URL = os.environ.get("MYPOS_URL", "https://mypos.com/@karmic-gochara")
    return {
        "text_fr": "Ce Daily Reading n'est qu'un fragment. Ton Alternative de Conscience complète, les 5 piliers et ta Carte Karmique révèlent ce qui se joue vraiment.",
        "button_fr": "Voir l'analyse complète",
        "text_en": "This Daily Reading is just a fragment. Your full Alternative of Consciousness, all 5 pillars and your Karmic Map reveal what's truly at play.",
        "button_en": "Get the full analysis",
        "url": MYPOS_URL,
    }
