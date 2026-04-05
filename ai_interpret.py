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


def _build_amsa_bloc(chart_data: dict, lang: str = "fr") -> str:
    """
    Formate les positions divisionnelles D9/D10/D60 des planètes clés
    (natal uniquement — les Amsas décrivent la nature fixe de l'âme).
    Retourne un bloc texte prêt à injecter dans le prompt.
    """
    natal = chart_data.get("natal", {})
    if not natal:
        return ""

    # Planètes clés par Amsa
    D9_PLANETS  = ["Lune ☽", "ASC ↑", "Nœud Nord ☊", "Nœud Sud ☋", "Vénus ♀", "Jupiter ♃"]
    D10_PLANETS = ["Soleil ☀", "Saturne ♄", "Mars ♂", "Jupiter ♃", "MC ↑"]
    D60_PLANETS = ["Lune ☽", "Soleil ☀", "Nœud Sud ☋", "Chiron ⚷", "Saturne ♄"]

    def fmt(planet_key: str, amsa: str) -> str:
        p = natal.get(planet_key)
        if not p:
            return None
        data = p.get(amsa)
        if not data:
            return None
        sign    = data.get("sign", "")
        part    = data.get("part", "")
        lord    = data.get("lord", "")   # D60 seulement
        lord_s  = f" [{lord}]" if lord else ""
        return f"  {planet_key:<22} {sign}{lord_s} (part {part})"

    lines_d9  = [r for p in D9_PLANETS  if (r := fmt(p, "d9"))]
    lines_d10 = [r for p in D10_PLANETS if (r := fmt(p, "d10"))]
    lines_d60 = [r for p in D60_PLANETS if (r := fmt(p, "d60"))]

    if not any([lines_d9, lines_d10, lines_d60]):
        return ""

    if lang == "en":
        header  = "DIVISIONAL CHARTS (NATAL AMSAS)"
        d9_lbl  = "D9 — Navamsha (dharma, soul purpose, marriage)"
        d10_lbl = "D10 — Dashamsha (professional karma, public action)"
        d60_lbl = "D60 — Shashtyamsha (karmic specificity, soul imprint)"
        instr   = ("Use these Amsas to deepen the natal reading: "
                   "the Navamsha sign refines the soul's incarnation dharma; "
                   "the Dashamsha reveals the professional mission; "
                   "the Shashtyamsha lord names the karmic sub-color of each planet.")
    else:
        header  = "CHARTS DIVISIONNELS (AMSAS NATAUX)"
        d9_lbl  = "D9 — Navamsha (dharma, vocation de l'âme, mariage)"
        d10_lbl = "D10 — Dashamsha (karma professionnel, action publique)"
        d60_lbl = "D60 — Shashtyamsha (spécificité karmique, empreinte de l'âme)"
        instr   = ("Utilise ces Amsas pour approfondir la lecture natale : "
                   "le signe Navamsha affine le dharma d'incarnation de l'âme ; "
                   "le Dashamsha révèle la mission professionnelle ; "
                   "le seigneur Shashtyamsha nomme la sous-couleur karmique de chaque planète.")

    bloc = f"\n{'─'*62}\n{header}\n{'─'*62}\n"
    if lines_d9:
        bloc += f"\n{d9_lbl}\n" + "\n".join(lines_d9) + "\n"
    if lines_d10:
        bloc += f"\n{d10_lbl}\n" + "\n".join(lines_d10) + "\n"
    if lines_d60:
        bloc += f"\n{d60_lbl}\n" + "\n".join(lines_d60) + "\n"
    bloc += f"\n{instr}\n"
    return bloc


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
    amsa_bloc      = _build_amsa_bloc(chart_data, lang=lang)
    date           = chart_data.get("transit_date", "")
    time           = chart_data.get("transit_time", "")
    name           = user.get("name", "l'utilisateur")

    natal_bloc   = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc   = nodal_cycle if nodal_cycle else ""
    frict_bloc   = transit_frict if transit_frict else ""

    if lang == "en":
        prompt = f"""siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no recap of natal positions, no introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

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
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (avec thèmes nakshatra si disponibles) :
{aspects_text}

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quels transits activent les schémas de moindre résistance ? Décris ce que l'âme fait quand elle est dans ce piège, en langage narratif direct.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Quels transits activent Chiron ou l'Axe des Portes ? La Porte Invisible est-elle sous pression ? La Voie de libération / Stage est-elle activée ? Décris le mouvement, pas la mécanique.

3. L'ÉPREUVE KARMIQUE (⚸) — Quel est le test de Lilith en cours ? Qu'est-ce qu'il rend insupportable ? Vers quoi il propulse ? Tu peux nommer ici les planètes et aspects pour créer le désir d'aller voir la carte.

4. ALTERNATIVE DE CONSCIENCE + MISE EN SCÈNE — Formule la bascule intérieure. Ce que l'âme doit cesser. Ce qu'elle doit activer. La maison de la Porte Visible comme lieu de manifestation. Termine par UNE seule phrase directe et actionnable.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer."""

    synthesis_model = os.environ.get("SYNTHESIS_MODEL", "claude-sonnet-4-6")
    msg = _get_client().messages.create(
        model=synthesis_model,
        max_tokens=4000,
        system=_build_system_prompt(user),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def build_prompt_only(chart_data: dict, user: dict = None, lang: str = "fr") -> dict:
    """
    Construit le prompt complet SANS appeler Claude.
    Utilisé par /synthesis/prompt pour l'inférence locale (Gemma 4 via AI Core).
    Retourne {"system": "...", "user": "..."} prêt à injecter dans n'importe quel LLM.
    """
    user = user or {}
    lang = user.get("lang", lang)

    aspects_text  = _aspects_to_text(chart_data.get("aspects", []))
    natal_context = _build_natal_context(user)
    nodal_cycle   = _detect_nodal_cycle(user, chart_data)
    transit_frict = _detect_transit_friction(chart_data, lang=lang)
    amsa_bloc     = _build_amsa_bloc(chart_data, lang=lang)
    date          = chart_data.get("transit_date", "")
    time          = chart_data.get("transit_time", "")
    name          = user.get("name", "l'utilisateur")

    natal_bloc = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc = nodal_cycle  if nodal_cycle  else ""
    frict_bloc = transit_frict if transit_frict else ""

    if lang == "en":
        user_prompt = f"""siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no recap of natal positions, no introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Active aspects (with nakshatra themes if available):
{aspects_text}

Apply the 4-step protocol:

1. KARMIC MEMORY (ROM ☋) — Which transits activate least-resistance patterns? Describe what the soul does when caught in this trap, in direct narrative language.

2. THE WOUND IN PROCESSING (RAM ⚷) — Which transits activate Chiron or the Door Axis? Is the Invisible Door under pressure? Is the Visible Door / Stage being activated? Describe the movement, not the mechanics.

3. KARMIC TRIAL (⚸) — What is Lilith's current test? What does it make unbearable? Where does it propel?

4. ALTERNATIVE DE CONSCIENCE + STAGING — Formulate the inner shift. What the soul must stop. What it must activate. End with ONE single direct and actionable sentence.

Develop each section as coherent soul-reading, narrative, no mechanical lists. Minimum 300 words. Do not truncate."""
    else:
        user_prompt = f"""Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucun récapitulatif des positions natales, aucune introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (avec thèmes nakshatra si disponibles) :
{aspects_text}

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quels transits activent les schémas de moindre résistance ? Décris ce que l'âme fait quand elle est dans ce piège, en langage narratif direct.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Quels transits activent Chiron ou l'Axe des Portes ? La Porte Invisible est-elle sous pression ? La Voie de libération / Stage est-elle activée ?

3. L'ÉPREUVE KARMIQUE (⚸) — Quel est le test de Lilith en cours ? Qu'est-ce qu'il rend insupportable ? Vers quoi il propulse ?

4. ALTERNATIVE DE CONSCIENCE + MISE EN SCÈNE — Formule la bascule intérieure. Ce que l'âme doit cesser. Ce qu'elle doit activer. Termine par UNE seule phrase directe et actionnable.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer."""

    return {
        "system": _build_system_prompt(user),
        "user":   user_prompt,
    }
