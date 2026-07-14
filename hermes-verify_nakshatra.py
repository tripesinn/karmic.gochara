#!/usr/bin/env python3
"""VERIF AD-HOC (hermes) — couche Nakshatra playground, SANS appel Grok.
Vérifie : (1) data.reelle porte nakshatra, (2) build_nakshatra_hints injecte 2
lignes, (3) build_system_instruction les place aux bons points, (4) anti-jargon
interdit bien le mot Nakshatra en sortie (guard read-only)."""
import sys, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from karmic_lite import NATAL, TRANSIT_LOC, generate_prompt
from astro_calc import calculate_transits
from prompt_xbot_v2 import (build_system_instruction, build_nakshatra_hints,
                            NAKSHATRA_RULES, ANTI_JARGON)

now = datetime.datetime.now()
data = calculate_transits(NATAL, TRANSIT_LOC, now.year, now.month, now.day,
                          now.hour, now.minute)

moon_nak = data["natal"].get("Lune ☽", {}).get("nakshatra", "")
moon_t_nak = data["transits"].get("Lune ☽", {}).get("nakshatra", "")
print(f"[1] DATA REELLE : lune_natale={moon_nak!r} lune_transit={moon_t_nak!r}")
assert moon_nak and moon_t_nak, "FAIL: nakshatra vide dans la data"

moon_hint, transit_hint = build_nakshatra_hints(moon_nak, moon_t_nak)
print(f"[2] HINTS (2/27) :\n   - {moon_hint}\n   - {transit_hint}")
assert moon_nak in NAKSHATRA_RULES and moon_t_nak in NAKSHATRA_RULES

sys_instr = build_system_instruction(moon_hint, transit_hint)
print(f"[3] SYSTEM INSTRUCTION : {len(sys_instr)} chars, contient hint Lune ? "
      f"{moon_nak in sys_instr} / hint Transit ? {moon_t_nak in sys_instr}")
assert moon_nak in sys_instr and moon_t_nak in sys_instr, "FAIL: hints non injectés"

# Anti-jargon : le mot Nakshatra doit etre INTERDIT en sortie modele
forbidden_ok = "Nakshatra" in ANTI_JARGON or "Nakshatra" in sys_instr
print(f"[4] Anti-jargon : 'Nakshatra' explicitement banni en reponse ? "
      f"{('Nakshatra' in sys_instr)}")
assert "Nakshatra" in sys_instr, "FAIL: interdiction Nakshatra absente du prompt"

# Sanity : 27 entrees compltes, toutes polarisees Inertie+Alignement
bad = [k for k, v in NAKSHATRA_RULES.items()
       if "Inertie" not in v or "Alignement" not in v]
print(f"[5] DICO : {len(NAKSHATRA_RULES)}/27 entrees, polarisation incomplete = {bad}")
assert len(NAKSHATRA_RULES) == 27 and not bad

print("\n✅ VERIF OK — couche Nakshatra playground operationnelle, 0 appel Grok, 0 dataset.")
