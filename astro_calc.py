"""
astro_calc.py — Moteur de calcul astrologique sidéral
Gochara Karmique

Ayanamsa  : Centre Galactique Djwhal Khul
Maisons   : Moonrise Chart (Chandra Lagna — ASC = début du signe de la Lune natale)
Nœuds     : Vrais (True Node)
Lilith    : Vraie (Osculating Apogee)
Orbe      : < 3°
"""

import swisseph as swe
from datetime import datetime
import pytz

# ── Ayanamsa Centre Galactique DK ───────────────────────────────────────────
DK_T0_JD   = 2442351.809028   # JD du 31/10/1974 07h25 UTC
DK_AYAN_T0 = 28.0             # 28°00′ — Centre Galactique DK


def _set_ayanamsa():
    swe.set_sid_mode(swe.SIDM_USER, DK_T0_JD, DK_AYAN_T0)


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

ASPECTS = {
    "Conjonction ☌":  0,
    "Opposition ☍":   180,
    "Trigone △":      120,
    "Carré □":        90,
    "Sextile ✶":      60,
}

ORB = 3.0

SIGNS = [
    "Bélier", "Taureau", "Gémeaux", "Cancer",
    "Lion", "Vierge", "Balance", "Scorpion",
    "Sagittaire", "Capricorne", "Verseau", "Poissons",
]

SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# ── Nakshatras (27 × 13°20′) ─────────────────────────────────────────────────
NAKSHATRAS = [
    "Ashwini",      # 0°00′ – 13°20′ Bélier
    "Bharani",      # 13°20′ – 26°40′ Bélier
    "Krittika",     # 26°40′ Bélier – 10°00′ Taureau
    "Rohini",       # 10°00′ – 23°20′ Taureau
    "Mrigashira",   # 23°20′ Taureau – 6°40′ Gémeaux
    "Ardra",        # 6°40′ – 20°00′ Gémeaux
    "Punarvasu",    # 20°00′ Gémeaux – 3°20′ Cancer
    "Pushya",       # 3°20′ – 16°40′ Cancer
    "Ashlesha",     # 16°40′ – 30°00′ Cancer
    "Magha",        # 0°00′ – 13°20′ Lion
    "Purva Phalguni",  # 13°20′ – 26°40′ Lion
    "Uttara Phalguni", # 26°40′ Lion – 10°00′ Vierge
    "Hasta",        # 10°00′ – 23°20′ Vierge
    "Chitra",       # 23°20′ Vierge – 6°40′ Balance
    "Swati",        # 6°40′ – 20°00′ Balance
    "Vishakha",     # 20°00′ Balance – 3°20′ Scorpion
    "Anuradha",     # 3°20′ – 16°40′ Scorpion
    "Jyeshtha",     # 16°40′ – 30°00′ Scorpion
    "Mula",         # 0°00′ – 13°20′ Sagittaire
    "Purva Ashadha",   # 13°20′ – 26°40′ Sagittaire
    "Uttara Ashadha",  # 26°40′ Sagittaire – 10°00′ Capricorne
    "Shravana",     # 10°00′ – 23°20′ Capricorne
    "Dhanishtha",   # 23°20′ Capricorne – 6°40′ Verseau
    "Shatabhisha",  # 6°40′ – 20°00′ Verseau
    "Purva Bhadrapada", # 20°00′ Verseau – 3°20′ Poissons
    "Uttara Bhadrapada",# 3°20′ – 16°40′ Poissons
    "Revati",       # 16°40′ – 30°00′ Poissons
]

# Régents planétaires des nakshatras (séquence Vimshotari)
NAKSHATRA_LORDS = [
    "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter",
    "Saturne", "Mercure",  # 1-9
    "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter",
    "Saturne", "Mercure",  # 10-18
    "Ketu", "Vénus", "Soleil", "Lune", "Mars", "Rahu", "Jupiter",
    "Saturne", "Mercure",  # 19-27
]


def lon_to_nakshatra(lon: float) -> dict:
    """
    Calcule le nakshatra, le pada (1-4) et le régent pour une longitude sidérale.
    Chaque nakshatra = 13°20′ = 13.333...°
    Chaque pada = 3°20′ = 3.333...°
    """
    lon = lon % 360
    nak_size = 360.0 / 27.0          # 13.3333°
    pada_size = nak_size / 4.0       # 3.3333°

    nak_idx  = int(lon / nak_size)
    pada_idx = int((lon % nak_size) / pada_size) + 1  # 1 à 4
    deg_in_nak = lon - (nak_idx * nak_size)

    return {
        "nakshatra": NAKSHATRAS[nak_idx],
        "pada":      pada_idx,
        "lord":      NAKSHATRA_LORDS[nak_idx],
        "deg_in_nak": round(deg_in_nak, 2),
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


# ── Portes Visible / Invisible (Castanier) ──────────────────────────────────

def calc_portes(saturn_lon: float, uranus_lon: float) -> dict:
    """
    Calcule la Porte Visible (PV) et la Porte Invisible (PI).
    PV = mi-point du PETIT ARC Saturne→Uranus.
    PI = PV + 180° (mod 360).
    Source : Catherine Castanier, Chiron et l'axe des Portes, pp. 26-27.
    """
    diff = (uranus_lon - saturn_lon) % 360

    if diff <= 180:
        # Uranus est "devant" Saturne dans le sens direct — petit arc
        midpoint = (saturn_lon + diff / 2.0) % 360
    else:
        # Le petit arc est dans l'autre sens
        diff_inv = 360 - diff
        midpoint = (saturn_lon - diff_inv / 2.0) % 360

    pv = midpoint % 360
    pi = (pv + 180.0) % 360

    nak_pv = lon_to_nakshatra(pv)
    nak_pi = lon_to_nakshatra(pi)

    return {
        "porte_visible": {
            "lon":        pv,
            "lon_raw":    pv,
            "display":    lon_to_display(pv),
            "nakshatra":  nak_pv["nakshatra"],
            "pada":       nak_pv["pada"],
            "lord":       nak_pv["lord"],
            "deg_in_nak": nak_pv["deg_in_nak"],
        },
        "porte_invisible": {
            "lon":        pi,
            "lon_raw":    pi,
            "display":    lon_to_display(pi),
            "nakshatra":  nak_pi["nakshatra"],
            "pada":       nak_pi["pada"],
            "lord":       nak_pi["lord"],
            "deg_in_nak": nak_pi["deg_in_nak"],
        },
    }


def _calc_positions(jd: float, lat: float, lon: float) -> dict:
    _set_ayanamsa()
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

    positions = {}

    for name, pid in PLANETS.items():
        try:
            result, _ = swe.calc_ut(jd, pid, flags)
            planet_lon = result[0] % 360
            speed = result[3]
            nak_data = lon_to_nakshatra(planet_lon)
            positions[name] = {
                "lon":        planet_lon,
                "lon_raw":    planet_lon,
                "speed":      speed,
                "retrograde": speed < 0,
                "display":    lon_to_display(planet_lon),
                "nakshatra":  nak_data["nakshatra"],
                "pada":       nak_data["pada"],
                "nak_lord":   nak_data["lord"],
            }
        except Exception:
            positions[name] = None

    # ── Nœud Sud ─────────────────────────────────────────────────────────────
    nn = positions.get("Nœud Nord ☊")
    if nn:
        ks_lon = (nn["lon"] + 180) % 360
        nak_data = lon_to_nakshatra(ks_lon)
        positions["Nœud Sud ☋"] = {
            "lon":        ks_lon,
            "lon_raw":    ks_lon,
            "speed":      0,
            "retrograde": False,
            "display":    lon_to_display(ks_lon),
            "nakshatra":  nak_data["nakshatra"],
            "pada":       nak_data["pada"],
            "nak_lord":   nak_data["lord"],
        }

    # ── Moonrise Chart : ASC = début du signe de la Lune ─────────────────────
    moon = positions.get("Lune ☽")
    if moon:
        moon_sign_start = int(moon["lon"] / 30) * 30.0
        nak_data = lon_to_nakshatra(moon_sign_start)
        positions["ASC ↑"] = {
            "lon":        moon_sign_start,
            "lon_raw":    moon_sign_start,
            "speed":      0,
            "retrograde": False,
            "display":    lon_to_display(moon_sign_start),
            "nakshatra":  nak_data["nakshatra"],
            "pada":       nak_data["pada"],
            "nak_lord":   nak_data["lord"],
        }

    # ── MC ───────────────────────────────────────────────────────────────────
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
        mc_lon = ascmc[1] % 360
        nak_data = lon_to_nakshatra(mc_lon)
        positions["MC ↑"] = {
            "lon":        mc_lon,
            "lon_raw":    mc_lon,
            "speed":      0,
            "retrograde": False,
            "display":    lon_to_display(mc_lon),
            "nakshatra":  nak_data["nakshatra"],
            "pada":       nak_data["pada"],
            "nak_lord":   nak_data["lord"],
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

    natal_pos   = _calc_positions(natal_jd,    natal["lat"],        natal["lon"])
    transit_pos = _calc_positions(transit_jd, transit_loc["lat"], transit_loc["lon"])

    # ── Portes natales ────────────────────────────────────────────────────────
    sat_natal = natal_pos.get("Saturne ♄")
    ura_natal = natal_pos.get("Uranus ♅")
    if sat_natal and ura_natal:
        portes_natal = calc_portes(sat_natal["lon"], ura_natal["lon"])
        natal_pos["Porte Visible ⊙"] = {
            **portes_natal["porte_visible"],
            "speed":      0,
            "retrograde": False,
            "nak_lord":   portes_natal["porte_visible"].get("lord", ""),
        }
        natal_pos["Porte Invisible ⊗"] = {
            **portes_natal["porte_invisible"],
            "speed":      0,
            "retrograde": False,
            "nak_lord":   portes_natal["porte_invisible"].get("lord", ""),
        }

    # ── Portes de transit ─────────────────────────────────────────────────────
    sat_transit = transit_pos.get("Saturne ♄")
    ura_transit = transit_pos.get("Uranus ♅")
    if sat_transit and ura_transit:
        portes_transit = calc_portes(sat_transit["lon"], ura_transit["lon"])
        transit_pos["Porte Visible ⊙"] = {
            **portes_transit["porte_visible"],
            "speed":      0,
            "retrograde": False,
            "nak_lord":   portes_transit["porte_visible"].get("lord", ""),
        }
        transit_pos["Porte Invisible ⊗"] = {
            **portes_transit["porte_invisible"],
            "speed":      0,
            "retrograde": False,
            "nak_lord":   portes_transit["porte_invisible"].get("lord", ""),
        }

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
                        "transit_nak":     t_data.get("nakshatra", ""),
                        "transit_pada":    t_data.get("pada", ""),
                        "natal_planet":    n_name,
                        "natal_display":   n_data["display"],
                        "natal_nak":       n_data.get("nakshatra", ""),
                        "aspect":          asp_name,
                        "orb":             round(orb_actual, 2),
                        "retrograde":      t_data["retrograde"],
                    })

    aspects.sort(key=lambda x: x["orb"])

    def _display_dict(pos_dict):
        result = {}
        for k, v in pos_dict.items():
            if v is not None:
                result[k] = {
                    "display":    v["display"],
                    "retrograde": v["retrograde"],
                    "nakshatra":  v.get("nakshatra", ""),
                    "pada":       v.get("pada", ""),
                    "nak_lord":   v.get("nak_lord", ""),
                    "lon_raw":    v.get("lon_raw", v.get("lon", 0)),
                }
        return result

    return {
        "aspects":       aspects,
        "natal":         _display_dict(natal_pos),
        "transits":      _display_dict(transit_pos),
        "transit_date":  f"{day:02d}/{month:02d}/{year}",
        "transit_time":  f"{hour:02d}h{minute:02d}",
    }