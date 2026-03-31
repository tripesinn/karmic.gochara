"""
ai_interpret.py — Gochara Karmique
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine centralisée dans doctrine.py — ce fichier ne contient que la logique d'appel API.
"""

import anthropic
import os

# ── Import doctrine centralisée ───────────────────────────────────────────────
from doctrine import SYSTEM_PROMPT, NAKSHATRA_KARMA, NODAL_CYCLES, HOUSE_MEANINGS

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
    Base = doctrine.SYSTEM_PROMPT (source unique de vérité).
    Injection du bloc natal personnalisé en fin de prompt.
    """
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

    # Thèmes karmiques nakshatra depuis la doctrine
    def nak_theme(nak_name: str, planet_key: str) -> str:
        if not nak_name:
            return ""
        entry = NAKSHATRA_KARMA.get(nak_name, {})
        theme = entry.get(planet_key, "")
        return f" — {theme}" if theme else ""

    natal_bloc = ""
    if cl_sign:
        natal_bloc = f"""

═══════════════════════════════════════════════════════════════
THÈME NATAL DE {name.upper()} — Référence de base pour tous les transits
═══════════════════════════════════════════════════════════════

Identité (H1 / Chandra Lagna)     : {cl_sign} {cl_deg}
Mémoire karmique — Ketu (ROM)     : {ketu_sign} H{ketu_h}{nak_theme(ketu_nak, "ketu")}
Dharma — Rahu                     : {rahu_sign} H{rahu_h}{nak_theme(rahu_nak, "rahu")}
Voie de libération (Porte Visible): {pv_sign} {pv_deg} H{pv_h}
Prison inconsciente (Porte Invis.): {pi_sign} {pi_deg} H{pi_h}
Blessure originelle — Chiron (RAM): {chiron_sign} H{chiron_h}{nak_theme(chiron_nak, "chiron")}
Épreuve karmique — Lilith         : {lilith_sign} H{lilith_h}{nak_theme(lilith_nak, "ketu")}
Saturne — Architecte              : {saturn_sign} H{saturn_h}
Jupiter — Porteur de cadeaux      : {jupiter_sign} H{jupiter_h}

Utilise TOUJOURS ce thème natal comme référence fixe. Ne jamais dévier.
Tu t'adresses à {name} en tutoiement direct.
"""

    # SYSTEM_PROMPT depuis doctrine.py + bloc natal personnalisé
    return SYSTEM_PROMPT + natal_bloc


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro  = " ℞" if a.get("retrograde") else ""
        t_nak  = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak  = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""

        # Enrichissement thème karmique nakshatra depuis doctrine
        t_nak_theme = ""
        n_nak_theme = ""
        t_planet_key = _planet_to_doctrine_key(a.get("transit_planet", ""))
        n_planet_key = _planet_to_doctrine_key(a.get("natal_planet", ""))
        if a.get("transit_nakshatra") and t_planet_key:
            entry = NAKSHATRA_KARMA.get(a["transit_nakshatra"], {})
            if entry.get(t_planet_key):
                t_nak_theme = f" → {entry[t_planet_key]}"
        if a.get("natal_nakshatra") and n_planet_key:
            entry = NAKSHATRA_KARMA.get(a["natal_nakshatra"], {})
            if entry.get(n_planet_key):
                n_nak_theme = f" → {entry[n_planet_key]}"

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
    }
    return mapping.get(planet_name, "")


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    lines = []
    fields = [
        ("Chandra Lagna H1",              "chandra_lagna_sign", "chandra_lagna_deg"),
        ("Mémoire karmique (Ketu)",        "ketu_sign",           "ketu_house"),
        ("Dharma (Rahu)",                  "rahu_sign",           "rahu_house"),
        ("Voie de libération",             "porte_visible_sign",  "porte_visible_house"),
        ("Prison inconsciente",            "porte_invisible_sign","porte_invisible_house"),
        ("Blessure originelle (Chiron)",   "chiron_sign",         "chiron_house"),
        ("Épreuve karmique (Lilith)",      "lilith_sign",         "lilith_house"),
        ("Saturne",                        "saturn_sign",         "saturn_house"),
        ("Jupiter",                        "jupiter_sign",        "jupiter_house"),
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
        return f"\n⚡ CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 90) <= 10:
        cycle = NODAL_CYCLES["square"]
        return f"\n⚡ CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 180) <= 10:
        cycle = NODAL_CYCLES["opposition"]
        return f"\n⚡ CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    return ""


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis(chart_data: dict, user: dict = None) -> str:
    """
    Génère la synthèse karmique automatique (onglet Gochara).
    chart_data : dict retourné par calculate_transits()
    user       : dict du profil utilisateur (session["profile"])
    """
    if user is None:
        user = {}

    aspects_text  = _aspects_to_text(chart_data.get("aspects", []))
    natal_context = _build_natal_context(user)
    nodal_cycle   = _detect_nodal_cycle(user, chart_data)
    date          = chart_data.get("transit_date", "")
    time          = chart_data.get("transit_time", "")
    name          = user.get("name", "l'utilisateur")

    natal_bloc = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc = nodal_cycle if nodal_cycle else ""

    prompt = f"""Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucun récapitulatif des positions natales, aucune introduction.
{natal_bloc}{nodal_bloc}

Aspects actifs (avec thèmes nakshatra si disponibles) :
{aspects_text}

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE — Quels transits activent les schémas de moindre résistance ? Décris ce que l'âme fait quand elle est dans ce piège, en langage narratif direct.

2. LA BLESSURE EN TRAITEMENT — Quels transits activent Chiron ou l'Axe des Portes ? La Prison inconsciente est-elle sous pression ? La Voie de libération est-elle activée ? Décris le mouvement, pas la mécanique.

3. L'ÉPREUVE KARMIQUE — Quel est le test de Lilith en cours ? Qu'est-ce qu'il rend insupportable ? Vers quoi il propulse ? Tu peux nommer ici les planètes et aspects pour créer le désir d'aller voir la carte.

4. ALTERNATIVE DE CONSCIENCE + MISE EN SCÈNE — Formule la bascule intérieure. Ce que l'âme doit cesser. Ce qu'elle doit activer. La maison de la Voie de libération comme lieu de manifestation. Termine par UNE seule phrase directe et actionnable qui peut servir d'accroche email.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer."""

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=_build_system_prompt(user),
        messages=[{"role": "user", "content": prompt}],
    )
