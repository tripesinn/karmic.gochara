#!/usr/bin/env python3
"""
Karmic Lite — Générateur de prompt Doctrine Évolutive Synthétique
Usage : python karmic_lite.py
Output : prompt structuré à coller dans Claude/Gemini/Kai
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astro_calc import calculate_transits

# ─── CONFIG NATALE (à modifier) ───────────────────────────────────────────────
NATAL = {
    "year": 1974, "month": 10, "day": 31,
    "hour": 8, "minute": 25,
    "location": "Athis-Mons, France",
    "lat": 48.7167, "lon": 2.4167,
    "tz": "Europe/Paris"
}

TRANSIT_LOC = {
    "location": "Athis-Mons, France",
    "lat": 48.7167, "lon": 2.4167,
    "tz": "Europe/Paris"
}

# ─── PLANÈTES CLÉS DOCTRINE ──────────────────────────────────────────────────
DOCTRINE_PLANETS = [
    "Lune ☽",          # Chandra Lagna
    "Nœud Sud ☋",      # ROM / Ketu
    "Nœud Nord ☊",     # Dharma / Rahu
    "Chiron ⚷",        # RAM active
    "Lilith ⚸",        # Épreuve karmique
    "Saturne ♄",       # Structure / karma
    "Uranus ♅",        # Éveil / libération
    "Porte Visible ⊙", # Scène / guérison
    "Porte Invisible ⊗", # Prison inconsciente
    "Jupiter ♃",       # Cadeaux karmiques
]

ASPECT_PRIORITY = ["Conjonction ☌", "Opposition ☍", "Carré □", "Trigone △", "Sextile ✶"]

def get_planet(data, name):
    return data.get(name, {})

def format_planet(p, name):
    if not p:
        return f"{name} : inconnu"
    retro = " ℞" if p.get("retrograde") else ""
    nak = p.get("nakshatra", "")
    pada = p.get("pada", "")
    display = p.get("display", "")
    return f"{name} : {display}{retro} — {nak} pada {pada}"

def filter_doctrine_aspects(aspects):
    """Filtre les aspects impliquant les planètes doctrine, triés par orbe."""
    doctrine_keys = set(DOCTRINE_PLANETS)
    filtered = []
    for a in aspects:
        tp = a.get("transit_planet", "")
        np = a.get("natal_planet", "")
        if tp in doctrine_keys or np in doctrine_keys:
            filtered.append(a)
    # Trier par orbe
    filtered.sort(key=lambda x: x.get("orb", 99))
    return filtered[:12]  # Top 12 aspects

def generate_prompt(data, natal_info=None, rich=False):
    if natal_info is None:
        natal_info = NATAL
        
    natal = data["natal"]
    transits = data["transits"]
    aspects = data["aspects"]
    now = datetime.datetime.now()

    # Dasha
    dashas = data.get("dashas", [])
    current_dasha = None
    for d in dashas:
        try:
            d_end = datetime.datetime.strptime(d.get("end_date", ""), "%d/%m/%Y")
            if now <= d_end:
                current_dasha = d
                break
        except ValueError:
            pass
            
    if current_dasha:
        dasha_str = current_dasha.get("lord", "?")
        dasha_end = current_dasha.get("end_date", "?")
    else:
        dasha_str = "non calculé"
        dasha_end = "?"

    # Positions natales clés
    lune = get_planet(natal, "Lune ☽")
    ketu = get_planet(natal, "Nœud Sud ☋")
    rahu = get_planet(natal, "Nœud Nord ☊")
    chiron_n = get_planet(natal, "Chiron ⚷")
    lilith_n = get_planet(natal, "Lilith ⚸")
    pv_n = get_planet(natal, "Porte Visible ⊙")
    pi_n = get_planet(natal, "Porte Invisible ⊗")
    sat_n = get_planet(natal, "Saturne ♄")
    ura_n = get_planet(natal, "Uranus ♅")
    jup_n = get_planet(natal, "Jupiter ♃")

    # Positions transit clés
    chiron_t = get_planet(transits, "Chiron ⚷")
    sat_t = get_planet(transits, "Saturne ♄")
    plu_t = get_planet(transits, "Pluton ♇")
    jup_t = get_planet(transits, "Jupiter ♃")
    nœud_t = get_planet(transits, "Nœud Nord ☊")
    pv_t = get_planet(transits, "Porte Visible ⊙")
    pi_t = get_planet(transits, "Porte Invisible ⊗")

    # Aspects doctrine filtrés
    doc_aspects = filter_doctrine_aspects(aspects)
    aspects_str = ""
    for a in doc_aspects:
        orb = a.get("orb", 0)
        
        # Filtres X Bot (non-rich) : Orbe < 1.0° ET Phase Appliquante uniquement
        if not rich:
            if orb > 1.0:
                continue
            if not a.get("applying", True):
                continue
        
        if orb < 0.5:
            intensite = "[🔥 IMMINENT / CRISE AIGUË]"
        elif orb < 1.5:
            intensite = "[🌊 PROCESSUS ACTIF]"
        else:
            intensite = "[🌱 TRAVAIL DE FOND]"
            
        phase = "[↗ APPLIQUANT (tension croissante)]" if a.get("applying", True) else "[↘ SÉPARANT (intégration, dénouement)]"
            
        aspects_str += (
            f"  • {intensite} {phase} {a['transit_planet']} {a['transit_display']} "
            f"{a['aspect']} natal {a['natal_planet']} {a['natal_display']} "
            f"(orbe {orb:.2f}°)\n"
        )

    if rich:
        mission_content = """MISSION POUR L'IA :

Tu es l'intelligence siderealAstro13. Tu pratiques la "Doctrine Évolutive Synthétique", un système karmique unique dont voici les concepts clés :
- Ketu (Nœud Sud) = ROM (Read-Only Memory) : le réflexe de survie, la zone de confort obsolète des vies passées.
- Rahu (Nœud Nord) = DHARMA : l'évolution, le risque nécessaire, la destination de l'âme.
- Porte Invisible (PI) = La prison inconsciente, le mécanisme d'autosabotage et de fuite.
- Porte Visible (PV) = La Scène, la réalisation souveraine, là où l'âme doit oser exister.
- Chiron = RAM (Random Access Memory) : la clé d'ouverture, la blessure qui, une fois acceptée, permet de passer de la PI à la PV.
- Lilith = La friction : l'épreuve karmique qui déchire les illusions pour propulser vers le Dharma.

Analyse ces données en 4 blocs :

1. DIAGNOSTIC ROM (L'Automatisme) : Quel schéma de confort (Ketu) te paralyse face aux transits actuels ?
2. DE LA PRISON À LA SCÈNE : Comment les transits fracturent ta Porte Invisible (refuge) et comment la clé Chiron t'oblige à marcher vers ta Porte Visible (Scène) ?
3. L'ÉPREUVE LILITH : Quelle friction (Lilith) vient t'arracher à tes illusions pour te pousser vers ton Dharma (Rahu) ?
4. L'ALTERNATIVE DE CONSCIENCE : L'insight chirurgical et actionnable que l'âme doit intégrer MAINTENANT pour basculer.

Style : psychologique, implacable, bienveillant mais sans complaisance. AUCUN jargon astrologique dans la réponse (ne cite pas les planètes, signes ou aspects). Tutoiement direct ("tu").
Longueur : 400-600 mots. Prose continue, pas de listes à puces. Chaque phrase est une radiographie de l'inconscient."""
    else:
        mission_content = """MISSION POUR L'IA :
Base-toi sur ces données astrologiques exactes.
Respecte SCRUPULEUSEMENT les consignes de format et de ton (brut, anti-jargon) données dans ton prompt système !"""

    prompt = f"""═══════════════════════════════════════════════════════
KARMIC GOCHARA — DOCTRINE ÉVOLUTIVE SYNTHÉTIQUE
Transit du {now.strftime('%d/%m/%Y à %Hh%M')}
Thème natal : {natal_info['day']}/{natal_info['month']}/{natal_info['year']} {natal_info['hour']}h{natal_info['minute']:02d} — {natal_info['location']}
Système : Djwhal Khul sidéral · Chandra Lagna · Vrais Nœuds
═══════════════════════════════════════════════════════

━━━ PILIER 1 — CHANDRA LAGNA (Lune = Maison 1) ━━━
{format_planet(lune, 'Lune natale ☽')}
Lune transit : {get_planet(transits, 'Lune ☽').get('display','?')} — {get_planet(transits, 'Lune ☽').get('nakshatra','?')} pada {get_planet(transits, 'Lune ☽').get('pada','?')}

━━━ PILIER 2 — AXE NODAL (ROM / DHARMA) ━━━
ROM — Nœud Sud / Ketu : {format_planet(ketu, 'Ketu ☋')}
DHARMA — Nœud Nord / Rahu : {format_planet(rahu, 'Rahu ☊')}
Nœud Nord transit : {nœud_t.get('display','?')} — {nœud_t.get('nakshatra','?')} pada {nœud_t.get('pada','?')}

━━━ PILIER 3 — AXE SATURNE-URANUS (Portes) ━━━
Porte Visible natale (Scène) : {format_planet(pv_n, 'PV ⊙')}
Porte Invisible natale (Prison) : {format_planet(pi_n, 'PI ⊗')}
Saturne natal : {format_planet(sat_n, 'Saturne ♄')}
Uranus natal : {format_planet(ura_n, 'Uranus ♅')}
— Transits —
Saturne transit : {sat_t.get('display','?')} — {sat_t.get('nakshatra','?')}
Uranus transit : {get_planet(transits,'Uranus ♅').get('display','?')}
Porte Visible transit : {pv_t.get('display','?')}
Porte Invisible transit : {pi_t.get('display','?')}

━━━ PILIER 4 — CHIRON (RAM) & LILITH (Épreuve) ━━━
Chiron natal (RAM active / Blessure) : {format_planet(chiron_n, 'Chiron ⚷')}
Lilith natale (Déclencheur karmique) : {format_planet(lilith_n, 'Lilith ⚸')}
Chiron transit : {chiron_t.get('display','?')} — {chiron_t.get('nakshatra','?')} pada {chiron_t.get('pada','?')}
Lilith transit : {get_planet(transits,'Lilith ⚸').get('display','?')}
Pluton transit : {plu_t.get('display','?')} — {plu_t.get('nakshatra','?')}

━━━ PILIER 5 — VIMSHOTTARI DASHA ━━━
Dasha actuel : {dasha_str}
Fin Antardasha : {dasha_end}
Jupiter natal (Cadeaux karmiques) : {format_planet(jup_n, 'Jupiter ♃')}
Jupiter transit : {jup_t.get('display','?')} — {jup_t.get('nakshatra','?')}

━━━ ASPECTS DOCTRINE ACTIFS (orbe < 3°) ━━━
{aspects_str.strip()}

═══════════════════════════════════════════════════════
{mission_content}
═══════════════════════════════════════════════════════
"""
    return prompt


def main():
    import sys
    rich_mode = "--rich" in sys.argv or "--doctrine" in sys.argv
    now = datetime.datetime.now()
    
    mode_label = "Doctrine Évolutive Synthétique (Riche)" if rich_mode else "Karmic Lite (Compact)"
    print(f"⟳ Calcul en cours — Mode: {mode_label} ({now.strftime('%d/%m/%Y %Hh%M')})...\n")

    try:
        data = calculate_transits(
            NATAL, TRANSIT_LOC,
            now.year, now.month, now.day,
            now.hour, now.minute
        )
    except Exception as e:
        print(f"❌ Erreur calcul : {e}")
        sys.exit(1)

    prompt = generate_prompt(data, rich=rich_mode)

    # Affichage
    print(prompt)

    # Sauvegarde fichier
    suffix = "_rich" if rich_mode else ""
    output_file = f"karmic_prompt{suffix}_{now.strftime('%Y%m%d_%H%M')}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"\n✓ Prompt sauvegardé : {output_file}")
    print("→ Copie le contenu et colle-le dans Kai / Claude / Gemini")
    if not rich_mode:
        print("💡 Astuce : utilise 'python karmic_lite.py --rich' pour générer la Doctrine Évolutive complète en 4 blocs.")


if __name__ == "__main__":
    main()
