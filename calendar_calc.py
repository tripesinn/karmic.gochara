"""
calendar_calc.py — Calendrier mensuel des transits importants
Gochara Karmique

Pour chaque jour du mois, détecte les conjonctions actives (orbe < 3°)
entre planètes lentes en transit et points natals clés (3 piliers + Soleil/Lune).
"""

import calendar as _calendar

from astro_calc import ORB, _calc_positions, get_julian_day
from transit_alerts import NATAL_LABELS, PLANET_LABELS, SLOW_PLANETS, TARGET_NATAL, _add_south_node

# Couleur par planète (pour le frontend)
PLANET_COLORS = {
    "Jupiter ♃":   "#c9a84c",   # or
    "Saturne ♄":   "#8888bb",   # violet-gris
    "Uranus ♅":    "#6ab5c0",   # turquoise
    "Neptune ♆":   "#6a80c0",   # bleu
    "Pluton ♇":    "#c06080",   # rouge sombre
    "Chiron ⚷":    "#d4a017",   # ambre
    "Nœud Nord ☊": "#b06030",   # rouille (Rahu)
    "Nœud Sud ☋":  "#707090",   # gris (Ketu)
}

# Couleur par point natal (pour le frontend)
NATAL_COLORS = {
    "Nœud Sud ☋":  "#c9a84c",   # Ketu — ROM — or
    "Chiron ⚷":    "#c090e0",   # RAM — violet
    "Nœud Nord ☊": "#e07050",   # Stage — rouille
    "Soleil ☀":    "#f0c040",   # jaune soleil
    "Lune ☽":      "#a0c0e0",   # blanc-bleu lune
}


def _natal_positions(profile: dict) -> dict:
    natal_jd = get_julian_day(
        profile["year"], profile["month"], profile["day"],
        profile["hour"], profile["minute"], profile["tz"],
    )
    nat_lat = float(profile["lat"])
    nat_lon = float(profile["lon"])
    return _add_south_node(_calc_positions(natal_jd, nat_lat, nat_lon))


def _transit_positions_for_day(profile: dict, year: int, month: int, day: int) -> dict:
    transit_jd = get_julian_day(
        year, month, day, 12, 0,
        profile.get("transit_tz") or profile["tz"],
    )
    tr_lat = float(profile.get("transit_lat") or profile["lat"])
    tr_lon = float(profile.get("transit_lon") or profile["lon"])
    return _add_south_node(_calc_positions(transit_jd, tr_lat, tr_lon))


def _day_conjunctions(natal_pos: dict, transit_pos: dict) -> list[dict]:
    """Retourne les conjonctions actives pour un jour, avec orbe et couleurs."""
    found = []
    for t_name, t_data in transit_pos.items():
        if t_data is None or t_name not in SLOW_PLANETS:
            continue
        t_lon = t_data["lon"]
        for n_name, n_data in natal_pos.items():
            if n_data is None or n_name not in TARGET_NATAL:
                continue
            n_lon = n_data["lon"]
            diff  = abs(t_lon - n_lon) % 360
            if diff > 180:
                diff = 360 - diff
            if diff <= ORB:
                found.append({
                    "transit":        t_name,
                    "transit_label":  PLANET_LABELS.get(t_name, t_name),
                    "transit_color":  PLANET_COLORS.get(t_name, "#c9a84c"),
                    "natal":          n_name,
                    "natal_label":    NATAL_LABELS.get(n_name, n_name),
                    "natal_color":    NATAL_COLORS.get(n_name, "#c090e0"),
                    "orb":            round(diff, 2),
                    "retrograde":     t_data.get("retrograde", False),
                })
    found.sort(key=lambda x: x["orb"])
    return found


def get_monthly_transits(profile: dict, year: int, month: int) -> dict:
    """
    Calcule les transits importants pour chaque jour du mois.
    Retourne un dict { "YYYY-MM-DD": [ {transit, natal, orb, ...}, ... ] }
    Seuls les jours avec au moins un transit actif sont inclus.
    """
    days_in_month = _calendar.monthrange(year, month)[1]
    natal_pos     = _natal_positions(profile)

    result = {}
    for day in range(1, days_in_month + 1):
        transit_pos  = _transit_positions_for_day(profile, year, month, day)
        conjunctions = _day_conjunctions(natal_pos, transit_pos)
        if conjunctions:
            key = f"{year}-{month:02d}-{day:02d}"
            result[key] = conjunctions

    return result
