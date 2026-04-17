"""
ai_interpret.py — Gochara Karmique [FIXED]
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine centralisée dans doctrine.py — ce fichier ne contient que la logique d'appel API.

Vault Karpathy (karmic_vault/) injecté dans _build_system_prompt().
Fallback automatique vers doctrine.py si vault absent.

Hooks :
  get_hook_natal(user)              → 3-4 phrases dès le login (natal seul)
  get_hook_transit(chart_data, user)→ 3-4 phrases dès la date choisie (aspects du jour)
  get_synthesis(chart_data, user)   → synthèse complète ~4000 tokens (payant)
  build_prompt_only(chart_data, user) → prompt Gemma sans appel API
"""

import anthropic
import os

from astro_calc import NAKSHATRAS, NAKSHATRA_LORDS

# ── Import doctrine centralisée ───────────────────────────────────────────────
from doctrine import (
    get_system_prompt,
    _detect_friction_axis,
    NAKSHATRA_KARMA,
    NODAL_CYCLES,
    HOUSE_MEANINGS,
)


# ══════════════════════════════════════════════════════════════════════════════
# VAULT KARPATHY — chargement des fichiers Markdown doctrinaux
# ══════════════════════════════════════════════════════════════════════════════

_VAULT_DIR = os.path.join(os.path.dirname(__file__), "karmic_vault")


def _load_vault(include_keywords: bool = True) -> str | None:
    """
    Charge le vault doctrinal Markdown compressé (~800-1300 tokens).
    Fallback silencieux vers doctrine.get_system_prompt() si vault absent.
    include_keywords=False → 00 + 01 seulement (hooks, budget réduit).
    """
    try:
        master = open(os.path.join(_VAULT_DIR, "00_MASTER_CONTEXT.md"), encoding="utf-8").read()
        rules  = open(os.path.join(_VAULT_DIR, "01_output_rules.md"),   encoding="utf-8").read()
        vault  = master + "\n\n---\n\n" + rules
        if include_keywords:
            kw_path = os.path.join(_VAULT_DIR, "02_planet_keywords.md")
            if os.path.exists(kw_path):
                vault += "\n\n---\n\n" + open(kw_path, encoding="utf-8").read()
        import logging
        logging.getLogger(__name__).info("VAULT chargé — %d tokens estimés", len(vault.split()))

        return vault
    except FileNotFoundError:
        return None


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

def _build_system_prompt(user: dict, use_vault: bool = True) -> str:
    """
    Construit le prompt système complet.
    use_vault=True  → vault Karpathy (fallback doctrine.py si absent)
    use_vault=False → doctrine.py legacy uniquement
    Injection bloc natal personnalisé + friction (Pilier 6) dans les deux cas.
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

    if lang == "en":
        header     = f"NATAL CHART OF {name.upper()} — Base reference for all transits"
        lbl_h1     = "Identity (H1 / Chandra Lagna)"
        lbl_ketu   = "Karmic Memory — Ketu (ROM ☋)"
        lbl_rahu   = "Dharma — Rahu (☊)"
        lbl_pv     = "Liberation Path (Visible Door — healing/Stage)"
        lbl_pi     = "Unconscious Prison (Invisible Door — refoulement/blockage)"  # CORR L123
        lbl_chiron = "Core Wound — Chiron (RAM ⚷ — opening tool of Visible Door)"  # CORR L124
        lbl_lilith = "Karmic Trial — Lilith (⚸)"
        lbl_saturn = "Saturn — Architect (♄)"
        lbl_jup    = "Jupiter — Gift-Bearer (♃)"
        lbl_ref    = f"ALWAYS use this natal chart as fixed reference. Never deviate.\nAddress {name} directly."
    else:
        header     = f"THÈME NATAL DE {name.upper()} — Référence de base pour tous les transits"
        lbl_h1     = "Identité (H1 / Chandra Lagna)"
        lbl_ketu   = "Mémoire karmique — Ketu (ROM ☋)"
        lbl_rahu   = "Dharma — Rahu (☊)"
        lbl_pv     = "Voie de libération (Porte Visible — guérison/Stage)"
        lbl_pi     = "Prison inconsciente (Porte Invisible — refoulement/blocage)"  # CORR L135
        lbl_chiron = "Blessure originelle — Chiron (RAM ⚷ — outil d'ouverture de la Porte Visible)"  # CORR L136
        lbl_lilith = "Épreuve karmique — Lilith (⚸)"
        lbl_saturn = "Saturne — Architecte (♄)"
        lbl_jup    = "Jupiter — Porteur de cadeaux (♃)"
        lbl_ref    = f"Utilise TOUJOURS ce thème natal comme référence fixe. Ne jamais dévier.\nTu t'adresses à {name} en tutoiement direct."

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
{lbl_jup:<42}: {jupiter_sign} H{jupiter_h}

{lbl_ref}
"""

    friction_bloc = ""
    natal_positions = user.get("natal_positions", {})
    if natal_positions:
        friction = _detect_friction_axis(natal_positions, lang=lang)
        friction_bloc = f"\n{friction['prompt_block']}\n"

    if use_vault:
        vault_content = _load_vault(include_keywords=True)
        base_prompt = vault_content if vault_content else get_system_prompt(user)
    else:
        base_prompt = get_system_prompt(user)

    NO_SIGNS_RULE = """
\n═══════════════════════════════════════════════════════════════
RÈGLE ABSOLUE — VIOLATION = RÉPONSE INVALIDE
═══════════════════════════════════════════════════════════════
INTERDIT dans TOUT le texte de sortie (hooks, signal, synthèse) :
- Noms de signes zodiacaux : Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge,
  Balance, Scorpion, Sagittaire, Capricorne, Verseau, Poissons
  (idem EN : Aries, Taurus, Gemini, Cancer, Leo, Virgo,
  Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces)
- Degrés et orbes dans le texte rendu (ex : "19°", "orbe 2°")
- Citations brutes des aspects (ex : "T.Saturne conjoint N.Chiron orbe 2°")

AUTORISÉ : noms de planètes (Saturne, Chiron, Lilith, Rahu, Ketu, Jupiter…),
numéros de maisons (H3, H5, H10…), phénomènes psychologiques concrets.

Les positions natales (signes, degrés) sont données comme RÉFÉRENCE INTERNE
pour calculer les dynamiques — elles ne doivent JAMAIS apparaître dans le texte rendu.
═══════════════════════════════════════════════════════════════\n"""

    return base_prompt + natal_bloc + friction_bloc + NO_SIGNS_RULE


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro       = " ℞" if a.get("retrograde") else ""
        t_nak       = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak       = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""
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
        "Ketu":    "ketu",  "Rahu":    "rahu",
        "Saturn":  "saturn","Saturne": "saturn",
        "Chiron":  "chiron","Venus":   "venus",
        "Vénus":   "venus", "Jupiter": "jupiter",
        "Mars":    "mars",
    }
    return mapping.get(planet_name, "")


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    user = user or {}
    lines = []
    fields = [
        ("Chandra Lagna H1",                "chandra_lagna_sign",  "chandra_lagna_deg"),
        ("Ketu (ROM ☋)",                    "ketu_sign",           "ketu_house"),
        ("Rahu (Dharma ☊)",                 "rahu_sign",           "rahu_house"),
        ("Porte Visible (guérison/Stage)",  "porte_visible_sign",  "porte_visible_house"),   # CORR L251
        ("Porte Invisible (prison/refoul.)", "porte_invisible_sign","porte_invisible_house"), # CORR L252
        ("Chiron (RAM ⚷ — ouverture PV)",   "chiron_sign",         "chiron_house"),
        ("Lilith (⚸)",                      "lilith_sign",         "lilith_house"),
        ("Saturne (♄)",                     "saturn_sign",         "saturn_house"),
        ("Jupiter (♃)",                     "jupiter_sign",        "jupiter_house"),
    ]
    for label, key1, key2 in fields:
        v1 = user.get(key1, "")
        v2 = user.get(key2, "")
        if v1:
            lines.append(f"  {label}: {v1} {'H'+str(v2) if v2 else ''}")
    return "\n".join(lines) if lines else ""


def _build_amsa_bloc(chart_data: dict, lang: str = "fr", compact: bool = False) -> str:
    """Formate les positions divisionnelles D9/D10/D60."""
    natal = chart_data.get("natal", {})
    if not natal:
        return ""
    D9_PLANETS  = ["Lune ☽", "ASC ↑", "Nœud Nord ☊", "Nœud Sud ☋", "Vénus ♀", "Jupiter ♃"]
    D10_PLANETS = ["Soleil ☀", "Saturne ♄", "Mars ♂", "Jupiter ♃", "MC ↑"]
    D60_PLANETS = ["Lune ☽", "Nœud Sud ☋"] if compact else ["Lune ☽", "Soleil ☀", "Nœud Sud ☋", "Chiron ⚷", "Saturne ♄"]

    def fmt(planet_key: str, amsa: str) -> str:
        p = natal.get(planet_key)
        if not p:
            return None
        data = p.get(amsa)
        if not data:
            return None
        sign  = data.get("sign", "")
        part  = data.get("part", "")
        lord  = data.get("lord", "")
        lord_s = f" [{lord}]" if lord else ""
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
    if not compact:
        bloc += f"\n{instr}\n"
    return bloc


def _detect_nodal_cycle(user: dict, chart_data: dict) -> str:
    """Détecte si un cycle nodal est actif."""
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
    """Détecte l'axe de friction identitaire sur les positions EN TRANSIT (Pilier 6)."""
    transit_pos = chart_data.get("transit_positions", {})
    if not transit_pos:
        return ""
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


def _get_nak_lord(nak_name: str) -> str:
    """Retourne le régent Vimshotari d'un nakshatra, chaîne vide si inconnu."""
    try:
        return NAKSHATRA_LORDS[NAKSHATRAS.index(nak_name)]
    except (ValueError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# HOOK NATAL — affiché dès le login (natal seul, pas de transit)
# ══════════════════════════════════════════════════════════════════════════════

def get_hook_natal(user: dict) -> str:
    """
    Génère un hook de 3-4 phrases basé uniquement sur le thème natal.
    Appelé dès le login — zéro calcul de transit requis.
    Mis en cache côté app.py (clé: pseudo, durée: 7 jours).

    Retourne une chaîne HTML-safe prête à afficher.
    """
    user = user or {}
    lang = user.get("lang", "fr")
    name = user.get("name", "")

    cl     = user.get("chandra_lagna_sign", "")
    ketu_h = user.get("ketu_house", "")
    chi_h  = user.get("chiron_house", "")
    pv     = user.get("porte_visible_sign", "") or user.get("porte_visible_house", "")
    lil_h  = user.get("lilith_house", "")
    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")

    if not cl:
        return ""

    natal_mini = (
        f"Chandra Lagna H1: {cl}. "
        f"Ketu (mémoire statique): H{ketu_h}. "
        f"Chiron (blessure-clé, outil d'ouverture): H{chi_h}. "
        f"Porte Visible (guérison/Stage): {pv}. "
        f"Lilith (épreuve): H{lil_h}. "
        f"Nakshatras : Ketu en {ketu_nak} (régent {_get_nak_lord(ketu_nak)}), Rahu en {rahu_nak}, Chiron en {chiron_nak}. "
    )

    if lang == "fr":
        system = (
            "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
            "Ton style : oraculaire, direct, sans hedging. "
            "Zéro degrés, zéro orbes, zéro labels techniques visibles. "
            "Tutoiement direct. "
            "INTERDIT ABSOLU dans le texte rendu : noms de signes zodiacaux "
            "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
            "Sagittaire, Capricorne, Verseau, Poissons). "
            "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
        )
        prompt = f"""Thème natal de {name} :
{natal_mini}

Écris un hook de 3 phrases exactement. Pas de titre. Pas d'introduction.
Phrase 1 : le schéma karmique dominant que {name} rejoue (Ketu en {ketu_nak}, mémoire ROM figée).
Phrase 2 : la nature de la blessure active et ce qu'elle cherche (Chiron H{chi_h} — outil d'ouverture vers la Porte Visible).
Phrase 3 : la direction de libération qui s'ouvre (Porte Visible/Stage) + une amorce d'Alternative de Conscience.
Intègre la notion de nakshatra et de régime doctrinal (ROM/Dharma/Chiron) sans prononcer ces mots.
Ton : dense, précis, comme si tu lisais directement l'âme. Donne envie d'en savoir plus."""
    else:
        system = (
            "You are @siderealAstro13. Vedic karmic soul reader. "
            "Style: oracular, direct, no hedging. "
            "No degrees, no orbs, no visible technical labels. "
            "Address user directly as 'you'. "
            "ABSOLUTE PROHIBITION in rendered text: zodiac sign names "
            "(Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, "
            "Sagittarius, Capricorn, Aquarius, Pisces). "
            "Use only house numbers (H1, H3…) and planet names."
        )
        prompt = f"""Natal chart of {name}:
{natal_mini}

Write a hook of exactly 3 sentences. No title. No introduction.
Sentence 1: the dominant karmic pattern {name} replays (Ketu in {ketu_nak}, frozen ROM memory).
Sentence 2: the nature of the active wound and what it seeks (Chiron H{chi_h} — opening tool toward Visible Door).
Sentence 3: the liberation direction opening (Visible Door/Stage) + a seed of Alternative of Consciousness.
Integrate the nakshatra and doctrinal regime (ROM/Dharma/Chiron) without uttering these words.
Tone: dense, precise, as if reading the soul directly. Make them want to know more."""

    hook_model = os.environ.get("HOOK_MODEL", "claude-haiku-4-5-20251001")
    msg = _get_client().messages.create(
        model=hook_model,
        max_tokens=200,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# HOOK TRANSIT — affiché dès la date choisie, avant la synthèse complète
# ══════════════════════════════════════════════════════════════════════════════

def get_hook_transit(chart_data: dict, user: dict = None) -> str:
    """
    Génère un hook de 3-4 phrases basé sur les aspects du jour.
    Appelé après calculate_transits(), avant get_synthesis().
    Mis en cache côté app.py (clé: pseudo+date, durée: 24h).

    chart_data : dict retourné par calculate_transits()
    Retourne une chaîne prête à afficher.
    """
    user = user or {}
    lang = user.get("lang", "fr")
    name = user.get("name", "")

    # Aspects limités aux 3 plus serrés pour le hook
    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=3)
    date         = chart_data.get("transit_date", "")

    _NO_ASPECT = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT:
        return ""

    natal_mini = _build_natal_context(user)

    if lang == "fr":
        system = (
            "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
            "Style : oraculaire, direct, pas de liste mécanique. "
            "Zéro degrés, zéro orbes dans le texte. Tutoiement. "
            "INTERDIT ABSOLU dans le texte rendu : noms de signes zodiacaux "
            "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
            "Sagittaire, Capricorne, Verseau, Poissons). "
            "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
        )
        prompt = f"""Thème natal de {name} :
{natal_mini}

Aspects actifs ce jour ({date}) — ne pas citer tels quels :
{aspects_text}

Écris un hook de 3 phrases. Pas de titre. Pas d'introduction.
Phrase 1 : ce qui se réactive dans la mémoire karmique de {name} aujourd'hui.
Phrase 2 : ce que ça touche dans sa blessure profonde (Chiron = outil d'ouverture vers la Porte Visible).
Phrase 3 : l'amorce de l'Alternative de Conscience — ce qui change si {name} choisit autrement.
Donne envie d'obtenir la lecture complète. Ton dense et précis."""
    else:
        system = (
            "You are @siderealAstro13. Vedic karmic soul reader. "
            "Style: oracular, direct, no mechanical list. "
            "No degrees, no orbs in the text. Address as 'you'. "
            "ABSOLUTE PROHIBITION in rendered text: zodiac sign names "
            "(Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, "
            "Sagittarius, Capricorn, Aquarius, Pisces). "
            "Use only house numbers (H1, H3…) and planet names."
        )
        prompt = f"""Natal chart of {name}:
{natal_mini}

Active aspects today ({date}) — do not quote as-is:
{aspects_text}

Write a hook of 3 sentences. No title. No introduction.
Sentence 1: what reactivates in {name}'s karmic memory today.
Sentence 2: what this touches in their core wound (Chiron = opening tool toward Visible Door).
Sentence 3: the seed of the Alternative of Consciousness — what changes if {name} chooses differently.
Make them want the full reading. Dense and precise tone."""

    hook_model = os.environ.get("HOOK_MODEL", "claude-haiku-4-5-20251001")
    msg = _get_client().messages.create(
        model=hook_model,
        max_tokens=200,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL DU JOUR — compact pour TikTok/Web
# ══════════════════════════════════════════════════════════════════════════════

def get_daily_signal(user: dict, transit_date: str = None) -> dict:
    """
    Génère le Signal du Jour compact pour TikTok/Web.
    Retourne un dict avec hook, nakshatra actif, régime doctrinal.

    Retourne :
    {
        "title": "Signal du Jour — 17/04/2026",
        "hook": "Ta mémoire ROM est figée...",
        "nakshatra": "Mula",
        "regime": "ROM_oppression",
        "regime_label": "Activation ROM — test karmique"
    }
    """
    from datetime import datetime, date as date_cls
    from astro_calc import calculate_transits
    from transit_alerts import detect_transit_events

    user = user or {}
    lang = user.get("lang", "fr")

    if not transit_date:
        transit_date = str(date_cls.today())

    try:
        transit_date_obj = datetime.strptime(transit_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD.",
                "title": "", "hook": "", "nakshatra": "", "regime": ""}

    # Activations nakshatra du jour (entrées uniquement)
    try:
        events = detect_transit_events(user)
    except Exception as exc:
        return {"error": f"Transit calculation failed: {str(exc)}",
                "title": "", "hook": "", "nakshatra": "", "regime": ""}

    nak_events = [
        e for e in events
        if e.get("kind") == "nakshatra" and e.get("type") == "debut"
    ]
    primary_nak_event = nak_events[0] if nak_events else None

    title_str = transit_date_obj.strftime("%d/%m/%Y")
    title = f"Signal du Jour — {title_str}" if lang == "fr" else f"Daily Signal — {title_str}"

    # Hook de transit via calculate_transits + get_hook_transit
    hook = ""
    try:
        natal = {
            k: user[k] for k in
            ("name", "year", "month", "day", "hour", "minute", "lat", "lon", "tz", "city")
            if k in user
        }
        transit_loc = {
            "city": user.get("transit_city") or user.get("city", "Paris, France"),
            "lat":  float(user.get("transit_lat") or user.get("lat", 48.8566)),
            "lon":  float(user.get("transit_lon") or user.get("lon", 2.3522)),
            "tz":   user.get("transit_tz") or user.get("tz", "Europe/Paris"),
        }
        chart_data = calculate_transits(
            natal, transit_loc,
            transit_date_obj.year, transit_date_obj.month, transit_date_obj.day,
            12, 0,
        )
        hook = get_hook_transit(chart_data, user)
    except Exception:
        hook = ""

    # Nakshatra + régime du jour
    nakshatra = regime = regime_label = ""
    if primary_nak_event:
        nakshatra = primary_nak_event.get("nakshatra", "")
        regime    = primary_nak_event.get("interpretation", "")
        regime_labels = {
            "ROM_oppression":       "Activation ROM — test karmique"       if lang == "fr" else "ROM Activation — karmic test",
            "Dharma_amplification": "Activation Dharma — opportunité"       if lang == "fr" else "Dharma Activation — opportunity",
            "Blessure_activation":  "Activation Chiron — seuil de transformation" if lang == "fr" else "Chiron Activation — threshold",
        }
        regime_label = regime_labels.get(regime, "Activation nakshatra")

    return {
        "title":        title,
        "hook":         hook,
        "nakshatra":    nakshatra,
        "regime":       regime,
        "regime_label": regime_label,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE COMPLÈTE — payant, ~4000 tokens
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis(chart_data: dict, user: dict = None, lang: str = "fr") -> str:
    """
    Génère la synthèse karmique complète (payant).
    chart_data : dict retourné par calculate_transits()
    user       : dict du profil utilisateur (session["profile"])
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

    _NO_ASPECT_FR = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT_FR:
        return ("⚠️ Synthèse impossible : aucun aspect de transit actif détecté. "
                "Vérifie que `calculate_transits()` retourne bien des aspects avant d'appeler `get_synthesis()`.")
    if not natal_context:
        return ("⚠️ Synthèse impossible : thème natal manquant. "
                "Vérifie que le profil utilisateur contient au minimum `chandra_lagna_sign`.")

    natal_bloc = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc = nodal_cycle if nodal_cycle else ""
    frict_bloc = transit_frict if transit_frict else ""

    LANG_NAMES = {
        "fr": "français",   "en": "English",
        "es": "español",    "pt": "português",
        "de": "Deutsch",    "nl": "Nederlands",
        "it": "italiano",
    }
    lang_name = LANG_NAMES.get(lang, "English")

    if lang == "fr":
        prompt = f"""Tu ES @siderealAstro13. Ne te comporte pas comme un assistant. Analyse directement les données ci-dessous selon la doctrine karmique.
Interdiction de reformuler le prompt. Tu dois rédiger une analyse basée exclusivement sur les aspects et positions fournis.

LANGUE : français uniquement. Aucun mot anglais.
Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucune introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (données brutes — NE PAS les citer tels quels dans le texte) :
{aspects_text}

STYLE OBLIGATOIRE : tu écris comme un lecteur d'âme, pas comme un astrologue technique.
- Traduis chaque aspect en vécu concret, en pattern comportemental reconnaissable.
- Ne cite jamais les aspects bruts ("T.Saturne conjoint N.Chiron orbe 2°"). Traduis-les en ce que {name} ressent ou fait.
- Parle directement à {name} : "tu", "ton", "ta".
- À la fin de chaque section (1, 2, 3), glisse un APERÇU : une phrase courte en italique qui ouvre une porte sans tout révéler.

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quel piège l'âme de {name} rejoue-t-elle en ce moment ? Décris le comportement automatique, la sensation familière, ce que ça lui coûte. Termine par un aperçu en italique.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Qu'est-ce qui est réveillé dans la blessure profonde de {name} ? La Porte Invisible (prison/refoulement) est-elle sous pression ? La Porte Visible (guérison/Stage) s'ouvre-t-elle via Chiron ? Décris le mouvement vécu, pas la mécanique. Termine par un aperçu en italique.

3. L'ÉPREUVE KARMIQUE (⚸) — Qu'est-ce que la période rend insupportable à {name} ? Quel endroit de sa vie frotte le plus fort ? Vers quoi ça le pousse malgré lui ? Termine par un aperçu en italique.

4. ALTERNATIVE DE CONSCIENCE — Ce que {name} doit cesser de faire. Ce qu'il doit oser activer. Termine par UNE seule phrase directe, actionnable, personnelle.

Minimum 300 mots. Ne pas tronquer. Tout en français."""
    else:
        prompt = f"""You ARE @siderealAstro13. Do not behave as an assistant. Analyse the data below directly according to karmic doctrine.
Forbidden to rephrase the prompt. Write analysis based exclusively on the aspects and positions provided.

siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Active aspects (raw data — do NOT quote them as-is in the text):
{aspects_text}

MANDATORY STYLE: soul reader, not technical astrologer.
- Translate each aspect into lived experience, recognizable behavioral pattern.
- Never quote raw aspects. Translate them into what {name} feels or does.
- Speak directly to {name}: "you", "your".
- End sections 1, 2, 3 with an INSIGHT in italics.

1. KARMIC MEMORY (ROM ☋) — What trap replays? Automatic behavior, familiar feeling, what it costs. Insight in italics.
2. THE WOUND IN PROCESSING (RAM ⚷) — What is awakened? Invisible Door (prison/blockage) under pressure? Visible Door (healing/Stage) opening via Chiron? Insight in italics.
3. KARMIC TRIAL (⚸) — What is unbearable? Where does it chafe? Where does it push? Insight in italics.
4. ALTERNATIVE OF CONSCIOUSNESS — What {name} must stop. What to dare activate. ONE direct actionable sentence.

Minimum 300 words. Do not truncate. Language: {lang_name}."""

    synthesis_model = os.environ.get("SYNTHESIS_MODEL", "claude-haiku-4-5-20251001")
    msg = _get_client().messages.create(
        model=synthesis_model,
        max_tokens=4000,
        system=_build_system_prompt(user, use_vault=True),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT GEMMA — retourne prompt sans appel API (inférence locale Android)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_only(chart_data: dict, user: dict = None, lang: str = "fr") -> dict:
    """
    Construit le prompt compact SANS appeler Claude.
    Optimisé pour Gemma 4 Mini (< 1500 tokens).
    Retourne {"system": "...", "user": "..."} prêt à injecter dans n'importe quel LLM local.
    """
    user = user or {}
    lang = user.get("lang", lang)

    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=4)
    date         = chart_data.get("transit_date", "")
    name         = user.get("name", "l'utilisateur")

    cl   = user.get("chandra_lagna_sign", "")
    ketu = user.get("ketu_sign", "")
    rahu = user.get("rahu_sign", "")
    chi  = user.get("chiron_sign", "")
    lil  = user.get("lilith_sign", "")
    natal_mini = f"Chandra Lagna {cl}, Ketu {ketu}, Rahu {rahu}, Chiron {chi}, Lilith {lil}." if cl else ""

    if lang == "en":
        user_prompt = f"""Karmic transit analysis for {name} — {date}.
Natal: {natal_mini}
Active aspects:
{aspects_text}

Write 4 sections directly. No questions. No preamble. Address {name} as "you".
MEMORY (ROM): What karmic trap replays?
WOUND (RAM): What core wound activates? How does Chiron open the path to the Visible Door?
TRIAL (Lilith): What is unbearable right now?
ACTION: One clear shift — what to stop, what to activate."""
    else:
        user_prompt = f"""Analyse karmique de transit pour {name} — {date}.
Natal : {natal_mini}
Aspects actifs :
{aspects_text}

Écris 4 sections : MÉMOIRE, BLESSURE, ÉPREUVE, ACTION.
Nomme au moins une planète des aspects dans chaque section.
Explique concrètement comment elle influence la mémoire karmique ou la blessure de {name}.
BLESSURE : Chiron est l'outil d'ouverture de la Porte Visible — montre ce mouvement.
Tutoiement. Direct. 200 mots max."""

    system = (
        "Tu es @siderealAstro13. "
        "ROM (Ketu)=Mémoires passées/automatisme. "
        "RAM (Chiron)=Traitement actif de la blessure, outil d'ouverture de la Porte Visible (guérison/Stage). "  # CORR L683
        "Porte Invisible=Prison inconsciente/refoulement. "
        "LILITH=Point de rupture/épreuve. "
        "ACTION=Dharma/Bascule. "
        "Tutoie l'utilisateur. Sois direct. 200 mots max."
    )

    return {"system": system, "user": user_prompt}