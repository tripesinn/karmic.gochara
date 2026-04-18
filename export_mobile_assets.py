"""
export_mobile_assets.py — Génère les assets Android depuis doctrine.py

Usage :
    python export_mobile_assets.py

Sortie :
    android/app/src/main/assets/nakshatra_karma.json
    android/app/src/main/assets/system_prompt_mobile.json

À relancer après chaque modification de doctrine.py.
Pré-requis : lancé depuis la racine du repo karmic.gochara.
"""

import json
import os
from doctrine import NAKSHATRA_KARMA, SYSTEM_PROMPT_MOBILE_FR, SYSTEM_PROMPT_MOBILE_EN

ASSETS_DIR = os.path.join("android", "app", "src", "main", "assets")


def export_nakshatra_karma():
    out_path = os.path.join(ASSETS_DIR, "nakshatra_karma.json")
    # Garde uniquement les planètes doctrinalement pertinentes pour mobile
    MOBILE_PLANETS = ["ketu", "chiron", "rahu", "lilith", "saturn", "jupiter", "mars", "venus"]
    compressed = {}
    for nak, entries in NAKSHATRA_KARMA.items():
        compressed[nak] = {k: v for k, v in entries.items() if k in MOBILE_PLANETS}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(compressed, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"OK {out_path}  ({size_kb} KB, {len(compressed)} nakshatras)")


def export_system_prompts():
    out_path = os.path.join(ASSETS_DIR, "system_prompt_mobile.json")
    data = {
        "fr": SYSTEM_PROMPT_MOBILE_FR,
        "en": SYSTEM_PROMPT_MOBILE_EN,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"OK {out_path}  ({size_kb} KB)")


if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)
    export_nakshatra_karma()
    export_system_prompts()
    print("Assets Android générés.")
