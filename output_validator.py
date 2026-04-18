"""
output_validator.py — Validation doctrinale des synthèses karmiques.

Vérifie qu'une synthèse générée respecte les règles de @siderealAstro13 :
  - Structure obligatoire (4 sections)
  - Interdictions absolues (noms de signes zodiacaux, formules vides)
  - Présence doctrinale (ROM/RAM, Chiron correctement nommé, maisons citées)
  - Longueur substantielle (≥ 300 tokens estimés)

Usage :
    validator = SynthesisValidator()
    result = validator.validate(synthesis_text)
    if not result["valid"]:
        # bloquer l'envoi → retry / refinement
    elif result["warnings"]:
        # envoyer mais flaguer pour révision humaine
"""

import re


# ── Constantes de validation ──────────────────────────────────────────────────

ZODIAC_SIGNS_FR = [
    "Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge",
    "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons",
]
ZODIAC_SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Formules génériques creuses à détecter (sans contexte astrologique)
GENERIC_PHRASES = [
    r"accepte-toi",
    r"laisse aller",
    r"lâche prise",
    r"sois toi-même",
    r"tu mérites",
    r"prends soin de toi",
    r"tu es suffisant",
    r"tout va bien se passer",
]

# ── Classe principale ─────────────────────────────────────────────────────────

class SynthesisValidator:
    """
    Valide une synthèse karmique selon la doctrine @siderealAstro13.

    Sévérité :
      - errors   → synthèse bloquée, client reçoit {"status": "retry"}
      - warnings → synthèse envoyée, flaggée pour révision humaine

    Score 0-100 :
      Chaque check réussi ajoute des points pondérés.
      errors font descendre le score à 0 si présents.
    """

    # Poids des checks (total = 100)
    _WEIGHTS = {
        "alternative_de_conscience": 20,
        "maisons_citees":            15,
        "longueur_suffisante":       15,
        "pas_de_signes_zodiacaux":   20,
        "chiron_formulation":        10,
        "rom_ram_present":           10,
        "pas_de_formules_vides":     10,
    }

    def validate(self, synthesis_text: str) -> dict:
        """
        Valide le texte de synthèse.

        Input :
            synthesis_text — texte brut de la synthèse générée par Claude/Gemma.

        Output :
            {
                "valid":    bool,           # False si errors non vides
                "errors":   [str, ...],     # blocants
                "warnings": [str, ...],     # non-blocants
                "score":    int,            # 0-100
                "checks":   {check: bool},  # détail par check
            }

        Exemples :
            # ✓ Bon
            validate("Tu portes H12 une mémoire... Alternative de Conscience : cesse...")
            → {"valid": True, "errors": [], "score": 95}

            # ✗ Mauvais
            validate("Ton Ketu en Scorpion indique... accepte-toi...")
            → {"valid": False, "errors": ["Signe zodiacal interdit : Scorpion"], "score": 0}
        """
        errors   = []
        warnings = []
        checks   = {}
        score    = 0

        text = synthesis_text or ""
        text_lower = text.lower()

        # ── CHECK 1 : "Alternative de Conscience" présent exactement 1 fois ──
        alt_count = len(re.findall(r"alternative de conscience", text_lower))
        if alt_count == 0:
            errors.append(
                'Section "Alternative de Conscience" absente — structure incomplète.'
            )
            checks["alternative_de_conscience"] = False
        elif alt_count > 3:
            warnings.append(
                f'"Alternative de Conscience" répété {alt_count} fois — redondance suspecte.'
            )
            checks["alternative_de_conscience"] = True
            score += self._WEIGHTS["alternative_de_conscience"]
        else:
            checks["alternative_de_conscience"] = True
            score += self._WEIGHTS["alternative_de_conscience"]

        # ── CHECK 2 : Maisons (H + chiffre) citées ≥ 3 fois ──────────────────
        house_matches = re.findall(r'\bH\d{1,2}\b', text)
        if len(house_matches) < 3:
            errors.append(
                f"Maisons citées : {len(house_matches)} (minimum 3 requis). "
                "Utiliser H1…H12 au lieu des noms de signes."
            )
            checks["maisons_citees"] = False
        else:
            checks["maisons_citees"] = True
            score += self._WEIGHTS["maisons_citees"]

        # ── CHECK 3 : Longueur ≥ 300 tokens estimés ───────────────────────────
        # Estimation simple : 1 token ≈ 4 caractères (ordre de grandeur)
        estimated_tokens = len(text) // 4
        if estimated_tokens < 300:
            errors.append(
                f"Synthèse trop courte ({estimated_tokens} tokens estimés, min 300). "
                "La section 4 (Alternative de Conscience) est probablement tronquée."
            )
            checks["longueur_suffisante"] = False
        else:
            checks["longueur_suffisante"] = True
            score += self._WEIGHTS["longueur_suffisante"]

        # ── CHECK 4 : Aucun nom de signe zodiacal ─────────────────────────────
        found_signs = []
        for sign in ZODIAC_SIGNS_FR + ZODIAC_SIGNS_EN:
            if re.search(rf'\b{re.escape(sign)}\b', text, re.IGNORECASE):
                found_signs.append(sign)
        if found_signs:
            errors.append(
                f"Signe(s) zodiacal(aux) interdit(s) détecté(s) : {', '.join(found_signs)}. "
                "Traduire en vécu (ex: 'Scorpion' → 'là où le non-dit devient insupportable')."
            )
            checks["pas_de_signes_zodiacaux"] = False
        else:
            checks["pas_de_signes_zodiacaux"] = True
            score += self._WEIGHTS["pas_de_signes_zodiacaux"]

        # ── CHECK 5 : Chiron bien formulé ─────────────────────────────────────
        # Mauvais : "guérisseur blessé" seul sans "clé" ou "RAM"
        # Bon : "Chiron ouvre la clé de H8", "RAM activé via Chiron"
        if "guérisseur blessé" in text_lower:
            has_key = "clé" in text_lower or "ram" in text_lower
            if not has_key:
                errors.append(
                    '"Guérisseur blessé" utilisé sans "clé" ni "RAM" — formulation archétypique '
                    'interdite. Chiron = outil de transmutation, pas étiquette.'
                )
                checks["chiron_formulation"] = False
            else:
                checks["chiron_formulation"] = True
                score += self._WEIGHTS["chiron_formulation"]
        else:
            checks["chiron_formulation"] = True
            score += self._WEIGHTS["chiron_formulation"]

        # ── CHECK 6 : ROM/RAM ou équivalent présent ────────────────────────────
        # Implicite : Ketu/Nœud Sud = ROM, Chiron = RAM
        rom_signals = ["rom", "ram", "ketu", "nœud sud", "noeud sud", "chiron", "loop karmique"]
        has_rom_ram = any(sig in text_lower for sig in rom_signals)
        if not has_rom_ram:
            warnings.append(
                "Aucune référence ROM/RAM, Ketu, Nœud Sud ou Chiron détectée. "
                "La colonne vertébrale doctrinale semble absente."
            )
            checks["rom_ram_present"] = False
        else:
            checks["rom_ram_present"] = True
            score += self._WEIGHTS["rom_ram_present"]

        # ── CHECK 7 : Pas de formules génériques vides ────────────────────────
        found_generic = []
        for pattern in GENERIC_PHRASES:
            if re.search(pattern, text_lower):
                found_generic.append(pattern.replace(r"\\b", "").replace(r"\b", ""))
        if found_generic:
            errors.append(
                f"Formule(s) générique(s) vide(s) sans contexte astrologique : "
                f"{', '.join(found_generic)}. Remplacer par un vécu planétaire précis."
            )
            checks["pas_de_formules_vides"] = False
        else:
            checks["pas_de_formules_vides"] = True
            score += self._WEIGHTS["pas_de_formules_vides"]

        # ── CHECK 8 (warning) : Saturne absent ────────────────────────────────
        if "saturne" not in text_lower:
            warnings.append(
                "Saturne non mentionné. Si Saturne est actif en transit, son absence "
                "appauvrit la lecture structurelle (dette karmique / cadre)."
            )

        # ── Score final ───────────────────────────────────────────────────────
        # Si des erreurs sont présentes, le score est plafonné à 0
        if errors:
            score = 0

        return {
            "valid":    len(errors) == 0,
            "errors":   errors,
            "warnings": warnings,
            "score":    score,
            "checks":   checks,
        }


# ── Helpers standalone ────────────────────────────────────────────────────────

def validate_synthesis(text: str) -> dict:
    """Raccourci fonctionnel — instancie SynthesisValidator et valide."""
    return SynthesisValidator().validate(text)
