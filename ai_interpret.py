"""
ai_interpret.py — Gochara Karmique
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine centralisée dans doctrine.py — ce fichier ne contient que la logique d'appel API.
"""

import anthropic
import os

# ── Import doctrine centralisée ───────────────────────────────────────────────
from doctrine import (
    get_system_prompt,
    _detect_friction_axis,
    NAKSHATRA_KARMA,
    NODAL_CYCLES,
    HOUSE_MEANINGS,
)

# ── Client singleton ──────────────────────────────────────────────────────────
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT SYSTÈME — personnalisé par utilisateur, doctrine centralisée
# ══════════════════════════════════════════════════════════════════════════════

def _build_system_prompt(user: dict) -> str:
    """
    Construit le prompt système complet.
    Base = doctrine.get_system_prompt(user) — source unique de vérité, multi-langue.
    Injection du bloc natal personnalisé en fin de prompt.
    Injection du bloc friction identitaire (Pilier 6) si positions disponibles.
    """
    user = user or {}
    lang = user.get("lang", "fr")

    name         = user.get("name", "l'utilisateur")
    cl_sign      = user.get("chandra_lagna_sign", "")
    cl_deg       = user.get("chandra_lagna_deg", "")
    ketu_sign    = user.get("ketu_sign", "")
    ketu_h       = user.get("ketu_house", "")
    rahu_sign    = user.get("rahu_sign", "")
    rahu_h       = user.get("rahu_house", "")
    pv_sign      = user.get("porte_visible_sign", "")
    pv_deg       = user.get("porte_visible_deg", "")
    pv_h         = user.get("porte_visible_house", "")
    pi_sign      = user.get("porte_invisible_sign", "")
    pi_deg       = user.get("porte_invisible_deg", "")
    pi_h         = user.get("porte_invisible_house", "")
    chiron_sign  = user.get("chiron_sign", "")
    chiron_h     = user.get("chiron_house", "")
    lilith_sign  = user.get("lilith_sign", "")
    lilith_h     = user.get("lilith_house", "")
    saturn_sign  = user.get("saturn_sign", "")
    saturn_h     = user.get("saturn_house", "")
    jupiter_sign = user.get("jupiter_sign", "")
    jupiter_h    = user.get("jupiter_house", "")

    # Enrichissement nakshatra via doctrine.py
    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")
    lilith_nak = user.get("lilith_nakshatra", "")

    def nak_theme(nak_name: str, planet_key: str) -> str:
        if not nak_name:
            return ""
        entry = NAKSHATRA_KARMA.get(nak_name, {})
        theme = entry.get(planet_key, "")
        return f" — {theme}" if theme else ""

    # ── Labels bilingues ──────────────────────────────────────────────────────
    if lang == "en":
        header       = f"NATAL CHART OF {name.upper()} — Base reference for all transits"
        lbl_h1       = "Identity (H1 / Chandra Lagna)"
        lbl_ketu     = "Karmic Memory — Ketu (ROM ☋)"
        lbl_rahu     = "Dharma — Rahu (☊)"
        lbl_pv       = "Liberation Path (Visible Door / Stage)"
        lbl_pi       = "Unconscious Prison (Invisible Door / RAM ⚷)"
        lbl_chiron   = "Core Wound — Chiron (RAM ⚷)"
        lbl_lilith   = "Karmic Trial — Lilith (⚸)"
        lbl_saturn   = "Saturn — Architect (♄)"
        lbl_jupiter  = "Jupiter — Gift-Bearer (♃)"
        lbl_ref      = f"ALWAYS use this natal chart as fixed reference. Never deviate.\nAddress {name} directly."
    else:
        header       = f"THÈME NATAL DE {name.upper()} — Référence de base pour tous les transits"
        lbl_h1       = "Identité (H1 / Chandra Lagna)"
        lbl_ketu     = "Mémoire karmique — Ketu (ROM ☋)"
        lbl_rahu     = "Dharma — Rahu (☊)"
        lbl_pv       = "Voie de libération (Porte Visible / Stage)"
        lbl_pi       = "Prison inconsciente (Porte Invisible / RAM ⚷)"
        lbl_chiron   = "Blessure originelle — Chiron (RAM ⚷)"
        lbl_lilith   = "Épreuve karmique — Lilith (⚸)"
        lbl_saturn   = "Saturne — Architecte (♄)"
        lbl_jupiter  = "Jupiter — Porteur de cadeaux (♃)"
        lbl_ref      = f"Utilise TOUJOURS ce thème natal comme référence fixe. Ne jamais dévier.\nTu t'adresses à {name} en tutoiement direct."

    natal_bloc = ""
    if cl_sign:
        natal_bloc = f"""

═══════════════════════════════════════════════════════════════
{header}
═══════════════════════════════════════════════════════════════

{lbl_h1:<42}: {cl_sign} {cl_deg}
{lbl_ketu:<42}: {ketu_sign} H{ketu_h}{nak_theme(ketu_nak, "ketu")}
{lbl_rahu:<42}: {rahu_sign} H{rahu_h}{nak_theme(rahu_nak, "rahu")}
{lbl_pv:<42}: {pv_sign} {pv_deg} H{pv_h}
{lbl_pi:<42}: {pi_sign} {pi_deg} H{pi_h}
{lbl_chiron:<42}: {chiron_sign} H{chiron_h}{nak_theme(chiron_nak, "chiron")}
{lbl_lilith:<42}: {lilith_sign} H{lilith_h}{nak_theme(lilith_nak, "ketu")}
{lbl_saturn:<42}: {saturn_sign} H{saturn_h}
{lbl_jupiter:<42}: {jupiter_sign} H{jupiter_h}

{lbl_ref}
"""

    # ── Pilier 6 : friction axis depuis profil natal ───────────────────────────
    friction_bloc = ""
    natal_positions = user.get("natal_positions", {})
    if natal_positions:
        friction = _detect_friction_axis(natal_positions, lang=lang)
        friction_bloc = f"\n{friction['prompt_block']}\n"

    # ── Assemblage final ──────────────────────────────────────────────────────
    # get_system_prompt() retourne le prompt doctrine complet dans la bonne langue
    return get_system_prompt(user) + natal_bloc + friction_bloc


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro      = " ℞" if a.get("retrograde") else ""
        t_nak      = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak      = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""

        t_nak_theme = ""
        n_nak_theme = ""
        t_planet_key = _planet_to_doctrine_key(a.get("transit_planet", ""))
        n_planet_key = _planet_to_doctrine_key(a.get("natal_planet", ""))
        if a.get("transit_nakshatra") and t_planet_key:
            entry = NAKSHATRA_KARMA.get(a["transit_nakshatra"], {})
            if entry.get(t_planet_key):
                t_nak_theme = f" -> {entry[t_planet_key]}"
        if a.get("natal_nakshatra") and n_planet_key:
            entry = NAKSHATRA_KARMA.get(a["natal_nakshatra"], {})
            if entry.get(n_planet_key):
                n_nak_theme = f" -> {entry[n_planet_key]}"

        lines.append(
            f"T.{a['transit_planet']}{retro} ({a.get('transit_display','')}{t_nak}{t_nak_theme}) "
            f"{a['aspect']} "
            f"N.{a['natal_planet']} ({a.get('natal_display','')}{n_nak}{n_nak_theme}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


def _planet_to_doctrine_key(planet_name: str) -> str:
    """Mappe le nom de planète vers la clé doctrine NAKSHATRA_KARMA."""
    mapping = {
        "Ketu":    "ketu",
        "Rahu":    "rahu",
        "Saturn":  "saturn",
        "Saturne": "saturn",
        "Chiron":  "chiron",
        "Venus":   "venus",
        "Vénus":   "venus",
        "Jupiter": "jupiter",
        "Mars":    "mars",
    }
    return mapping.get(planet_name, "")


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    user = user or {}
    lines = []
    fields = [
        ("Chandra Lagna H1",              "chandra_lagna_sign",  "chandra_lagna_deg"),
        ("Ketu (ROM ☋)",                  "ketu_sign",           "ketu_house"),
        ("Rahu (Dharma ☊)",               "rahu_sign",           "rahu_house"),
        ("Porte Visible / Stage",         "porte_visible_sign",  "porte_visible_house"),
        ("Porte Invisible (RAM ⚷)",       "porte_invisible_sign","porte_invisible_house"),
        ("Chiron (RAM ⚷)",                "chiron_sign",         "chiron_house"),
        ("Lilith (⚸)",                    "lilith_sign",         "lilith_house"),
        ("Saturne (♄)",                   "saturn_sign",         "saturn_house"),
        ("Jupiter (♃)",                   "jupiter_sign",        "jupiter_house"),
    ]
    for label, key1, key2 in fields:
        v1 = user.get(key1, "")
        v2 = user.get(key2, "")
        if v1:
            lines.append(f"  {label}: {v1} {'H'+str(v2) if v2 else ''}")
    return "\n".join(lines) if lines else ""


def _detect_nodal_cycle(user: dict, chart_data: dict) -> str:
    """
    Détecte si un cycle nodal est actif.
    Utilise doctrine.NODAL_CYCLES pour les descriptions.
    """
    nn_transit = chart_data.get("transit_positions", {}).get("true_node_lon")
    nn_natal   = chart_data.get("natal_positions",   {}).get("true_node_lon")
    if nn_transit is None or nn_natal is None:
        return ""

    diff = abs(nn_transit - nn_natal) % 360
    if diff > 180:
        diff = 360 - diff

    if diff <= 10:
        cycle = NODAL_CYCLES["return"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 90) <= 10:
        cycle = NODAL_CYCLES["square"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 180) <= 10:
        cycle = NODAL_CYCLES["opposition"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    return ""


def _detect_transit_friction(chart_data: dict, lang: str = "fr") -> str:
    """
    Détecte l'axe de friction identitaire sur les positions EN TRANSIT (Pilier 6).
    Retourne le prompt_block prêt à injecter, ou chaîne vide.
    """
    transit_pos = chart_data.get("transit_positions", {})
    if not transit_pos:
        return ""

    # Construire un dict compatible _detect_friction_axis avec préfixe transit_
    positions = {}
    for planet in ("venus", "jupiter", "mars", "saturn"):
        raw = transit_pos.get(f"{planet}_lon") or transit_pos.get(planet, {}).get("lon_raw")
        if raw is not None:
            positions[f"transit_{planet}"] = {"lon_raw": float(raw)}

    if not positions:
        return ""

    friction = _detect_friction_axis(positions, lang=lang)
    if friction["label"] == "low" and not friction["aspects"]:
        return ""
    return f"\n{friction['prompt_block']}\n"


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis(chart_data: dict, user: dict = None, lang: str = "fr") -> str:
    """
    Génère la synthèse karmique automatique (onglet Gochara).
    chart_data : dict retourné par calculate_transits()
    user       : dict du profil utilisateur (session["profile"])
    """
    user = user or {}
    lang = user.get("lang", lang)  # lang du profil prioritaire

    aspects_text   = _aspects_to_text(chart_data.get("aspects", []))
    natal_context  = _build_natal_context(user)
    nodal_cycle    = _detect_nodal_cycle(user, chart_data)
    transit_frict  = _detect_transit_friction(chart_data, lang=lang)
    date           = chart_data.get("transit_date", "")
    time           = chart_data.get("transit_time", "")
    name           = user.get("name", "l'utilisateur")

    natal_bloc   = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc   = nodal_cycle if nodal_cycle else ""
    frict_bloc   = transit_frict if transit_frict else ""

    if lang == "en":
        prompt = f"""siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no recap of natal positions, no introduction.
{natal_bloc}{nodal_bloc}{frict_bloc}

Active aspects (with nakshatra themes if available):
{aspects_text}

Apply the 4-step protocol:

1. KARMIC MEMORY (ROM ☋) — Which transits activate least-resistance patterns? Describe what the soul does when caught in this trap, in direct narrative language.

2. THE WOUND IN PROCESSING (RAM ⚷) — Which transits activate Chiron or the Door Axis? Is the Invisible Door under pressure? Is the Visible Door / Stage being activated? Describe the movement, not the mechanics.

3. KARMIC TRIAL (⚸) — What is Lilith's current test? What does it make unbearable? Where does it propel? You may name planets and aspects here to create desire to explore the chart.

4. ALTERNATIVE DE CONSCIENCE + STAGING — Formulate the inner shift. What the soul must stop. What it must activate. The Visible Door's house as manifestation space. End with ONE single direct and actionable sentence.

Develop each section as coherent soul-reading, narrative, no mechanical lists. Minimum 300 words. Do not truncate."""
    else:
        prompt = f"""Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucun récapitulatif des positions natales, aucune introduction.
{natal_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (avec thèmes nakshatra si disponibles) :
{aspects_text}

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quels transits activent les schémas de moindre résistance ? Décris ce que l'âme fait quand elle est dans ce piège, en langage narratif direct.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Quels transits activent Chiron ou l'Axe des Portes ? La Porte Invisible est-elle sous pression ? La Voie de libération / Stage est-elle activée ? Décris le mouvement, pas la mécanique.

3. L'ÉPREUVE KARMIQUE (⚸) — Quel est le test de Lilith en cours ? Qu'est-ce qu'il rend insupportable ? Vers quoi il propulse ? Tu peux nommer ici les planètes et aspects pour créer le désir d'aller voir la carte.

4. ALTERNATIVE DE CONSCIENCE + MISE EN SCÈNE — Formule la bascule intérieure. Ce que l'âme doit cesser. Ce qu'elle doit activer. La maison de la Porte Visible comme lieu de manifestation. Termine par UNE seule phrase directe et actionnable.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer."""

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=_build_system_prompt(user),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# HOOK EXTENSION CHROME — 4 phrases, Alternative de Conscience du jour
# ══════════════════════════════════════════════════════════════════════════════

def get_hook(natal_pos: dict, transit_pos: dict, profile: dict, lang: str = "fr") -> str:
    """
    Génère un hook karmic de 4 phrases max.
    natal_pos / transit_pos : dicts issus de _calc_positions()
    Clés attendues : "Nœud Sud ☋", "Chiron ⚷", "Porte Visible ⊙",
                     "Nœud Nord ☊", "Lune ☽", "Saturne ♄", "Uranus ♅", etc.
    """
    from astro_calc import SIGNS

    def sign_of(pos_dict, key):
        p = pos_dict.get(key)
        if p and p.get("lon") is not None:
            return SIGNS[int(p["lon"] / 30) % 12]
        return "inconnu"

    def house_of(pos_dict, key, moon_lon):
        p = pos_dict.get(key)
        if p and p.get("lon") is not None and moon_lon is not None:
            lagna_sign = int(moon_lon / 30) % 12
            planet_sign = int(p["lon"] / 30) % 12
            return ((planet_sign - lagna_sign) % 12) + 1
        return "?"

    moon = natal_pos.get("Lune ☽")
    moon_lon = moon["lon"] if moon else None

    rom_sign   = sign_of(natal_pos, "Nœud Sud ☋")
    rom_house  = house_of(natal_pos, "Nœud Sud ☋", moon_lon)
    ram_sign   = sign_of(natal_pos, "Chiron ⚷")
    ram_house  = house_of(natal_pos, "Chiron ⚷", moon_lon)
    pv_sign    = sign_of(natal_pos, "Porte Visible ⊙")
    pv_house   = house_of(natal_pos, "Porte Visible ⊙", moon_lon)
    rahu_sign  = sign_of(natal_pos, "Nœud Nord ☊")
    rahu_house = house_of(natal_pos, "Nœud Nord ☊", moon_lon)
    lagna      = sign_of(natal_pos, "Lune ☽")

    active = []
    slow_planets = [
        "Saturne ♄", "Jupiter ♃", "Uranus ♅",
        "Neptune ♆", "Pluton ♇", "Rahu ☊", "Ketu ☋",
        "Chiron ⚷", "Mars ♂"
    ]
    natal_points = {
        "ROM (Ketu natal)":       natal_pos.get("Nœud Sud ☋"),
        "RAM (Chiron natal)":     natal_pos.get("Chiron ⚷"),
        "Porte Visible natale":   natal_pos.get("Porte Visible ⊙"),
        "Dharma (Rahu natal)":    natal_pos.get("Nœud Nord ☊"),
        "Lune natale":            natal_pos.get("Lune ☽"),
    }

    ASPECTS = {"conjonction": 0, "opposition": 180, "carré": 90, "trigone": 120, "sextile": 60}
    ORB = 3.0

    for t_name in slow_planets:
        t_planet = transit_pos.get(t_name)
        if not t_planet or t_planet.get("lon") is None:
            continue
        t_lon = t_planet["lon"]
        t_sign = SIGNS[int(t_lon / 30) % 12]
        for n_label, n_planet in natal_points.items():
            if not n_planet or n_planet.get("lon") is None:
                continue
            n_lon = n_planet["lon"]
            diff = abs(t_lon - n_lon) % 360
            if diff > 180:
                diff = 360 - diff
            for asp_name, asp_angle in ASPECTS.items():
                if abs(diff - asp_angle) <= ORB:
                    orb_val = round(abs(diff - asp_angle), 1)
                    active.append(
                        f"{t_name.split()[0]} transit en {t_sign} : {asp_name} avec {n_label} (orbe {orb_val}°)"
                    )

    transit_str = "\n".join(active[:5]) if active else "Aucun transit majeur actif aujourd'hui — période de latence karmique."

    prompt = f"""Tu es l'intelligence siderealAstro13. Génère un hook karmic de 4 phrases MAXIMUM.

THÈME NATAL (Jyotish sidéral DK, Chandra Lagna) :
- Chandra Lagna : {lagna}
- ROM (Ketu) : {rom_sign} H{rom_house} — mémoire karmique figée
- RAM (Chiron) : {ram_sign} H{ram_house} — blessure active, clé de la Porte Visible
- Stage / Porte Visible : {pv_sign} H{pv_house} — lieu de manifestation du Dharma
- Dharma (Rahu) : {rahu_sign} H{rahu_house} — direction d'expansion

TRANSITS ACTIFS AUJOURD'HUI :
{transit_str}

RÈGLES ABSOLUES :
- 4 phrases MAXIMUM, pas une de plus
- Phrase 1 : nomme le transit le plus puissant et son activation sur ROM ou RAM
- Phrases 2-3 : tension entre l'automatisme (ROM) et l'appel au Stage
- Phrase 4 : "L'Alternative de Conscience : [insight transformateur concret, actionnable aujourd'hui]"
- Zéro degrés, zéro symboles techniques dans l'output
- Tutoiement, style direct et transformateur
- Langue : {"français" if lang == "fr" else "english"}
- Zéro preamble, commence directement"""

    for attempt in range(3):
        try:
            msg = _get_client().messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            if attempt == 2:
                raise e
            import time
            time.sleep(2 ** attempt)


# ══════════════════════════════════════════════════════════════════════════════
# HOOK INVITÉ — 1 phrase teaser (résume #1 #2 #3, ouvre le désir du #4)
# ══════════════════════════════════════════════════════════════════════════════

def get_guest_section(natal_pos: dict, transit_pos: dict, section: int = 1, lang: str = "fr") -> str:
    """
    Génère la section karmique demandée (1 à 4) pour le mode invité.
    Section 1 : ROM — Mémoire Karmique
    Section 2 : RAM — Blessure en traitement
    Section 3 : Épreuve Karmique (Lilith)
    Section 4 : Alternative de Conscience (actionnable)
    150 tokens max, style oracle direct.
    """
    from astro_calc import SIGNS

    def sign_of(d, k):
        p = d.get(k)
        return SIGNS[int(p["lon"] / 30) % 12] if p and p.get("lon") is not None else "?"

    def house_of(d, k, moon_lon):
        p = d.get(k)
        if p and p.get("lon") is not None and moon_lon is not None:
            return ((int(p["lon"] / 30) % 12) - (int(moon_lon / 30) % 12)) % 12 + 1
        return "?"

    moon     = natal_pos.get("Lune ☽")
    moon_lon = moon["lon"] if moon else None
    lagna    = sign_of(natal_pos, "Lune ☽")
    rom      = f"Ketu {sign_of(natal_pos, 'Nœud Sud ☋')} H{house_of(natal_pos, 'Nœud Sud ☋', moon_lon)}"
    ram      = f"Chiron {sign_of(natal_pos, 'Chiron ⚷')} H{house_of(natal_pos, 'Chiron ⚷', moon_lon)}"
    stage    = f"{sign_of(natal_pos, 'Porte Visible ⊙')} H{house_of(natal_pos, 'Porte Visible ⊙', moon_lon)}"
    lilith   = f"Lilith {sign_of(natal_pos, 'Lilith ⚸')} H{house_of(natal_pos, 'Lilith ⚸', moon_lon)}"

    slow = ["Saturne ♄", "Jupiter ♃", "Uranus ♅", "Rahu ☊", "Ketu ☋", "Chiron ⚷", "Mars ♂"]
    actifs = []
    for t_name in slow:
        tp = transit_pos.get(t_name)
        if tp and tp.get("lon") is not None:
            actifs.append(f"{t_name.split()[0]} en {SIGNS[int(tp['lon']/30)%12]}")
    transit_str = ", ".join(actifs[:3]) if actifs else "transits du jour"

    section = max(1, min(4, section))

    PROMPTS_FR = {
        1: f"""Tu es siderealAstro13. Écris UNIQUEMENT la section #1 — Mémoire Karmique (ROM).
Contexte : Chandra Lagna={lagna}, ROM={rom}. Transits : {transit_str}.
2 phrases max. Nomme le schéma automatique que l'âme rejoue aujourd'hui. Langage narratif, tutoiement, zéro mécanique.
Zéro préambule.""",
        2: f"""Tu es siderealAstro13. Écris UNIQUEMENT la section #2 — Blessure en Traitement (RAM).
Contexte : RAM={ram}, ROM={rom}, Lagna={lagna}. Transits : {transit_str}.
2 phrases max. Nomme ce que les transits rouvrent dans Chiron. Ce qui est sous pression. Zéro mécanique.
Zéro préambule.""",
        3: f"""Tu es siderealAstro13. Écris UNIQUEMENT la section #3 — Épreuve Karmique.
Contexte : {lilith}, Stage={stage}, Lagna={lagna}. Transits : {transit_str}.
2 phrases max. Ce que l'épreuve rend insupportable. Vers quoi elle propulse malgré tout. Zéro mécanique.
Zéro préambule.""",
        4: f"""Tu es siderealAstro13. Écris UNIQUEMENT la section #4 — Alternative de Conscience.
Contexte : ROM={rom}, Stage={stage}, RAM={ram}. Transits : {transit_str}.
2 phrases max. Ce que l'âme doit CESSER (ROM). Ce qu'elle doit ACTIVER (Stage). Termine par UNE phrase directe actionnable aujourd'hui.
Zéro préambule.""",
    }

    PROMPTS_EN = {
        1: f"""You are siderealAstro13. Write ONLY section #1 — Karmic Memory (ROM).
Context: Chandra Lagna={lagna}, ROM={rom}. Transits: {transit_str}.
2 sentences max. Name the automatic pattern the soul is replaying today. Narrative language, second person, no mechanics.
No preamble.""",
        2: f"""You are siderealAstro13. Write ONLY section #2 — The Wound in Processing (RAM).
Context: RAM={ram}, ROM={rom}, Lagna={lagna}. Transits: {transit_str}.
2 sentences max. Name what the transits are reopening in Chiron. What is under pressure. No mechanics.
No preamble.""",
        3: f"""You are siderealAstro13. Write ONLY section #3 — Karmic Trial.
Context: {lilith}, Stage={stage}, Lagna={lagna}. Transits: {transit_str}.
2 sentences max. What the trial makes unbearable. Where it propels despite everything. No mechanics.
No preamble.""",
        4: f"""You are siderealAstro13. Write ONLY section #4 — Alternative of Consciousness.
Context: ROM={rom}, Stage={stage}, RAM={ram}. Transits: {transit_str}.
2 sentences max. What the soul must STOP (ROM). What it must ACTIVATE (Stage). End with ONE direct, concrete, actionable sentence for today.
No preamble.""",
    }

    prompts = PROMPTS_EN if lang == "en" else PROMPTS_FR
    prompt  = prompts[section]

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


# Alias conservé pour compatibilité extension v2
def get_guest_hook(natal_pos: dict, transit_pos: dict, lang: str = "fr") -> str:
    """
    Génère UNE SEULE phrase teaser pour le mode invité.
    Résume la tension karmique active (#1 ROM + #2 RAM + #3 Épreuve)
    et crée le désir de découvrir l'Alternative de Conscience (#4).
    """
    from astro_calc import SIGNS

    def sign_of(d, k):
        p = d.get(k)
        return SIGNS[int(p["lon"] / 30) % 12] if p and p.get("lon") is not None else "?"

    def house_of(d, k, moon_lon):
        p = d.get(k)
        if p and p.get("lon") is not None and moon_lon is not None:
            return ((int(p["lon"] / 30) % 12) - (int(moon_lon / 30) % 12)) % 12 + 1
        return "?"

    moon     = natal_pos.get("Lune ☽")
    moon_lon = moon["lon"] if moon else None
    lagna    = sign_of(natal_pos, "Lune ☽")
    rom      = f"Ketu {sign_of(natal_pos, 'Nœud Sud ☋')} H{house_of(natal_pos, 'Nœud Sud ☋', moon_lon)}"
    ram      = f"Chiron {sign_of(natal_pos, 'Chiron ⚷')} H{house_of(natal_pos, 'Chiron ⚷', moon_lon)}"
    stage    = f"{sign_of(natal_pos, 'Porte Visible ⊙')} H{house_of(natal_pos, 'Porte Visible ⊙', moon_lon)}"

    # Transits actifs significatifs
    slow = ["Saturne ♄", "Jupiter ♃", "Uranus ♅", "Rahu ☊", "Ketu ☋", "Chiron ⚷", "Mars ♂"]
    actifs = []
    for t_name in slow:
        tp = transit_pos.get(t_name)
        if tp and tp.get("lon") is not None:
            actifs.append(f"{t_name.split()[0]} en {SIGNS[int(tp['lon']/30)%12]}")
    transit_str = ", ".join(actifs[:4]) if actifs else "transits actifs"

    if lang == "en":
        prompt = f"""You are siderealAstro13. Write ONE SINGLE sentence (30-50 words max).

This sentence must:
- Name the karmic tension active today from: ROM={rom}, RAM={ram}, Stage={stage}, Chandra Lagna={lagna}
- Reference today's key transits: {transit_str}
- Create an irresistible desire to discover the Alternative of Consciousness (section #4)
- No solution, only tension and suspense
- Direct oracle style, second person
- End with "…" or a question that opens the desire for more

Write the sentence only, no preamble."""
    else:
        prompt = f"""Tu es siderealAstro13. Écris UNE SEULE phrase (30-50 mots max).

Cette phrase doit :
- Nommer la tension karmique active aujourd'hui depuis : ROM={rom}, RAM={ram}, Stage={stage}, Chandra Lagna={lagna}
- Référencer les transits clés du jour : {transit_str}
- Créer un désir irrésistible de découvrir l'Alternative de Conscience (section #4)
- Pas de solution — seulement la tension et la suspension
- Style oracle direct, tutoiement
- Terminer par "…" ou une question qui ouvre l'envie d'aller plus loin

Écris uniquement la phrase, sans préambule."""

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
