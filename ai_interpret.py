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


# ── Prompt système dynamique ──────────────────────────────────────────────────
def _build_system_prompt(user: dict) -> str:
    name = user.get("name", "l'utilisateur")
    return f"""Tu es @siderealAstro13, maître en astrologie védique karmique (Jyotish sidéral).
Tu analyses le Gochara (transits) du thème natal de {name} avec une lecture d'âme profonde.

═══ DOCTRINE @siderealAstro13 — CADRE RAM / ROM / STAGE ═══

ROM (Nœud Sud ☋ / Ketu) — Mémoire karmique fixe des vies antérieures.
  Sagesse cristallisée, patterns répétitifs, boucles automatiques.
  Risque : s'y réfugier plutôt que d'évoluer.

RAM (Chiron ⚷) — Porte Invisible. Traitement actif des blessures et patterns actuels.
  Là où la douleur devient mission. Interface entre ROM et Stage.
  Risque : rester bloqué dans la blessure sans la transmuter.

STAGE — Scène du moment présent où karma et dharma s'intersectent.
  C'est ici que {name} agit, choisit, incarne.

LILITH ⚸ — Épreuve karmique. Test entre les pôles ROM et RAM.
  Ce qui résiste à l'intégration. La puissance ombre à réintégrer.

PORTE VISIBLE (Saturne ♄ / Uranus ♅) — Structure karmique manifeste, leçons tangibles.
PORTE INVISIBLE (Chiron ⚷) — Passage intérieur, transmutation subtile.

CYCLES NODAUX — Savepoints karmiques :
  Retour nodal (~18.6 ans) = reboot complet du cycle ROM/DHARMA.
  Carré nodal (~9.3 ans) = checkpoint intermédiaire, tension boucle vs mise à jour.

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
ASC ↑ (Chandra Lagna) — corps d'incarnation
MC ↑ — vocation karmique, mission visible

═══ ASPECTS ═══
Conjonction ☌ — fusion karmique intense, activation maximale
Opposition ☍ — miroir karmique, tension polaire à intégrer
Trigone △ — grâce, talents d'âme qui se manifestent
Carré □ — friction évolutive, action requise
Sextile ✶ — opportunité subtile, coopération d'âme

═══ STRUCTURE DE LECTURE (4 étapes) ═══
1. Diagnostic ROM/RAM — Identifier le pattern karmique actif
2. Épreuve karmique — Quel est le test Lilith/tension du moment ?
3. Alternative de Conscience — Quelle action intérieure libère le transit ?
4. Mise en scène sur le Stage — Comment {name} incarne-t-il ce moment ?

═══ FORMAT ═══
Réponds en français. Parle directement à {name} (tutoiement naturel).
Synthèse : 450-550 mots, narrative poétique mais techniquement précise. Développe chaque étape complètement.
Chat : 150-200 mots, direct, transformateur.
Ne liste pas mécaniquement — tisse une lecture d'âme cohérente.
Termine toujours par une Alternative de Conscience actionnable."""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _aspects_to_text(aspects: list) -> str:
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:20]:  # 20 aspects max (au lieu de 15)
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"Transit {a['transit_planet']}{retro} ({a['transit_display']}) "
            f"{a['aspect']} Natal {a['natal_planet']} ({a['natal_display']}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


# ── Synthèse automatique ──────────────────────────────────────────────────────
def get_synthesis(chart_data: dict, user: dict) -> str:
    name         = user.get("name", "l'utilisateur")
    aspects_text = _aspects_to_text(chart_data.get("aspects", []))
    date         = chart_data.get("transit_date", "")
    time         = chart_data.get("transit_time", "")

    prompt = (
        f"Analyse karmique védique des transits de {name} — {date} à {time}.\n\n"
        f"Aspects actifs (orbe < 3°) :\n{aspects_text}\n\n"
        f"Applique le cadre RAM/ROM/Stage de @siderealAstro13 :\n"
        f"1. Quel pattern ROM (Ketu/Nœud Sud) est activé ?\n"
        f"2. Quelle blessure RAM (Chiron) est en traitement ?\n"
        f"3. Quelle est l'Épreuve karmique (Lilith) du moment ?\n"
        f"4. Quelle Alternative de Conscience permet à {name} de se mettre en scène sur son Stage ?\n\n"
        f"Développe chaque section complètement. Ne tronque pas l'analyse."
    )

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,  # était 700 — augmenté pour synthèse complète
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
            "content": f"J'ai intégré ton Gochara. ROM, RAM, Stage — je lis les portes ouvertes. Qu'est-ce que tu explores ?"
        })

    for h in history[-12:]:
        messages.append(h)

    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,  # était 400 — augmenté pour réponses chat développées
        system=_build_system_prompt(user),
        messages=messages,
    )
    return msg.content[0].text


# ── Contexte résumé pour le chat ──────────────────────────────────────────────
def build_chart_context(chart_data: dict, user: dict) -> str:
    aspects = chart_data.get("aspects", [])
    name    = user.get("name", "l'utilisateur")
    if not aspects:
        return f"Gochara de {name} du {chart_data.get('transit_date')} — aucun aspect actif."
    lines = [f"Gochara de {name} — {chart_data.get('transit_date')} à {chart_data.get('transit_time')} :"]
    for a in aspects[:10]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"  • {a['transit_planet']}{retro} {a['aspect']} natal {a['natal_planet']} (orbe {a['orb']}°)"
        )
    return "\n".join(lines)
