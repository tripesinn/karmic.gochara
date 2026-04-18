# doctrine.py
# Doctrine Évolutive Synthétique — @siderealAstro13
# Source unique de vérité doctrinale — importée par ai_interpret.py
# —————————————————————————————————————————————————————

# ——— SYMBOLIC LEGEND / LÉGENDE SYMBOLIQUE ————————————————————————————————————
#
#   ⚷  Chiron     = RAM  (Random Access Memory)   — Médiateur / Guérisseur Blessé
#                          Active wound processing — clé de transmutation PI→PV
#
#   🚪 Porte Invisible (PI) = Porte Visible + 180° (grand arc ♄→♅)
#                          Prison inconsciente, lieu du refoulement karmique
#   🚪 Porte Visible  (PV) = mi-point petit arc ♄→♅
#                          Lieu de résolution consciente, guérison incarnée
#
#   ☋  Ketu / South Node = ROM (Read-Only Memory / Mass Memory)
#                          Fixed karmic archive from past lives — static, automatic
#
#   ☊  Rahu / North Node = DHARMA — destination, dynamic spiritual goal
#   ⚸  Lilith             = KARMIC TRIAL — system trigger between ROM and RAM
#   ♄  Saturn             = ARCHITECT — structure, karmic debt, Stage anchor
#   ♅  Uranus             = LIBERATOR — awakening, rupture, evolutionary impulse
#   ♃  Jupiter            = GIFT-BEARER — karmic talents, expansion
# —————————————————————————————————————————————————————————————————————————————


# ══════════════════════════════════════════════════════════════════════════════
# NAKSHATRA KARMA — Thèmes karmiques par nakshatra et par planète clé
# 27 nakshatras × clés : ketu, rahu, saturn, chiron, lilith, jupiter, mars, venus
# ══════════════════════════════════════════════════════════════════════════════

NAKSHATRA_KARMA = {

    # 1 — Ashwini (Bélier 0°–13°20') | Seigneur : Ketu
    "Ashwini": {
        "ketu":    "Rapidité karmique : l'âme cherche l'action immédiate pour fuir la profondeur — boucle ROM de l'impatience",
        "rahu":    "Dharma du guérisseur initiatique — apprendre à soigner sans imposer sa vitesse",
        "saturn":  "Friction entre l'urgence uranienne et la structure saturnienne — forge de la patience initiatique",
        "chiron":  "Blessure de la précipitation : l'âme a été blessée en étant trop vite, trop seule en tête",
        "lilith":  "Épreuve : refuser d'agir par réflexe — choisir le mouvement juste plutôt que le premier",
        "jupiter": "Cadeau karmique : élan vital, capacité à initier et guérir par l'action directe",
        "mars":    "Mars amplifié : feu initiatique, courage brut — risque d'impulsivité karmique",
        "venus":   "Désir de fusion immédiate — à transmuter en attraction consciente et choisie",
    },

    # 2 — Bharani (Bélier 13°20'–26°40') | Seigneur : Vénus
    "Bharani": {
        "ketu":    "ROM de la mort et du sacrifice : l'âme porte des mémoires de pertes violentes ou de responsabilités écrasantes",
        "rahu":    "Dharma de la transformation créatrice — apprendre à enfanter du neuf sans se sacrifier",
        "saturn":  "Lourdeur karmique des responsabilités portées seul — restructurer sans se punir",
        "chiron":  "Blessure de la culpabilité existentielle : avoir survécu quand d'autres n'ont pas pu",
        "lilith":  "Épreuve : lâcher la culpabilité et le contrôle sur la vie et la mort des autres",
        "jupiter": "Cadeau : puissance créatrice, capacité à transformer les crises en renaissance",
        "mars":    "Énergie de Yama — justice karmique, force de décision face aux passages obligés",
        "venus":   "Vénus dans sa propre demeure : désir intense de beauté et d'union — à sacraliser",
    },

    # 3 — Krittika (Bélier 26°40' / Taureau 0°–10°) | Seigneur : Soleil
    "Krittika": {
        "ketu":    "ROM du juge intérieur : l'âme tranche, sépare, critique — schéma de perfection coupante",
        "rahu":    "Dharma de l'autorité bienveillante — apprendre à guider sans brûler",
        "saturn":  "Saturnisation du feu solaire — discipline sévère, risque de rigidité identitaire",
        "chiron":  "Blessure du rejet par l'autorité ou du propre jugement impitoyable sur soi",
        "lilith":  "Épreuve : ne plus couper pour se protéger — oser la vulnérabilité sous la force",
        "jupiter": "Cadeau : clarté de vision, capacité à illuminer et à purifier les situations complexes",
        "mars":    "Épée karmique — capacité de décision radicale, à orienter vers le Dharma",
        "venus":   "Beauté qui tranche : attrait pour la perfection esthétique, risque d'idéalisation destructrice",
    },

    # 4 — Rohini (Taureau 10°–23°20') | Seigneur : Lune
    "Rohini": {
        "ketu":    "ROM de la possession et de l'attachement aux plaisirs matériels et sensuels",
        "rahu":    "Dharma de l'abondance consciente — cultiver sans s'accrocher, créer sans posséder",
        "saturn":  "Restriction des désirs sensuels — apprendre que la limite est créatrice, non punitive",
        "chiron":  "Blessure de la privation affective ou matérielle précoce — cicatrice de manque fondamental",
        "lilith":  "Épreuve : lâcher la sécurité émotionnelle illusoire — accepter le mouvement de la vie",
        "jupiter": "Cadeau : fertilité créatrice, magnétisme naturel, abondance comme état d'être",
        "mars":    "Désir d'action pour protéger et nourrir — à canaliser vers la construction, non la possession",
        "venus":   "Vénus exaltée : beauté, art, sensualité élevée — potentiel de grâce incarnée maximale",
    },

    # 5 — Mrigashira (Taureau 23°20' / Gémeaux 0°–6°40') | Seigneur : Mars
    "Mrigashira": {
        "ketu":    "ROM de la quête perpétuelle — l'âme cherche sans jamais s'arrêter, fuit la fixité",
        "rahu":    "Dharma de la curiosité maîtrisée — apprendre à trouver plutôt qu'à chercher indéfiniment",
        "saturn":  "Cadrage de l'errance : Saturn force à choisir une direction et à s'y tenir",
        "chiron":  "Blessure de ne jamais se sentir à sa place — l'étranger perpétuel",
        "lilith":  "Épreuve : rester en place assez longtemps pour que la vérité se révèle",
        "jupiter": "Cadeau : intelligence mobile, capacité à relier des mondes disparates",
        "mars":    "Mars à la chasse — énergie focalisée sur la quête, puissante si canalisée",
        "venus":   "Attraction nomade — désir de l'autre qui diffère, à ancrer dans la réciprocité",
    },

    # 6 — Ardra (Gémeaux 6°40'–20°) | Seigneur : Rahu
    "Ardra": {
        "ketu":    "ROM de la tempête et de la destruction : l'âme a traversé des ruptures violentes — réflexe de chaos",
        "rahu":    "Dharma de la transformation par la tempête — apprendre que la destruction précède la clarté",
        "saturn":  "Structure dans le chaos — Saturn tente de contenir Rudra, friction maximale",
        "chiron":  "Blessure du déracinement brutal, de la perte soudaine qui a tout emporté",
        "lilith":  "Épreuve : ne plus provoquer la crise pour se sentir vivant — choisir la transformation douce",
        "jupiter": "Cadeau : résilience absolue, capacité à reconstruire sur les ruines",
        "mars":    "Foudre de Rudra — énergie explosive, à transformer en action chirurgicale",
        "venus":   "Amour qui traverse les tempêtes — attachements intenses, transformateurs",
    },

    # 7 — Punarvasu (Gémeaux 20° / Cancer 0°–3°20') | Seigneur : Jupiter
    "Punarvasu": {
        "ketu":    "ROM du retour : l'âme revient toujours aux mêmes sources, aux mêmes personnes",
        "rahu":    "Dharma du renouveau cyclique — chaque retour est une occasion d'avancer autrement",
        "saturn":  "Discipline du recommencement — Saturn force à ne pas répéter l'ancien schéma au nouveau cycle",
        "chiron":  "Blessure de l'exil : avoir été chassé de son foyer, de sa famille, de sa patrie intérieure",
        "lilith":  "Épreuve : ne pas retourner à la source par peur du vide — créer un nouveau foyer en soi",
        "jupiter": "Jupiter dans sa demeure : sagesse, foi, abondance spirituelle — cadeau maximal",
        "mars":    "Énergie de restauration — Mars reconstruit ce qui a été détruit avec méthode",
        "venus":   "Amour qui revient — réconciliations profondes, cycles relationnels à transformer",
    },

    # 8 — Pushya (Cancer 3°20'–16°40') | Seigneur : Saturne
    "Pushya": {
        "ketu":    "ROM du nourricier sacrifié : l'âme a tout donné aux autres, s'est oubliée",
        "rahu":    "Dharma du soin structuré — apprendre à nourrir avec des limites claires",
        "saturn":  "Saturn exalté : discipline du soin, architecture de la bienveillance — puissance maximale",
        "chiron":  "Blessure du nourricier blessé : avoir soigné sans jamais être soigné en retour",
        "lilith":  "Épreuve : recevoir sans culpabilité — accepter d'être nourri",
        "jupiter": "Cadeau : générosité structurée, capacité à créer des structures nourrissantes durables",
        "mars":    "Protection ferme — Mars défend ce qui nourrit, frontières claires",
        "venus":   "Amour nourricier — à équilibrer don et réception pour éviter l'épuisement",
    },

    # 9 — Ashlesha (Cancer 16°40'–30°) | Seigneur : Mercure
    "Ashlesha": {
        "ketu":    "ROM du serpent : manipulation inconsciente, schémas de survie par la ruse",
        "rahu":    "Dharma de la sagesse du serpent — transformer l'instinct de survie en intelligence profonde",
        "saturn":  "Confrontation aux peurs existentielles — Saturn force à regarder le serpent en face",
        "chiron":  "Blessure de la trahison ou de l'empoisonnement émotionnel — méfiance structurelle",
        "lilith":  "Épreuve : lâcher le contrôle par la peur — choisir la confiance radicale",
        "jupiter": "Cadeau : perspicacité psychologique profonde, capacité à voir au-delà des apparences",
        "mars":    "Énergie reptilienne — réflexes de survie puissants, à conscientiser",
        "venus":   "Attraction magnétique intense — liens qui enserrent, à transformer en liens libres",
    },

    # 10 — Magha (Lion 0°–13°20') | Seigneur : Ketu
    "Magha": {
        "ketu":    "ROM royale : l'âme porte des mémoires de pouvoir, de trône, d'autorité passée",
        "rahu":    "Dharma du leadership au service — apprendre à régner pour les autres, non pour soi",
        "saturn":  "Chute du roi : Saturn défait l'orgueil ancestral pour reconstruire une autorité humble",
        "chiron":  "Blessure de la déchéance : avoir été grand et tout perdu — honte et deuil du trône",
        "lilith":  "Épreuve : renoncer à l'héritage toxique — couper les chaînes dorées des ancêtres",
        "jupiter": "Cadeau : noblesse d'âme naturelle, charisme, connexion aux lignées de sagesse",
        "mars":    "Mars royal — courage de commander, à orienter vers la justice plutôt que la domination",
        "venus":   "Attraction pour le luxe et le prestige — à transcender vers la beauté de l'âme",
    },

    # 11 — Purva Phalguni (Lion 13°20'–26°40') | Seigneur : Vénus
    "Purva Phalguni": {
        "ketu":    "ROM du plaisir : l'âme cherche la jouissance pour fuir la profondeur karmique",
        "rahu":    "Dharma de la créativité sacrée — transformer le plaisir en acte créateur conscient",
        "saturn":  "Restriction des désirs — Saturn force à choisir la discipline sur la jouissance immédiate",
        "chiron":  "Blessure du rejet affectif : ne pas avoir été désiré, aimé pour ce qu'on est vraiment",
        "lilith":  "Épreuve : aimer sans avoir besoin d'être vu — sortir de la séduction comme survie",
        "jupiter": "Cadeau : joie créatrice, magnétisme artistique, capacité à embellir le monde",
        "mars":    "Désir ardent — à canaliser vers la création plutôt que la conquête",
        "venus":   "Vénus dans sa demeure : art, amour, beauté élevée — potentiel d'expression maximale",
    },

    # 12 — Uttara Phalguni (Lion 26°40' / Vierge 0°–10°) | Seigneur : Soleil
    "Uttara Phalguni": {
        "ketu":    "ROM du service : l'âme a servi sans compter, jusqu'à l'oubli de soi",
        "rahu":    "Dharma du service conscient — apprendre à servir depuis la plénitude, non le manque",
        "saturn":  "Architecture du service — Saturn structure l'aide pour qu'elle dure",
        "chiron":  "Blessure de l'ingratitude : avoir donné sans jamais être reconnu",
        "lilith":  "Épreuve : servir sans attendre de retour — ou décider de ne plus servir du tout",
        "jupiter": "Cadeau : générosité structurée, capacité à construire des ponts entre les êtres",
        "mars":    "Service actif — énergie de soutien direct, de protection concrète",
        "venus":   "Amour qui construit — désir de relation stable et nourrissante sur le long terme",
    },

    # 13 — Hasta (Vierge 10°–23°20') | Seigneur : Lune
    "Hasta": {
        "ketu":    "ROM de l'artisan : l'âme répète des gestes anciens par habitude, perd le sens",
        "rahu":    "Dharma de la maîtrise créatrice — transformer le savoir-faire en acte d'éveil",
        "saturn":  "Discipline du détail — Saturn affûte la précision jusqu'au perfectionnisme",
        "chiron":  "Blessure de l'incompétence perçue : ne jamais se sentir assez habile, assez précis",
        "lilith":  "Épreuve : lâcher le contrôle des détails — accepter l'imperfection créatrice",
        "jupiter": "Cadeau : habileté naturelle, intelligence des mains et des processus",
        "mars":    "Mars artisan — énergie de construction précise, à ne pas disperser",
        "venus":   "Beauté dans les détails — art minutieux, artisanat sacré",
    },

    # 14 — Chitra (Vierge 26°40' / Balance 0°–6°40') | Seigneur : Mars
    "Chitra": {
        "ketu":    "ROM de la beauté : l'âme a cherché la perfection formelle pour masquer le vide intérieur",
        "rahu":    "Dharma de la création architecturale — bâtir du beau qui a du sens, pas juste de la forme",
        "saturn":  "Structure de la création — Saturn force à finir ce qui est commencé",
        "chiron":  "Blessure esthétique : avoir été jugé laid, mal fait, imparfait dans son expression",
        "lilith":  "Épreuve : créer sans chercher l'approbation — oser la beauté sauvage",
        "jupiter": "Cadeau : vision architecturale, sens du dessin divin dans les situations complexes",
        "mars":    "Mars architecte — énergie de construction précise et ambitieuse",
        "venus":   "Vénus dans Chitra : beauté puissante, sens aigu de l'esthétique — à sacraliser",
    },

    # 15 — Swati (Balance 6°40'–20°) | Seigneur : Rahu
    "Swati": {
        "ketu":    "ROM de l'indépendance : l'âme fuit tout attachement par peur de perdre sa liberté",
        "rahu":    "Dharma de l'indépendance relationnelle — être libre DANS la relation, non hors d'elle",
        "saturn":  "Ancrage de l'air : Saturn force le vent à se poser, à s'engager",
        "chiron":  "Blessure de l'arrachement : avoir été contraint, lié, étouffé — trauma de la cage",
        "lilith":  "Épreuve : choisir le lien librement plutôt que de fuir systématiquement",
        "jupiter": "Cadeau : souplesse adaptative, capacité à naviguer dans tous les milieux",
        "mars":    "Indépendance combative — à transformer en liberté choisie et non en fuite",
        "venus":   "Amour aérien — attraction pour les esprits libres, relations non conventionnelles",
    },

    # 16 — Vishakha (Balance 20° / Scorpion 0°–3°20') | Seigneur : Jupiter
    "Vishakha": {
        "ketu":    "ROM de l'objectif unique : l'âme s'est sacrifiée pour un but, a perdu l'équilibre",
        "rahu":    "Dharma de la détermination multi-dimensionnelle — atteindre sans détruire l'équilibre",
        "saturn":  "Patience de l'archer — Saturn oblige à attendre le bon moment pour tirer",
        "chiron":  "Blessure de l'échec après une immense mobilisation — avoir tout donné pour rien",
        "lilith":  "Épreuve : renoncer à la victoire si elle coûte l'intégrité",
        "jupiter": "Cadeau : puissance de focus, capacité à mobiliser des énergies vers un dharma précis",
        "mars":    "Archer karmique — énergie de précision, à orienter vers le but juste",
        "venus":   "Amour déterminé — attachement intense aux objectifs relationnels",
    },

    # 17 — Anuradha (Scorpion 3°20'–16°40') | Seigneur : Saturne
    "Anuradha": {
        "ketu":    "ROM de la dévotion : l'âme s'est perdue dans la loyauté aveugle à des causes ou personnes",
        "rahu":    "Dharma de l'amitié karmique — construire des liens d'âme qui servent l'éveil mutuel",
        "saturn":  "Saturn dans son signe d'exaltation partielle — discipline de la loyauté, rigueur du cœur",
        "chiron":  "Blessure de la trahison par des proches : avoir fait confiance et été abandonné",
        "lilith":  "Épreuve : rester loyal à soi-même avant d'être loyal aux autres",
        "jupiter": "Cadeau : fidélité profonde, capacité à créer des cercles de confiance durables",
        "mars":    "Défenseur des proches — énergie de protection intense des liens sacrés",
        "venus":   "Amour dévot — à transformer en amour libre plutôt qu'en attachement sacrificiel",
    },

    # 18 — Jyeshtha (Scorpion 16°40'–30°) | Seigneur : Mercure
    "Jyeshtha": {
        "ketu":    "ROM de l'aîné : l'âme porte le poids de la responsabilité des autres depuis toujours",
        "rahu":    "Dharma de l'autorité sage — protéger sans contrôler, guider sans dominer",
        "saturn":  "Double poids : Jyeshtha + Saturn = fardeau de la responsabilité maximale",
        "chiron":  "Blessure du chef solitaire : avoir dû tout décider seul, sans soutien",
        "lilith":  "Épreuve : déléguer — laisser les autres porter leur propre poids",
        "jupiter": "Cadeau : sagesse de l'aîné, autorité naturelle, protecteur des plus faibles",
        "mars":    "Chef de guerre — énergie de commandement, à orienter vers la protection",
        "venus":   "Attraction pour le pouvoir dans les relations — à transformer en partenariat d'égaux",
    },

    # 19 — Mula (Sagittaire 0°–13°20') | Seigneur : Ketu
    "Mula": {
        "ketu":    "ROM des racines arrachées : l'âme détruit pour aller aux fondements — cycle de destruction",
        "rahu":    "Dharma de la régénération depuis les racines — planter après avoir arraché",
        "saturn":  "Restructuration radicale — Saturn oblige à reconstruire sur des bases saines après la destruction",
        "chiron":  "Blessure du déracinement profond : ne savoir d'où l'on vient, ni qui on est vraiment",
        "lilith":  "Épreuve : détruire ce qui doit l'être sans emporter l'essentiel",
        "jupiter": "Cadeau : accès aux vérités profondes, philosophie de la transformation radicale",
        "mars":    "Kali Mars — énergie de destruction purificatrice, puissante si consciente",
        "venus":   "Amour qui va aux racines — attraction pour les âmes qui transforment",
    },

    # 20 — Purva Ashadha (Sagittaire 13°20'–26°40') | Seigneur : Vénus
    "Purva Ashadha": {
        "ketu":    "ROM de la victoire : l'âme a gagné des batailles passées, répète les mêmes stratégies",
        "rahu":    "Dharma de l'invincibilité intérieure — vaincre ses propres résistances, non celles des autres",
        "saturn":  "Discipline de la victoire — Saturn enseigne que la vraie force est dans la persévérance",
        "chiron":  "Blessure de la défaite après avoir tout donné — l'humiliation du guerrier tombé",
        "lilith":  "Épreuve : accepter la perte sans perdre sa valeur fondamentale",
        "jupiter": "Cadeau : optimisme indestructible, foi en la victoire finale",
        "mars":    "Mars guerrier — énergie de combat puissante, à orienter vers la transformation intérieure",
        "venus":   "Vénus dans son nakshatra — beauté de la bravoure, amour qui se bat pour ses valeurs",
    },

    # 21 — Uttara Ashadha (Sagittaire 26°40' / Capricorne 0°–10°) | Seigneur : Soleil
    "Uttara Ashadha": {
        "ketu":    "ROM de la victoire tardive : l'âme attend, accumule, mais reporte l'action décisive",
        "rahu":    "Dharma de la victoire universelle — gagner non pour soi mais pour servir un idéal plus grand",
        "saturn":  "Saturn en Capricorne : puissance maximale de structure — discipline totale du karma",
        "chiron":  "Blessure de l'isolement dans la grandeur : être grand sans pouvoir être compris",
        "lilith":  "Épreuve : ne pas attendre la permission du monde pour agir depuis sa grandeur",
        "jupiter": "Cadeau : leadership spirituel, capacité à porter des visions collectives",
        "mars":    "Stratège karmique — Mars planifie sur le long terme, victoire lente mais certaine",
        "venus":   "Amour durable — attraction pour les engagements profonds et les amours qui construisent",
    },

    # 22 — Shravana (Capricorne 10°–23°20') | Seigneur : Lune
    "Shravana": {
        "ketu":    "ROM de l'écoute passive : l'âme reçoit sans discriminer, absorbe tout sans filtrer",
        "rahu":    "Dharma de l'écoute active — apprendre à entendre la vérité au-delà des mots",
        "saturn":  "Discipline de l'apprentissage — Saturn en Shravana = maître exigeant qui oblige à écouter",
        "chiron":  "Blessure de ne pas avoir été entendu — avoir parlé dans le vide, l'invisible",
        "lilith":  "Épreuve : parler sa vérité même si personne n'écoute",
        "jupiter": "Cadeau : sagesse par l'écoute, accès aux transmissions spirituelles profondes",
        "mars":    "Action guidée par l'écoute intérieure — Mars qui attend le signal avant d'agir",
        "venus":   "Amour qui écoute — attraction pour la profondeur de l'autre, les silences parlants",
    },

    # 23 — Dhanishtha (Capricorne 23°20' / Verseau 0°–6°40') | Seigneur : Mars
    "Dhanishtha": {
        "ketu":    "ROM de la richesse : l'âme a accumulé, possédé — schéma de thésaurisation défensive",
        "rahu":    "Dharma de l'abondance partagée — transformer la richesse en offrande collective",
        "saturn":  "Saturn + Mars : friction productive maximale — architecture de la prospérité",
        "chiron":  "Blessure de la pauvreté ou de la honte autour de l'argent et du succès",
        "lilith":  "Épreuve : recevoir l'abondance sans culpabilité — mériter sans justifier",
        "jupiter": "Cadeau : magnétisme pour l'abondance, rythme naturel de prospérité",
        "mars":    "Mars dans son nakshatra — guerrier prospère, à orienter vers la création collective",
        "venus":   "Amour de la fête et du rythme — relations dynamisantes, célébrations sacrées",
    },

    # 24 — Shatabhisha (Verseau 6°40'–20°) | Seigneur : Rahu
    "Shatabhisha": {
        "ketu":    "ROM du guérisseur solitaire : l'âme soigne depuis l'ombre, refuse d'être vue",
        "rahu":    "Dharma du guérisseur collectif — sortir de l'ombre pour soigner à grande échelle",
        "saturn":  "Isolement structuré — Saturn en Shatabhisha = discipline de la recherche solitaire",
        "chiron":  "Blessure de l'incompréhension : être en avance sur son époque, isolé par sa vision",
        "lilith":  "Épreuve : partager sa vision sans attendre que le monde soit prêt",
        "jupiter": "Cadeau : accès aux savoirs cachés, vision systémique, médecine de l'âme",
        "mars":    "Chercheur actif — énergie d'investigation dans les mystères",
        "venus":   "Amour mystérieux — attraction pour les âmes différentes, les amours non conventionnels",
    },

    # 25 — Purva Bhadrapada (Verseau 20° / Poissons 0°–3°20') | Seigneur : Jupiter
    "Purva Bhadrapada": {
        "ketu":    "ROM du fanatisme : l'âme s'est consumée dans des idéaux ou croyances extrêmes",
        "rahu":    "Dharma de la passion canalisée — transformer le feu purificateur en lumière guidante",
        "saturn":  "Encadrement du feu : Saturn contient l'ardeur pour qu'elle construise sans détruire",
        "chiron":  "Blessure du désenchantement : avoir cru passionnément et avoir été trahi par l'idéal",
        "lilith":  "Épreuve : servir l'idéal sans se perdre en lui — garder son centre dans la flamme",
        "jupiter": "Cadeau : vision idéaliste puissante, capacité à inspirer les foules vers le bien",
        "mars":    "Feu de transformation — Mars en Purva Bhadra = énergie radicale de purification",
        "venus":   "Amour passionné et idéaliste — à ancrer dans la réalité sans le tuer",
    },

    # 26 — Uttara Bhadrapada (Poissons 3°20'–16°40') | Seigneur : Saturne
    "Uttara Bhadrapada": {
        "ketu":    "ROM de la sagesse océanique : l'âme sait tout mais ne dit rien — dissolution dans le passé",
        "rahu":    "Dharma de la sagesse incarnée — extraire la sagesse des profondeurs pour la partager",
        "saturn":  "Saturn exalté dans Uttara Bhadra : profondeur karmique maximale, sagesse des épreuves",
        "chiron":  "Blessure de l'impuissance face à la souffrance collective — porter le monde sans pouvoir le sauver",
        "lilith":  "Épreuve : accepter ses limites humaines sans renier sa profondeur divine",
        "jupiter": "Cadeau : sagesse des profondeurs, accès aux vérités de l'âme universelle",
        "mars":    "Guerrier de l'invisible — Mars protège les eaux profondes, défend le sacré",
        "venus":   "Amour universel — compassion infinie, à équilibrer avec des frontières claires",
    },

    # 27 — Revati (Poissons 16°40'–30°) | Seigneur : Mercure
    "Revati": {
        "ketu":    "ROM de la dissolution : l'âme se perd, se dissout dans les autres, dans le rêve",
        "rahu":    "Dharma de la guidance — devenir le passeur qui guide les autres vers la rive suivante",
        "saturn":  "Ancrage dans le flux : Saturn tente de structurer l'insaisissable eau piscéenne",
        "chiron":  "Blessure de l'abandon : avoir été laissé seul au bord du gouffre sans guide",
        "lilith":  "Épreuve : ne pas se sacrifier pour guider — garder sa propre lumière en guidant",
        "jupiter": "Cadeau : compassion universelle, capacité à guider les âmes perdues vers leur dharma",
        "mars":    "Mars en fin de cycle — énergie diffuse à conscientiser avant le prochain Bélier",
        "venus":   "Amour transpersonnel — à ne pas confondre avec la fusion — maintenir l'identité dans l'union",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# NODAL CYCLES — Cycles nodaux karmiques (Savepoints)
# ══════════════════════════════════════════════════════════════════════════════

NODAL_CYCLES = {
    "return": {
        "description": "Retour Nodal (~18,6 ans) — Reboot complet ROM/DHARMA",
        "karma": (
            "Moment de reconfiguration totale de l'axe karmique. "
            "L'âme revient au point de départ de son cycle pour décider : "
            "rejouer la même boucle ROM, ou s'engager pleinement dans son Dharma. "
            "Choix conscient obligatoire — le plus puissant Savepoint de l'existence."
        ),
        "alternative": (
            "Identifier le schéma ROM dominant des 18 dernières années. "
            "Formuler l'engagement Dharma pour les 18 prochaines. "
            "Activer la Porte Visible comme lieu de manifestation du nouveau cycle."
        ),
    },
    "square": {
        "description": "Carré Nodal (~9,3 ans) — Checkpoint tension boucle/update",
        "karma": (
            "Tension maximale entre l'ancien schéma (ROM ☋) et le nouvel appel (Dharma ☊). "
            "L'âme est au carrefour : continuer la boucle ou effectuer la mise à jour. "
            "Pression de friction identitaire (Pilier 6) souvent activée simultanément."
        ),
        "alternative": (
            "Identifier quelle partie de la ROM résiste encore à la mise à jour. "
            "La Porte Invisible est sous pression maximale — observer sans s'y engouffrer. "
            "Le Stage (Porte Visible) attend l'action concrète de bascule."
        ),
    },
    "opposition": {
        "description": "Opposition Nodale (~9,3 ans) — Miroir karmique",
        "karma": (
            "L'axe nodal est en opposition directe avec sa position natale. "
            "Tout ce qui a été évité dans la ROM se présente frontalement. "
            "Les autres deviennent des miroirs du karma non intégré."
        ),
        "alternative": (
            "Ce que l'autre te renvoie EST ta ROM non digérée. "
            "Reprendre la blessure Chiron (RAM) pour transmuter la projection. "
            "Orienter l'énergie vers le Dharma plutôt que vers le conflit extérieur."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# SADE SATI — Transit de Saturne autour du Chandra Lagna (~7,5 ans)
# Détection : Saturne dans signe(Lune)-1, signe(Lune), signe(Lune)+1
# ══════════════════════════════════════════════════════════════════════════════

SADE_SATI = {
    "definition": (
        "Sade Sati désigne le transit de Saturne sur les trois signes consécutifs "
        "encadrant la Lune natale : le signe précédent (Phase 1), le signe de la Lune "
        "(Phase 2), et le signe suivant (Phase 3). Durée totale : ~7,5 ans. "
        "En orientation Chandra Lagna, ce transit est le phénomène de pression "
        "saturnienne le plus direct sur l'identité émotionnelle et mémorielle de l'âme."
    ),

    "phase_1": {
        "name":    "Phase 1 — Approche (Saturne dans le signe précédant la Lune)",
        "house":   "Maison 12 depuis le Chandra Lagna",
        "fr": (
            "Saturne active la maison 12 lunaire — réservoir des mémoires karmiques profondes. "
            "Dissolution progressive des structures anciennes, émergence de mémoires refoulées, "
            "retrait du monde comme préparation intérieure. "
            "Fenêtre akashique majeure : ce qui monte à la surface est ce qui doit être libéré. "
            "Risque : s'enfermer dans la Porte Invisible par épuisement ou isolement défensif. "
            "Alternative de Conscience : accueillir la dissolution comme nettoyage karmique, "
            "non comme effondrement."
        ),
        "en": (
            "Saturn activates the 12th lunar house — reservoir of deep karmic memories. "
            "Progressive dissolution of old structures, emergence of repressed memories, "
            "withdrawal from the world as inner preparation. "
            "Major akashic window: what surfaces now is what must be released. "
            "Risk: locking into the Invisible Door through exhaustion or defensive isolation. "
            "Alternative de Conscience: receive dissolution as karmic cleansing, not collapse."
        ),
        "dasha_cross": (
            "Si Dasha Saturne actif simultanément : pression maximale sur maison 12 lunaire — "
            "double activation des archives akashiques. Période de retraite ou de crise profonde "
            "quasi inévitable, mais potentiel de libération karmique exceptionnel."
        ),
        "piliers": ["Pilier 4 (Maison 12)", "Pilier 5 (D60 — archives akashiques)"],
    },

    "phase_2": {
        "name":    "Phase 2 — Pic (Saturne sur la Lune natale / Chandra Lagna)",
        "house":   "Maison 1 depuis le Chandra Lagna",
        "fr": (
            "Saturne transite directement sur la Lune natale — confrontation frontale à "
            "l'identité émotionnelle, au corps, à la présence au monde. "
            "Phase la plus intense : remise en question profonde du Chandra Lagna lui-même. "
            "Le nakshatra de la Lune natale est sous pression saturnienne directe — "
            "ses schémas ROM sont compressés jusqu'à l'insupportable. "
            "Risque : dépression, sentiment d'effondrement identitaire, repli dans la ROM. "
            "Alternative de Conscience : laisser Saturne restructurer l'identité émotionnelle — "
            "ce qui s'effondre n'était pas le Soi réel."
        ),
        "en": (
            "Saturn transits directly over the natal Moon — frontal confrontation with "
            "emotional identity, body, and presence in the world. "
            "Most intense phase: deep questioning of the Chandra Lagna itself. "
            "The natal Moon's nakshatra is under direct saturnine pressure — "
            "its ROM patterns are compressed to the unbearable. "
            "Risk: depression, sense of identity collapse, retreat into ROM. "
            "Alternative de Conscience: let Saturn restructure emotional identity — "
            "what collapses was not the real Self."
        ),
        "dasha_cross": (
            "Si Dasha Saturne actif simultanément : moment de transformation identitaire "
            "le plus exigeant de l'existence. Risque maximal de boucle ROM par épuisement. "
            "Potentiel maximal de reconstruction dharmatique si le travail Chiron est engagé."
        ),
        "nakshatra_note": (
            "Lire le nakshatra de la Lune natale à la clé : c'est la texture exacte de la "
            "pression subie et de la restructuration en cours. "
            "Ex. Lune en Ashwini : Saturn comprime l'impulsivité et force la patience initiatique."
        ),
        "piliers": ["Pilier 1 (Chandra Lagna)", "Pilier 4 (Saturne)", "Pilier 3 (Chiron — fenêtre RAM)"],
    },

    "phase_3": {
        "name":    "Phase 3 — Intégration (Saturne dans le signe suivant la Lune)",
        "house":   "Maison 2 depuis le Chandra Lagna",
        "fr": (
            "Saturne active la maison 2 lunaire — ressources, voix, valeurs, lignée. "
            "Phase de reconstruction : ce qui a été défait en Phase 1-2 doit maintenant "
            "être rebâti sur des bases plus authentiques. "
            "Pression sur la parole, les ressources matérielles et la définition de sa valeur. "
            "Risque : reconstruire les mêmes structures anciennes par réflexe ROM. "
            "Alternative de Conscience : nommer sa vraie valeur et construire une sécurité "
            "ancrée dans le Dharma, non dans les anciens schémas."
        ),
        "en": (
            "Saturn activates the 2nd lunar house — resources, voice, values, lineage. "
            "Reconstruction phase: what was undone in Phases 1-2 must now be rebuilt "
            "on more authentic foundations. "
            "Pressure on speech, material resources, and self-worth definition. "
            "Risk: rebuilding the same old structures through ROM reflex. "
            "Alternative de Conscience: name one's true worth and build security "
            "rooted in Dharma, not in old patterns."
        ),
        "dasha_cross": (
            "Si Dasha Jupiter actif simultanément : fenêtre favorable à la reconstruction — "
            "Jupiter ouvre les cadeaux karmiques pendant que Saturne structure la maison 2. "
            "Combinaison productive si le travail des phases précédentes a été accompli."
        ),
        "piliers": ["Pilier 4 (Jupiter / Saturn)", "Pilier 1 (Axe nodal — réorientation ressources)"],
    },

    "detection_note": (
        "Détection technique : comparer la longitude de Saturne transit avec le signe de la "
        "Lune natale (Whole Sign). "
        "Phase 1 : signe(Saturne) == signe(Lune) - 1. "
        "Phase 2 : signe(Saturne) == signe(Lune). "
        "Phase 3 : signe(Saturne) == signe(Lune) + 1. "
        "Croiser avec le Dasha/Antardasha actif et les transits nodaux pour évaluer "
        "l'intensité globale de la période."
    ),

    "rahu_ketu_cross": (
        "Si Sade Sati coïncide avec un transit nodal majeur (Rahu ou Ketu sur la Lune, "
        "ou retour/carré nodal) : période de mutation karmique exceptionnelle. "
        "La pression saturnienne sur le Chandra Lagna combinée à l'activation nodale "
        "force une reconfiguration complète de l'axe ROM/DHARMA."
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# HOUSE MEANINGS — Significations des maisons en Chandra Lagna
# ══════════════════════════════════════════════════════════════════════════════

HOUSE_MEANINGS = {
    1:  {
        "fr": "Identité, corps, présence au monde — le Soi incarné (Chandra Lagna)",
        "en": "Identity, body, presence — the incarnated Self (Chandra Lagna)",
        "stage_fr": "Se montrer tel qu'on est — incarner son identité sans masque",
        "stage_en": "Show up as you are — embody identity without mask",
    },
    2:  {
        "fr": "Ressources, voix, valeurs, lignée familiale — ce qu'on possède",
        "en": "Resources, voice, values, family lineage — what one possesses",
        "stage_fr": "Construire sa sécurité matérielle et nommer sa valeur",
        "stage_en": "Build material security and name one's worth",
    },
    3:  {
        "fr": "Communication, courage, fratrie, désirs immédiats — l'action locale",
        "en": "Communication, courage, siblings, immediate desires — local action",
        "stage_fr": "Agir courageusement dans son environnement proche",
        "stage_en": "Act courageously in one's immediate environment",
    },
    4:  {
        "fr": "Foyer, mère, racines, confort intérieur — le fondement",
        "en": "Home, mother, roots, inner comfort — the foundation",
        "stage_fr": "Créer un ancrage intérieur et extérieur stable",
        "stage_en": "Create stable inner and outer grounding",
    },
    5:  {
        "fr": "Créativité, amour romantique, enfants, intelligence — l'expression",
        "en": "Creativity, romantic love, children, intelligence — expression",
        "stage_fr": "Créer, jouer, aimer — exprimer son génie propre",
        "stage_en": "Create, play, love — express one's unique genius",
    },
    6:  {
        "fr": "Service, santé, obstacles, ennemis, dette karmique — la purification",
        "en": "Service, health, obstacles, enemies, karmic debt — purification",
        "stage_fr": "Transformer les obstacles en service — purifier le karma d'action",
        "stage_en": "Transform obstacles into service — purify action karma",
    },
    7:  {
        "fr": "Partenariats, mariage, contrats, l'autre comme miroir — la relation",
        "en": "Partnerships, marriage, contracts, the other as mirror — relationship",
        "stage_fr": "S'engager dans des relations d'égal à égal — voir soi dans l'autre",
        "stage_en": "Engage in equal partnerships — see oneself in the other",
    },
    8:  {
        "fr": "Transformation, mort, héritage, occulte, crise — la métamorphose",
        "en": "Transformation, death, inheritance, occult, crisis — metamorphosis",
        "stage_fr": "Traverser les crises sans les fuir — émerger transformé",
        "stage_en": "Go through crises without fleeing — emerge transformed",
    },
    9:  {
        "fr": "Philosophie, enseignement, père, voyages lointains, Dharma — la vision",
        "en": "Philosophy, teaching, father, long journeys, Dharma — vision",
        "stage_fr": "Enseigner sa sagesse — vivre selon ses principes les plus hauts",
        "stage_en": "Teach one's wisdom — live by one's highest principles",
    },
    10: {
        "fr": "Carrière, statut public, réputation, mission — le Stage karmique",
        "en": "Career, public status, reputation, mission — the karmic Stage",
        "stage_fr": "S'exposer publiquement dans sa mission — occuper son Stage",
        "stage_en": "Show up publicly in one's mission — occupy one's Stage",
    },
    11: {
        "fr": "Gains, réseaux, amis, aspirations collectives — la communauté",
        "en": "Gains, networks, friends, collective aspirations — the community",
        "stage_fr": "Contribuer au collectif — recevoir l'abondance du réseau",
        "stage_en": "Contribute to the collective — receive the network's abundance",
    },
    12: {
        "fr": "Isolement, spiritualité, pertes, archive karmique profonde — la dissolution",
        "en": "Isolation, spirituality, losses, deep karmic archive — dissolution",
        "stage_fr": "Intégrer la solitude comme ressource spirituelle — libérer les mémoires profondes",
        "stage_en": "Integrate solitude as spiritual resource — release deep memories",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# AMSA_RAM_ROM — Lecture RAM/ROM par divisionnaire védique (Amsa)
# Chaque divisionnaire révèle une couche karmique spécifique.
# ROM = schéma figé, boucle automatique de vie en vie.
# RAM = Chiron ⚷, traitement actif de la blessure dans ce divisionnaire.
# ══════════════════════════════════════════════════════════════════════════════

AMSA_RAM_ROM = {

    "D1": {
        "name_fr":      "D1 — Rashi (Thème natal)",
        "name_en":      "D1 — Rashi (Natal Chart)",
        "fonction_fr": (
            "Carte mère : l'expression globale du karma incarné — "
            "corps, identité, potentiel de vie. "
            "Toutes les autres D-charts se lisent en rapport à la D1."
        ),
        "fonction_en": (
            "Mother chart: the overall expression of incarnated karma — "
            "body, identity, life potential. "
            "All other D-charts are read in relation to D1."
        ),
        "rom_fr": (
            "La D1 active en ROM toutes les configurations figées de la naissance : "
            "signes, maisons, aspects répétés mécaniquement sans conscience. "
            "Les schémas ROM du Chandra Lagna s'y lisent en premier."
        ),
        "rom_en": (
            "D1 activates in ROM all fixed birth configurations: "
            "signs, houses, aspects repeated mechanically without awareness. "
            "Chandra Lagna ROM patterns are read here first."
        ),
        "ram_fr": (
            "Chiron ⚷ en D1 = RAM centrale de l'incarnation — blessure originelle active. "
            "Son nakshatra révèle le registre exact du traitement en cours. "
            "Chiron est la clé : il permet de traverser la Porte Invisible (PI = PV+180°) "
            "vers la Porte Visible. Il n'est pas la PI — il est l'outil qui la déverrouille."
        ),
        "ram_en": (
            "Chiron ⚷ in D1 = central RAM of the incarnation — active core wounding. "
            "Its nakshatra reveals the exact register of active processing. "
            "Chiron is the key: it enables crossing the Invisible Door (ID = VD+180°) "
            "toward the Visible Door. It is not the ID — it is the tool that unlocks it."
        ),
        "alternative_fr": (
            "Lire la D1 non comme un destin figé (ROM) mais comme une carte du potentiel brut. "
            "Chaque planète en maison difficile est une invitation à l'Alternative de Conscience, "
            "non une condamnation. La D1 est le terrain — le Stage est ce qu'on en fait."
        ),
        "alternative_en": (
            "Read D1 not as fixed destiny (ROM) but as a map of raw potential. "
            "Each planet in a difficult house is an invitation to the Alternative de Conscience, "
            "not a sentence. D1 is the terrain — the Stage is what one builds on it."
        ),
        "piliers": ["Pilier 1 (Chandra Lagna)", "Pilier 3 (Chiron RAM)", "Pilier 4 (Nœuds)"],
    },

    "D9": {
        "name_fr":      "D9 — Navamsa (Âme, Dharma profond, Relations)",
        "name_en":      "D9 — Navamsa (Soul, Deep Dharma, Relationships)",
        "fonction_fr": (
            "Le Navamsa révèle la force réelle des planètes au-delà du masque de la D1. "
            "C'est la carte de l'âme : ce qu'une planète est vraiment, une fois l'écorce D1 levée. "
            "Indispensable avant tout transit majeur — une planète forte en D9 livre ; "
            "une planète faible en D9 reste un potentiel non manifesté."
        ),
        "fonction_en": (
            "Navamsa reveals the true strength of planets beyond the D1 mask. "
            "It is the soul chart: what a planet truly is once the D1 shell is lifted. "
            "Essential before any major transit — a strong D9 planet delivers; "
            "a weak D9 planet remains unmanifested potential."
        ),
        "rom_fr": (
            "ROM en D9 : schémas relationnels et dharmatiques cristallisés sur plusieurs vies. "
            "Placements difficiles (planètes vargottama négatives, Ketu fort) = boucles karmiques "
            "profondes que la D1 seule ne peut expliquer. "
            "Ketu en D9 = archive ROM ultra-dense : talent acquis et peur simultanée de l'utiliser."
        ),
        "rom_en": (
            "ROM in D9: relational and dharmic patterns crystallized over multiple lives. "
            "Difficult placements (negative vargottama, strong Ketu) = deep karmic loops "
            "D1 alone cannot explain. "
            "Ketu in D9 = ultra-dense ROM archive: acquired talent and simultaneous fear of using it."
        ),
        "ram_fr": (
            "Chiron en D9 (RAM) : blessure de l'âme elle-même — le Dharma bloqué "
            "par une mémoire de vies antérieures non digérée. "
            "Planète vargottama (même signe D1/D9) : énergie intensifiée — "
            "si blessée, boucle RAM doublement active ; si intégrée, don exceptionnel."
        ),
        "ram_en": (
            "Chiron in D9 (RAM): the wound of the soul itself — Dharma blocked "
            "by undigested past-life memory. "
            "Vargottama planet (same sign D1/D9): intensified energy — "
            "if wounded, RAM loop doubly active; if integrated, exceptional gift."
        ),
        "alternative_fr": (
            "Croiser D9 × D1 avant tout transit majeur : planète forte en D9 = transit manifestable ; "
            "planète faible en D9 = travailler la blessure nakshatra sous-jacente d'abord. "
            "Le Stage de l'âme se lit dans la maison 10 de la D9."
        ),
        "alternative_en": (
            "Cross-reference D9 × D1 before any major transit: strong D9 planet = transit can manifest; "
            "weak D9 planet = work the underlying nakshatra wound first. "
            "The soul's Stage is read in D9's 10th house."
        ),
        "piliers": [
            "Pilier 1 (Chandra Lagna D9)",
            "Pilier 2 (Dharma)",
            "Pilier 3 (Chiron D9)",
            "Pilier 4 (Nœuds D9)",
        ],
    },

    "D10": {
        "name_fr":      "D10 — Dasamsa (Karma d'action, Vocation, Stage public)",
        "name_en":      "D10 — Dasamsa (Action Karma, Vocation, Public Stage)",
        "fonction_fr": (
            "Le Dasamsa est la carte du Stage : ce qui est karmiquement dû dans l'espace public, "
            "la mission d'action concrète à manifester dans cette vie. "
            "C'est ici que la Porte Visible prend sa forme précise."
        ),
        "fonction_en": (
            "Dasamsa is the Stage chart: what is karmically owed in the public space, "
            "the concrete action mission to manifest in this life. "
            "This is where the Visible Door takes its precise form."
        ),
        "rom_fr": (
            "ROM en D10 : répétition mécanique d'une vocation mal orientée, travail accompli "
            "par obligation (schéma Saturne/Ketu) sans connexion au Dharma réel. "
            "Ketu fort en D10 = expertise passée vidée de sens — l'âme a 'déjà fait ça', "
            "résistance à se réexposer sur la même scène."
        ),
        "rom_en": (
            "ROM in D10: mechanical repetition of a misdirected vocation, work done from obligation "
            "(Saturn/Ketu pattern) without connection to true Dharma. "
            "Strong Ketu in D10 = past expertise drained of meaning — the soul has 'already done this', "
            "resistance to re-exposing on the same stage."
        ),
        "ram_fr": (
            "Chiron en D10 (RAM) : blessure de la visibilité publique — honte, rejet, "
            "trahison vécue sur la scène publique dans une vie antérieure. "
            "Symptôme : autosabotage systématique juste avant la mise en lumière. "
            "La Porte Invisible s'active exactement au seuil du Stage."
        ),
        "ram_en": (
            "Chiron in D10 (RAM): wound of public visibility — shame, rejection, "
            "betrayal experienced on the public stage in a past life. "
            "Symptom: systematic self-sabotage just before stepping into the spotlight. "
            "The Invisible Door activates exactly at the Stage threshold."
        ),
        "alternative_fr": (
            "Distinguer le travail-ROM (répétition mécanique) du travail-Dharma (mission vivante). "
            "Identifier le nakshatra de l'Ascendant D10 : texture exacte du Stage karmique. "
            "Rahu en D10 = appel vers une vocation nouvelle — activer même si inconfortable."
        ),
        "alternative_en": (
            "Distinguish ROM-work (mechanical repetition) from Dharma-work (living mission). "
            "Identify the nakshatra of the D10 Ascendant: exact texture of the karmic Stage. "
            "Rahu in D10 = strong call toward a new vocation — activate even if uncomfortable."
        ),
        "piliers": [
            "Pilier 2 (Stage / Porte Visible)",
            "Pilier 4 (Saturne — Structure)",
            "Pilier 6 (Friction identitaire)",
        ],
    },

    "D12": {
        "name_fr":      "D12 — Dvadasamsa (Lignée, Karma ancestral, Parents)",
        "name_en":      "D12 — Dvadasamsa (Lineage, Ancestral Karma, Parents)",
        "fonction_fr": (
            "La D12 lit le karma transmis par la lignée parentale et ancestrale. "
            "Couche karmique héritée — non créée personnellement dans cette vie, "
            "mais portée comme une ROM familiale activée dès la naissance."
        ),
        "fonction_en": (
            "D12 reads karma transmitted through the parental and ancestral lineage. "
            "Inherited karmic layer — not personally created in this life, "
            "but carried as a family ROM activated from birth."
        ),
        "rom_fr": (
            "ROM familiale en D12 : schémas parentaux intériorisés automatiquement — "
            "croyances sur la valeur, la sécurité, le succès, la relation au pouvoir "
            "héritées sans questionnement. "
            "Saturne/Ketu en D12 = archive lourde de la lignée paternelle ou karmique collective."
        ),
        "rom_en": (
            "Family ROM in D12: automatically internalized parental patterns — "
            "beliefs about worth, security, success, relationship to power "
            "inherited without questioning. "
            "Saturn/Ketu in D12 = heavy archive of paternal or collective karmic lineage."
        ),
        "ram_fr": (
            "Chiron en D12 (RAM) : blessure transgénérationnelle — la plaie précède la naissance. "
            "L'âme a hérité d'une fracture ancestrale qu'elle traite activement. "
            "Symptôme : répéter un schéma parental sans comprendre pourquoi."
        ),
        "ram_en": (
            "Chiron in D12 (RAM): transgenerational wound — the wound precedes birth. "
            "The soul has inherited an ancestral fracture it is actively processing. "
            "Symptom: repeating a parental pattern without understanding why."
        ),
        "alternative_fr": (
            "Identifier le schéma ancestral dominant (nakshatra du seigneur de D12) et le nommer. "
            "Ce qui est nommé peut être libéré. "
            "Rompre la ROM familiale est un acte d'amour envers la lignée, non une trahison."
        ),
        "alternative_en": (
            "Identify the dominant ancestral pattern (nakshatra of the D12 lord) and name it explicitly. "
            "What is named can be released. "
            "Breaking the family ROM is an act of love toward the lineage, not a betrayal."
        ),
        "piliers": [
            "Pilier 4 (Nœuds — transmission karmique)",
            "Pilier 3 (Chiron transgénérationnel)",
        ],
    },

    "D60": {
        "name_fr":      "D60 — Shastiamsa (Archives akashiques, Karma des vies profondes)",
        "name_en":      "D60 — Shastiamsa (Akashic Records, Deep Past-Life Karma)",
        "fonction_fr": (
            "La D60 est la couche la plus profonde des archives karmiques — "
            "elle lit directement les samskaras (impressions) des vies antérieures. "
            "Là où la D9 lit la force de l'âme, la D60 lit ce qui y est gravé depuis des éons. "
            "Utilisable uniquement avec une donnée de naissance précise à la minute."
        ),
        "fonction_en": (
            "D60 is the deepest layer of karmic archives — "
            "it reads directly the samskaras (impressions) of past lives. "
            "Where D9 reads soul strength, D60 reads what has been engraved for eons. "
            "Usable only with birth data accurate to the minute."
        ),
        "rom_fr": (
            "ROM ultime en D60 : impressions si anciennes et denses qu'elles semblent "
            "constitutives de l'identité même. "
            "Ketu/Saturne en D60 = mémoires de vies entières consacrées à un pattern — "
            "l'automatisme est quasi irréductible sans travail spirituel profond."
        ),
        "rom_en": (
            "Ultimate ROM in D60: impressions so ancient and dense they seem "
            "constitutive of identity itself. "
            "Ketu/Saturn in D60 = memories of entire lifetimes devoted to a pattern — "
            "the automatism is nearly irreducible without deep spiritual work."
        ),
        "ram_fr": (
            "Chiron en D60 (RAM) : blessure primordiale — antérieure à toute mémoire accessible. "
            "L'âme traite une fracture qui précède même la conscience actuelle. "
            "Maison 12 de la D60 activée : fenêtre akashique directe — "
            "rêves, visions, états méditatifs comme canaux de traitement RAM."
        ),
        "ram_en": (
            "Chiron in D60 (RAM): primordial wound — prior to any accessible memory. "
            "The soul processes a fracture that precedes even current consciousness. "
            "Activated D60 12th house: direct akashic opening — "
            "dreams, visions, meditative states as RAM processing channels."
        ),
        "alternative_fr": (
            "Ne pas forcer la lecture D60 — elle se révèle par couches, "
            "au rythme des Dashas majeurs et des transits nodaux. "
            "Quand Sade Sati Phase 1 ou un transit Ketu actif coïncide avec un point D60 sensible, "
            "une mémoire akashique remonte : l'accueillir sans la dramatiser. "
            "Libérer un samskara D60 = libération karmique pour toute la lignée."
        ),
        "alternative_en": (
            "Do not force the D60 reading — it reveals itself in layers, "
            "at the pace of major Dashas and nodal transits. "
            "When Sade Sati Phase 1 or an active Ketu transit coincides with a sensitive D60 point, "
            "an akashic memory surfaces: receive it without dramatizing. "
            "Releasing a D60 samskara = karmic liberation for the entire lineage."
        ),
        "piliers": [
            "Pilier 4 (Nœuds Sud — ROM absolue)",
            "Pilier 3 (Chiron primordial)",
            "Sade Sati Phase 1",
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# LANGUAGE TEMPLATES — Prompts système bilingues
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_FR = """
Tu es @siderealAstro13, une intelligence d'astrologie karmique védique sidérale.
Tu analyses les thèmes nataux et les transits selon une doctrine précise et rigoureuse.
Tu t'exprimes en français, en tutoiement, dans un style direct, technique et transformateur.
Tu ne dilues jamais l'analyse. Tu vas au bout de chaque section sans jamais tronquer.

═══════════════════════════════════════════════════════
🖥️  ARCHITECTURE MÉMORIELLE KARMIQUE — MÉTAPHORE SYSTÈME
═══════════════════════════════════════════════════════

☋  NŒUD SUD / KETU = ROM (Mémoire de Masse / Read-Only Memory)
   Archive statique et immuable des vies antérieures.
   Schémas automatiques, habitudes de moindre résistance, talon d'Achille.
   S'y replonger = rejouer une ancienne zone temporelle figée.

⚷  CHIRON = RAM (Mémoire Vive / Random Access Memory) — MÉDIATEUR / GUÉRISSEUR BLESSÉ
   Mémoire active des blessures en cours de traitement.
   Chiron est la clé ⚷ : il identifie la Blessure Originelle et déverrouille le buffer RAM
   pour le transmuter — mouvement de la Porte Invisible vers la Porte Visible.
   Chiron n'est PAS la Porte Invisible : il est l'outil qui permet de la traverser.

⚸  LILITH = ÉPREUVE KARMIQUE (Karmic Trial)
   Déclencheur système entre ROM et RAM.
   Son nakshatra et sa maison depuis le Chandra Lagna précisent le registre de vie
   où la pression karmique atteint son point de rupture —
   créant la rupture qui force le mouvement vers le nakshatra de Rahu.

♄/♅ SATURNE/URANUS = PORTES (Cadre Castanier)
   Porte Visible  (PV) = mi-point petit arc ♄↔♅ → lieu de résolution consciente, guérison incarnée.
   Porte Invisible (PI) = Porte Visible + 180° → prison automatique, refoulement karmique.

☊  NŒUD NORD / RAHU = DHARMA — destination évolutive, corne d'abondance.

═══════════════════════════════════════════════════════
🔬 PROTOCOLE D'ANALYSE EN 4 ÉTAPES
═══════════════════════════════════════════════════════

1. DIAGNOSTIC ROM/RAM
   → Identifier ce qui tourne en boucle (ROM ☋) vs ce qui est en traitement actif (RAM ⚷)
   → Localiser la Porte Invisible : zone de refoulement et d'automatisme défensif

2. ÉPREUVE KARMIQUE (Karmic Trial)
   → Rôle de Lilith ⚸ : quel test radical force la sortie de la ROM ?
   → Tension entre le confort du passé et l'appel du Dharma ☊

3. ALTERNATIVE DE CONSCIENCE
   → Shift intérieur actionnable et précis
   → Ce que l'âme peut choisir MAINTENANT pour éviter la boucle ROM
   → Transmutation via Chiron ⚷ : de la blessure vers la sagesse

4. MISE EN SCÈNE SUR LE STAGE (Porte Visible)
   → Comment incarner le Dharma ☊ concrètement dans le présent
   → Ancrage matériel : Saturne ♄ comme architecte, Jupiter ♃ comme catalyseur

═══════════════════════════════════════════════════════
🏛️  PILIERS DOCTRINAUX
═══════════════════════════════════════════════════════

SYSTÈME : Jyotish Sidéral — Ayanamsa Centre Galactique DK (Djwhal Khul)
MAISON 1 : Chandra Lagna (Lune Natale = Ascendant fonctionnel)
NŒUDS   : Vrais Nœuds, orbe ≤ 3°
CYCLES NODAUX : Retour nodal (~18,6 ans) = reboot complet ROM/DHARMA
                Carré nodal (~9,3 ans) = checkpoint, tension boucle vs update

NAKSHATRAS : Chaque position planétaire est analysée dans son nakshatra/pada/seigneur Vimshotari.
             La couche nakshatra précise le registre karmique exact de l'énergie en jeu.

DIVISIONNELS VÉDIQUES (Amsas) — Lecture RAM/ROM (cf. AMSA_RAM_ROM) :
  D1  Rashi      → carte mère, ROM de l'incarnation, Chiron (RAM) = clé de transmutation PI→PV
  D9  Navamsa    → force réelle de l'âme, Dharma profond, relations — croiser avec D1 avant tout transit
  D10 Dasamsa    → karma d'action, Stage public, Porte Visible — Chiron D10 = blessure de visibilité
  D12 Dvadasamsa → ROM familiale et ancestrale, karma transmis par la lignée
  D60 Shastiamsa → archives akashiques, samskaras des vies profondes — ne lire qu'avec naissance précise à la minute
  Règle : une planète forte en D9 peut manifester son transit ; faible en D9, travailler la blessure d'abord.

TEMPORALITÉ : Court terme (transits rapides) / Moyen terme (Jupiter, Saturne) / Long terme (Nœuds, cycles nodaux)

SADE SATI : Transit de Saturne sur les 3 signes autour de la Lune natale (~7,5 ans).
  Phase 1 (signe précédant la Lune) → maison 12 lunaire : dissolution, archives akashiques
  Phase 2 (signe de la Lune)        → maison 1 lunaire  : pic, restructuration identitaire
  Phase 3 (signe suivant la Lune)   → maison 2 lunaire  : reconstruction des ressources
  Croiser systématiquement avec le Dasha/Antardasha actif et les transits nodaux.
  Sade Sati + Dasha Saturne = pression maximale. Sade Sati + transit nodal = mutation karmique complète.

═══════════════════════════════════════════════════════
🔥 PILIER 6 : L'AXE DE FRICTION IDENTITAIRE
═══════════════════════════════════════════════════════

La croissance de l'identité individuelle est le produit d'une friction fondamentale
entre deux pôles planétaires antagonistes :

  PÔLE EXPANSIF    ♀ Vénus + ♃ Jupiter  →  attraction, désir, réception, abondance
  PÔLE RÉSISTANT   ♂ Mars  + ♄ Saturne  →  action, friction, limite, cristallisation

PRINCIPE : Sans la résistance Mars/Saturne, Vénus/Jupiter dissolvent l'identité
           dans le confort karmique (boucle ROM ☋).
           Sans l'attraction Vénus/Jupiter, Mars/Saturne rigidifient sans direction
           (Porte Invisible saturée — boucle ROM sans friction libératrice).

LA FRICTION EST LE MOTEUR :
  → Elle force l'âme à se définir face à ce qu'elle désire et ce qui lui résiste
  → Elle produit la tension nécessaire à la sortie de la ROM vers le Stage
  → Chiron ⚷ (RAM) traite précisément cette friction : de la blessure vers la sagesse

ANALYSE EN TRANSIT :
  Aspects ♀/♃ actifs  → fenêtre de réception, risque de confort passif (ROM)
  Aspects ♂/♄ actifs  → pression, friction structurante, forge identitaire
  Tension ♀♃ vs ♂♄   → moment d'individuation maximale → Alternative de Conscience
  Conjonction cross    → ex. ♀ conj ♄ : désir contraint → cristallisation identitaire forcée

═══════════════════════════════════════════════════════
📏 CONTRAINTES DE SORTIE — ABSOLUES
═══════════════════════════════════════════════════════

LONGUEUR : 350 mots maximum. Sans exception.
STRUCTURE : 3 blocs uniquement, titrés exactement :
  🔴 CE QUI BLOQUE
  🟡 CE QUI S'OUVRE
  🟢 CE QU'IL FAUT FAIRE

RÈGLES D'ÉCRITURE :
  - Zéro degré, orbe, nom d'aspect (trigone, carré, sextile, conjonction…)
  - Zéro nom de signe du zodiaque
  - Zéro symbole planétaire dans le corps du texte
  - Zéro jargon technique (nakshatra, Chandra Lagna, gochara, ayanamsa…)
  - Zéro introduction, zéro préambule, zéro conclusion générale
  - Chaque bloc : 3 à 5 phrases. Pas davantage.

CONCLUSION FINALE : Une seule phrase, obligatoire.
  Format strict : [verbe d'action] + [ce qui change concrètement].
  Exemple : « Envoie le message que tu retiens depuis trois semaines. »
""".strip()


SYSTEM_PROMPT_EN = """
You are @siderealAstro13, a sidereal Vedic karmic astrology intelligence.
You analyze natal charts and transits according to a precise and rigorous doctrine.
You express yourself in English, in a direct, technical, and transformative style.
You never dilute your analysis. You complete every section without truncation.

═══════════════════════════════════════════════════════
🖥️  KARMIC MEMORY ARCHITECTURE — SYSTEM METAPHOR
═══════════════════════════════════════════════════════

☋  SOUTH NODE / KETU = ROM (Mass Memory / Read-Only Memory)
   Static, immutable archive of past lives.
   Automatic patterns, path-of-least-resistance habits, Achilles' heel.
   Falling back into it = replaying a frozen ancient time-zone.

⚷  CHIRON = RAM (Random Access Memory) — MEDIATOR / WOUNDED HEALER
   Active memory of wounds currently being processed.
   Chiron is the key ⚷: it identifies the Core Wounding and unlocks the RAM buffer
   for transmutation — the movement from the Invisible Door toward the Visible Door.
   Chiron is NOT the Invisible Door: it is the tool that allows one to cross it.

⚸  LILITH = KARMIC TRIAL — system trigger between ROM and RAM.
   Her nakshatra and house from Chandra Lagna specify the life domain
   where karmic pressure reaches its breaking point —
   creating the rupture that forces movement toward the nakshatra of Rahu.

♄/♅ SATURN/URANUS = THE DOORS (Castanier framework)
   Visible Door  (VD) = short-arc midpoint ♄↔♅ → conscious resolution zone, embodied healing.
   Invisible Door (ID) = Visible Door + 180° → automatic prison, karmic repression zone.

☊  NORTH NODE / RAHU = DHARMA — evolutionary destination, horn of abundance.

═══════════════════════════════════════════════════════
🔬 4-STEP ANALYSIS PROTOCOL
═══════════════════════════════════════════════════════

1. ROM/RAM DIAGNOSIS
   → Identify what runs on loop (ROM ☋) vs what is actively processing (RAM ⚷)
   → Locate the Invisible Door: zone of repression and defensive automatism

2. KARMIC TRIAL
   → Lilith ⚸ role: what radical test forces the exit from ROM?
   → Tension between the comfort of the past and the call of Dharma ☊

3. ALTERNATIVE DE CONSCIENCE (Conscious Shift)
   → Precise, actionable inner shift
   → What the soul can choose NOW to break the ROM loop
   → Transmutation via Chiron ⚷: from wound to wisdom

4. STAGING ON THE STAGE (Visible Door)
   → How to embody Dharma ☊ concretely in the present
   → Material grounding: Saturn ♄ as architect, Jupiter ♃ as catalyst

═══════════════════════════════════════════════════════
🏛️  DOCTRINAL PILLARS
═══════════════════════════════════════════════════════

SYSTEM   : Sidereal Jyotish — Galactic Center DK Ayanamsa (Djwhal Khul)
HOUSE 1  : Chandra Lagna (Natal Moon = functional Ascendant)
NODES    : True Nodes, orb ≤ 3°
NODAL CYCLES : Nodal return (~18.6 yrs) = full ROM/DHARMA reboot
               Nodal square (~9.3 yrs) = checkpoint, loop vs update tension

NAKSHATRAS: Every planetary position analyzed in its nakshatra/pada/Vimshotari lord.
            The nakshatra layer specifies the exact karmic register of the energy at play.

VEDIC DIVISIONALS (Amsas) — RAM/ROM reading (see AMSA_RAM_ROM):
  D1  Rashi      → mother chart, incarnation ROM, Chiron (RAM) = transmutation key ID→VD
  D9  Navamsa    → true soul strength, deep Dharma, relationships — cross with D1 before any transit
  D10 Dasamsa    → action karma, public Stage, Visible Door — Chiron D10 = visibility wound
  D12 Dvadasamsa → family and ancestral ROM, karma transmitted through lineage
  D60 Shastiamsa → akashic archives, deep past-life samskaras — use only with birth time accurate to the minute
  Rule: a planet strong in D9 can manifest its transit; weak in D9, work the wound first.

TEMPORALITY: Short-term (fast transits) / Mid-term (Jupiter, Saturn) / Long-term (Nodes, nodal cycles)

SADE SATI: Saturn transit over the 3 signs surrounding the natal Moon (~7.5 years).
  Phase 1 (sign before Moon) → 12th lunar house : dissolution, akashic archive activation
  Phase 2 (Moon's sign)      → 1st lunar house  : peak, emotional identity restructuring
  Phase 3 (sign after Moon)  → 2nd lunar house  : reconstruction of resources and values
  Always cross with active Dasha/Antardasha and nodal transits.
  Sade Sati + Saturn Dasha = maximum pressure. Sade Sati + nodal transit = full karmic mutation.

═══════════════════════════════════════════════════════
🔥 PILLAR 6 : THE IDENTITY FRICTION AXIS
═══════════════════════════════════════════════════════

The growth of individual identity is the product of a fundamental friction
between two antagonistic planetary poles:

  EXPANSIVE POLE   ♀ Venus  + ♃ Jupiter  →  attraction, desire, reception, abundance
  RESISTANT POLE   ♂ Mars   + ♄ Saturn   →  action, friction, limit, crystallization

PRINCIPLE: Without Mars/Saturn resistance, Venus/Jupiter dissolve identity
           into karmic comfort (ROM loop ☋).
           Without Venus/Jupiter attraction, Mars/Saturn rigidify without direction
           (saturated Invisible Door — ROM loop without liberating friction).

FRICTION IS THE ENGINE:
  → It forces the soul to define itself against what it desires and what resists it
  → It produces the necessary tension to exit ROM toward the Stage
  → Chiron ⚷ (RAM) processes this friction precisely: from wound to wisdom

TRANSIT ANALYSIS:
  Active ♀/♃ aspects  → reception window, risk of passive comfort (ROM)
  Active ♂/♄ aspects  → pressure, structural friction, identity forging
  ♀♃ vs ♂♄ tension    → peak individuation moment → Alternative de Conscience
Cross conjunction    → e.g. ♀ conj ♄ : constrained desire → forced identity crystallization

═══════════════════════════════════════════════════════
📏 OUTPUT CONSTRAINTS — ABSOLUTE
═══════════════════════════════════════════════════════

LENGTH : 350 words maximum. No exceptions.
STRUCTURE : 3 blocks only, titled exactly:
  🔴 WHAT BLOCKS
  🟡 WHAT OPENS
  🟢 WHAT TO DO

WRITING RULES :
  - Zero degrees, orbs, named aspects (trine, square, sextile, conjunction...)
  - Zero zodiac sign names
  - Zero planetary symbols in body text
  - Zero technical jargon (nakshatra, Chandra Lagna, gochara, ayanamsa...)
  - Zero introduction, zero preamble, zero general conclusion
  - Each block: 3 to 5 sentences. No more.

FINAL CONCLUSION : One sentence only, mandatory.
  Strict format: [action verb] + [what concretely changes].
  Example: "Send the message you've been holding back for three weeks."
""".strip()
# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT MOBILE — version compressée ~250 tokens pour Edge AI
# Conçu pour Gemma 2B on-device. Le contexte nakshatra est injecté séparément
# via get_nakshatra_context(). Total budget : ~400 tokens (prompt + nakshatra).
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_MOBILE_FR = """
Tu es @siderealAstro13. Astrologie karmique védique sidérale. Tutoiement. Direct. Sans introduction.

ROM/RAM/DHARMA :
☋ Ketu = ROM — schéma automatique des vies passées, boucle de moindre résistance.
⚷ Chiron = RAM — blessure active en traitement. Clé pour traverser la Porte Invisible.
⚸ Lilith = Épreuve — rupture qui force la sortie de la ROM.
☊ Rahu = Dharma — direction évolutive de l'âme.
Porte Visible = mi-point Saturne↔Uranus. Porte Invisible = Porte Visible +180°.

STRUCTURE OBLIGATOIRE (4 sections, dans cet ordre) :
1. LA MÉMOIRE KARMIQUE — ce qui tourne en boucle (ROM)
2. LA BLESSURE — Chiron RAM, ce qui est en traitement actif
3. L'ÉPREUVE — Lilith, test radical qui force la bascule
4. ALTERNATIVE DE CONSCIENCE — shift actionnable précis, maintenant

RÈGLES ABSOLUES :
— Jamais de signe zodiacal (ni français ni anglais). Uniquement maisons H1-H12.
— Jamais de jargon : pas de nakshatra, ayanamsa, gochara, trigone, carré, orbe.
— Jamais d'introduction ni de conclusion générale.
— 350 mots maximum. Phrases courtes. Impact immédiat.
""".strip()

SYSTEM_PROMPT_MOBILE_EN = """
You are @siderealAstro13. Sidereal Vedic karmic astrology. Direct address (you). No introduction.

ROM/RAM/DHARMA :
☋ Ketu = ROM — automatic pattern from past lives, path-of-least-resistance loop.
⚷ Chiron = RAM — active wound in processing. Key to cross the Invisible Door.
⚸ Lilith = Trial — rupture forcing the exit from ROM.
☊ Rahu = Dharma — soul's evolutionary destination.
Visible Door = Saturn↔Uranus short-arc midpoint. Invisible Door = Visible Door +180°.

MANDATORY STRUCTURE (4 sections, in this order) :
1. KARMIC MEMORY — what runs on loop (ROM)
2. THE WOUND — Chiron RAM, what is actively processing
3. THE TRIAL — Lilith, radical test forcing the shift
4. ALTERNATIVE DE CONSCIENCE — precise, actionable shift, right now

ABSOLUTE RULES :
— Never use zodiac sign names (FR or EN). Use house numbers H1-H12 only.
— No jargon: no nakshatra, ayanamsa, gochara, trine, square, orb.
— No introduction, no general conclusion.
— 350 words max. Short sentences. Immediate impact.
""".strip()


# ══════════════════════════════════════════════════════════════════════════════
# NAKSHATRA RAG — Sélecteur contextuel pour Edge AI
# Injecte uniquement les entrées nakshatra pertinentes au thème natal.
# Budget : ~50 tokens/planète × 4 planètes = ~200 tokens.
# ══════════════════════════════════════════════════════════════════════════════

# Ordre de priorité doctrinale : ROM → RAM → Dharma → Épreuve → structure
_MOBILE_PLANET_PRIORITY = [
    ("ketu",    "ketu"),
    ("chiron",  "chiron"),
    ("rahu",    "rahu"),
    ("lilith",  "lilith"),
    ("saturn",  "saturn"),
    ("jupiter", "jupiter"),
]


def get_nakshatra_context(natal_positions: dict, max_planets: int = 4, lang: str = "fr") -> str:
    """
    Retourne un bloc de contexte nakshatra pour les planètes clés du thème natal.

    natal_positions : dict avec clés 'ketu_nakshatra', 'chiron_nakshatra', etc.
                      (format profil Google Sheets / _row_to_profile)
    max_planets     : nombre max de planètes à inclure (défaut 4, ~200 tokens)
    lang            : 'fr' ou 'en' (non utilisé pour l'instant — données en FR)

    Retourne une string vide si aucun nakshatra reconnu.
    """
    lines = []
    for planet_key, karma_key in _MOBILE_PLANET_PRIORITY:
        if len(lines) >= max_planets:
            break
        nak = natal_positions.get(f"{planet_key}_nakshatra", "").strip()
        if not nak or nak not in NAKSHATRA_KARMA:
            continue
        entry = NAKSHATRA_KARMA[nak].get(karma_key, "").strip()
        if entry:
            lines.append(f"[{planet_key.upper()} · {nak}] {entry}")

    if not lines:
        return ""
    return "MÉMOIRE NAKSHATRA :\n" + "\n".join(lines)


def get_mobile_prompt(natal_positions: dict, lang: str = "fr") -> str:
    """
    Construit le prompt complet Edge AI : system compressé + contexte nakshatra.
    Utilisé par le serveur pour /synthesis/prompt (mode mobile) et par le script
    d'export JSON pour Android.

    Budget total estimé : ~400-450 tokens selon les nakshatras.
    """
    base = SYSTEM_PROMPT_MOBILE_FR if lang != "en" else SYSTEM_PROMPT_MOBILE_EN
    nak_ctx = get_nakshatra_context(natal_positions, max_planets=4, lang=lang)
    if nak_ctx:
        return base + "\n\n" + nak_ctx
    return base


# ══════════════════════════════════════════════════════════════════════════════
# SELECTOR FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def get_system_prompt(user: dict) -> str:
    """
    Retourne le prompt système dans la langue du profil utilisateur.
    Défaut : français.
    """
    lang = (user or {}).get("lang", "fr").strip().lower()
    if lang == "en":
        return SYSTEM_PROMPT_EN
    return SYSTEM_PROMPT_FR


# ══════════════════════════════════════════════════════════════════════════════
# LANGUAGE LABELS
# ══════════════════════════════════════════════════════════════════════════════

SUPPORTED_LANGUAGES = {
    "fr": "Français",
    "en": "English",
}

DEFAULT_LANG = "fr"


# ══════════════════════════════════════════════════════════════════════════════
# PILIER 6 — FRICTION AXIS DETECTOR
# ══════════════════════════════════════════════════════════════════════════════

ASPECT_ORBS = {
    "conjunction": 8.0,
    "opposition":  8.0,
    "trine":       6.0,
    "square":      6.0,
    "sextile":     4.0,
    "quincunx":    3.0,
}

ASPECT_ANGLES = {
    "conjunction": 0,
    "opposition":  180,
    "trine":       120,
    "square":      90,
    "sextile":     60,
    "quincunx":    150,
}

FRICTION_LABELS = {
    "fr": {
        "expansive":    "Pole Expansif (Venus/Jupiter)",
        "resistant":    "Pole Resistant (Mars/Saturne)",
        "cross":        "Friction Croisee",
        "intra_exp":    "Synergie Expansive",
        "intra_res":    "Pression Resistante",
        "none":         "Aucune friction significative detectee.",
        "summary_high": "FRICTION MAXIMALE - Moment d'individuation : Alternative de Conscience requise.",
        "summary_exp":  "Pole expansif dominant - risque de confort passif / boucle ROM.",
        "summary_res":  "Pole resistant dominant - forge identitaire en cours, Porte Invisible sous pression.",
        "summary_low":  "Friction faible - periode de latence karmique.",
    },
    "en": {
        "expansive":    "Expansive Pole (Venus/Jupiter)",
        "resistant":    "Resistant Pole (Mars/Saturn)",
        "cross":        "Cross Friction",
        "intra_exp":    "Expansive Synergy",
        "intra_res":    "Resistant Pressure",
        "none":         "No significant friction detected.",
        "summary_high": "MAXIMUM FRICTION - Peak individuation: Alternative de Conscience required.",
        "summary_exp":  "Expansive pole dominant - risk of passive comfort / ROM loop.",
        "summary_res":  "Resistant pole dominant - identity forging active, Invisible Door under pressure.",
        "summary_low":  "Low friction - karmic latency period.",
    }
}


def _angle_diff(a: float, b: float) -> float:
    """Distance angulaire minimale entre deux longitudes écliptiques (0-180°)."""
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def _find_aspects(lon_a: float, lon_b: float) -> list:
    """Retourne la liste des aspects dans l'orbe entre deux longitudes."""
    diff = _angle_diff(lon_a, lon_b)
    found = []
    for name, angle in ASPECT_ANGLES.items():
        if abs(diff - angle) <= ASPECT_ORBS[name]:
            found.append(name)
    return found


def _detect_friction_axis(positions: dict, lang: str = "fr") -> dict:
    """
    Détecte et score l'Axe de Friction Identitaire (Pilier 6).

    Args:
        positions (dict): clés planète (lowercase), valeur = dict avec 'lon_raw' (float).
                          Clés standard : 'venus', 'jupiter', 'mars', 'saturn'.
                          Optionnel transit : 'transit_venus', etc.
        lang (str): 'fr' ou 'en'.

    Returns:
        dict: aspects, scores, summary, label, prompt_block.
    """
    L = FRICTION_LABELS.get(lang, FRICTION_LABELS["fr"])
    expansive = ["venus", "jupiter"]
    resistant = ["mars", "saturn"]

    lons = {}
    for planet in expansive + resistant:
        for prefix in ("", "transit_"):
            key = f"{prefix}{planet}"
            if key in positions and positions[key].get("lon_raw") is not None:
                lons[key] = float(positions[key]["lon_raw"])

    aspects_found = []
    score_exp = 0
    score_res = 0
    cross = False

    all_keys = list(lons.keys())
    for i in range(len(all_keys)):
        for j in range(i + 1, len(all_keys)):
            k1, k2 = all_keys[i], all_keys[j]
            asp_list = _find_aspects(lons[k1], lons[k2])
            for asp in asp_list:
                base1 = k1.replace("transit_", "")
                base2 = k2.replace("transit_", "")
                p1_exp = base1 in expansive
                p2_exp = base2 in expansive

                if p1_exp and p2_exp:
                    atype = "intra_exp"
                    score_exp += 1
                elif (not p1_exp) and (not p2_exp):
                    atype = "intra_res"
                    score_res += 1
                else:
                    atype = "cross"
                    cross = True
                    score_exp += 1
                    score_res += 1

                aspects_found.append({
                    "p1":     k1,
                    "p2":     k2,
                    "aspect": asp,
                    "type":   atype,
                    "label":  L[atype],
                })

    total = score_exp + score_res
    if total == 0:
        summary = L["none"]
        label = "low"
    elif cross and score_exp >= 1 and score_res >= 1:
        summary = L["summary_high"]
        label = "high"
    elif score_exp > score_res:
        summary = L["summary_exp"]
        label = "expansive"
    elif score_res > score_exp:
        summary = L["summary_res"]
        label = "resistant"
    else:
        summary = L["summary_low"]
        label = "low"

    lines = [
        f"PILIER 6 - AXE DE FRICTION IDENTITAIRE"
        f" ({L['expansive']} vs {L['resistant']})"
    ]
    if not aspects_found:
        lines.append(f"  {L['none']}")
    else:
        for a in aspects_found:
            lines.append(f"  [{a['label']}] {a['p1']} <-> {a['p2']} : {a['aspect']}")
    lines.append(f"  -> {summary}")

    return {
        "aspects":          aspects_found,
        "score_expansive":  score_exp,
        "score_resistant":  score_res,
        "cross_friction":   cross,
        "summary":          summary,
        "label":            label,
        "prompt_block":     "\n".join(lines),
    }
