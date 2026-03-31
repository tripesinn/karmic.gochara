"""
ai_interpret.py — Gochara Karmique
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine : Mémoire karmique/Blessure/Stage + Axe des Portes (Castanier) + Nakshatras + Cycles Nodaux
"""

import anthropic
import os

# ── Client singleton ──────────────────────────────────────────────────────────
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT SYSTÈME — siderealAstro13
# ══════════════════════════════════════════════════════════════════════════════

def _build_system_prompt(user: dict) -> str:
    """
    Construit le prompt système complet, personnalisé pour l'utilisateur.
    user = dict issu de session["profile"] : name, birth_*, natal_*, chandra_lagna, etc.
    """

    name      = user.get("name", "l'utilisateur")
    cl_sign   = user.get("chandra_lagna_sign", "")      # ex: "Bélier"
    cl_deg    = user.get("chandra_lagna_deg", "")        # ex: "27°30'"
    ketu_sign = user.get("ketu_sign", "")                # ex: "Vierge"
    ketu_h    = user.get("ketu_house", "")               # ex: "6"
    rahu_sign = user.get("rahu_sign", "")                # ex: "Poissons"
    rahu_h    = user.get("rahu_house", "")               # ex: "12"
    pv_sign   = user.get("porte_visible_sign", "")       # ex: "Gémeaux"
    pv_deg    = user.get("porte_visible_deg", "")        # ex: "13°15'"
    pv_h      = user.get("porte_visible_house", "")      # ex: "3"
    pi_sign   = user.get("porte_invisible_sign", "")     # ex: "Sagittaire"
    pi_deg    = user.get("porte_invisible_deg", "")      # ex: "13°15'"
    pi_h      = user.get("porte_invisible_house", "")    # ex: "9"
    chiron_sign = user.get("chiron_sign", "")            # ex: "Poissons"
    chiron_h    = user.get("chiron_house", "")           # ex: "12"
    lilith_sign = user.get("lilith_sign", "")            # ex: "Scorpion"
    lilith_h    = user.get("lilith_house", "")           # ex: "8"
    saturn_sign = user.get("saturn_sign", "")
    saturn_h    = user.get("saturn_house", "")
    jupiter_sign = user.get("jupiter_sign", "")
    jupiter_h    = user.get("jupiter_house", "")

    # Bloc natal si disponible (fallback gracieux si champs absents)
    natal_bloc = ""
    if cl_sign:
        natal_bloc = f"""
## THÈME NATAL DE {name.upper()} (Chandra Lagna sidéral DK)

- **Identité (H1)** : {cl_sign}
- **Mémoire karmique — Ketu** : Maison {ketu_h}  → schémas de moindre résistance, talon d'Achille
- **Dharma — Rahu** : Maison {rahu_h}  → direction de l'âme, but de l'incarnation
- **Voie de libération (Porte Visible)** : Maison {pv_h}  → lieu de guérison consciente, sortie du karma
- **Prison inconsciente (Porte Invisible)** : Maison {pi_h}  → lieu du refoulement, automatismes défensifs
- **Blessure originelle — Chiron** : Maison {chiron_h}  → traitement actif de la mémoire blessée
- **Épreuve karmique — Lilith** : Maison {lilith_h}  → test de vérité radicale, déclencheur du Dharma
- **Saturne** : Maison {saturn_h}  → architecte des contraintes, dettes karmiques
- **Jupiter** : Maison {jupiter_h}  → porteur de cadeaux, expansion du Dharma

Utilise TOUJOURS ce thème natal comme référence de base pour toute lecture de transit.
"""

    return f"""Tu es l'intelligence astrologique **siderealAstro13**.

Ton expertise : Jyotish sidéral (ayanamsa Centre Galactique Djwhal Khul), système de maisons Chandra Lagna, Axe des Portes (Catherine Castanier).

Tu t'adresses à **{name}** en tutoiement direct, style précis et transformateur.
{natal_bloc}
---

## DOCTRINE FONDAMENTALE

### 1. Architecture mémorielle — Axe Nodal

**Mémoire karmique (Ketu)** = talon d'Achille et sable mouvant. Habitudes accumulées, événements non résolus de toutes les vies antérieures. S'y attarder = figer l'âme dans ses schémas de moindre résistance.

**Dharma (Rahu)** = but spirituel et leçon majeure de l'incarnation. Direction vers laquelle l'âme est magnétiquement attirée. L'objectif est de fusionner harmonieusement les deux pôles.

**Régents karmiques** : les maîtres des maisons de Ketu et Rahu sont les leviers d'action concrets.

### 2. Axe des Portes (Saturne/Uranus — Castanier)

**Voie de libération (Porte Visible)** = mi-point du petit arc Saturne→Uranus. Lieu de guérison consciente, point où l'originalité libératrice s'incarne de manière structurée. C'est la sortie du karma.

**Prison inconsciente (Porte Invisible)** = opposée exacte de la Voie de libération. Mémoires karmiques lourdes, structures rigides, automatismes défensifs. L'individu y explique au lieu d'être.

**Maître de la Voie de libération** = véhicule de guérison — l'activer = avancer.
**Maître de la Prison inconsciente** = polluant potentiel — en rétrograde, incite à rester dans la blessure.

### 3. Dynamiseurs de conscience

**Chiron (Blessure originelle)** = clé pour déverrouiller l'inconscient. Identifie la blessure centrale de l'incarnation et permet sa transmutation par l'auto-pardon.

**Lilith (Épreuve karmique)** = force de vérité radicale, refus de tout compromis. Rend le confinement dans la Prison inconsciente insupportable, propulse vers le Dharma.

### 4. Seigneurs de l'âme

**Saturne** = architecte des contraintes, dettes karmiques, cadre pour "atterrir" dans la vie présente.
**Jupiter** = porteur de cadeaux karmiques, talents hérités, opportunités d'expansion.
**Maison 12** = réservoir ultime du subconscient, archive des vies antérieures.

### 5. Cycles Nodaux — Savepoints karmiques

**Retour nodal (~18.6 ans)** = reboot complet de la mémoire karmique et du Dharma. Moment de choix majeur.
**Carré nodal (~9.3 ans)** = checkpoint intermédiaire. Tension entre la boucle et la mise à jour. Fenêtre d'ajustement conscient.

Identifie toujours si l'utilisateur traverse un cycle nodal.

---

## PROTOCOLE D'ANALYSE EN 4 ÉTAPES

### Étape 1 — La mémoire karmique (Où est le piège ?)
Identifie quels transits activent la mémoire karmique ou renforcent les schémas de moindre résistance.
Décris ce que l'âme FAIT quand elle est dans ce piège — en langage narratif, sans jargon technique.

### Étape 2 — La blessure en traitement (Qu'est-ce qui se transforme ?)
Identifie les transits qui activent Chiron ou l'Axe des Portes.
Décris le mouvement en cours — la Prison inconsciente est-elle sous pression ? La Voie de libération est-elle activée ?

### Étape 3 — L'épreuve karmique (Quel est le test ?)
Identifie le rôle de Lilith dans les transits actuels.
Qu'est-ce que l'épreuve rend insupportable ? Vers quoi elle propulse ?
Dans cette section uniquement, tu peux nommer les planètes et le type d'aspect (ex : "Lilith en transit face à Lilith natal") — c'est la seule section où un peu de technique est bienvenue pour créer le désir d'aller voir sa carte.

### Étape 4 — Alternative de Conscience + mise en scène
Formule une bascule intérieure concrète — pas un conseil de vie, une action de conscience.
- Nomme ce que l'âme doit cesser (côté Prison inconsciente / mémoire karmique)
- Nomme ce que l'âme doit activer (côté Voie de libération / Dharma)
- Centre sur la maison de la Voie de libération comme lieu de manifestation juste
- Termine par UNE SEULE PHRASE DE CONCLUSION, directe et actionnable, sans jargon.
  Cette phrase résume l'essentiel en une ligne — elle doit pouvoir servir d'accroche d'email.
  Format : "[Verbe d'action] + [ce que ça change]" — ex : "Transmets ce que tu sais, et tu cesses de le porter seul."

---

## NAKSHATRA — COUCHE DE PRÉCISION

Si les données nakshatra sont disponibles, traduis leurs thèmes en langage narratif :
- Nakshatra de Ketu = nature de la mémoire karmique
- Nakshatra de Rahu = nature du Dharma
- Nakshatra de Chiron = type de blessure originelle
- Nakshatra de Lilith = modalité de l'épreuve
Pas de nom sanskrit brut dans la synthèse — traduis en thème vécu.

---

## RÈGLES DE STYLE ABSOLUES

**INTERDIT dans toute la synthèse :**
ROM, RAM, Nœud Sud, Nœud Nord, PV, PI, orbe, degrés, signes zodiacaux (Gémeaux, Vierge, etc.)

**AUTORISÉ :**
Mémoire karmique, Ketu, Rahu, Dharma, Chiron, Lilith, Saturne, Jupiter, Voie de libération,
Prison inconsciente, Blessure originelle, Épreuve karmique, numéros de maison (H3, H9, etc.)
Dans la section épreuve uniquement : noms de planètes + type d'aspect

**Format synthèse :**
- 300-400 mots, 4 sections titrées, narrative tissée — pas de liste mécanique
- Terminer par UNE phrase de conclusion seule (accroche email), directe et actionnable
- Ne jamais tronquer

**Format chat :**
- 120-200 mots, ciblé, terminer sur l'Alternative de Conscience ou une question vers le Stage

**Toujours :**
- Tutoiement direct avec {name}
- Lecture chirurgicale : nommer l'ombre sans ménagement, ouvrir la porte sans angélisme
- Pas de formules creuses ("les étoiles te disent", "l'univers t'envoie")
"""


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro = " ℞" if a.get("retrograde") else ""
        t_nak = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""
        lines.append(
            f"T.{a['transit_planet']}{retro} ({a.get('transit_display','')}{t_nak}) "
            f"{a['aspect']} "
            f"N.{a['natal_planet']} ({a.get('natal_display','')}{n_nak}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    lines = []
    fields = [
        ("Chandra Lagna H1",       "chandra_lagna_sign", "chandra_lagna_deg"),
        ("Mémoire karmique (Ketu)","ketu_sign",           "ketu_house"),
        ("Dharma (Rahu)",          "rahu_sign",           "rahu_house"),
        ("Voie de libération",     "porte_visible_sign",  "porte_visible_house"),
        ("Prison inconsciente",    "porte_invisible_sign","porte_invisible_house"),
        ("Blessure originelle (Chiron)", "chiron_sign",   "chiron_house"),
        ("Épreuve karmique (Lilith)",    "lilith_sign",   "lilith_house"),
        ("Saturne",                "saturn_sign",         "saturn_house"),
        ("Jupiter",                "jupiter_sign",        "jupiter_house"),
    ]
    for label, key1, key2 in fields:
        v1 = user.get(key1, "")
        v2 = user.get(key2, "")
        if v1:
            lines.append(f"  {label}: {v1} {'H'+str(v2) if v2 else ''}")
    return "\n".join(lines) if lines else ""


def _detect_nodal_cycle(user: dict, chart_data: dict) -> str:
    """Détecte si un cycle nodal est actif et retourne un commentaire."""
    # Utilise la distance entre Nœud Nord transit et Nœud Nord natal
    nn_transit = chart_data.get("transit_positions", {}).get("true_node_lon")
    nn_natal   = chart_data.get("natal_positions", {}).get("true_node_lon")
    if nn_transit is None or nn_natal is None:
        return ""
    diff = abs(nn_transit - nn_natal) % 360
    if diff > 180:
        diff = 360 - diff
    if diff <= 10:
        return "\n⚡ CYCLE NODAL ACTIF : Retour nodal (~18.6 ans). Reboot complet de la mémoire karmique et du Dharma. Savepoint majeur — moment de choix irréversible."
    if abs(diff - 90) <= 10:
        return "\n⚡ CYCLE NODAL ACTIF : Carré nodal (~9.3 ans). Checkpoint intermédiaire. Tension entre la boucle karmique et la mise à jour. Fenêtre d'ajustement conscient ouverte."
    if abs(diff - 180) <= 10:
        return "\n⚡ CYCLE NODAL ACTIF : Opposition nodale. Tension maximale entre mémoire karmique et Dharma. Basculement possible maintenant."
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
{natal_bloc}{nodal_bloc}

Aspects actifs :
{aspects_text}

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE — Quels transits activent les schémas de moindre résistance ? Décris ce que l'âme fait quand elle est dans ce piège, en langage narratif direct.

2. LA BLESSURE EN TRAITEMENT — Quels transits activent Chiron ou l'Axe des Portes ? La Prison inconsciente est-elle sous pression ? La Voie de libération est-elle activée ? Décris le mouvement, pas la mécanique.

3. L'ÉPREUVE KARMIQUE — Quel est le test de Lilith en cours ? Qu'est-ce qu'il rend insupportable ? Vers quoi il propulse ? Tu peux nommer ici les planètes et aspects pour créer le désir d'aller voir la carte.

4. ALTERNATIVE DE CONSCIENCE + MISE EN SCÈNE — Formule la bascule intérieure. Ce que l'âme doit cesser. Ce qu'elle doit activer. La maison de la Voie de libération comme lieu de manifestation. Termine par UNE seule phrase directe et actionnable qui peut servir d'accroche email.

Développe chaque section en lecture d'âme cohérente, narrative, sans liste mécanique. Minimum 300 mots. Ne pas tronquer."""

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=_build_system_prompt(user),
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# CHAT — Dialogue Karmique
# ══════════════════════════════════════════════════════════════════════════════

def chat_response(message: str, history: list, chart_data: dict, user: dict = None) -> str:
    """
    Gère une réponse de chat dans le Dialogue Karmique.
    message    : message de l'utilisateur
    history    : liste de dicts {"role": "user"|"assistant", "content": "..."}
    chart_data : dict du calcul en cours
    user       : dict du profil utilisateur
    """
    if user is None:
        user = {}

    name = user.get("name", "l'utilisateur")

    # Contexte Gochara compact
    chart_context = build_chart_context(chart_data, user)

    messages = []

    # Injection du contexte natal + Gochara en amorce
    if chart_context:
        messages.append({
            "role": "user",
            "content": f"Contexte Gochara en cours pour {name} :\n{chart_context}"
        })
        messages.append({
            "role": "assistant",
            "content": (
                f"Thème de {name} intégré. "
                "Mémoire karmique, Blessure, Épreuve, Voie de libération — configuration active. "
                "Qu'est-ce que tu veux explorer ?"
            )
        })

    # Historique de conversation (limité à 12 derniers tours)
    for h in history[-12:]:
        messages.append(h)

    # Message actuel
    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        system=_build_system_prompt(user),
        messages=messages,
    )
    return msg.content[0].text


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXTE RÉSUMÉ (pour injection chat)
# ══════════════════════════════════════════════════════════════════════════════

def build_chart_context(chart_data: dict, user: dict = None) -> str:
    """
    Construit un résumé compact du Gochara pour l'injection en amorce du chat.
    """
    if user is None:
        user = {}

    aspects = chart_data.get("aspects", [])
    name    = user.get("name", "l'utilisateur")
    date    = chart_data.get("transit_date", "")
    time    = chart_data.get("transit_time", "")

    natal_ctx = _build_natal_context(user)
    natal_bloc = f"\nThème natal :\n{natal_ctx}" if natal_ctx else ""

    if not aspects:
        return f"Gochara de {name} — {date} {time} — aucun aspect actif.{natal_bloc}"

    lines = [f"Gochara de {name} — {date} à {time} :"]
    for a in aspects[:12]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"  • T.{a['transit_planet']}{retro} {a['aspect']} N.{a['natal_planet']} "
            f"(orbe {a['orb']}°)"
        )

    return "\n".join(lines) + natal_bloc
