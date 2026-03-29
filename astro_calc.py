"""
astro_calc.py — Moteur de calcul astrologique sidéral
Gochara Karmique

Ayanamsa  : Djwhal Khul (SE_SIDM_DJWHAL_KHUL = 6)
Maisons   : Moonrise Chart (Chandra Lagna — ASC = début du signe de la Lune natale)
Nœuds     : Vrais (True Node)
Lilith    : Vraie (Osculating Apogee)
Orbe      : < 3°
"""

import swisseph as swe
from datetime import datetime
import pytz

# ── Ayanamsa ────────────────────────────────────────────────────────────────
DJWHAL_KHUL = getattr(swe, "SIDM_DJWHAL_KHUL", 6)

# ── Planètes ─────────────────────────────────────────────────────────────────
PLANETS = {
    "Soleil ☀":      swe.SUN,
    "Lune ☽":        swe.MOON,
    "Mercure ☿":     swe.MERCURY,
    "Vénus ♀":       swe.VENUS,
    "Mars ♂":        swe.MARS,
    "Jupiter ♃":     swe.JUPITER,
    "Saturne ♄":     swe.SATURN,
    "Uranus ♅":      swe.URANUS,
    "Neptune ♆":     swe.NEPTUNE,
    "Pluton ♇":      swe.PLUTO,
    "Chiron ⚷":      swe.CHIRON,
    "Nœud Nord ☊":   swe.TRUE_NODE,
    "Lilith ⚸":      swe.OSCU_APOG,
}

# ── Aspects ───────────────────────────────────────────────────────────────────
ASPECTS = {
    "Conjonction ☌":  0,
    "Opposition ☍":   180,
    "Trigone △":      120,
    "Carré □":        90,
    "Sextile ✶":      60,
}

ORB = 3.0

# ── Signes ────────────────────────────────────────────────────────────────────
SIGNS = [
    "Bélier", "Taureau", "Gémeaux", "Cancer",
    "Lion", "Vierge", "Balance", "Scorpion",
    "Sagittaire", "Capricorne", "Verseau", "Poissons",
]

SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# ── Planètes clés pour la carte karmique siderealAstro13 ─────────────────────
KARMIC_PLANETS = {
    "Nœud Nord ☊",
    "Nœud Sud ☋",
    "Chiron ⚷",
    "Lilith ⚸",
    "Saturne ♄",
    "Uranus ♅",
    "Soleil ☀",
    "Lune ☽",
    "Mars ♂",
    "Jupiter ♃",
    "Vénus ♀",
    "Mercure ☿",
    "ASC ↑",
    "MC ↑",
}


def lon_to_display(lon: float) -> str:
    lon = lon % 360
    idx = int(lon / 30)
    deg = int(lon % 30)
    minutes = int(((lon % 30) % 1) * 60)
    return f"{SIGN_SYMBOLS[idx]} {SIGNS[idx]} {deg}°{minutes:02d}′"


def get_julian_day(year, month, day, hour, minute, tz_str: str) -> float:
    tz = pytz.timezone(tz_str)
    dt_local = tz.localize(datetime(year, month, day, hour, minute, 0))
    dt_utc = dt_local.astimezone(pytz.utc)
    return swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def _calc_positions(jd: float, lat: float, lon: float) -> dict:
    swe.set_sid_mode(DJWHAL_KHUL)
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

    positions = {}

    for name, pid in PLANETS.items():
        try:
            result, _ = swe.calc_ut(jd, pid, flags)
            planet_lon = result[0] % 360
            speed = result[3]
            positions[name] = {
                "lon": planet_lon,
                "speed": speed,
                "retrograde": speed < 0,
                "display": lon_to_display(planet_lon),
            }
        except Exception:
            positions[name] = None

    # Nœud Sud
    nn = positions.get("Nœud Nord ☊")
    if nn:
        ks_lon = (nn["lon"] + 180) % 360
        positions["Nœud Sud ☋"] = {
            "lon": ks_lon,
            "speed": 0,
            "retrograde": False,
            "display": lon_to_display(ks_lon),
        }

    # Moonrise Chart (Chandra Lagna)
    moon = positions.get("Lune ☽")
    if moon:
        moon_sign_start = int(moon["lon"] / 30) * 30.0
        positions["ASC ↑"] = {
            "lon": moon_sign_start,
            "speed": 0,
            "retrograde": False,
            "display": lon_to_display(moon_sign_start),
        }

    # MC
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
        mc_lon = ascmc[1] % 360
        positions["MC ↑"] = {
            "lon": mc_lon,
            "speed": 0,
            "retrograde": False,
            "display": lon_to_display(mc_lon),
        }
    except Exception:
        pass

    return positions


def calculate_transits(natal: dict, transit_loc: dict,
                       year: int, month: int, day: int,
                       hour: int, minute: int) -> dict:
    natal_jd = get_julian_day(
        natal["year"], natal["month"], natal["day"],
        natal["hour"], natal["minute"], natal["tz"],
    )
    transit_jd = get_julian_day(year, month, day, hour, minute, transit_loc["tz"])

    natal_pos  = _calc_positions(natal_jd,  natal["lat"],        natal["lon"])
    transit_pos = _calc_positions(transit_jd, transit_loc["lat"], transit_loc["lon"])

    aspects = []
    skip_transit = {"Nœud Sud ☋"}

    for t_name, t_data in transit_pos.items():
        if t_data is None or t_name in skip_transit:
            continue
        t_lon = t_data["lon"]

        for n_name, n_data in natal_pos.items():
            if n_data is None:
                continue
            n_lon = n_data["lon"]

            diff = abs(t_lon - n_lon) % 360
            if diff > 180:
                diff = 360 - diff

            for asp_name, asp_angle in ASPECTS.items():
                orb_actual = abs(diff - asp_angle)
                if orb_actual <= ORB:
                    aspects.append({
                        "transit_planet":  t_name,
                        "transit_display": t_data["display"],
                        "natal_planet":    n_name,
                        "natal_display":   n_data["display"],
                        "aspect":          asp_name,
                        "orb":             round(orb_actual, 2),
                        "retrograde":      t_data["retrograde"],
                    })

    aspects.sort(key=lambda x: x["orb"])

    # ── dict d'affichage (inclut lon brute pour le rendu SVG) ────────────────
    def _display_dict(pos_dict):
        return {
            k: {
                "display":    v["display"],
                "retrograde": v["retrograde"],
                "lon":        round(v["lon"], 4),   # ← lon brute pour SVG
            }
            for k, v in pos_dict.items() if v is not None
        }

    return {
        "aspects":       aspects,
        "natal":         _display_dict(natal_pos),
        "transits":      _display_dict(transit_pos),
        "transit_date":  f"{day:02d}/{month:02d}/{year}",
        "transit_time":  f"{hour:02d}h{minute:02d}",
    }
