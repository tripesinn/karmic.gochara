"""
_generate_pada_table.py
Génère karmic_vault/08_pada_table.md + pada_table.csv
108 padas = 27 nakshatras × 4 padas
Navamsa : (nak_idx * 4 + pada_idx) % 12
"""

import csv, os

# ── Séquence Navamsa D9 (index 0-11) ────────────────────────────────────────
NAVAMSA = [
    ("Bélier",    "Mars"),
    ("Taureau",   "Vénus"),
    ("Gémeaux",   "Mercure"),
    ("Cancer",    "Lune"),
    ("Lion",      "Soleil"),
    ("Vierge",    "Mercure"),
    ("Balance",   "Vénus"),
    ("Scorpion",  "Mars"),
    ("Sagittaire","Jupiter"),
    ("Capricorne","Saturne"),
    ("Verseau",   "Saturne"),
    ("Poissons",  "Jupiter"),
]

SIGNS = ["Bélier","Taureau","Gémeaux","Cancer","Lion","Vierge",
         "Balance","Scorpion","Sagittaire","Capricorne","Verseau","Poissons"]

def get_sign(nak_idx, pada_idx):
    lon = nak_idx * 13.3333 + pada_idx * 3.3333
    return SIGNS[int(lon / 30)]

# ── 27 Nakshatras : (nom, vimshotari, régime, divinité) ─────────────────────
NAKSHATRAS = [
    ("Ashwini",            "Ketu",    "ROM",     "Ashvins"),
    ("Bharani",            "Vénus",   "Dharma",  "Yama"),
    ("Krittika",           "Soleil",  "Blessure","Agni"),
    ("Rohini",             "Lune",    "Dharma",  "Brahma"),
    ("Mrigashira",         "Mars",    "ROM",     "Soma"),
    ("Ardra",              "Mercure", "Blessure","Rudra"),
    ("Punarvasu",          "Jupiter", "Dharma",  "Aditi"),
    ("Pushya",             "Saturne", "ROM",     "Brihaspati"),
    ("Ashlesha",           "Mercure", "Blessure","Sarpa"),
    ("Magha",              "Ketu",    "ROM",     "Pitris"),
    ("Purva Phalguni",     "Vénus",   "Dharma",  "Aryaman"),
    ("Uttara Phalguni",    "Soleil",  "Blessure","Bhaga"),
    ("Hasta",              "Lune",    "Dharma",  "Savitri"),
    ("Chitra",             "Mars",    "ROM",     "Tvashtri"),
    ("Swati",              "Rahu",    "Dharma",  "Vayu"),
    ("Vishakha",           "Jupiter", "Dharma",  "Indra-Agni"),
    ("Anuradha",           "Saturne", "ROM",     "Mitra"),
    ("Jyeshtha",           "Mercure", "Blessure","Indra"),
    ("Mula",               "Ketu",    "ROM",     "Nirriti"),
    ("Purva Ashadha",      "Vénus",   "Dharma",  "Apah"),
    ("Uttara Ashadha",     "Soleil",  "Blessure","Vishvadevas"),
    ("Shravana",           "Lune",    "Dharma",  "Vishnu"),
    ("Dhanishtha",         "Mars",    "ROM",     "Vasus"),
    ("Shatabhisha",        "Rahu",    "Dharma",  "Varuna"),
    ("Purva Bhadrapada",   "Jupiter", "Dharma",  "Aja Ekapada"),
    ("Uttara Bhadrapada",  "Saturne", "ROM",     "Ahir Budhnya"),
    ("Revati",             "Mercure", "Blessure","Pushan"),
]

# ── 108 Tensions vécues [nak_idx][pada_idx] ──────────────────────────────────
TENSIONS = [
    # 0 Ashwini — ROM — peur primale de naître, paralysie à l'aube
    [
        "L'élan vers le nouveau se retourne en fuite — démarrer sans direction pour ne pas s'arrêter.",
        "Le confort du familier prend le visage de l'amour — rester devient une forme de désertion.",
        "Le mental fabrique mille raisons de ne pas commencer — l'analyse remplace l'acte.",
        "La peur de naître cherche refuge dans la mémoire émotionnelle — la nostalgie remplace le passage.",
    ],
    # 1 Bharani — Dharma — transformation du désir en créativité responsable
    [
        "La visibilité s'ouvre — créer en son propre nom, sans attendre permission.",
        "Le discernement affine la création — trier ce qui mérite vraiment d'être enfanté.",
        "La beauté devient vecteur de transformation — l'esthétique au service du sens.",
        "Le désir se retourne vers sa source — créer à partir de ce qui a failli détruire.",
    ],
    # 2 Krittika — Blessure — purification par le feu, perfectionnisme brûlant
    [
        "La croyance en sa propre vision brûle ce qui ne s'y conforme pas — clarté qui exclut.",
        "La rigueur se retourne contre soi — la discipline devient auto-punition.",
        "La critique sociale prend le masque de la liberté — détruire les normes pour en imposer d'autres.",
        "La purification cherche l'absolu — brûler jusqu'à l'os pour atteindre une perfection impossible.",
    ],
    # 3 Rohini — Dharma — croissance fertile, abondance stable
    [
        "L'élan créateur plante sans forcer — initier ce qui demande à croître.",
        "La patience devient une forme d'amour — nourrir sans épuiser, construire sans hâte.",
        "La parole nourrit — transmettre ce qui a germé, nommer ce qui croît.",
        "La mémoire fertilise — ce qui vient des profondeurs devient la fondation du nouveau.",
    ],
    # 4 Mrigashira — ROM — quête sans fin, manque chronique
    [
        "La recherche de sens se transforme en course à la reconnaissance — trouver devient montrer.",
        "Chaque réponse ouvre dix nouvelles questions — l'analyse est la forme même du manque.",
        "La quête se projette sur l'autre — ce qu'on cherche en soi, on l'exige du partenaire.",
        "L'insatisfaction chronique devient conflit — la fuite prend la forme de l'affrontement.",
    ],
    # 5 Ardra — Blessure — tempête mentale, chaos qui nettoie
    [
        "La tempête est dans le langage — les mots déchirent avant de clarifier.",
        "La turbulence émotionnelle est le signal — ce qui noie est aussi ce qui lave.",
        "L'ego est balayé par la tempête — la crise d'identité précède la clarté.",
        "Le chaos se met en ordre après l'orage — analyser ce qui a survécu à la destruction.",
    ],
    # 6 Punarvasu — Dharma — retour rédempteur, renaissance après l'exil
    [
        "Le foyer intérieur retrouvé — revenir à soi après avoir cherché partout ailleurs.",
        "La lumière revient après l'obscurité — s'incarner à nouveau avec plus de clarté.",
        "Le retour s'accompagne d'intégration — apprendre de l'exil, reformuler le chemin.",
        "La réconciliation avec l'autre et avec soi — la relation comme lieu de renaissance.",
    ],
    # 7 Pushya — ROM — nourriture contrainte, dépendance aux structures
    [
        "La quête de sens passe par les systèmes extérieurs — croire que quelqu'un d'autre détient la clé.",
        "La structure devient prison — se nourrir de règles au lieu de se nourrir de soi.",
        "L'appartenance au groupe remplace l'autonomie — la tribu valide ce qu'on devrait sentir seul.",
        "La spiritualité devient dépendance — chercher le nourrissement dans l'au-delà pour éviter le présent.",
    ],
    # 8 Ashlesha — Blessure — étreinte serpentine, contrôle invisible
    [
        "La blessure se tapit dans les émotions — le contrôle émotionnel comme mécanisme de survie.",
        "La manipulation cherche la lumière — séduire pour exister, contrôler pour être vu.",
        "L'intellect devient l'arme — comprendre les failles de l'autre avant qu'il comprenne les siennes.",
        "Le lien devient étreinte — la relation comme territoire à sécuriser plutôt qu'à habiter.",
    ],
    # 9 Magha — ROM — héritage ancestral écrasant, identification au prestige
    [
        "L'énergie ancestrale s'emballe — agir pour le clan sans jamais demander si c'est son propre chemin.",
        "Le prestige familial se traduit en attachement aux possessions — honorer la lignée par l'accumulation.",
        "L'histoire familiale tourne en boucle dans le mental — justifier le passé au lieu de le traverser.",
        "La mémoire ancestrale envahit l'émotionnel — les réactions d'aujourd'hui appartiennent à une autre époque.",
    ],
    # 10 Purva Phalguni — Dharma — création ludique, amour conscient
    [
        "La joie créatrice comme expression de soi — briller sans calcul, créer pour l'amour de créer.",
        "L'artisanat conscient — créer avec précision ce qui touche vraiment.",
        "L'amour comme acte créateur — la relation qui inspire l'œuvre.",
        "La création comme transmutation — enfanter à partir de la blessure sublimée.",
    ],
    # 11 Uttara Phalguni — Blessure — leadership blessé, rédemption par l'intégrité
    [
        "L'autorité blessée cherche à se valider — diriger pour prouver, pas pour servir.",
        "Le leadership s'intellectualise — analyser le pouvoir plutôt que l'exercer avec intégrité.",
        "L'autorité cherche l'approbation — diriger d'un côté, plaire de l'autre.",
        "La blessure du pouvoir se retourne en transformation — ce qui a été abusé peut maintenant être transmué.",
    ],
    # 12 Hasta — Dharma — habileté manifestée, création pratique incarnée
    [
        "La vision s'incarne par les mains — appliquer la sagesse concrètement, sans rester dans les idées.",
        "La discipline de la pratique — maîtrise acquise par la répétition consciente.",
        "L'originalité s'exprime dans la forme — innover dans le faire, pas seulement dans le penser.",
        "La grâce passe par le corps — créer depuis l'intuition sans perdre la précision.",
    ],
    # 13 Chitra — ROM — perfectionnisme paralysant, construction sans fin
    [
        "Le détail devient obsession — perfectionner est une façon de ne jamais terminer.",
        "L'esthétique remplace le sens — construire pour plaire au lieu de construire pour incarner.",
        "La perfection devient contrôle — l'artisan se transforme en tyran de sa propre création.",
        "L'idéal de perfection s'étend à l'infini — la vision s'emballe, l'œuvre reste inachevée.",
    ],
    # 14 Swati — Dharma — indépendance gagnée, liberté responsable
    [
        "L'indépendance ne rejette pas le lien — bouger librement sans couper ce qui nourrit.",
        "La liberté s'acquiert en traversant la résistance — l'autonomie naît après le conflit.",
        "La liberté porte un sens — explorer sans errer, s'ouvrir sans se perdre.",
        "La liberté s'ancre dans la structure — indépendance sans chaos.",
    ],
    # 15 Vishakha — Dharma — bifurcation du choix, victoire sur deux fronts
    [
        "L'hésitation entre deux chemins révèle une valeur — choisir ce qui est vrai, pas ce qui est confortable.",
        "La décision coûte quelque chose — couper l'une des voies pour avancer dans l'autre.",
        "La vision dharmica guide le choix — sélectionner ce qui sert le sens, pas l'ego.",
        "Le choix s'incarne dans la durée — s'engager au-delà de l'enthousiasme initial.",
    ],
    # 16 Anuradha — ROM — obéissance anxieuse, dévotion figée
    [
        "La dévotion cherche un maître — s'effacer derrière une doctrine pour éviter d'être soi.",
        "La fidélité devient obligation — servir par peur de la solitude, pas par choix conscient.",
        "Le groupe devient la raison d'être — fondre dans le collectif pour ne pas exister seul.",
        "L'amour se dissout dans l'idéal — aimer un concept plutôt qu'une personne réelle.",
    ],
    # 17 Jyeshtha — Blessure — aîné usé, fardeau du contrôle
    [
        "Le pouvoir s'accroche par peur de l'effondrement — contrôler avant d'être contrôlé.",
        "L'autorité se drape dans la sagesse — le sage fatigué qui ne peut plus se remettre en cause.",
        "Le fardeau devient identité — se définir par ce qu'on porte, pas par ce qu'on est.",
        "Le contrôle se collectivise — diriger le groupe pour ne pas voir son propre épuisement.",
    ],
    # 18 Mula — ROM — obsession du contrôle, cycle de ruine
    [
        "La destruction se déguise en quête de sens — démolir ce qui ne s'aligne pas avec la croyance.",
        "Le contrôle s'accroche aux structures même quand elles s'effondrent — résister à ce qui doit tomber.",
        "L'auto-sabotage prend la forme de l'idéalisme — détruire ce qui fonctionne pour servir une vision abstraite.",
        "La peur de tout perdre se réfugie dans la spiritualité — fuir dans le transcendant pour éviter l'effondrement réel.",
    ],
    # 19 Purva Ashadha — Dharma — victoire invincible, confiance en sa force
    [
        "La foi en sa propre direction — avancer sans avoir besoin que les autres valident.",
        "La victoire se construit lentement — honorer le processus autant que le résultat.",
        "La force individuelle au service du collectif — vaincre pour tous, pas pour soi seul.",
        "La victoire se transcende — réussir, puis lâcher le résultat.",
    ],
    # 20 Uttara Ashadha — Blessure — victoire morale, rédemption par l'intégrité
    [
        "La victoire cherche un sens supérieur — gagner n'est pas suffisant sans la justification éthique.",
        "L'intégrité se construit dans la durée — la victoire acquise pas à pas, sans raccourcis.",
        "La victoire morale au service du collectif — réussir pour ceux qui n'ont pas pu.",
        "La victoire se dissout dans le sens universel — réussir, puis offrir le résultat.",
    ],
    # 21 Shravana — Dharma — écoute sacrée, apprentissage vivant
    [
        "Écouter la structure — apprendre de ce qui dure, honorer ce qui a résisté au temps.",
        "Écouter le collectif — recevoir la sagesse du groupe sans y fondre son identité.",
        "Écouter le silence — la connaissance arrive quand on arrête de parler.",
        "L'écoute précède l'acte — agir seulement quand le signal intérieur est clair.",
    ],
    # 22 Dhanishtha — ROM — accumulation compulsive, insatisfaction permanente
    [
        "L'accumulation prend la forme de la discipline — construire des réserves qu'on n'utilisera jamais.",
        "L'avidité se collectivise — accumuler des réseaux, du statut, des contacts — toujours plus.",
        "Le désir de richesse se spiritualise — l'accumulation devient une quête de sens déguisée.",
        "La pénurie redoutée déclenche l'action violente — prendre avant que quelqu'un d'autre ne prenne.",
    ],
    # 23 Shatabhisha — Dharma — guérison cachée, révélation de l'invisible
    [
        "La guérison passe par la singularité assumée — être trop différent est le don, pas le problème.",
        "Les profondeurs révèlent — plonger dans l'invisible pour ramener ce qui soigne.",
        "La révélation demande du courage — nommer ce qui était caché, même si ça dérange.",
        "La guérison prend une forme — incarner le mystère dans quelque chose de concret et beau.",
    ],
    # 24 Purva Bhadrapada — Dharma — croissance par le feu, expansion post-crise
    [
        "L'épreuve restructure — la crise révèle ce qui résiste vraiment au chaos.",
        "La grâce arrive après la destruction — ce qui reste après le feu est ce qui comptait.",
        "L'énergie de la rage se retourne en élan créateur — transformer l'incendie en départ.",
        "La nouvelle naissance s'ancre dans la valeur retrouvée — reconstruire sur ce qui est vrai.",
    ],
    # 25 Uttara Bhadrapada — ROM — prospérité enchaînée, confort qui étouffe
    [
        "Le privilège se justifie par la sagesse — rationaliser le confort comme un mérite spirituel.",
        "La sécurité acquise devient un territoire à défendre — la prospérité transformée en forteresse.",
        "L'attachement aux possessions et au statut rend le changement physiquement impossible.",
        "Le mental négocie sans cesse avec la chaîne dorée — comprendre la prison mais refuser de la quitter.",
    ],
    # 26 Revati — Blessure — doute de soi malgré la bonne volonté, infantilisation
    [
        "La bienveillance se noie dans le doute — aider sans croire que cela compte vraiment.",
        "La protection se structure en rigidité — guider avec les mains trop serrées.",
        "L'aide cherche le détachement — guider sans s'impliquer, pour éviter la peur de mal faire.",
        "Se perdre dans la guidance de l'autre — accompagner jusqu'à oublier sa propre voix.",
    ],
]

assert len(TENSIONS) == 27, f"Attendu 27, got {len(TENSIONS)}"
for i, t in enumerate(TENSIONS):
    assert len(t) == 4, f"Nak {i} a {len(t)} tensions, attendu 4"

# ── Génération ───────────────────────────────────────────────────────────────

rows = []
for ni, (nak, vim, regime, div) in enumerate(NAKSHATRAS):
    for pi in range(4):
        nav_idx = (ni * 4 + pi) % 12
        nav_sign, nav_lord = NAVAMSA[nav_idx]
        sign = get_sign(ni, pi)
        tension = TENSIONS[ni][pi]
        rows.append({
            "N":           ni * 4 + pi + 1,
            "Nakshatra":   nak,
            "Pada":        pi + 1,
            "Signe":       sign,
            "Nav_Signe":   nav_sign,
            "Nav_Lord":    nav_lord,
            "Vimshotari":  vim,
            "Regime":      regime,
            "Divinite":    div,
            "Tension":     tension,
        })

assert len(rows) == 108, f"Attendu 108 lignes, got {len(rows)}"
print(f"✓ {len(rows)} padas générés")

# ── CSV ──────────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join("karmic_vault", "pada_table.csv")
os.makedirs("karmic_vault", exist_ok=True)
with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"✓ CSV → {CSV_PATH}")

# ── Markdown ─────────────────────────────────────────────────────────────────
MD_PATH = os.path.join("karmic_vault", "08_pada_table.md")

md_lines = [
    "# 08_pada_table.md",
    "## Table des 108 Padas | Doctrine Évolutive Synthétique",
    "",
    "**Règle Navamsa** : `(nak_index × 4 + pada_index) % 12`  ",
    "**Régents Navamsa** : Bélier/Mars · Taureau/Vénus · Gémeaux/Mercure · Cancer/Lune · Lion/Soleil · Vierge/Mercure · Balance/Vénus · Scorpion/Mars · Sagittaire/Jupiter · Capricorne/Saturne · Verseau/Saturne · Poissons/Jupiter  ",
    "**Usage** : injection dans `get_hook_lunar_pada()` — Signal du Jour, alertes Lune, hook quotidien  ",
    "",
    "---",
    "",
]

current_nak = None
for r in rows:
    if r["Nakshatra"] != current_nak:
        current_nak = r["Nakshatra"]
        ni = (r["N"] - 1) // 4
        nak_data = NAKSHATRAS[ni]
        md_lines += [
            f"### {ni+1}. {r['Nakshatra']} | {r['Vimshotari']} | {r['Regime']} | {r['Divinite']}",
            "",
            f"| Pada | Signe | Navamsa | Régent | Tension Vécue |",
            f"|------|-------|---------|--------|---------------|",
        ]
    md_lines.append(
        f"| P{r['Pada']} | {r['Signe']} | {r['Nav_Signe']} | {r['Nav_Lord']} | {r['Tension']} |"
    )
md_lines.append("")

# ── Tableau résumé ───────────────────────────────────────────────────────────
md_lines += [
    "---",
    "",
    "## Tableau Index — 108 Padas",
    "",
    "| # | Nakshatra | Pada | Nav. Lord | Régime | Divinité |",
    "|---|-----------|------|-----------|--------|----------|",
]
for r in rows:
    md_lines.append(
        f"| {r['N']:>3} | {r['Nakshatra']:<22} | P{r['Pada']} | {r['Nav_Lord']:<8} | {r['Regime']:<8} | {r['Divinite']} |"
    )

md_lines += [
    "",
    "---",
    "",
    "## Mode d'emploi — Hook quotidien Lune",
    "",
    "```python",
    "# Dans get_hook_lunar_pada(moon_lon_sid) :",
    "nak_idx  = int(moon_lon_sid / 13.3333)          # 0-26",
    "pada_idx = int((moon_lon_sid % 13.3333) / 3.3333) # 0-3",
    "nav_idx  = (nak_idx * 4 + pada_idx) % 12",
    "",
    "# Lookup → pad['Tension'], pad['Nav_Lord'], pad['Divinite'], pad['Regime']",
    "# Injection dans le prompt Signal du Jour (3 phrases, règles 01_output_rules.md)",
    "```",
    "",
    "**Format hook public (sans natal)** :",
    "```",
    "◆ Lune en [Nakshatra] · Pada [N] · [Régime]",
    "[Tension Vécue du pada — 1 phrase oraculaire]",
    "[Nav_Lord colore l'expression — keyword planète transposé en vécu]",
    "[Amorce Alternative de Conscience]",
    "```",
    "",
    "**Format hook perso (avec natal, H1-H12)** :",
    "```",
    "◆ Lune traverse ta H[X] aujourd'hui — [Nakshatra], Pada [N]",
    "[Tension Vécue adaptée à la maison]",
    "[Interaction avec Ketu/Chiron natal si aspect < 3°]",
    "[Alternative de Conscience personnalisée]",
    "```",
]

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")
print(f"✓ Markdown → {MD_PATH}")

# ── Validation ───────────────────────────────────────────────────────────────
print("\n── Validation séquence Navamsa (10 premiers) ──")
for r in rows[:10]:
    print(f"  {r['Nakshatra']:22} P{r['Pada']} → {r['Nav_Signe']:12} / {r['Nav_Lord']}")

print(f"\n── Répartition régimes ──")
from collections import Counter
c = Counter(r["Regime"] for r in rows)
for k, v in sorted(c.items()):
    print(f"  {k:<10}: {v:>3} padas ({v/108*100:.1f}%)")
