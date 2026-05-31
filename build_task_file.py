"""
build_task_file.py — Karmic Gochara
Compile le vault doctrinal + données natales en un fichier .task
prêt à être consommé par Gemma 3 1B int4 sur Android (OPFS).

Usage dans app.py :
    from build_task_file import build_task_file
    task = build_task_file(user, natal_data, transit_data)
"""

import hashlib
import json
from datetime import UTC, datetime

# ─────────────────────────────────────────────
# VAULT CORE — ~150 tokens, toujours injecté
# ─────────────────────────────────────────────

VAULT_CORE = """# Karmic Gochara — Doctrine Core
Jyotish sidéral DK. Chandra Lagna = H1. Nœuds vrais. Orbe max 3°.

KETU = mémoire ROM. Loop passé. Automatisme. Ne pas renforcer — identifier → interrompre.
RAHU = Dharma. Direction évolutive. Inconfort fertile.
PV = mi-point petit arc Saturne→Uranus. Guérison consciente. Sortie du loop.
PI = PV+180°. Prison inconsciente. Jamais une destination.
CHIRON = clé de la PV. Blessure originelle. Transmutation par auto-pardon. Pas la PI.
LILITH = épreuve limite. Rend la PI insupportable. Propulse vers le Dharma.
SATURNE = dette karmique. Structure nécessaire. Atterrissage forcé.
JUPITER = cadeaux karmiques. Talents hérités. Expansion accessible.

SORTIE OBLIGATOIRE :
[BLOCAGE] 2 phrases. Phénomène vécu. Zéro nom de planète. Zéro signe zodiacal.
[ALTERNATIVE] 1 phrase : verbe impératif + abandon du schéma + ce qui s'ouvre.
Ton : oraculaire. Direct. Zéro encouragement. Zéro hedging. Zéro degré."""

# ─────────────────────────────────────────────
# RÈGLES DE SORTIE — ~100 tokens, toujours injecté
# ─────────────────────────────────────────────

VAULT_RULES = """# Règles absolues
Tu reçois un JSON pré-analysé. Tu rédiges. Tu ne calcules pas.
JAMAIS : degrés · signes · noms de planètes dans [BLOCAGE] · "peut-être" · "il semblerait"
JAMAIS : dépasser 150 mots · consoler · encourager · expliquer la doctrine
TOUJOURS : phénomène psychologique concret · Alternative de Conscience en dernière ligne
FORMAT valide :
**[BLOCAGE]** [2 phrases]
**[ALTERNATIVE]** [verbe impératif] + [abandon] — [ce qui s'ouvre]"""

# ─────────────────────────────────────────────
# NAKSHATRAS — lookup par degré sidéral
# ─────────────────────────────────────────────

NAKSHATRAS = [
    ("Ashwini",           0.0,   13.333, "ROM: urgence perpétuelle, peur de l'inertie. RAM: impuissance, intervention trop tardive. DHARMA: vitesse ≠ direction."),
    ("Bharani",          13.333, 26.667, "ROM: culpabilité existentielle, responsabilités portées seul. RAM: blessure de survie. DHARMA: enfanter sans se sacrifier."),
    ("Krittika",         26.667, 40.0,   "ROM: autorité tranchante, séparation nécessaire. RAM: peur de blesser en aidant. DHARMA: discernement protecteur."),
    ("Rohini",           40.0,   53.333, "ROM: nostalgie d'un paradis perdu. RAM: blessure de convoitise. DHARMA: croître sans dépendre de l'admiration."),
    ("Mrigashira",       53.333, 66.667, "ROM: errance spirituelle. RAM: insatisfaction chronique. DHARMA: l'objet de la quête est intérieur."),
    ("Ardra",            66.667, 80.0,   "ROM: destructions massives, chaos émotionnel. RAM: trahison ou abandon brutal. DHARMA: souffrance → sagesse."),
    ("Punarvasu",        80.0,   93.333, "ROM: rôle de protecteur ou gardien. RAM: peur de ne pas pouvoir revenir. DHARMA: donner depuis une source."),
    ("Pushya",           93.333, 106.667,"ROM: responsabilités sacerdotales. RAM: s'être oublié pour les autres. DHARMA: structures qui nourrissent l'âme."),
    ("Ashlesha",        106.667, 120.0,  "ROM: manipulations, secrets toxiques. RAM: méfiance profonde. DHARMA: intuition laser pour guérir."),
    ("Magha",           120.0,   133.333,"ROM: gloire passée, honneur ancestral lourd. RAM: sentiment d'imposture. DHARMA: autorité avec humilité."),
    ("Purva Phalguni",  133.333, 146.667,"ROM: nostalgie d'insouciance et luxe. RAM: peur que la vie soit un décor vide. DHARMA: créer du sens."),
    ("Uttara Phalguni", 146.667, 160.0,  "ROM: alliances stratégiques pour préserver l'ordre. RAM: blessure du second rôle. DHARMA: service désintéressé."),
    ("Hasta",           160.0,   173.333,"ROM: manipulation de la matière, calculs de pouvoir. RAM: peur de perdre le contrôle. DHARMA: maîtrise = danse avec les cycles."),
    ("Chitra",          173.333, 186.667,"ROM: perfection esthétique superficielle. RAM: peur d'être une façade vide. DHARMA: aligner esprit et forme."),
    ("Swati",           186.667, 200.0,  "ROM: nomadisme, fuite de l'engagement. RAM: blessure de l'isolement. DHARMA: racines intérieures."),
    ("Vishakha",        200.0,   213.333,"ROM: ambitions dévorantes, rivalités. RAM: victoire toujours incomplète. DHARMA: gratitude."),
    ("Anuradha",        213.333, 226.667,"ROM: allégeances secrètes. RAM: trahison amicale. DHARMA: dévotion inconditionnelle."),
    ("Jyeshtha",        226.667, 240.0,  "ROM: abus de pouvoir par peur. RAM: peur d'être détrôné. DHARMA: vulnérabilité assumée."),
    ("Mula",            240.0,   253.333,"ROM: destructions radicales, auto-sabotage. RAM: déracinement. DHARMA: détruire le corrompu pour libérer l'essence."),
    ("Purva Ashadha",   253.333, 266.667,"ROM: guerres de religion, dogmes. RAM: aveuglement, faux combat. DHARMA: purification."),
    ("Uttara Ashadha",  266.667, 280.0,  "ROM: conquêtes solitaires sans partage. RAM: isolement au sommet. DHARMA: alliance."),
    ("Shravana",        280.0,   293.333,"ROM: réceptacle passif aux ordres. RAM: peur de ne pas être entendu. DHARMA: écoute intérieure."),
    ("Dhanishta",       293.333, 306.667,"ROM: richesses matérielles vides. RAM: symphonie interrompue. DHARMA: danser avec l'imprévisible."),
    ("Shatabhisha",     306.667, 320.0,  "ROM: paria détenteur de secrets. RAM: stigmatisation, peur d'être trop bizarre. DHARMA: acceptation."),
    ("Purva Bhadrapada",320.0,   333.333,"ROM: fanatisme destructeur. RAM: peur de sa propre puissance. DHARMA: alchimie de la colère."),
    ("Uttara Bhadrapada",333.333,346.667,"ROM: ascèse prolongée, hibernation. RAM: peur d'être oublié. DHARMA: action ancrée."),
    ("Revati",          346.667, 360.0,  "ROM: guide pour les égarés. RAM: hypersensibilité à la cruauté. DHARMA: accompagner les fins de cycles."),
]

# ─────────────────────────────────────────────
# MAISONS CHANDRA LAGNA
# ─────────────────────────────────────────────

HOUSE_CONTEXTS = {
    1:  "H1: identité incarnée. ROM: ne pas appartenir à son corps/image. RAM: exister trop ou pas assez. DHARMA: aligner état intérieur et expression.",
    2:  "H2: ressources, valeurs. ROM: privation ou détachement forcé. RAM: peur que rien ne suffise. DHARMA: valeur propre indépendante du clan.",
    3:  "H3: communication, mental. ROM: efforts vains, messages non reçus. RAM: peur d'être mal compris. DHARMA: agitation → initiative.",
    4:  "H4: racines, sécurité. ROM: nostalgie du foyer idéal. RAM: difficulté à se sentir chez soi. DHARMA: base émotionnelle inébranlable.",
    5:  "H5: créativité, joie. ROM: talent déjà vu, futilité. RAM: peur de ne pas être aimé pour son génie. DHARMA: créer sans validation.",
    6:  "H6: service, santé. ROM: luttes répétitives, résoudre les problèmes des autres. RAM: fragilité somatisée. DHARMA: adversité → purification.",
    7:  "H7: relation, miroir. ROM: désillusion, union impossible. RAM: peur de se perdre ou d'être abandonné. DHARMA: équilibre soi/autre.",
    8:  "H8: transformation profonde. ROM: crises violentes, secrets de pouvoir. RAM: peur de l'effondrement. DHARMA: mort/renaissance sans peur.",
    9:  "H9: sens, Dharma supérieur. ROM: scepticisme envers les dogmes. RAM: sentiment d'abandon par le divin. DHARMA: incarner sa propre vérité.",
    10: "H10: mission publique. ROM: désintérêt pour les titres ou pouvoir déjà exercé. RAM: peur de l'échec public. DHARMA: agir par nature profonde.",
    11: "H11: collectif, idéaux. ROM: outsider dans les réseaux. RAM: peur de ne pas trouver sa tribu. DHARMA: servir les idéaux collectifs.",
    12: "H12: dissolution, archives. ROM: retrait inné, vies monacales. RAM: peur de s'éteindre. DHARMA: solitude → plénitude.",
}

# ─────────────────────────────────────────────
# PLANET KEYWORDS — 1 ligne par planète active
# ─────────────────────────────────────────────

PLANET_KEYWORDS = {
    "Pluton":   "mort symbolique · pouvoir à traverser · transformation irréversible",
    "Neptune":  "perte de repères · idéalisation piège · perméabilité excessive",
    "Uranus":   "rupture nécessaire · éveil soudain · originalité à incarner",
    "Saturne":  "dette à honorer · restriction structurante · atterrissage forcé",
    "Chiron":   "blessure originelle · clé de la Porte Visible · transmutation par l'aveu",
    "Jupiter":  "talent hérité · expansion accessible · cadeau à recevoir",
    "Mars":     "impulsion non canalisée · conflit intérieur · énergie à structurer",
    "Vénus":    "attachement compensatoire · valeur à redéfinir · attraction miroir",
    "Mercure":  "récit limitant · dispersion mentale · reformulation nécessaire",
    "Soleil":   "identité en transition · visibilité à assumer · ego en restructuration",
    "Lune":     "mémoire émotionnelle · réaction conditionnée · besoin de sécurité archaïque",
    "Ketu":     "répétition automatique · fuite dans le familier · loop de moindre résistance",
    "Rahu":     "appel évolutif · inconfort fertile · direction nouvelle",
    "Lilith":   "vérité radicale · refus du compromis · épreuve limite",
}

ASPECT_SIGNALS = {
    "conjonction": "Point de bascule. Fusion des deux énergies. Crise ou saut.",
    "opposition":  "Conflit conscient. L'autre reflète le loop. Choix forcé.",
    "carré":       "Blocage actif. La résistance est le signal. Ne pas contourner.",
    "trigone":     "Talent latent accessible. Risque : ne pas le saisir.",
    "sextile":     "Fenêtre courte. Agir maintenant.",
    "quinconce":   "Malaise diffus. Correction subtile requise. Rien ne colle.",
}

SEMANTIC_CLUSTERS = {
    "ROM_loop":    ["habitude", "familier", "peur de perdre", "réaction automatique"],
    "RAM_process": ["douleur utile", "conscience de la plaie", "nettoyage", "clé"],
    "STAGE_action":["visibilité", "exposition", "rôle public", "incarnation"],
    "DHARMA_shift":["oser l'inconnu", "poussée", "appel du futur", "vérité"],
    "PI_trap":     ["enfermement", "automatisme défensif", "mur invisible", "prison confortable"],
}

# ─────────────────────────────────────────────
# LOOKUP FUNCTIONS
# ─────────────────────────────────────────────

def get_nakshatra(longitude_sid: float) -> tuple[str, str]:
    """Retourne (nom, contexte_doctrinal) pour un degré sidéral 0-360."""
    lon = longitude_sid % 360
    for name, start, end, context in NAKSHATRAS:
        if start <= lon < end:
            return name, context
    return "Revati", NAKSHATRAS[26][3]  # fallback 359.999


def get_active_clusters(natal: dict, transit: dict) -> list[str]:
    """Détermine les clusters sémantiques actifs selon le contexte."""
    clusters = []

    # ROM toujours présent (Ketu natal)
    clusters.append("ROM_loop")

    # Stage activé si transit sur maison du Stage
    if transit.get("house") == natal.get("stage_house"):
        clusters.append("STAGE_action")

    # RAM activé si transit implique Chiron ou PI
    planet = transit.get("planet", "")
    if planet in ["Chiron", "Saturne", "Uranus"] or transit.get("house") == natal.get("chiron_house"):
        clusters.append("RAM_process")

    # PI trap si transit sur maison PI
    if transit.get("house") == natal.get("pi_house"):
        clusters.append("PI_trap")

    # Dharma shift si transit sur Rahu ou maison Rahu
    if planet in ["Rahu", "Jupiter"] or transit.get("house") == natal.get("rahu_house"):
        clusters.append("DHARMA_shift")

    return list(dict.fromkeys(clusters))  # dédoublonner, ordre préservé


def build_gemma_system_prompt(natal: dict, transit: dict, lang: str = "fr") -> str:
    """
    Assemble le system prompt compressé pour Gemma 1B.
    Budget cible : 450-550 tokens.
    """
    parts = [VAULT_CORE, "\n---\n", VAULT_RULES]

    # Nakshatra Ketu (ROM natal)
    ketu_lon = natal.get("ketu_longitude", 0.0)
    ketu_nak, ketu_ctx = get_nakshatra(ketu_lon)
    parts.append(f"\n---\n# ROM Natal ({ketu_nak})\n{ketu_ctx}")

    # Nakshatra Chiron (RAM natal)
    chiron_lon = natal.get("chiron_longitude", 0.0)
    chiron_nak, chiron_ctx = get_nakshatra(chiron_lon)
    parts.append(f"\n# RAM Natal ({chiron_nak})\n{chiron_ctx}")

    # Maison transit active
    transit_house = transit.get("house")
    if transit_house and transit_house in HOUSE_CONTEXTS:
        parts.append(f"\n# Maison activée\n{HOUSE_CONTEXTS[transit_house]}")

    # Planète en transit — keyword 1 ligne
    planet = transit.get("planet", "")
    if planet in PLANET_KEYWORDS:
        parts.append(f"\n# Planète active : {planet}\n{PLANET_KEYWORDS[planet]}")

    # Aspect — signal doctrinal
    aspect = transit.get("aspect", "").lower()
    if aspect in ASPECT_SIGNALS:
        parts.append(f"\n# Aspect : {aspect}\n{ASPECT_SIGNALS[aspect]}")

    # Langue
    if lang == "en":
        parts.append("\n---\nRespond in English. Same format. Same rules.")

    return "".join(parts)


# ─────────────────────────────────────────────
# MAPPING astro_calc.py → build_task_file
# ─────────────────────────────────────────────

def _house_of(planet_lon: float, asc_lon: float) -> int:
    """
    Calcule la maison Chandra Lagna d'une planète.
    ASC = début du signe de la Lune natale (multiple de 30°).
    Maison 1 = signe de la Lune. Maison 2 = signe suivant. Etc.
    """
    diff = (planet_lon - asc_lon) % 360
    return int(diff / 30) + 1


def extract_natal_for_task(calc_result: dict) -> dict:
    """
    Convertit le dict retourné par calculate_transits() (clé "natal")
    en natal_data compatible avec build_task_file().

    Args:
        calc_result : dict complet retourné par calculate_transits()
                      (contient "natal", "transits", "aspects")

    Returns:
        natal_data dict avec toutes les clés attendues par build_task_file()
    """
    natal = calc_result.get("natal", {})

    # Récupère les longitudes brutes
    def lon(key):
        p = natal.get(key)
        return p["lon_raw"] if p else 0.0

    asc_lon      = lon("ASC ↑")
    ketu_lon     = lon("Nœud Sud ☋")
    rahu_lon     = lon("Nœud Nord ☊")
    chiron_lon   = lon("Chiron ⚷")
    saturn_lon   = lon("Saturne ♄")
    uranus_lon   = lon("Uranus ♅")
    pv_lon       = lon("Porte Visible ⊙")
    pi_lon       = lon("Porte Invisible ⊗")

    return {
        # Longitudes sidérales 0-360
        "ketu_longitude":    ketu_lon,
        "chiron_longitude":  chiron_lon,
        "saturn_longitude":  saturn_lon,
        "uranus_longitude":  uranus_lon,
        "pv_longitude":      pv_lon,
        "pi_longitude":      pi_lon,
        "rahu_longitude":    rahu_lon,
        "asc_longitude":     asc_lon,

        # Maisons Chandra Lagna
        "ketu_house":    _house_of(ketu_lon,   asc_lon),
        "chiron_house":  _house_of(chiron_lon,  asc_lon),
        "pv_house":      _house_of(pv_lon,      asc_lon),
        "pi_house":      _house_of(pi_lon,      asc_lon),
        "rahu_house":    _house_of(rahu_lon,    asc_lon),
        "stage_house":   _house_of(pv_lon,      asc_lon),  # Stage = PV house
    }


def extract_dominant_transit(calc_result: dict) -> dict:
    """
    Extrait le transit dominant depuis les aspects calculés.
    Priorité : planètes lentes > orbe le plus petit.
    Retourne un dict transit_data compatible avec build_task_file().
    """
    aspects = calc_result.get("aspects", [])
    natal   = calc_result.get("natal", {})

    # Priorité planètes lentes
    PRIORITY = ["Pluton ♇", "Neptune ♆", "Uranus ♅", "Saturne ♄",
                "Chiron ⚷", "Jupiter ♃", "Rahu", "Lilith ⚸",
                "Mars ♂", "Vénus ♀", "Mercure ☿", "Soleil ☀", "Lune ☽"]

    def priority(asp):
        t = asp["transit_planet"]
        for i, p in enumerate(PRIORITY):
            if p in t:
                return i
        return 99

    if not aspects:
        return {"planet": "", "house": 1, "aspect": "", "target": ""}

    # Trier par priorité puis orbe
    sorted_asp = sorted(aspects, key=lambda x: (priority(x), x["orb"]))
    best = sorted_asp[0]

    # Calculer la maison du transit
    asc_lon = natal.get("ASC ↑", {})
    asc_lon = asc_lon.get("lon_raw", 0.0) if asc_lon else 0.0

    transits = calc_result.get("transits", {})
    t_planet = best["transit_planet"]
    t_data   = transits.get(t_planet, {})
    t_lon    = t_data.get("lon_raw", 0.0) if t_data else 0.0
    t_house  = _house_of(t_lon, asc_lon) if t_lon else 1

    # Nom court planète (sans symbole)
    planet_clean = t_planet.split(" ")[0] if t_planet else ""

    # Aspect court
    aspect_clean = best["aspect"].split(" ")[0].lower()

    return {
        "planet":  planet_clean,
        "house":   t_house,
        "aspect":  aspect_clean,
        "target":  best["natal_planet"],
        "orb":     best["orb"],
    }


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────

def build_task_file(user: dict, natal_data: dict, transit_data: dict) -> dict:
    """
    Construit le fichier .task complet prêt pour OPFS Android.

    Args:
        user        : dict profil Google Sheets {name, lang, ...}
        natal_data  : dict depuis astro_calc.py {ketu_longitude, chiron_longitude,
                      ketu_house, chiron_house, stage_house, pv_house, pi_house,
                      rahu_house, pv_longitude, pi_longitude, ...}
        transit_data: dict transit actif {planet, house, aspect, target, ...}

    Returns:
        dict — le .task complet (à sérialiser en JSON)
    """
    lang = user.get("lang", "fr")

    # Lookup Nakshatras
    ketu_nak, _ = get_nakshatra(natal_data.get("ketu_longitude", 0.0))
    chiron_nak, _ = get_nakshatra(natal_data.get("chiron_longitude", 0.0))

    # Clusters actifs
    clusters = get_active_clusters(natal_data, transit_data)

    # System prompt compilé
    gemma_prompt = build_gemma_system_prompt(natal_data, transit_data, lang)

    # Payload JSON pour Gemma (données factuelles, pas de doctrine)
    gemma_payload = {
        "prenom": user.get("name", ""),
        "lang": lang,
        "natal": {
            "ketu_house": natal_data.get("ketu_house"),
            "chiron_house": natal_data.get("chiron_house"),
            "stage_house": natal_data.get("stage_house"),
            "pv_house": natal_data.get("pv_house"),
            "pi_house": natal_data.get("pi_house"),
            "nakshatra_ketu": ketu_nak,
            "nakshatra_chiron": chiron_nak,
        },
        "transit_actif": transit_data,
        "clusters_actifs": clusters,
        "tone": "oraculaire · direct · zéro encouragement",
    }

    # Fingerprint (invalidation cache si natal change)
    fingerprint_source = f"{natal_data.get('ketu_longitude')}{natal_data.get('chiron_longitude')}{natal_data.get('pv_longitude')}"
    fingerprint = hashlib.sha256(fingerprint_source.encode()).hexdigest()[:12]

    task = {
        "version": "1.0-GEMMA-100",
        "project": "Gochara Karmique",
        "generated_at": datetime.now(UTC).isoformat(),
        "user": user.get("name", ""),
        "lang": lang,
        "fingerprint": fingerprint,
        "gemma_system_prompt": gemma_prompt,
        "gemma_payload": gemma_payload,
        # Données brutes conservées pour debug / régénération
        "_natal_raw": natal_data,
    }

    return task


# ─────────────────────────────────────────────
# ROUTE Flask — à ajouter dans app.py
# ─────────────────────────────────────────────

FLASK_ROUTE = '''
# ── Dans app.py ──────────────────────────────────────────
from build_task_file import build_task_file, extract_natal_for_task, extract_dominant_transit
import json

@app.route("/generate_task")
def generate_task():
    """Génère et retourne le fichier .task pour l\'utilisateur connecté."""
    if "user" not in session:
        return jsonify({"error": "not_authenticated"}), 401

    user = get_user_profile(session["user"])  # depuis profiles.py

    # Calcul natal via astro_calc.py
    now = datetime.now()
    calc_result = calculate_transits(
        natal={
            "year":   int(user["birth_year"]),
            "month":  int(user["birth_month"]),
            "day":    int(user["birth_day"]),
            "hour":   int(user["birth_hour"]),
            "minute": int(user["birth_minute"]),
            "lat":    float(user["birth_lat"]),
            "lon":    float(user["birth_lon"]),
            "tz":     user["birth_tz"],
        },
        transit_loc=TRANSIT_LOC_DEFAULT,
        year=now.year, month=now.month, day=now.day,
        hour=now.hour, minute=now.minute,
    )

    natal_data   = extract_natal_for_task(calc_result)
    transit_data = extract_dominant_transit(calc_result)

    task = build_task_file(user, natal_data, transit_data)

    response = make_response(json.dumps(task, ensure_ascii=False, indent=2))
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = f\'attachment; filename="karmic_{user["name"]}.task"\'
    return response
'''

# ─────────────────────────────────────────────
# TEST LOCAL
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Simule le dict retourné par calculate_transits() pour Jérôme natal
    # Ketu Gémeaux ~7° → lon sidérale ~67°
    # Chiron Poissons ~19° → lon sidérale ~349°
    # Lune Bélier → ASC = 0° (début Bélier)
    # PV Lion H5 → ~130°, PI Verseau H11 → ~310°

    mock_calc_result = {
        "natal": {
            "ASC ↑":            {"lon_raw": 0.0,   "retrograde": False, "nakshatra": "Ashwini",  "pada": 1, "nak_lord": "Ketu",    "display": "♈ Bélier 0°00′",   "d9": None, "d10": None, "d60": None},
            "Nœud Sud ☋":       {"lon_raw": 66.9,  "retrograde": False, "nakshatra": "Ardra",    "pada": 2, "nak_lord": "Rahu",    "display": "♊ Gémeaux 6°54′",  "d9": None, "d10": None, "d60": None},
            "Nœud Nord ☊":      {"lon_raw": 246.9, "retrograde": False, "nakshatra": "Vishakha", "pada": 3, "nak_lord": "Jupiter", "display": "♐ Sagittaire 6°54′","d9": None, "d10": None, "d60": None},
            "Chiron ⚷":         {"lon_raw": 349.5, "retrograde": True,  "nakshatra": "Revati",   "pada": 4, "nak_lord": "Mercure", "display": "♓ Poissons 19°30′", "d9": None, "d10": None, "d60": None},
            "Saturne ♄":        {"lon_raw": 90.0,  "retrograde": False, "nakshatra": "Punarvasu","pada": 1, "nak_lord": "Jupiter", "display": "♋ Cancer 0°00′",   "d9": None, "d10": None, "d60": None},
            "Uranus ♅":         {"lon_raw": 190.0, "retrograde": False, "nakshatra": "Swati",    "pada": 2, "nak_lord": "Rahu",    "display": "♎ Balance 10°00′",  "d9": None, "d10": None, "d60": None},
            "Porte Visible ⊙":  {"lon_raw": 140.0, "retrograde": False, "nakshatra": "Magha",    "pada": 3, "nak_lord": "Ketu",    "display": "♌ Lion 20°00′",     "d9": None, "d10": None, "d60": None},
            "Porte Invisible ⊗":{"lon_raw": 320.0, "retrograde": False, "nakshatra": "Shatabhisha","pada":1,"nak_lord": "Rahu",   "display": "♒ Verseau 20°00′",  "d9": None, "d10": None, "d60": None},
            "Jupiter ♃":        {"lon_raw": 290.0, "retrograde": False, "nakshatra": "Uttara Ashadha","pada":2,"nak_lord":"Soleil","display": "♑ Capricorne 20°00′","d9":None,"d10": None, "d60": None},
        },
        "transits": {
            "Saturne ♄": {"lon_raw": 1.0, "retrograde": False, "nakshatra": "Ashwini", "pada": 1, "nak_lord": "Ketu", "display": "♈ Bélier 1°00′", "d9": None, "d10": None, "d60": None},
        },
        "aspects": [
            {
                "transit_planet":  "Saturne ♄",
                "transit_display": "♈ Bélier 1°00′",
                "transit_nak":     "Ashwini",
                "transit_pada":    1,
                "natal_planet":    "ASC ↑",
                "natal_display":   "♈ Bélier 0°00′",
                "natal_nak":       "Ashwini",
                "aspect":          "Conjonction ☌",
                "orb":             1.0,
                "retrograde":      False,
            }
        ],
    }

    test_user = {"name": "jero", "lang": "fr"}

    natal_data   = extract_natal_for_task(mock_calc_result)
    transit_data = extract_dominant_transit(mock_calc_result)

    print("=== natal_data extrait ===")
    print(json.dumps(natal_data, ensure_ascii=False, indent=2))
    print("\n=== transit_data extrait ===")
    print(json.dumps(transit_data, ensure_ascii=False, indent=2))

    task = build_task_file(test_user, natal_data, transit_data)

    print("\n=== .task généré ===")
    print(json.dumps(task, ensure_ascii=False, indent=2))
    print(f"\n=== System prompt ({len(task['gemma_system_prompt'].split())} mots) ===")
    print(task["gemma_system_prompt"])
    print(f"\n=== Clusters actifs : {task['gemma_payload']['clusters_actifs']} ===")
    print(f"\n=== Maisons : Ketu H{natal_data['ketu_house']} · Chiron H{natal_data['chiron_house']} · PV H{natal_data['pv_house']} · PI H{natal_data['pi_house']} ===")