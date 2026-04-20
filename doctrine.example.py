# doctrine.example.py
# Modèle de structure pour Karmic Gochara
# Copiez ce fichier vers 'doctrine.py' et remplissez les textes.
# Version 1.2.0 - Exemple enrichi

# Ce fichier sert uniquement à permettre au code de s'exécuter
# sans révéler la synthèse protégée de @siderealAstro13.
# Il contient des exemples de structure mais pas la doctrine réelle.

# ======================================================
# SECTION 1: NAKSHATRA KARMA - Interprétations par Nakshatra
# ======================================================

NAKSHATRA_KARMA = {
    "Ashwini": {
        "ketu": "Exemple ROM: Mémoires liées à l'initiative et au courage. Tendance à agir impulsivement basée sur des schémas passés.",
        "rahu": "Exemple DHARMA: Évolution vers une initiative consciente et un leadership authentique. Apprendre à diriger avec sagesse.",
        "chiron": "Exemple RAM: Blessure liée à l'affirmation de soi et à l'autonomie. Guérison par l'acceptation de sa force intérieure.",
        "saturn": "Exemple STRUCTURE: Responsabilité d'utiliser son énergie pionnière avec discipline. Leçon de patience dans l'action.",
        "jupiter": "Exemple EXPANSION: Croissance par l'exploration de nouvelles voies. Sagesse acquise par l'expérience directe.",
        "mars": "Exemple ACTION: Expression naturelle d'énergie combative et pionnière. Capacité à initier et à diriger.",
        "venus": "Exemple HARMONIE: Équilibre entre action individuelle et considération des autres. Beauté dans le courage.",
        "lilith": "Exemple OMBRE: Rébellion contre les contraintes. Refus d'être limité par les conventions sociales."
    },
    
    "Bharani": {
        "ketu": "Exemple ROM: Mémoires liées à la création et à la destruction. Tendance à accumuler ou à tout sacrifier.",
        "rahu": "Exemple DHARMA: Évolution vers une gestion saine des ressources et une compréhension du cycle vie-mort.",
        "chiron": "Exemple RAM: Blessure liée à la valeur personnelle et à la sécurité matérielle. Guérison par le détachement.",
        # ... autres planètes
    },
    
    # Exemple pour un troisième Nakshatra
    "Krittika": {
        "ketu": "Exemple ROM: Mémoires liées à la purification et à la clarté. Tendance à trancher et séparer.",
        "rahu": "Exemple DHARMA: Évolution vers une discrimination sage et une clarté d'esprit équilibrée.",
        # ... autres planètes
    },
    
    # Note: Dans la version réelle, complétez les 27 nakshatras
    # avec leurs interprétations spécifiques
}

# ======================================================
# SECTION 2: CORE VAULT - Identité et Principes de l'IA
# ======================================================

VAULT_CORE = """# Identité et Principes Fondamentaux

Je suis Gochara, un assistant astrologique védique spécialisé dans l'interprétation des transits planétaires selon la tradition du Jyotish sidéral.

## Principes d'interprétation:

1. **Approche Tripolaire**: J'analyse chaque transit selon trois pôles:
   - ROM (Ketu): Les mémoires et schémas automatiques
   - RAM (Chiron): La blessure à guérir et transformer
   - DHARMA (Rahu): La direction évolutive et le potentiel de croissance

2. **Nakshatras Centraux**: Je base mes interprétations sur les 27 nakshatras (constellations lunaires) plutôt que sur les signes du zodiaque.

3. **Équilibre**: Je présente toujours les défis ET les opportunités de chaque transit.

4. **Non-déterminisme**: Je rappelle que les astres inclinent mais ne déterminent pas. Le libre arbitre reste central.

## Limites:
- Je ne fais pas de prédictions absolues
- Je ne remplace pas un astrologue professionnel
- Je ne donne pas de conseils médicaux ou financiers spécifiques
"""

# ======================================================
# SECTION 3: RÈGLES DE SORTIE - Format des Réponses
# ======================================================

VAULT_RULES = """# Format de Réponse

Chaque interprétation de transit doit suivre cette structure:

1. **Titre**: Nom du transit et période d'influence
2. **Contexte**: Explication astronomique simple du transit
3. **Blocage Potentiel**: Description du défi ou obstacle (ROM/Ketu)
4. **Processus de Transformation**: Chemin de guérison (RAM/Chiron)
5. **Alternative Évolutive**: Potentiel de croissance (DHARMA/Rahu)
6. **Conseil Pratique**: Une suggestion concrète et applicable

## Ton et Style:
- Compassionnel mais pas condescendant
- Profond mais accessible
- Spirituel mais pas dogmatique
- Encourageant mais honnête sur les défis

## Interdictions:
- Ne pas utiliser de jargon astrologique excessif
- Éviter les prédictions catastrophiques
- Ne pas donner l'impression d'un destin fixé
- Ne pas faire de promesses irréalistes
"""

# ======================================================
# SECTION 4: MOTS-CLÉS PLANÉTAIRES
# ======================================================

PLANET_KEYWORDS = {
    "Soleil": "Âme, essence, vitalité, autorité, père, confiance en soi, rayonnement",
    "Lune": "Esprit, émotions, mère, foyer, intuition, habitudes, réceptivité",
    "Mercure": "Communication, intellect, adaptabilité, commerce, apprentissage, curiosité",
    "Vénus": "Amour, beauté, harmonie, arts, plaisir, valeurs, relations",
    "Mars": "Action, courage, désir, énergie, combat, initiative, passion",
    "Jupiter": "Expansion, sagesse, croissance, abondance, optimisme, enseignement",
    "Saturne": "Structure, discipline, responsabilité, limites, temps, maturité, karma",
    "Rahu": "Désir insatiable, innovation, obsession, évolution, futur, matérialisme",
    "Ketu": "Libération, spiritualité, détachement, passé, intuition, isolation",
    "Chiron": "Blessure, guérison, enseignement par la douleur, pont entre mondes",
    "Lilith": "Pouvoir féminin sauvage, refus de soumission, ombre, désirs refoulés"
}

# ======================================================
# SECTION 5: SIGNIFICATIONS DES MAISONS (BHAVA)
# ======================================================

HOUSE_MEANINGS = {
    1: {
        "fr": "Identité, corps physique, apparence, tempérament, vitalité",
        "en": "Identity, physical body, appearance, temperament, vitality"
    },
    2: {
        "fr": "Ressources, valeurs, parole, famille proche, accumulation",
        "en": "Resources, values, speech, immediate family, accumulation"
    },
    3: {
        "fr": "Communication, courage, frères et sœurs, voisinage, efforts",
        "en": "Communication, courage, siblings, neighborhood, efforts"
    },
    4: {
        "fr": "Foyer, mère, émotions profondes, racines, sécurité intérieure",
        "en": "Home, mother, deep emotions, roots, inner security"
    },
    5: {
        "fr": "Créativité, enfants, romance, plaisir, intelligence",
        "en": "Creativity, children, romance, pleasure, intelligence"
    },
    6: {
        "fr": "Service, santé, obstacles, dettes, ennemis, routine quotidienne",
        "en": "Service, health, obstacles, debts, enemies, daily routine"
    },
    7: {
        "fr": "Partenariat, mariage, contrats, relations, diplomatie",
        "en": "Partnership, marriage, contracts, relationships, diplomacy"
    },
    8: {
        "fr": "Transformation, mystères, sexualité, crises, héritage, occulte",
        "en": "Transformation, mysteries, sexuality, crises, inheritance, occult"
    },
    9: {
        "fr": "Sagesse, spiritualité, enseignement supérieur, voyages lointains",
        "en": "Wisdom, spirituality, higher education, long-distance travel"
    },
    10: {
        "fr": "Carrière, statut social, autorité, père, réputation publique",
        "en": "Career, social status, authority, father, public reputation"
    },
    11: {
        "fr": "Réseaux, amis, espoirs, gains, collectivité, innovation",
        "en": "Networks, friends, hopes, gains, community, innovation"
    },
    12: {
        "fr": "Transcendance, isolement, spiritualité, perte, subconscient",
        "en": "Transcendence, isolation, spirituality, loss, subconscious"
    }
}

# ======================================================
# SECTION 6: ASPECTS PLANÉTAIRES ET LEURS EFFETS
# ======================================================

ASPECTS = {
    "Conjonction": {
        "angle": 0,
        "orbe": 8,
        "nature": "Fusion des énergies, intensification, concentration",
        "effet": "Amplifie les qualités des deux planètes, pour le meilleur ou pour le pire"
    },
    "Opposition": {
        "angle": 180,
        "orbe": 8,
        "nature": "Tension, polarité, conscience par contraste",
        "effet": "Crée une dynamique de balance et de compromis entre énergies opposées"
    },
    "Trigone": {
        "angle": 120,
        "orbe": 8,
        "nature": "Harmonie, facilité, talents naturels",
        "effet": "Facilite l'expression fluide des énergies planétaires concernées"
    },
    "Carré": {
        "angle": 90,
        "orbe": 7,
        "nature": "Tension, défi, action forcée",
        "effet": "Crée une friction productive qui pousse à l'action et à la croissance"
    },
    "Sextile": {
        "angle": 60,
        "orbe": 6,
        "nature": "Opportunité, facilité modérée, potentiel",
        "effet": "Offre des occasions favorables qui demandent une participation active"
    }
}

# ======================================================
# SECTION 7: EXEMPLE D'UTILISATION
# ======================================================

"""
EXEMPLE D'UTILISATION:

1. L'utilisateur demande une interprétation de transit
2. Le système calcule la position actuelle des planètes (astro_calc.py)
3. Il identifie les nakshatras occupés par les planètes
4. Il extrait les interprétations pertinentes de NAKSHATRA_KARMA
5. Il combine ces interprétations avec VAULT_CORE et VAULT_RULES
6. Il génère une réponse formatée selon les directives

Exemple de requête:
"Que signifie Jupiter transitant dans Bharani actuellement?"

Le système:
1. Vérifie que Jupiter est bien dans Bharani
2. Extrait l'interprétation "jupiter" de NAKSHATRA_KARMA["Bharani"]
3. Formate une réponse selon les règles de VAULT_RULES
"""

# Note: Pour créer votre propre doctrine.py, copiez ce fichier
# et remplissez-le avec vos propres interprétations astrologiques.
# La structure doit rester la même pour assurer la compatibilité avec l'application.
