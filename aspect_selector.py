"""
aspect_selector.py — Sélection dominante des aspects pour la synthèse karmique.

Réduit la liste brute d'aspects (triée par orbe) à 1 aspect par maison natale,
en gardant l'orbe le plus serré. Évite la redondance dans le prompt IA.
"""

import re


def extract_house(display_string: str) -> str | None:
    """
    Extrait le numéro de maison d'une string d'affichage planétaire.

    Exemples :
        "Poissons ♓ H12 21°14'" → "H12"
        "Verseau ♒ H3 08°00'"   → "H3"
        "Bélier ♈ 05°22'"       → None  (pas de maison)
        ""                       → None

    La maison est encodée comme `H` suivi d'un ou deux chiffres,
    précédé d'un espace ou en début de token.
    """
    if not display_string:
        return None
    match = re.search(r'\bH(\d{1,2})\b', display_string)
    return f"H{match.group(1)}" if match else None


def select_dominant_aspects(aspects_list: list[dict]) -> dict[str, dict]:
    """
    Sélectionne l'aspect le plus significatif par maison natale.

    Input :
        aspects_list — liste triée par orbe croissant, format :
        [
            {
                "transit_planet":  "Saturne ♄",
                "transit_display": "Verseau ♒ 15°22'",
                "natal_planet":    "Chiron ⚷",
                "natal_display":   "Poissons ♓ H12 21°14'",
                "aspect":          "conjonction",
                "orb":             0.8,
                "retrograde":      False,
                "transit_nak":     "Shatabhisha",
                "natal_nak":       "Revati",
            },
            ...
        ]

    Output :
        dict maison → aspect_dict (1 seul par maison, orbe minimal) :
        {
            "H12": {"transit_planet": "Saturne ♄", "natal_planet": "Chiron ⚷", "orb": 0.8, ...},
            "H3":  {"transit_planet": "Soleil ☉",  "natal_planet": "Lilith ⚸",  "orb": 1.2, ...},
        }

    Aspects sans maison détectable (planètes sans position Chandra Lagna) sont ignorés.
    La liste en input doit déjà être triée par orbe — la première occurrence par maison gagne.

    Exemple d'appel :
        result = calculate_transits(...)
        aspects = result["aspects"]          # déjà triés par orbe
        dominant = select_dominant_aspects(aspects)
        # → {"H12": {...}, "H5": {...}, ...}
    """
    dominant: dict[str, dict] = {}

    for aspect in aspects_list:
        natal_display = aspect.get("natal_display", "")
        house = extract_house(natal_display)

        if house is None:
            continue

        if house not in dominant:
            dominant[house] = aspect

    return dominant


def select_dominant_aspects_ranked(
    aspects_list: list[dict],
    max_houses: int = 5,
) -> list[dict]:
    """
    Variante plate : retourne une liste d'aspects dominants (1/maison),
    limitée à `max_houses`, triée par orbe.

    Utile pour injecter directement dans un prompt IA sans gestion de dict.

    Exemple :
        top = select_dominant_aspects_ranked(aspects, max_houses=4)
        for a in top:
            print(a["transit_planet"], "→", a["natal_planet"], a["orb"])
    """
    by_house = select_dominant_aspects(aspects_list)
    ranked = sorted(by_house.values(), key=lambda a: a["orb"])
    return ranked[:max_houses]
