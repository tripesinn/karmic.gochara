"""
transit_alerts.py — Détection et envoi des alertes de transit important
Gochara Karmique

Logique :
  - Planètes lentes en transit : Jupiter, Saturne, Uranus, Neptune, Pluton, Chiron, Nœuds
  - Points natals cibles : Ketu (Nœud Sud), Chiron, Rahu (Nœud Nord), Soleil, Lune
  - Aspect : Conjonction (orbe < 3°)
  - Alerte si un transit entre ou sort de l'orbe entre J-1 et aujourd'hui
"""

import os
from datetime import date, timedelta
from urllib.parse import quote

import requests as req

from astro_calc import NAKSHATRA_LORDS, NAKSHATRAS, ORB, _calc_positions, get_julian_day

# Planètes lentes en transit — celles qui déclenchent des alertes
SLOW_PLANETS = {
    "Jupiter ♃", "Saturne ♄", "Uranus ♅", "Neptune ♆", "Pluton ♇",
    "Chiron ⚷", "Nœud Nord ☊", "Nœud Sud ☋",
}

# Points natals surveillés
TARGET_NATAL = {
    "Nœud Sud ☋",   # Ketu — ROM — Mémoire karmique
    "Chiron ⚷",     # RAM — Porte Invisible
    "Nœud Nord ☊",  # Rahu — Stage
    "Soleil ☀",
    "Lune ☽",
}

# Labels lisibles pour l'email
PLANET_LABELS = {
    "Jupiter ♃":   "Jupiter",
    "Saturne ♄":   "Saturne",
    "Uranus ♅":    "Uranus",
    "Neptune ♆":   "Neptune",
    "Pluton ♇":    "Pluton",
    "Chiron ⚷":    "Chiron",
    "Nœud Nord ☊": "Rahu (Nœud Nord)",
    "Nœud Sud ☋":  "Ketu (Nœud Sud)",
}

NATAL_LABELS = {
    "Nœud Sud ☋":  "ton Ketu natal (Mémoire karmique)",
    "Chiron ⚷":    "ton Chiron natal (Porte Invisible)",
    "Nœud Nord ☊": "ton Rahu natal (Stage / Dharma)",
    "Soleil ☀":    "ton Soleil natal",
    "Lune ☽":      "ta Lune natale",
}


NAK_SIZE = 360.0 / 27.0  # 13.333°

# Régime doctrinal par point natal
# Ketu = ROM (Mémoire karmique) → activation oppressive : test, friction, répétition
# Rahu = Dharma (Direction d'évolution) → activation amplifiante : opportunité, expansion
# Chiron = Porte Invisible (Blessure-seuil) → activation de transformation
_NAK_INTERPRETATION = {
    "Ketu":   "ROM_oppression",
    "Rahu":   "Dharma_amplification",
    "Chiron": "Blessure_activation",
}

# Labels email pour les nakshatras natals
NAK_NATAL_LABELS = {
    "Ketu":   "nakshatra de ton Ketu natal",
    "Rahu":   "nakshatra de ton Rahu natal",
    "Chiron": "nakshatra de ton Chiron natal",
}

# Couleurs email selon le régime doctrinal
_INTERPRETATION_COLORS = {
    "ROM_oppression":      "#e57373",  # rouge-brique — friction karmique
    "Dharma_amplification": "#6ab56a", # vert doré — expansion
    "Blessure_activation": "#b07ecf",  # violet Chiron — seuil
}

# Libellés interprétatifs dans l'email
_INTERPRETATION_LABELS = {
    "ROM_oppression":       "Activation ROM — test karmique",
    "Dharma_amplification": "Activation Dharma — opportunité",
    "Blessure_activation":  "Activation Chiron — seuil de transformation",
}


# Régime doctrinal intrinsèque de chaque nakshatra (source : 07_nakshatra_keywords.md)
NAKSHATRA_REGIME = {
    "Ashwini":             "ROM_oppression",
    "Bharani":             "Dharma_amplification",
    "Krittika":            "Blessure_activation",
    "Rohini":              "Dharma_amplification",
    "Mrigashira":          "ROM_oppression",
    "Ardra":               "Blessure_activation",
    "Punarvasu":           "Dharma_amplification",
    "Pushya":              "ROM_oppression",
    "Ashlesha":            "Blessure_activation",
    "Magha":               "ROM_oppression",
    "Purva Phalguni":      "Dharma_amplification",
    "Uttara Phalguni":     "Blessure_activation",
    "Hasta":               "Dharma_amplification",
    "Chitra":              "ROM_oppression",
    "Swati":               "Dharma_amplification",
    "Vishakha":            "Dharma_amplification",
    "Anuradha":            "ROM_oppression",
    "Jyeshtha":            "Blessure_activation",
    "Mula":                "ROM_oppression",
    "Purva Ashadha":       "Dharma_amplification",
    "Uttara Ashadha":      "Blessure_activation",
    "Shravana":            "Dharma_amplification",
    "Dhanishtha":          "ROM_oppression",
    "Shatabhisha":         "Dharma_amplification",
    "Purva Bhadrapada":    "Dharma_amplification",
    "Uttara Bhadrapada":   "ROM_oppression",
    "Revati":              "Blessure_activation",
}


def detect_global_nak_transits(target_date: date = None) -> list[dict]:
    """
    Détecte les planètes lentes qui entrent dans un nouveau nakshatra aujourd'hui.
    Sans profil natal — météo astrologique globale.

    Retourne une liste d'événements :
    [
        {
            "transit":      "Saturne ♄",
            "nakshatra":    "Mula",
            "lord":         "Ketu",
            "regime":       "ROM_oppression",
            "regime_label": "Activation ROM — test karmique",
        },
        ...
    ]
    """
    from astro_calc import lon_to_nakshatra

    if target_date is None:
        target_date = date.today()
    yesterday = target_date - timedelta(days=1)

    # Lieu arbitraire (les planètes lentes sont indépendantes du lieu)
    ref_lat, ref_lon, ref_tz = 48.8566, 2.3522, "Europe/Paris"

    jd_today = get_julian_day(
        target_date.year, target_date.month, target_date.day, 12, 0, ref_tz
    )
    jd_yest = get_julian_day(
        yesterday.year, yesterday.month, yesterday.day, 12, 0, ref_tz
    )

    pos_today = _add_south_node(_calc_positions(jd_today, ref_lat, ref_lon))
    pos_yest  = _add_south_node(_calc_positions(jd_yest,  ref_lat, ref_lon))

    _regime_labels = {
        "ROM_oppression":       "Activation ROM — test karmique",
        "Dharma_amplification": "Activation Dharma — opportunité",
        "Blessure_activation":  "Activation Chiron — seuil de transformation",
    }

    events = []
    for planet in SLOW_PLANETS:
        t_data = pos_today.get(planet)
        y_data = pos_yest.get(planet)
        if t_data is None or y_data is None:
            continue
        nak_today = lon_to_nakshatra(t_data["lon"])["nakshatra"]
        nak_yest  = lon_to_nakshatra(y_data["lon"])["nakshatra"]
        if nak_today != nak_yest:
            regime = NAKSHATRA_REGIME.get(nak_today, "neutre")
            try:
                lord = NAKSHATRA_LORDS[NAKSHATRAS.index(nak_today)]
            except (ValueError, IndexError):
                lord = ""
            events.append({
                "transit":      planet,
                "nakshatra":    nak_today,
                "lord":         lord,
                "regime":       regime,
                "regime_label": _regime_labels.get(regime, "Activation nakshatra"),
            })

    return events


def _nak_lon_range(nak_name: str) -> tuple[float, float] | None:
    """Retourne (start_lon, end_lon) pour un nakshatra donné."""
    try:
        idx = NAKSHATRAS.index(nak_name)
    except ValueError:
        return None
    start = idx * NAK_SIZE
    return start, start + NAK_SIZE


def _active_nak_activations(natal_naks: dict, transit_pos: dict) -> dict[tuple, dict]:
    """
    Détecte les planètes lentes dans le nakshatra natal de Ketu/Rahu/Chiron.
    natal_naks : {"Ketu": "Mula", "Rahu": "Swati", "Chiron": "Ashwini"}

    Retourne : {(transit_planet_name, natal_point_key): enriched_dict}
    enriched_dict = {
        "nakshatra":      str,   # ex. "Mula"
        "lord":           str,   # ex. "Ketu"  (régent Vimshotari)
        "interpretation": str,   # "ROM_oppression" | "Dharma_amplification" | "Blessure_activation"
    }
    """
    active = {}
    for point_key, nak_name in natal_naks.items():
        if not nak_name:
            continue
        rng = _nak_lon_range(nak_name)
        if not rng:
            continue
        start, end = rng
        try:
            nak_idx = NAKSHATRAS.index(nak_name)
            lord = NAKSHATRA_LORDS[nak_idx]
        except (ValueError, IndexError):
            lord = ""
        interp = _NAK_INTERPRETATION.get(point_key, "neutre")
        for t_name, t_data in transit_pos.items():
            if t_data is None or t_name not in SLOW_PLANETS:
                continue
            t_lon = t_data["lon"] % 360
            if end <= 360:
                in_range = start <= t_lon < end
            else:
                in_range = t_lon >= start or t_lon < end % 360
            if in_range:
                active[(t_name, point_key)] = {
                    "nakshatra":      nak_name,
                    "lord":           lord,
                    "interpretation": interp,
                }
    return active


def _add_south_node(positions: dict) -> dict:
    """Ajoute Nœud Sud si Nœud Nord présent."""
    nn = positions.get("Nœud Nord ☊")
    if nn:
        ks_lon = (nn["lon"] + 180) % 360
        positions["Nœud Sud ☋"] = {
            "lon": ks_lon,
            "speed": 0,
            "retrograde": False,
        }
    return positions


def _active_conjunctions(natal_pos: dict, transit_pos: dict) -> set[tuple]:
    """Retourne l'ensemble des paires (transit_planet, natal_point) en conjonction < 3°."""
    active = set()
    for t_name, t_data in transit_pos.items():
        if t_data is None or t_name not in SLOW_PLANETS:
            continue
        t_lon = t_data["lon"]
        for n_name, n_data in natal_pos.items():
            if n_data is None or n_name not in TARGET_NATAL:
                continue
            n_lon = n_data["lon"]
            diff = abs(t_lon - n_lon) % 360
            if diff > 180:
                diff = 360 - diff
            if diff <= ORB:
                active.add((t_name, n_name))
    return active


def _positions_for_day(profile: dict, target_date: date) -> tuple[dict, dict]:
    """Calcule positions natales et de transit (à midi) pour une date donnée."""
    natal_jd = get_julian_day(
        profile["year"], profile["month"], profile["day"],
        profile["hour"], profile["minute"], profile["tz"],
    )
    transit_jd = get_julian_day(
        target_date.year, target_date.month, target_date.day,
        12, 0, profile.get("transit_tz") or profile["tz"],
    )
    nat_lat = float(profile["lat"])
    nat_lon = float(profile["lon"])
    tr_lat  = float(profile.get("transit_lat") or profile["lat"])
    tr_lon  = float(profile.get("transit_lon") or profile["lon"])

    natal_pos   = _add_south_node(_calc_positions(natal_jd,   nat_lat, nat_lon))
    transit_pos = _add_south_node(_calc_positions(transit_jd, tr_lat,  tr_lon))
    return natal_pos, transit_pos


def detect_transit_events(profile: dict) -> list[dict]:
    """
    Compare les conjonctions importantes d'hier et d'aujourd'hui.
    Retourne les transits qui commencent ou se terminent aujourd'hui.
    """
    today     = date.today()
    yesterday = today - timedelta(days=1)

    natal_pos, today_transit    = _positions_for_day(profile, today)
    _,         yesterday_transit = _positions_for_day(profile, yesterday)

    today_active     = _active_conjunctions(natal_pos, today_transit)
    yesterday_active = _active_conjunctions(natal_pos, yesterday_transit)

    events = []
    for pair in today_active - yesterday_active:
        events.append({"type": "debut", "kind": "conjunction", "transit": pair[0], "natal": pair[1]})
    for pair in yesterday_active - today_active:
        events.append({"type": "fin", "kind": "conjunction", "transit": pair[0], "natal": pair[1]})

    # --- Détection des événements de lunaison (Nouvelle/Pleine Lune) ---
    lunation_events = detect_lunation_events(profile, natal_pos, today_transit)
    if lunation_events:
        events.extend(lunation_events)

    # Activations nakshatra : planète lente entre dans le nakshatra natal de Ketu/Rahu/Chiron
    natal_naks = {
        "Ketu":   profile.get("ketu_nakshatra", ""),
        "Rahu":   profile.get("rahu_nakshatra", ""),
        "Chiron": profile.get("chiron_nakshatra", ""),
    }
    today_naks     = _active_nak_activations(natal_naks, today_transit)
    yesterday_naks = _active_nak_activations(natal_naks, yesterday_transit)

    for key in set(today_naks) - set(yesterday_naks):
        t_name, point_key = key
        info = today_naks[key]
        events.append({
            "type": "debut", "kind": "nakshatra",
            "transit": t_name, "natal": point_key,
            "nakshatra": info["nakshatra"],
            "lord": info["lord"],
            "interpretation": info["interpretation"],
        })
    for key in set(yesterday_naks) - set(today_naks):
        t_name, point_key = key
        info = yesterday_naks[key]
        events.append({
            "type": "fin", "kind": "nakshatra",
            "transit": t_name, "natal": point_key,
            "nakshatra": info["nakshatra"],
            "lord": info["lord"],
            "interpretation": info["interpretation"],
        })

    return events


def detect_lunation_events(profile: dict, natal_pos: dict, transit_pos: dict) -> list[dict]:
    """
    Détecte si une Nouvelle ou Pleine Lune a lieu aujourd'hui
    dans le nakshatra de la Lune natale de l'utilisateur.
    """
    from astro_calc import lon_to_nakshatra
    moon_natal = natal_pos.get("Lune ☽")
    if not moon_natal:
        return []

    sun_transit = transit_pos.get("Soleil ☀")
    moon_transit = transit_pos.get("Lune ☽")
    if not sun_transit or not moon_transit:
        return []

    sun_lon = sun_transit["lon"]
    moon_lon = moon_transit["lon"]
    natal_moon_nak = moon_natal.get("nakshatra")
    if not natal_moon_nak:
        return []

    events = []
    # Vérifie Nouvelle Lune (conjonction)
    diff_conj = abs(sun_lon - moon_lon) % 360
    if diff_conj > 180:
        diff_conj = 360 - diff_conj
    
    if diff_conj <= ORB:
        lunation_nak = lon_to_nakshatra(moon_lon)["nakshatra"]
        if lunation_nak == natal_moon_nak:
            events.append({
                "type": "debut", "kind": "lunation",
                "transit": "Nouvelle Lune 🌑", "natal": "Lune ☽",
                "nakshatra": lunation_nak, "lord": NAKSHATRA_LORDS[NAKSHATRAS.index(lunation_nak)],
                "interpretation": "Nouvelle Lune dans votre Nakshatra lunaire natal",
            })

    # Vérifie Pleine Lune (opposition)
    diff_opp = abs(sun_lon - moon_lon - 180) % 360
    if diff_opp > 180:
        diff_opp = 360 - diff_opp

    if diff_opp <= ORB:
        lunation_nak = lon_to_nakshatra(moon_lon)["nakshatra"]
        if lunation_nak == natal_moon_nak:
            events.append({
                "type": "debut", "kind": "lunation",
                "transit": "Pleine Lune 🌕", "natal": "Lune ☽",
                "nakshatra": lunation_nak, "lord": NAKSHATRA_LORDS[NAKSHATRAS.index(lunation_nak)],
                "interpretation": "Pleine Lune dans votre Nakshatra lunaire natal",
            })
            
    return events


def _build_alert_html(profile: dict, events: list[dict], upgrade_cta: bool = False) -> str:
    name      = profile.get("name") or profile.get("pseudo", "")
    today_str = date.today().strftime("%d/%m/%Y")

    # Contexte du premier événement encodé dans l'URL CTA
    ctx_url = "/?open=synthesis"
    if events:
        e0 = events[0]
        t_label = PLANET_LABELS.get(e0["transit"], e0["transit"])
        nak     = e0.get("nakshatra", "")
        point   = e0.get("natal", "")
        regime  = e0.get("interpretation", e0.get("kind", ""))
        ctx_val = quote(f"{t_label}|{nak}|{point}|{regime}", safe="")
        ctx_url = f"/?open=synthesis&ctx={ctx_val}"

    upgrade_block = (
        '<div style="margin-top:20px;padding:16px;border:1px solid #4b0082;border-radius:3px;'
        'text-align:center;background:rgba(75,0,130,0.08)">'
        '<p style="color:#c0a0e0;font-size:13px;margin:0 0 12px;">'
        "C'était ta seule alerte incluse dans ta Lecture.<br>"
        'Passe à <strong>Illimit&eacute; &mdash; 9,99&nbsp;&euro;/mois</strong>'
        ' pour recevoir chaque activation karmique.</p>'
        '<a href="https://karmicgochara.app/?upgrade=subscription"'
        ' style="display:inline-block;background:transparent;color:#d4a017;text-decoration:none;'
        'padding:8px 20px;border:1px solid #d4a017;border-radius:3px;font-size:12px;letter-spacing:0.08em;">'
        '&#10022; PASSER &Agrave; ILLIMIT&Eacute; &rarr;</a></div>'
    ) if upgrade_cta else ""

    rows = ""
    for e in events:
        is_debut = e["type"] == "debut"
        icon     = "▶" if is_debut else "■"
        color    = "#6ab56a" if is_debut else "#e57373"
        t_label  = PLANET_LABELS.get(e["transit"], e["transit"])
        
        if e.get("kind") == "lunation":
            color     = "#d4a017" # Or
            icon      = "●"
            t_label   = e["transit"]
            nak_name  = e.get("nakshatra", "")
            lord      = e.get("lord", "")
            n_label   = f"{nak_name} ({lord}) — nakshatra de ta Lune natale"
            label     = e.get("interpretation", "Cycle lunaire majeur")
        elif e.get("kind") == "nakshatra":
            interp    = e.get("interpretation", "")
            color     = _INTERPRETATION_COLORS.get(interp, "#9090b0")
            lord      = e.get("lord", "")
            nak_name  = e.get("nakshatra", "")
            n_label   = f"{nak_name} ({lord}) — {NAK_NATAL_LABELS.get(e['natal'], e['natal'])}"
            label     = _INTERPRETATION_LABELS.get(interp, "Activation nakshatra")
            label     = label if is_debut else label.replace("Activation", "Fin d'activation").replace("activation", "fin d'activation")
        else: # Conjunction
            n_label   = NATAL_LABELS.get(e["natal"], e["natal"])
            label     = "Début de transit" if is_debut else "Fin de transit"
            
        rows += f"""
        <tr>
          <td style="padding:10px 8px;color:{color};font-size:20px;vertical-align:top;">{icon}</td>
          <td style="padding:10px 8px;vertical-align:top;">
            <div style="color:#d4a017;font-weight:bold;font-size:14px;">{t_label}</div>
            <div style="color:#c090e0;font-size:13px;margin-top:2px;">⊕ {n_label}</div>
            <div style="color:#9090b0;font-size:11px;margin-top:2px;">{label}</div>
          </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 620px; margin: 0 auto; background: #0f0f2a;
                border: 1px solid #4b0082; border-radius: 4px; padding: 30px; }}
  h1 {{ color: #d4a017; font-size: 19px; border-bottom: 1px solid #4b0082; padding-bottom: 10px; margin-top: 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
  tr {{ border-bottom: 1px solid #1a1a30; }}
  .footer {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
  .support a {{ background: #d4a017; color: #000; text-decoration: none;
                padding: 7px 18px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
  <h1>✦ Alerte Transit Karmique</h1>
  <p style="color:#9090b0;font-size:12px;margin-top:0;">{name} · {today_str} · Astrologie Védique Sidérale</p>
  <table>{rows}</table>
  <div style="margin-top:28px;text-align:center;">
    <a href="https://karmicgochara.app{ctx_url}" style="display:inline-block;background:#d4a017;color:#0a0a1a;text-decoration:none;padding:12px 28px;border-radius:3px;font-weight:bold;font-size:14px;letter-spacing:0.08em;">
      ✦ VOIR MON INTERPRÉTATION →
    </a>
    <p style="margin-top:12px;font-size:11px;color:#606080;">
      Connecte-toi · ouvre ton chatbot · pose la question que ça soulève.
    </p>
  </div>
  {upgrade_block}
  <div class="footer">
    Karmic Gochara · DK Ayanamsa · Chandra Lagna · True Nodes · Orbe &lt; 3°<br>
    <a href="https://karmicgochara.app/" style="color:#4b4b70;text-decoration:none;">Gérer mes alertes</a>
  </div>
</div>
</body>
</html>"""


def send_alert_email(profile: dict, events: list[dict], upgrade_cta: bool = False) -> bool:
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        return False
    email = (profile.get("email") or "").strip()
    if not email:
        return False

    html      = _build_alert_html(profile, events, upgrade_cta=upgrade_cta)
    today_str = date.today().strftime("%d/%m/%Y")

    try:
        r = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type":  "application/json",
            },
            json={
                "from":     "Gochara Karmique <karmic.gochara@astro.jeromemalige.fr>",
                "reply_to": "astro@jeromemalige.fr",
                "to":       [email],
                "subject":  f"✦ Transit Alert — {today_str}",
                "html":     html,
            },
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False


def find_next_major_transit_event(profile: dict, max_days_in_future: int = 365) -> dict | None:
    """
    Trouve le prochain événement de transit majeur (conjonction) dans le futur.
    Retourne l'événement avec sa date.
    """
    start_date = date.today()
    
    # Need natal positions once
    natal_pos, _ = _positions_for_day(profile, start_date)

    # Get active conjunctions for yesterday to see what's new today.
    _, yesterday_transit = _positions_for_day(profile, start_date - timedelta(days=1))
    yesterday_active = _active_conjunctions(natal_pos, yesterday_transit)

    for i in range(max_days_in_future):
        current_date = start_date + timedelta(days=i)
        _, current_transit = _positions_for_day(profile, current_date)
        current_active = _active_conjunctions(natal_pos, current_transit)

        new_events = current_active - yesterday_active
        if new_events:
            pair = list(new_events)[0]
            event = {
                "date": current_date.strftime("%d/%m/%Y"),
                "type": "debut",
                "kind": "conjunction",
                "transit": pair[0],
                "natal": pair[1]
            }
            return event
        
        yesterday_active = current_active
    
    return None

def _build_next_event_alert_html(profile: dict, event: dict) -> str:
    name = profile.get("name") or profile.get("pseudo", "")
    event_date = event["date"]
    t_label = PLANET_LABELS.get(event["transit"], event["transit"])
    n_label = NATAL_LABELS.get(event["natal"], event["natal"])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 620px; margin: 0 auto; background: #0f0f2a;
                border: 1px solid #4b0082; border-radius: 4px; padding: 30px; }}
  h1 {{ color: #d4a017; font-size: 19px; border-bottom: 1px solid #4b0082; padding-bottom: 10px; margin-top: 0; }}
  .event-details {{ margin-top: 20px; padding: 16px; border: 1px solid #d4a017; border-radius: 3px; background: rgba(212, 160, 23, 0.08); text-align: center; }}
  .footer {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>✦ Votre prochain événement karmique important</h1>
  <p style="color:#9090b0;font-size:12px;margin-top:0;">{name}, merci pour votre confiance.</p>
  <p>En tant que membre "Lecture", nous vous informons de votre prochain transit majeur :</p>
  <div class="event-details">
    <p style="font-size:16px; color:#d4a017; margin:0 0 10px;">Le {event_date}</p>
    <p style="font-size:14px; color:#e8e0d0; margin:0;">{t_label} sera en conjonction avec {n_label}.</p>
    <p style="font-size:12px; color:#9090b0; margin-top:10px;">C'est un moment clé pour votre chemin karmique.</p>
  </div>
  <div style="margin-top:28px;text-align:center;">
    <a href="https://karmicgochara.app/?open=synthesis" style="display:inline-block;background:#d4a017;color:#0a0a1a;text-decoration:none;padding:12px 28px;border-radius:3px;font-weight:bold;font-size:14px;letter-spacing:0.08em;">
      ✦ EXPLORER MON THÈME NATAL →
    </a>
  </div>
  <div class="footer">
    Karmic Gochara · DK Ayanamsa · Chandra Lagna · True Nodes · Orbe &lt; 3°<br>
  </div>
</div>
</body>
</html>"""

def send_next_event_alert_email(profile: dict, event: dict) -> bool:
    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        return False
    email = (profile.get("email") or "").strip()
    if not email:
        return False

    html = _build_next_event_alert_html(profile, event)
    
    try:
        r = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type":  "application/json",
            },
            json={
                "from":     "Gochara Karmique <karmic.gochara@astro.jeromemalige.fr>",
                "reply_to": "astro@jeromemalige.fr",
                "to":       [email],
                "subject":  "✦ Votre prochain événement karmique",
                "html":     html,
            },
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False




def run_daily_alerts() -> dict:
    """Point d'entrée principal — appelé par la route /cron/daily."""
    from profiles import get_all_profiles, get_and_consume_alert

    profiles = get_all_profiles()
    results  = {"total": len(profiles), "processed": 0, "alerted": 0, "skipped": 0, "errors": 0}

    for profile in profiles:
        if not profile.get("alerts_enabled"):
            continue
        if not profile.get("email"):
            continue

        plan = profile.get("plan", "free")
        quota = get_and_consume_alert(profile.get("pseudo", ""), plan)
        if not quota["ok"]:
            results["skipped"] += 1
            continue

        results["processed"] += 1
        try:
            events = detect_transit_events(profile)
            if events:
                sent = send_alert_email(profile, events, upgrade_cta=quota["is_last"])
                if sent:
                    results["alerted"] += 1
        except Exception:
            results["errors"] += 1

    return results


def _is_sade_sati_start(profile: dict, today: date) -> bool:
    """Vérifie si Sade Sati commence aujourd'hui."""
    # Cette fonction nécessite un état persistant ou une comparaison plus fine
    # que ce que `detect_transit_events` fournit. Pour l'instant, c'est un placeholder.
    # Dans une vraie app, on comparerait la position de Saturne d'hier et d'aujourd'hui
    # par rapport à la 12ème maison de la Lune natale.
    return False # Placeholder

def _is_saturn_return(profile: dict, today: date) -> bool:
    """Vérifie si c'est un retour de Saturne."""
    # Placeholder
    return False

def _is_nodal_opposition(profile: dict, today: date) -> bool:
    """Vérifie l'opposition des noeuds."""
    # Placeholder
    return False

def generate_transit_alert(user_id: str, birth_data: dict, current_date: date, subscription_status: str) -> dict:
    """
    Core logic for the Transit Alert Agent.
    """
    events = detect_transit_events(birth_data)
    
    # Placeholder logic to determine milestones
    sade_sati_start = _is_sade_sati_start(birth_data, current_date)
    saturn_return = _is_saturn_return(birth_data, current_date)
    nodal_opposition = _is_nodal_opposition(birth_data, current_date)

    # Generate narrative based on events
    if sade_sati_start:
        analysis = "Le cycle de Sade Sati commence. C'est une période de profonds changements et de défis."
        premium_teaser = "Découvrez comment naviguer cette période intense..."
        urgency = "high"
    elif saturn_return:
        analysis = "Votre retour de Saturne est arrivé. C'est un moment de grande maturation et de responsabilité."
        premium_teaser = "Comprenez les leçons que Saturne vous apporte..."
        urgency = "high"
    elif nodal_opposition:
        analysis = "L'opposition de vos noeuds lunaires indique un tournant karmique."
        premium_teaser = "Alignez-vous avec votre destinée..."
        urgency = "medium"
    elif events:
        # Simplified narrative from the first detected event
        e = events[0]
        t_planet = e.get('transit', 'Un transit')
        n_planet = e.get('natal', 'votre thème')
        analysis = f"{t_planet} active {n_planet}, initiant une nouvelle phase de votre parcours."
        premium_teaser = "Débloquez l'interprétation complète de cet aspect..."
        urgency = "low"
    else:
        # No major events today
        return None

    # Common fields
    cta_text = "🔮 Débloquer la Lecture Complète" if subscription_status == "free" else "🔮 Lire Mon Interprétation"
    disclaimer = "Ceci est une interprétation astrologique et ne remplace pas un avis médical ou professionnel. Les résultats ne sont pas garantis."

    return {
        "analysis": analysis,
        "urgency": urgency,
        "premium_teaser": premium_teaser,
        "recommendations": ["Méditez sur ces thèmes.", "Notez vos rêves.", "Soyez attentif aux synchronicités."],
        "cta_button_text": cta_text,
        "disclaimer": disclaimer,
        "confidence": 0.85
    }
