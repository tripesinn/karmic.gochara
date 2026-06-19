#!/usr/bin/env python3
"""Build the Gemma prompts for jero's profile."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["STRIPE_PRICE_TEST_GEMMA"] = "price_dummy_lecture"
os.environ["STRIPE_PRICE_GEMMA_UNLIMITED"] = "price_dummy_unlimited"
os.environ["KARMIC_STRIPE_SECRET_KEY"] = "***"
os.environ["GOOGLE_CREDENTIALS_JSON"] = "{}"
os.environ["SHEET_ID"] = "dummy_sheet_id"

import sys as _sys
from unittest.mock import MagicMock

_sys.modules['gspread'] = MagicMock()
_sys.modules['google'] = MagicMock()
_sys.modules['google.oauth2'] = MagicMock()
_sys.modules['google.oauth2.service_account'] = MagicMock()

import profiles

profiles.GoogleSheetsSession = MagicMock()
profiles.update_profile = MagicMock()
profiles.consume_plan_synthesis = MagicMock(return_value=True)
profiles.get_profile_by_pseudo = MagicMock(return_value={"pseudo": "jero", "name": "Jérôme"})
profiles.get_all_profiles = MagicMock(return_value=[])

from ai_interpret import build_prompt_natal, build_prompt_only
from astro_calc import calculate_transits

# Jero's real natal data: 1987-04-03 12:00 Paris
natal_data = {
    "name": "Jérôme",
    "year": 1987, "month": 4, "day": 3,
    "hour": 12, "minute": 0,
    "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris",
    "city": "Paris, France"
}

transit_loc = {
    "city": "Paris, France",
    "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"
}

# Calculate for today (2026-06-06)
chart = calculate_transits(natal_data, transit_loc, 2026, 6, 6, 12, 0)
print("=== THÈME CALCULÉ ===", flush=True)
print(f"Chandra Lagna: {chart['natal'].get('chandra_lagna_display', '?')}", flush=True)
print(f"Ketu: {chart['natal'].get('ketu_display', '?')}", flush=True)
print(f"Rahu: {chart['natal'].get('rahu_display', '?')}", flush=True)
print(f"Chiron: {chart['natal'].get('chiron_display', '?')}", flush=True)
print(f"PV: {chart['natal'].get('porte_visible_display', '?')}", flush=True)
print(f"Transits: {len(chart.get('transits', {}))} planets", flush=True)
print(f"Aspects: {len(chart.get('aspects', []))} aspects", flush=True)
print()

# Enrich with natal data that _enrich_profile_with_natal would add
def _sign(display):
    parts = (display or "").strip().split()
    return parts[1] if len(parts) >= 2 else ""
def _house(planet_display, asc_sign):
    # Just use the house from the chart directly
    return ""

natal = chart["natal"]

# Build enriched profile
enriched = {
    "name": "Jérôme",
    "pseudo": "jero",
    "lang": "fr",
    "chandra_lagna_sign": _sign(natal.get("chandra_lagna_display", "")),
    "ketu_sign": _sign(natal.get("ketu_display", "")),
    "ketu_house": str(natal.get("ketu_info", {}).get("chandra_house", "")),
    "chiron_sign": _sign(natal.get("chiron_display", "")),
    "chiron_house": str(natal.get("chiron_info", {}).get("chandra_house", "")),
    "rahu_sign": _sign(natal.get("rahu_display", "")),
    "porte_visible_sign": _sign(natal.get("porte_visible_display", "")),
    "porte_visible_house": str(natal.get("porte_visible_info", {}).get("chandra_house", "")),
    "lilith_sign": _sign(natal.get("lilith_display", "")),
    "lilith_house": str(natal.get("lilith_info", {}).get("chandra_house", "")),
    "ketu_nakshatra": natal.get("ketu_info", {}).get("nakshatra", ""),
    "chiron_nakshatra": natal.get("chiron_info", {}).get("nakshatra", ""),
    "rahu_nakshatra": natal.get("rahu_info", {}).get("nakshatra", ""),
}

print("=== ENRICHED ===", flush=True)
for k, v in enriched.items():
    if v:
        print(f"  {k}: {v}", flush=True)
print()

# Build natal prompt
print("=" * 60, flush=True)
print("=== PROMPT 1: NATAL HOOK (3 phrases) ===", flush=True)
print("=" * 60, flush=True)
natal_result = build_prompt_natal(enriched, lang="fr")
print("\n--- SYSTEM ---", flush=True)
print(natal_result['system'], flush=True)
print("\n--- USER ---", flush=True)
print(natal_result['user'], flush=True)

# Build synthesis prompt
print("\n\n" + "=" * 60, flush=True)
print("=== PROMPT 2: SYNTHÈSE COMPLÈTE (4 blocs) ===", flush=True)
print("=" * 60, flush=True)
synthesis_result = build_prompt_only(chart, enriched, lang="fr", is_free=False)
print("\n--- SYSTEM ---", flush=True)
print(synthesis_result['system'], flush=True)
print("\n--- USER ---", flush=True)
print(synthesis_result['user'], flush=True)

print("\n\n✅ DONE", flush=True)