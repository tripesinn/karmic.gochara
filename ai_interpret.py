"""
ai_interpret.py — Interprétation karmique védique via Claude API
Gochara Karmique — @siderealAstro13 • Architecture multi-utilisateurs
"""

import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# ── Base de connaissances Nakshatras (planètes karmiquement critiques) ────────
NAKSHATRA_KARMA = {
    # ── KETU / NŒUD SUD (ROM) ─────────────────────────────────────────────
    "Ashwini": {
        "regent": "Ketu", "element": "Feu",
        "rom_theme": "Sauveur compulsif, guérison impulsive, héroïsme automatique",
        "ram_activation": "Chiron ici : blessure du sauvetage — tu guéris les autres pour éviter ta propre blessure",
        "ketu_ici": "ROM en mode guerrier-guérisseur : patterns d'urgence des vies passées",
        "rahu_ici": "Dharma d'incarnation lente, patience, recevoir avant de donner",
        "saturne_ici": "Karma d'action précipitée — ralentir EST la leçon",
        "chiron_ici": "Blessure de l'impuissance au moment critique — transmuter en présence calme",
        "stage": "Agir depuis le centre, pas depuis l'urgence",
    },
    "Bharani": {
        "regent": "Vénus", "element": "Feu",
        "rom_theme": "Porteur du poids des autres, sacrifice chronique, retenue du désir",
        "ram_activation": "Chiron ici : blessure de ce qui ne peut pas naître — deuil d'un potentiel",
        "ketu_ici": "ROM de la mort et renaissance : patterns de retenue créatrice accumulée",
        "rahu_ici": "Dharma d'assumer pleinement sa créativité sans culpabilité",
        "saturne_ici": "Karma de responsabilité excessive — apprendre à déléguer le poids",
        "chiron_ici": "Blessure du porteur : tu portes ce qui ne t'appartient pas",
        "stage": "Créer depuis la joie, pas depuis l'obligation",
    },
    "Krittika": {
        "regent": "Soleil", "element": "Feu",
        "rom_theme": "Critique intérieure acérée, perfection punitive, autorité blessée",
        "ram_activation": "Chiron ici : blessure de l'autorité paternelle — le juge intérieur",
        "ketu_ici": "ROM du discernement tranchant : vies de prêtres, juges, chirurgiens",
        "rahu_ici": "Dharma de brûler l'inauthentique avec douceur",
        "saturne_ici": "Karma de jugement — la sévérité se retourne contre soi",
        "chiron_ici": "Blessure de la lumière coupée — potentiel solaire réprimé",
        "stage": "Illuminer sans brûler — discerner sans trancher",
    },
    "Rohini": {
        "regent": "Lune", "element": "Terre",
        "rom_theme": "Attachement sensuel, fixation sur la beauté, possession affective",
        "ram_activation": "Chiron ici : blessure de l'abondance refusée ou perdue",
        "ketu_ici": "ROM de la fertilité : vies d'artistes, agriculteurs, mères",
        "rahu_ici": "Dharma de créer sans s'accrocher à la forme",
        "saturne_ici": "Karma d'abondance bloquée — restriction des plaisirs comme leçon",
        "chiron_ici": "Blessure de l'enracinement : tu ne te permets pas de fleurir",
        "stage": "S'ancrer dans le présent matériel sans y être emprisonné",
    },
    "Mrigashira": {
        "regent": "Mars", "element": "Terre",
        "rom_theme": "Chercheur éternel, fuite vers le prochain horizon, insatisfaction chronique",
        "ram_activation": "Chiron ici : blessure de la quête — chercher ce qui est déjà là",
        "ketu_ici": "ROM du chasseur : vies de nomades, explorateurs, chercheurs de sens",
        "rahu_ici": "Dharma d'habiter pleinement un lieu, une voie, une relation",
        "saturne_ici": "Karma de dispersion — la discipline de la profondeur",
        "chiron_ici": "Blessure de l'incomplétude : jamais assez loin, jamais assez",
        "stage": "Trouver le sacré dans l'immobile",
    },
    "Ardra": {
        "regent": "Rahu", "element": "Terre",
        "rom_theme": "Tempête émotionnelle, destruction créatrice, chaos comme refuge",
        "ram_activation": "Chiron ici : blessure de la tempête intérieure non intégrée",
        "ketu_ici": "ROM du chaos transformateur : vies de révolutionnaires, chamans de crise",
        "rahu_ici": "Dharma de canaliser la tempête en innovation",
        "saturne_ici": "Karma de la destruction non maîtrisée — apprendre à reconstruire",
        "chiron_ici": "Blessure du radical : tu détruis avant qu'on te détruise",
        "stage": "Être l'œil du cyclone, pas le vent lui-même",
    },
    "Punarvasu": {
        "regent": "Jupiter", "element": "Eau",
        "rom_theme": "Retour compulsif, renaissance sans intégration, optimisme défensif",
        "ram_activation": "Chiron ici : blessure du retour — peur que ce qui était ne revienne jamais",
        "ketu_ici": "ROM de l'éternel recommencement : maître de la renaissance cyclique",
        "rahu_ici": "Dharma de l'expansion sans régression",
        "saturne_ici": "Karma des cycles répétés — identifier et clore la boucle",
        "chiron_ici": "Blessure de l'exil : tu cherches un foyer que tu portes en toi",
        "stage": "Revenir à soi-même comme acte de dharma",
    },
    "Pushya": {
        "regent": "Saturne", "element": "Eau",
        "rom_theme": "Nourrisseur compulsif, auto-sacrifice, besoin d'être nécessaire",
        "ram_activation": "Chiron ici : blessure du soin — donner sans jamais recevoir",
        "ketu_ici": "ROM du gardien : vies de prêtres, parents, gardiens communautaires",
        "rahu_ici": "Dharma de recevoir et permettre à l'autre de donner",
        "saturne_ici": "Karma de la responsabilité nourricière — épuisement comme signal",
        "chiron_ici": "Blessure de la faim spirituelle : tu nourris tout sauf ton âme",
        "stage": "Se nourrir soi-même pour nourrir juste",
    },
    "Ashlesha": {
        "regent": "Mercure", "element": "Eau",
        "rom_theme": "Contrôle subtil, manipulation inconsciente, intelligence défensive",
        "ram_activation": "Chiron ici : blessure de la trahison — intelligence utilisée pour se protéger",
        "ketu_ici": "ROM du serpent : vies de magiciens, guérisseurs de venin, diplomates",
        "rahu_ici": "Dharma d'utiliser la sagesse du serpent au service de l'éveil",
        "saturne_ici": "Karma du contrôle — lâcher-prise comme acte courageux",
        "chiron_ici": "Blessure du non-dit : la vérité tue ou guérit — tu choisis la silence",
        "stage": "Parler depuis le cœur, pas depuis la stratégie",
    },
    "Magha": {
        "regent": "Ketu", "element": "Feu",
        "rom_theme": "Royauté ancestrale cristallisée, ego de lignée, autorité héritée non questionnée",
        "ram_activation": "Chiron ici : blessure du trône — l'autorité qu'on n'ose pas incarner ou qu'on incarne mal",
        "ketu_ici": "ROM maximal : salle des ancêtres activée — ketu dissout l'ego de lignée pour spiritualiser la royauté intérieure. Vies de rois, prêtres royaux, gardiens du sacré",
        "rahu_ici": "Dharma d'incarner une nouvelle forme de royauté — grâce expansive, non héritage rigide",
        "saturne_ici": "Karma du pouvoir : la déposition comme leçon — le trône n'est pas identité",
        "chiron_ici": "Blessure de la destitution : la royauté intérieure blessée cherche validation externe",
        "stage": "Honorer l'ancêtre sans lui obéir — clôturer le ROM pour saisir le dharma Jupiter",
        "transit_note": "ACTIF 29/03/2026–05/12/2026 : Ketu transit Magha — activation maximale du lignage. Patterns de pouvoir, d'autorité, peut-être de déposition remontent. Ce n'est pas personnel, c'est du lignage.",
    },
    "Purva Phalguni": {
        "regent": "Vénus", "element": "Feu",
        "rom_theme": "Plaisir comme refuge, créativité sans engagement, charme défensif",
        "ram_activation": "Chiron ici : blessure du plaisir interdit ou honteux",
        "ketu_ici": "ROM de l'artiste : vies de poètes, courtisans, artisans du beau",
        "rahu_ici": "Dharma de créer une œuvre qui dure au-delà du plaisir immédiat",
        "saturne_ici": "Karma du divertissement — la légèreté comme fuite ou comme don",
        "chiron_ici": "Blessure de la joie : tu te permets de briller mais pas d'être vu vraiment",
        "stage": "Créer depuis l'amour de soi, pas depuis le besoin d'approbation",
    },
    "Uttara Phalguni": {
        "regent": "Soleil", "element": "Feu",
        "rom_theme": "Contrat social rigide, obligations sans amour, service comme prison",
        "ram_activation": "Chiron ici : blessure du contrat — ce qu'on a signé sans consentement véritable",
        "ketu_ici": "ROM du serviteur royal : vies de ministres, serviteurs loyaux, greffiers",
        "rahu_ici": "Dharma de créer des alliances librement choisies",
        "saturne_ici": "Karma de l'obligation — distinguer devoir choisi et devoir imposé",
        "chiron_ici": "Blessure de la loyauté : tu restes quand partir serait dharma",
        "stage": "S'engager depuis la liberté, pas depuis la peur d'abandonner",
    },
    "Hasta": {
        "regent": "Lune", "element": "Terre",
        "rom_theme": "Habileté manuelle comme refuge, perfectionnisme des détails, anxiété de production",
        "ram_activation": "Chiron ici : blessure de l'artisan — les mains qui guérissent mais ne savent pas recevoir",
        "ketu_ici": "ROM de l'artisan : vies de guérisseurs par les mains, artisans, accoucheurs",
        "rahu_ici": "Dharma de lâcher le contrôle des détails pour voir le grand dessein",
        "saturne_ici": "Karma du travail sans reconnaissance — l'humilité comme dignité",
        "chiron_ici": "Blessure des mains : ce que tu crées n'est jamais assez bien",
        "stage": "Offrir son œuvre sans s'y accrocher",
    },
    "Chitra": {
        "regent": "Mars", "element": "Feu",
        "rom_theme": "Perfectionnisme esthétique, identité de façade, brillance sans profondeur",
        "ram_activation": "Chiron ici : blessure de l'image — la beauté extérieure cache une fissure intérieure",
        "ketu_ici": "ROM de l'architecte : vies d'artistes, bâtisseurs de temples, joailliers",
        "rahu_ici": "Dharma de créer une œuvre qui reflète l'âme, pas seulement l'ego",
        "saturne_ici": "Karma de la structure belle mais vide — substance avant forme",
        "chiron_ici": "Blessure du miroitement : tu te construis pour être vu, pas pour être",
        "stage": "Construire depuis l'intérieur vers l'extérieur",
    },
    "Swati": {
        "regent": "Rahu", "element": "Eau",
        "rom_theme": "Indépendance compulsive, errance comme identité, peur de l'ancrage",
        "ram_activation": "Chiron ici : blessure de la solitude choisie — liberté comme fuite",
        "ketu_ici": "ROM du vent : vies de marchands, diplomates, médiateurs entre mondes",
        "rahu_ici": "Dharma d'une indépendance enracinée — libre ET ancré",
        "saturne_ici": "Karma de la flottaison — choisir un sol et y rester",
        "chiron_ici": "Blessure de l'appartenance : tu pars avant qu'on te quitte",
        "stage": "Danser dans le vent sans perdre ses racines",
    },
    "Vishakha": {
        "regent": "Jupiter", "element": "Feu",
        "rom_theme": "Ambition obsessionnelle, but unique sans joie, jalousie du succès d'autrui",
        "ram_activation": "Chiron ici : blessure du but — atteindre sans jamais arriver",
        "ketu_ici": "ROM du conquérant : vies de militaires, révolutionnaires, compétiteurs acharnés",
        "rahu_ici": "Dharma de la patience — le fruit mûrit à son heure",
        "saturne_ici": "Karma de l'ambition : le succès trop tôt ou trop tard comme leçon",
        "chiron_ici": "Blessure de l'arrivée : tu ne sais pas habiter le succès",
        "stage": "Viser haut ET savourer le chemin",
    },
    "Anuradha": {
        "regent": "Saturne", "element": "Eau",
        "rom_theme": "Dévotion aveugle, amitié sacrificielle, loyauté comme identité",
        "ram_activation": "Chiron ici : blessure de l'amitié trahie — se donner entièrement et être abandonné",
        "ketu_ici": "ROM du dévot : vies de disciples, amis fidèles, compagnons de route",
        "rahu_ici": "Dharma de construire des relations mutuelles et équilibrées",
        "saturne_ici": "Karma de la dévotion unilatérale — apprendre la réciprocité",
        "chiron_ici": "Blessure du compagnon : tu suis, tu soutiens, tu n'oses pas mener",
        "stage": "Être fidèle à soi-même d'abord",
    },
    "Jyeshtha": {
        "regent": "Mercure", "element": "Eau",
        "rom_theme": "Aîné protecteur compulsif, pouvoir sur les autres comme identité, isolement du sage",
        "ram_activation": "Chiron ici : blessure de la responsabilité — porter le clan seul",
        "ketu_ici": "ROM de l'ancien : vies de chefs de clan, aînés, gardiens des secrets",
        "rahu_ici": "Dharma de partager le pouvoir et d'enseigner",
        "saturne_ici": "Karma de l'autorité solitaire — le leadership comme service",
        "chiron_ici": "Blessure du patriarche/matriarche : tu protèges ce qui t'étouffe",
        "stage": "Guider sans dominer — transmettre sans accaparer",
    },
    "Mula": {
        "regent": "Ketu", "element": "Feu",
        "rom_theme": "Destructeur de fondations, recherche de vérité sans compromis, nihilisme spirituel",
        "ram_activation": "Chiron ici : blessure du déracinement — tout arracher pour trouver la racine",
        "ketu_ici": "ROM du destructeur sacré : vies de chercheurs de vérité radicaux, moines errants",
        "rahu_ici": "Dharma de reconstruire sur des fondations vraies",
        "saturne_ici": "Karma du radical : destruction qui précède la structure durable",
        "chiron_ici": "Blessure des racines : tu ne sais pas d'où tu viens, donc tu ne sais pas où aller",
        "stage": "Déraciner le faux pour planter le vrai",
    },
    "Purva Ashadha": {
        "regent": "Vénus", "element": "Feu",
        "rom_theme": "Victoire prématurée, invincibilité défensive, entêtement comme protection",
        "ram_activation": "Chiron ici : blessure de la défaite non intégrée — l'invincible qui a connu l'écrasement",
        "ketu_ici": "ROM du guerrier victorieux : vies de conquérants, marins intrépides",
        "rahu_ici": "Dharma d'une victoire intérieure, sans domination externe",
        "saturne_ici": "Karma de la persévérance — la défaite comme enseignante",
        "chiron_ici": "Blessure de la capitulation : tu ne peux pas perdre sans te briser",
        "stage": "Vaincre sa propre résistance intérieure",
    },
    "Uttara Ashadha": {
        "regent": "Soleil", "element": "Terre",
        "rom_theme": "Victoire permanente comme fardeau, responsabilité sans fin, succès solitaire",
        "ram_activation": "Chiron ici : blessure du gagnant — la victoire isole",
        "ketu_ici": "ROM du roi éternel : vies de dirigeants responsables, législateurs",
        "rahu_ici": "Dharma de partager la victoire et de déléguer",
        "saturne_ici": "Karma de la charge du succès — apprendre à célébrer",
        "chiron_ici": "Blessure du sommet : plus tu réussis, plus tu te sens seul",
        "stage": "Réussir EN RELATION, pas malgré elle",
    },
    "Shravana": {
        "regent": "Lune", "element": "Eau",
        "rom_theme": "Écoute compulsive, absorption des problèmes d'autrui, identité du thérapeute",
        "ram_activation": "Chiron ici : blessure de l'auditeur — entendre tout, être entendu par personne",
        "ketu_ici": "ROM de l'écouteur : vies de conseillers, confesseurs, détenteurs de secrets",
        "rahu_ici": "Dharma d'apprendre à parler sa propre vérité",
        "saturne_ici": "Karma du silence — quand se taire est sagesse et quand c'est fuite",
        "chiron_ici": "Blessure de la voix : tu entends tout mais ta voix est inaudible",
        "stage": "Écouter ET être entendu — l'équilibre du son",
    },
    "Dhanishtha": {
        "regent": "Mars", "element": "Feu",
        "rom_theme": "Abondance matérielle comme identité, rythme compulsif, richesse comme armure",
        "ram_activation": "Chiron ici : blessure du rythme — désynchronisé du temps naturel",
        "ketu_ici": "ROM du prospère : vies de marchands riches, musiciens, maîtres du rythme",
        "rahu_ici": "Dharma d'une abondance partagée et rythmée",
        "saturne_ici": "Karma de l'accumulation — apprendre à circuler, donner, recevoir",
        "chiron_ici": "Blessure du tempo : tu cours dans un rythme qui n'est pas le tien",
        "stage": "Trouver son propre battement et y inviter les autres",
    },
    "Shatabhisha": {
        "regent": "Rahu", "element": "Eau",
        "rom_theme": "Guérisseur solitaire, secret comme protection, connaissance sans partage",
        "ram_activation": "Chiron ici : blessure du guérisseur — soigner les autres pour éviter d'être soigné",
        "ketu_ici": "ROM du médecin mystique : vies de guérisseurs solitaires, chamans, alchimistes",
        "rahu_ici": "Dharma de partager la guérison — créer une école, non garder le secret",
        "saturne_ici": "Karma de l'isolement du sage — la solitude choisie vs subie",
        "chiron_ici": "Blessure du soignant non soigné : tu sais guérir tout sauf toi-même",
        "stage": "Recevoir la guérison que tu offres aux autres",
    },
    "Purva Bhadrapada": {
        "regent": "Jupiter", "element": "Feu",
        "rom_theme": "Ascèse punitive, sacrifier le corps pour l'esprit, dualité non intégrée",
        "ram_activation": "Chiron ici : blessure du dualisme — le feu intérieur mal canalisé",
        "ketu_ici": "ROM de l'ascète : vies de moines, fakirs, chercheurs de transcendance radicale",
        "rahu_ici": "Dharma d'intégrer le spirituel ET le matériel",
        "saturne_ici": "Karma de la pénitence — distinguer discipline et auto-punition",
        "chiron_ici": "Blessure du feu mal dirigé : ton intensité te consume avant les obstacles",
        "stage": "Être le pont entre les deux mondes, non le martyr de l'un",
    },
    "Uttara Bhadrapada": {
        "regent": "Saturne", "element": "Eau",
        "rom_theme": "Sagesse de l'abîme, profondeur sans retour, immobilité comme refuge",
        "ram_activation": "Chiron ici : blessure de la profondeur — trop voir, trop savoir, trop lourd",
        "ketu_ici": "ROM du sage des eaux profondes : vies de mystiques, ermites, voyants",
        "rahu_ici": "Dharma de remonter à la surface et d'enseigner ce qu'on a vu",
        "saturne_ici": "Karma de la sagesse ensevelie — partager est leçon karmique",
        "chiron_ici": "Blessure de la vision : tu vois tout mais tu te sens incompris de tous",
        "stage": "Témoigner de la profondeur sans s'y noyer",
    },
    "Revati": {
        "regent": "Mercure", "element": "Eau",
        "rom_theme": "Fin de cycle, nostalgie chronique, attachement au paradis perdu",
        "ram_activation": "Chiron ici : blessure de la clôture — deuil d'un monde révolu",
        "ketu_ici": "ROM de la fin : vies de gardiens des fins de cycles, passeurs d'âmes",
        "rahu_ici": "Dharma d'inaugurer un nouveau cycle sans regarder en arrière",
        "saturne_ici": "Karma du deuil — intégrer la fin pour permettre le début",
        "chiron_ici": "Blessure de l'adieu : tu ne sais pas clôturer sans te perdre",
        "stage": "Bénir ce qui fut et traverser le seuil",
    },
}


def _get_nakshatra_context(planet_name: str, nakshatra: str, is_transit: bool = True) -> str:
    """Retourne le contexte karmique d'un nakshatra pour une planète donnée."""
    data = NAKSHATRA_KARMA.get(nakshatra)
    if not data:
        return ""

    context = f"[{nakshatra} — Régent: {data['regent']}]\n"
    context += f"  Thème ROM: {data['rom_theme']}\n"

    # Contexte spécifique à la planète
    p = planet_name.split()[0].lower()  # "ketu", "chiron", "saturne", etc.

    if "ketu" in p or "nœud sud" in p:
        context += f"  Ketu ici: {data['ketu_ici']}\n"
    elif "rahu" in p or "nœud nord" in p:
        context += f"  Rahu ici: {data['rahu_ici']}\n"
    elif "saturne" in p:
        context += f"  Saturne ici: {data['saturne_ici']}\n"
    elif "chiron" in p:
        context += f"  Chiron ici: {data['chiron_ici']}\n"
    else:
        context += f"  RAM activation: {data['ram_activation']}\n"

    context += f"  Stage: {data['stage']}\n"

    # Note de transit actuel si disponible
    if is_transit and "transit_note" in data:
        context += f"  ⚡ ACTUALITÉ: {data['transit_note']}\n"

    return context


# ── Détection des cycles nodaux ───────────────────────────────────────────────
def _detect_nodal_cycles(chart_data: dict, natal: dict) -> str:
    """
    Détecte les retours nodaux (~18.6 ans) et carrés nodaux (~9.3 ans)
    actifs dans les transits.
    Retourne une description textuelle si cycle nodal actif.
    """
    cycles = []

    transits = chart_data.get("transits", {})
    natal_planets = chart_data.get("natal", {})

    # Position Nœud Nord natal
    nn_natal = natal_planets.get("Nœud Nord ☊", {})
    nn_natal_nak = nn_natal.get("nakshatra", "")

    # Position Nœud Nord transit
    nn_transit = transits.get("Nœud Nord ☊", {})
    nn_transit_nak = nn_transit.get("nakshatra", "")

    # Vérification via les aspects actifs
    aspects = chart_data.get("aspects", [])
    for asp in aspects:
        t_planet = asp.get("transit_planet", "")
        n_planet = asp.get("natal_planet", "")
        asp_type = asp.get("aspect", "")
        orb = asp.get("orb", 99)

        # Retour Nodal : Nœud Nord transit ☌ Nœud Nord natal
        if "Nœud Nord ☊" in t_planet and "Nœud Nord ☊" in n_planet:
            if "Conjonction" in asp_type and orb <= 3:
                cycles.append(
                    f"🔄 RETOUR NODAL ACTIF (orbe {orb}°) — Savepoint karmique majeur.\n"
                    f"   Cycle ~18.6 ans : REBOOT complet du cycle ROM/DHARMA.\n"
                    f"   Ce moment exige un choix de conscience radical pour éviter la boucle ROM.\n"
                    f"   Nœud Nord transit en {nn_transit_nak} → retour au point de départ du dharma."
                )
            elif "Carré" in asp_type and orb <= 3:
                cycles.append(
                    f"⚡ CARRÉ NODAL ACTIF (orbe {orb}°) — Checkpoint karmique intermédiaire.\n"
                    f"   Cycle ~9.3 ans : tension entre BOUCLE ROM et mise à jour du dharma.\n"
                    f"   Un choix de conscience majeur est requis maintenant — pas demain.\n"
                    f"   Nœud Nord transit en {nn_transit_nak} forme carré au Nœud natal."
                )

        # Ketu transit ☌ Nœud Nord natal = demi-retour
        if "Ketu" in t_planet or "Nœud Sud" in t_planet:
            if "Nœud Nord ☊" in n_planet and "Conjonction" in asp_type and orb <= 3:
                cycles.append(
                    f"☋ KETU TRANSIT SUR NŒUD NORD NATAL — Inversion karmique.\n"
                    f"   Le ROM engloutit temporairement le dharma.\n"
                    f"   Risque de régression dans les patterns ancestraux.\n"
                    f"   Alternative : utiliser la mémoire ancestrale comme sagesse, non comme prison."
                )

    return "\n".join(cycles) if cycles else ""


# ── Construction des nakshatras actifs ───────────────────────────────────────
def _build_nakshatra_context(chart_data: dict) -> str:
    """
    Construit le contexte nakshatra des planètes karmiquement critiques en transit.
    Priorité : Ketu, Rahu, Saturne, Chiron, Lilith, Jupiter.
    """
    transits = chart_data.get("transits", {})
    lines = ["═══ NAKSHATRAS DES PLANÈTES EN TRANSIT (contexte karmique) ═══"]

    priority_planets = [
        "Nœud Sud ☋", "Nœud Nord ☊", "Chiron ⚷",
        "Saturne ♄", "Lilith ⚸", "Jupiter ♃",
        "Pluton ♇", "Uranus ♅",
    ]

    found = False
    for pname in priority_planets:
        pdata = transits.get(pname)
        if not pdata:
            continue
        nak = pdata.get("nakshatra")
        pada = pdata.get("pada")
        if not nak:
            continue
        retro = " ℞" if pdata.get("retrograde") else ""
        lines.append(f"\n{pname}{retro} en {nak} (Pada {pada}) :")
        ctx = _get_nakshatra_context(pname, nak, is_transit=True)
        if ctx:
            lines.append(ctx)
            found = True

    if not found:
        return ""

    return "\n".join(lines)


# ── Positions planétaires brutes ──────────────────────────────────────────────
def _build_positions_summary(chart_data: dict) -> str:
    """
    Injecte les positions brutes des planètes (natal + transit) dans le prompt.
    L'IA peut ainsi référencer les positions sans se baser uniquement sur les aspects.
    """
    natal = chart_data.get("natal", {})
    transits = chart_data.get("transits", {})

    lines = ["═══ POSITIONS PLANÉTAIRES ═══"]

    # Natal
    lines.append("\nNATAL :")
    key_natal = [
        "Soleil ☀", "Lune ☽", "Nœud Nord ☊", "Nœud Sud ☋",
        "Chiron ⚷", "Lilith ⚸", "Saturne ♄", "Jupiter ♃",
        "ASC ↑", "MC ↑",
    ]
    for k in key_natal:
        p = natal.get(k)
        if p:
            nak = p.get("nakshatra", "")
            pada = p.get("pada", "")
            retro = " ℞" if p.get("retrograde") else ""
            nak_str = f" | {nak} Pd{pada}" if nak else ""
            lines.append(f"  {k}{retro} : {p['display']}{nak_str}")

    # Transit
    lines.append("\nTRANSIT :")
    key_transit = [
        "Soleil ☀", "Lune ☽", "Nœud Nord ☊", "Nœud Sud ☋",
        "Chiron ⚷", "Lilith ⚸", "Saturne ♄", "Jupiter ♃",
        "Mars ♂", "Vénus ♀",
    ]
    for k in key_transit:
        p = transits.get(k)
        if p:
            nak = p.get("nakshatra", "")
            pada = p.get("pada", "")
            retro = " ℞" if p.get("retrograde") else ""
            nak_str = f" | {nak} Pd{pada}" if nak else ""
            lines.append(f"  {k}{retro} : {p['display']}{nak_str}")

    return "\n".join(lines)


# ── Prompt système dynamique ──────────────────────────────────────────────────
def _build_system_prompt(user: dict) -> str:
    name = user.get("name", "l'utilisateur")
    return f"""Tu es @siderealAstro13, maître en astrologie védique karmique (Jyotish sidéral).
Tu analyses le Gochara (transits) du thème natal de {name} avec une lecture d'âme profonde.

═══ DOCTRINE @siderealAstro13 — CADRE RAM / ROM / STAGE ═══

ROM (Nœud Sud ☋ / Ketu) — Mémoire karmique fixe des vies antérieures.
  Sagesse cristallisée, patterns répétitifs, boucles automatiques.
  Risque : s'y réfugier plutôt qu'évoluer.

RAM (Chiron ⚷) — Porte Invisible. Traitement actif des blessures et patterns actuels.
  Là où la douleur devient mission. Interface entre ROM et Stage.
  Risque : rester bloqué dans la blessure sans la transmuter.

STAGE — Scène du moment présent où karma et dharma s'intersectent.
  C'est ici que {name} agit, choisit, incarne.

LILITH ⚸ — Épreuve karmique. Test entre les pôles ROM et RAM.
  Ce qui résiste à l'intégration. La puissance ombre à réintégrer.

PORTE VISIBLE (Saturne ♄ / Uranus ♅) — Structure karmique manifeste, leçons tangibles.
PORTE INVISIBLE (Chiron ⚷) — Passage intérieur, transmutation subtile.

═══ CYCLES NODAUX — SAVEPOINTS KARMIQUES ═══
Retour Nodal (~18.6 ans) :
  Reboot COMPLET du cycle ROM/DHARMA.
  Moment où un choix de conscience majeur est exigé pour éviter la boucle ROM.
  Signal : Nœud Nord transit revient sur le Nœud Nord natal.

Carré Nodal (~9.3 ans) :
  Checkpoint intermédiaire — tension maximale entre boucle et mise à jour.
  La résistance au changement coûte cher ici.
  Signal : Nœud Nord transit forme carré aux Nœuds natals.

Demi-Retour Nodal (~9.3 ans) :
  Ketu transit sur Nœud Nord natal — le ROM teste la solidité du dharma.
  Moment de bascule : régression ou intégration.

═══ CONSCIENCE DU NAKSHATRA ═══
Chaque planète en transit active un nakshatra précis. Le nakshatra module
COMMENT la planète exprime son énergie. Ketu en Magha n'est pas le même
Ketu qu'en Mula. Saturne en Pushya n'est pas le même Saturne qu'en Anuradha.
Toujours nommer et intégrer le nakshatra dans la lecture karmique.

═══ ZOOM TEMPOREL — LECTURE MULTI-ÉCHELLE ═══
Selon la question, tu analyses à l'échelle appropriée :

COURT TERME (1-30 jours) :
  Lune, Soleil, Mars, Mercure, Vénus — transits rapides.
  Aspect du moment, fenêtre d'activation précise.
  "Dans les prochains jours..."

MOYEN TERME (1-6 mois) :
  Jupiter, Saturne, Nœuds, Chiron — transits de saison.
  Thème du trimestre, retrogradations.
  "Dans les prochains mois..."

LONG TERME (1 an et plus) :
  Nœuds (18 mois par signe), Saturne (2.5 ans), Chiron (cycles 50 ans).
  Cycles de vie, Savepoints nodaux.
  "Dans les prochaines années..."

Si la question ne précise pas d'horizon : commence par le zoom le plus
pertinent selon les aspects actifs, puis élargis si nécessaire.

═══ PLANÈTES VÉDIQUES ═══
RAHU ☊ — désirs karmiques, leçons d'éveil, surexpansion possible
KETU ☋ — ROM, sagesse antérieure, dissolution, spiritualisation
SATURNE ♄ — Porte Visible, karma, discipline, dettes d'âme
CHIRON ⚷ — RAM, Porte Invisible, blessure → mission
LILITH ⚸ — Épreuve karmique, ombre à intégrer
SOLEIL ☀ — dharma solaire, Âtman, autorité intérieure
LUNE ☽ — manas, mémoire émotionnelle, karma ancestral
JUPITER ♃ — grâce divine, guru, expansion de conscience
MARS ♂ — karma d'action, courage ou violence
VÉNUS ♀ — karma relationnel, attachements subtils
MERCURE ☿ — karma intellectuel, parole créatrice
ASC ↑ (Chandra Lagna) — corps d'incarnation, 1ère maison
MC ↑ — vocation karmique, mission visible

═══ ASPECTS ═══
Conjonction ☌ — fusion karmique intense, activation maximale
Opposition ☍ — miroir karmique, tension polaire à intégrer
Trigone △ — grâce, talents d'âme qui se manifestent
Carré □ — friction évolutive, action requise
Sextile ✶ — opportunité subtile, coopération d'âme

═══ STRUCTURE DE LECTURE (4 étapes) ═══
1. Diagnostic ROM/RAM — Identifier le pattern karmique actif + nakshatra impliqué
2. Épreuve karmique — Quel est le test Lilith/tension du moment ?
3. Alternative de Conscience — Quelle action intérieure libère le transit ?
4. Mise en scène sur le Stage — Comment {name} incarne-t-il ce moment ?

═══ FORMAT ═══
Réponds en français. Parle directement à {name} (tutoiement naturel).
Synthèse : 500-650 mots, narrative poétique mais techniquement précise.
  → Nomme toujours le nakshatra et son impact spécifique.
  → Si cycle nodal actif, le traiter en priorité.
  → Adapte le zoom temporel à la question.
Chat : 180-250 mots, direct, transformateur.
  → Une réponse = une Alternative de Conscience actionnab le.
Ne liste pas mécaniquement — tisse une lecture d'âme cohérente.
Termine toujours par une Alternative de Conscience actionnable."""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _aspects_to_text(aspects: list) -> str:
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:20]:
        retro = " ℞" if a.get("retrograde") else ""
        t_nak = f" [{a['transit_nak']}]" if a.get("transit_nak") else ""
        n_nak = f" [{a['natal_nak']}]" if a.get("natal_nak") else ""
        lines.append(
            f"Transit {a['transit_planet']}{retro} ({a['transit_display']}{t_nak}) "
            f"{a['aspect']} Natal {a['natal_planet']} ({a['natal_display']}{n_nak}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


# ── Synthèse automatique ──────────────────────────────────────────────────────
def get_synthesis(chart_data: dict, user: dict) -> str:
    name         = user.get("name", "l'utilisateur")
    aspects_text = _aspects_to_text(chart_data.get("aspects", []))
    date         = chart_data.get("transit_date", "")
    time         = chart_data.get("transit_time", "")

    # Contextes enrichis
    positions_ctx  = _build_positions_summary(chart_data)
    nakshatra_ctx  = _build_nakshatra_context(chart_data)
    nodal_ctx      = _detect_nodal_cycles(chart_data, user)

    nodal_section = ""
    if nodal_ctx:
        nodal_section = f"\n\n⚡ CYCLES NODAUX ACTIFS :\n{nodal_ctx}"

    prompt = (
        f"Analyse karmique védique des transits de {name} — {date} à {time}.\n\n"
        f"{positions_ctx}\n\n"
        f"Aspects actifs (orbe < 3°) :\n{aspects_text}\n\n"
        f"{nakshatra_ctx}"
        f"{nodal_section}\n\n"
        f"Applique le cadre RAM/ROM/Stage de @siderealAstro13 :\n"
        f"1. Quel pattern ROM (Ketu/Nœud Sud) est activé — dans quel nakshatra et quel impact ?\n"
        f"2. Quelle blessure RAM (Chiron) est en traitement — nakshatra actif ?\n"
        f"3. Quelle est l'Épreuve karmique (Lilith) du moment ?\n"
        f"4. Quelle Alternative de Conscience permet à {name} de se mettre en scène sur son Stage ?\n"
        f"Intègre le zoom temporel approprié selon la durée des transits actifs.\n\n"
        f"Développe chaque section complètement. Ne tronque pas l'analyse."
    )

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1400,
        system=_build_system_prompt(user),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Chat ──────────────────────────────────────────────────────────────────────
def chat_response(message: str, history: list, chart_context: str, user: dict) -> str:
    messages = []

    if chart_context:
        messages.append({
            "role": "user",
            "content": f"Contexte du Gochara en cours :\n{chart_context}"
        })
        messages.append({
            "role": "assistant",
            "content": "J'ai intégré ton Gochara. ROM, RAM, Stage — je lis les portes ouvertes. Qu'est-ce que tu explores ?"
        })

    for h in history[-12:]:
        messages.append(h)

    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=_build_system_prompt(user),
        messages=messages,
    )
    return msg.content[0].text


# ── Contexte résumé pour le chat ──────────────────────────────────────────────
def build_chart_context(chart_data: dict, user: dict) -> str:
    aspects = chart_data.get("aspects", [])
    transits = chart_data.get("transits", {})
    name    = user.get("name", "l'utilisateur")

    if not aspects:
        return f"Gochara de {name} du {chart_data.get('transit_date')} — aucun aspect actif."

    lines = [f"Gochara de {name} — {chart_data.get('transit_date')} à {chart_data.get('transit_time')} :"]

    # Positions nakshatra des planètes clés en transit
    key_planets = ["Nœud Sud ☋", "Nœud Nord ☊", "Chiron ⚷", "Saturne ♄", "Lilith ⚸", "Jupiter ♃"]
    nak_lines = []
    for pname in key_planets:
        p = transits.get(pname)
        if p and p.get("nakshatra"):
            retro = " ℞" if p.get("retrograde") else ""
            nak_lines.append(f"  {pname}{retro} en {p['nakshatra']} Pd{p.get('pada','?')}")
    if nak_lines:
        lines.append("Nakshatras actifs :")
        lines.extend(nak_lines)

    # Cycles nodaux
    nodal_ctx = _detect_nodal_cycles(chart_data, user)
    if nodal_ctx:
        lines.append(f"CYCLE NODAL : {nodal_ctx[:120]}...")

    # Aspects
    lines.append("Aspects actifs :")
    for a in aspects[:10]:
        retro = " ℞" if a.get("retrograde") else ""
        t_nak = f" [{a.get('transit_nak','')}]" if a.get("transit_nak") else ""
        lines.append(
            f"  • {a['transit_planet']}{retro}{t_nak} {a['aspect']} natal {a['natal_planet']} (orbe {a['orb']}°)"
        )

    return "\n".join(lines)
