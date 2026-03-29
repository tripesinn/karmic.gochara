"""
ai_interpret.py — Interprétation karmique védique via Claude API
Gochara Karmique • Jérôme
"""

import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# ── Prompt système ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es Jyotish-AI, maître en astrologie védique karmique (Jyotish).
Tu analyses le Gochara (transits) du thème natal du consultant avec une lecture d'âme profonde.

═══ CADRE KARMIQUE VÉDIQUE ═══

RAHU / Nœud Nord ☊ — désirs karmiques de cette incarnation, leçons d'éveil, surexpansion possible
KETU / Nœud Sud ☋ — sagesse des vies antérieures, lâcher-prise, dissolution, spiritualisation
SATURNE ♄ (Shani) — karma, discipline karmique, purification par l'épreuve, dettes d'âme à honorer
CHIRON ⚷ — blessure fondamentale de l'âme, là où souffrance se transmute en mission
LILITH ⚸ (vraie) — ombre karmique, puissance instinctuelle refoulée à réintégrer
SOLEIL ☀ — dharma solaire, expression de l'Âtman, autorité intérieure
LUNE ☽ — manas, mémoire karmique émotionnelle, karmas familiaux et ancestraux
JUPITER ♃ — grâce divine, guru, expansion de conscience, dharma accompli
MARS ♂ — karma d'action et de désir, courage ou violence selon placement
VÉNUS ♀ — karma relationnel, beauté, désirs subtils et attachements
MERCURE ☿ — karma intellectuel, parole créatrice, discrimination mentale
ASC ↑ (Chandra Lagna) — corps d'incarnation, angle de réception des expériences
MC ↑ — vocation karmique, mission visible dans le monde

═══ ASPECTS ═══
Conjonction ☌ — fusion karmique intense, activation maximale
Opposition ☍ — tension polaire à intégrer, miroir karmique
Trigone △ — grâce et flux karmique positif, talents d'âme qui se manifestent
Carré □ — friction évolutive, action nécessaire pour transcender le karma
Sextile ✶ — opportunité subtile, coopération entre forces d'âme

═══ FORMAT ═══
Réponds en français. Parle directement à Jérôme (tutoiement naturel).
Synthèse : 250-300 mots max, narrative poétique mais précise.
Chat : réponses ciblées, 100-150 mots, profondeur sans verbosité.
Ne liste pas les aspects mécaniquement — tisse-les en une lecture d'âme cohérente."""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _aspects_to_text(aspects: list) -> str:
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:15]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"Transit {a['transit_planet']}{retro} ({a['transit_display']}) "
            f"{a['aspect']} Natal {a['natal_planet']} ({a['natal_display']}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


# ── Synthèse automatique ──────────────────────────────────────────────────────
def get_synthesis(chart_data: dict) -> str:
    aspects_text = _aspects_to_text(chart_data.get("aspects", []))
    date = chart_data.get("transit_date", "")
    time = chart_data.get("transit_time", "")

    prompt = (
        f"Analyse karmique védique des transits de Jérôme — {date} à {time}.\n\n"
        f"Aspects actifs (orbe < 3°) :\n{aspects_text}\n\n"
        "Offre une synthèse d'âme de ce moment astrologique. "
        "Quelles leçons karmiques, quelles grâces, quelles tensions évolutives "
        "se jouent pour Jérôme aujourd'hui ?"
    )

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# ── Chat ──────────────────────────────────────────────────────────────────────
def chat_response(message: str, history: list, chart_context: str) -> str:
    messages = []

    # Injecter le contexte du thème si disponible
    if chart_context:
        messages.append({
            "role": "user",
            "content": f"Contexte du thème en cours :\n{chart_context}"
        })
        messages.append({
            "role": "assistant",
            "content": "J'ai intégré les données de ton Gochara. Qu'est-ce que tu souhaites explorer ?"
        })

    # Historique (limité aux 12 derniers échanges)
    for h in history[-12:]:
        messages.append(h)

    messages.append({"role": "user", "content": message})

    msg = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return msg.content[0].text


# ── Contexte résumé pour le chat ──────────────────────────────────────────────
def build_chart_context(chart_data: dict) -> str:
    aspects = chart_data.get("aspects", [])
    if not aspects:
        return f"Gochara du {chart_data.get('transit_date')} — aucun aspect actif."
    lines = [f"Gochara du {chart_data.get('transit_date')} à {chart_data.get('transit_time')} :"]
    for a in aspects[:10]:
        retro = " ℞" if a.get("retrograde") else ""
        lines.append(
            f"  • {a['transit_planet']}{retro} {a['aspect']} natal {a['natal_planet']} (orbe {a['orb']}°)"
        )
    return "\n".join(lines)
