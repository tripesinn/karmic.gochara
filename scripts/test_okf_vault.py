import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_interpret import _load_vault

# Mock user and chart_data
mock_user = {
    "pseudo": "test_user",
    "ketu_nakshatra": "Ashwini",
    "rahu_nakshatra": "Bharani",
    "chiron_nakshatra": "Krittika",
    "lilith_nakshatra": "Rohini",
}

mock_chart_data = {
    "transits": {
        "Saturn": {"lon_raw": 340.5},
        "Uranus": {"lon_raw": 55.2}
    },
    "aspects": [
        {
            "transit_planet": "Saturn",
            "natal_planet": "Chiron",
            "aspect": "Carré",
            "transit_nakshatra": "Pushya",
            "natal_nakshatra": "Ardra"
        }
    ]
}

print("=== TESTING SELECTIVE OKF LOAD ===")
vault = _load_vault(include_keywords=True, user=mock_user, chart_data=mock_chart_data)
if vault:
    print(f"Vault loaded successfully! Length: {len(vault)} characters.")
    # Check if specific terms exist in the output
    print("\nContains Ashwini (Natal Ketu Nakshatra)?:", "Ashwini" in vault)
    print("Contains Bharani (Natal Rahu Nakshatra)?:", "Bharani" in vault)
    print("Contains Saturn (Transit Planet)?:", "Saturne" in vault)
    print("Contains Carré (Transit Aspect)?:", "carré" in vault or "Carré" in vault)
    
    # Check if some unreferenced concepts are absent
    print("Contains Purva Phalguni (Unused Nakshatra)?:", "Purva Phalguni" in vault)
    print("Contains Pluton (Unused Planet)?:", "Pluton" in vault or "pluton" in vault)
else:
    print("Failed to load vault.")
