"""
synthesis_pipeline.py — Orchestration du flux complet de synthèse karmique.

Flux : aspect_selector → Gemma → output_validator

Usage :
    pipeline = SynthesisPipeline()
    result = pipeline.generate_synthesis(
        natal_pos=calc_result["natal"],
        transit_pos=calc_result["transits"],
        aspects_list=calc_result["aspects"],
        user_data={"pseudo": "alice", "lang": "fr"},
        context="hook",
    )
    if result["valid"]:
        return result["synthesis"]
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from aspect_selector import select_dominant_aspects, select_dominant_aspects_ranked
from output_validator import SynthesisValidator


# ── Config / Env vars ─────────────────────────────────────────────────────────

GEMMA_MODEL      = os.environ.get("GEMMA_MODEL",      "gemma-2-9b-it")
GEMMA_ENDPOINT   = os.environ.get("GEMMA_ENDPOINT",   "")
GEMMA_AUTH       = os.environ.get("GEMMA_AUTH",       "")
GEMMA_MAX_TOKENS_HOOK      = int(os.environ.get("GEMMA_MAX_TOKENS_HOOK",      500))
GEMMA_MAX_TOKENS_SYNTHESIS = int(os.environ.get("GEMMA_MAX_TOKENS_SYNTHESIS", 2000))
GEMMA_MAX_TOKENS_CALENDAR  = int(os.environ.get("GEMMA_MAX_TOKENS_CALENDAR",  800))

VAULT_PATH  = Path(os.environ.get("VAULT_PATH", "karmic_vault/"))
RETRY_LIMIT = int(os.environ.get("RETRY_LIMIT", 3))

ORB_HOOK      = float(os.environ.get("ORB_HOOK",      1.0))
ORB_SYNTHESIS = float(os.environ.get("ORB_SYNTHESIS", 3.0))

# Nombre max d'aspects injectés selon contexte
MAX_ASPECTS = {
    "hook":      3,
    "calendar":  4,
    "synthesis": 6,
}


# ── Pipeline principal ────────────────────────────────────────────────────────

class SynthesisPipeline:
    """
    Orchestre le flux complet de génération et validation d'une synthèse karmique.

    Le pipeline encapsule :
      1. Sélection des aspects dominants (aspect_selector)
      2. Construction du prompt Gemma (vault + aspects + instructions)
      3. Appel Gemma (local ou cloud)
      4. Validation doctrinale (output_validator)
      5. Retry avec feedback d'erreurs (max RETRY_LIMIT)
    """

    def __init__(self):
        self._vault_cache: str | None = None
        self._validator = SynthesisValidator()

    # ── Méthode principale ────────────────────────────────────────────────────

    def generate_synthesis(
        self,
        natal_pos: dict,
        transit_pos: dict,
        aspects_list: list[dict],
        user_data: dict,
        context: str = "hook",
    ) -> dict:
        """
        Génère une synthèse karmique validée pour un utilisateur.

        Input :
            natal_pos    — positions natales (output de calculate_transits()["natal"])
            transit_pos  — positions transit (output de calculate_transits()["transits"])
            aspects_list — liste d'aspects triée par orbe (calculate_transits()["aspects"])
            user_data    — dict avec au minimum :
                           {"pseudo": str, "lang": "fr"|"en", "name": str (optionnel)}
            context      — "hook" | "calendar" | "synthesis"
                           Détermine le format de sortie et le nombre d'aspects utilisés.

        Output :
            {
                "synthesis":  str,                   # texte généré (même si invalide après retries)
                "valid":      bool,                  # True si validation doctrinale passée
                "validation": {                      # dernier résultat de validate()
                    "score":    int,
                    "errors":   [str, ...],
                    "warnings": [str, ...],
                    "checks":   {str: bool},
                },
                "retry_count":                int,   # 0-RETRY_LIMIT
                "context":                    str,
                "aspects_used":               list,  # aspects injectés dans le prompt
                "human_review_recommended":   bool,  # True si warnings présents
                "refinement_needed":          bool,  # True si exhausted retries invalide
                "timestamp":                  str,   # ISO 8601 UTC
            }

        Exemples de contexte :
            context="hook"      → 3 phrases, ≤ 500 tokens, aspects orbe < 1°
            context="calendar"  → 4-5 phrases, ≤ 800 tokens, résumé journalier
            context="synthesis" → 4 sections complètes, ≤ 2000 tokens

        Logique retry :
            Si validate() retourne errors → rebuild prompt avec feedback erreurs → retry.
            Après RETRY_LIMIT tentatives, retourne quand même le dernier résultat
            avec refinement_needed=True.
        """
        # a) Sélection des aspects dominants selon contexte
        orb_threshold = ORB_HOOK if context == "hook" else ORB_SYNTHESIS
        filtered = [a for a in aspects_list if a.get("orb", 99) <= orb_threshold]
        max_asp  = MAX_ASPECTS.get(context, 4)
        aspects_used = select_dominant_aspects_ranked(filtered, max_houses=max_asp)

        # b) Charge le vault (avec cache)
        vault_context = self.get_vault_context()

        synthesis      = ""
        validation_result = {"score": 0, "errors": [], "warnings": [], "checks": {}}
        retry_count    = 0
        error_feedback = []

        while retry_count <= RETRY_LIMIT:
            # b) Construction du prompt
            prompt = self.build_gemma_prompt(
                aspects_dict=aspects_used,
                vault_context=vault_context,
                user_data=user_data,
                context=context,
                error_feedback=error_feedback,
            )

            # c) Appel Gemma
            synthesis = self.call_gemma_api(prompt, context=context)

            # d) Validation
            validation_result = self._validator.validate(synthesis)

            # e) Logique retry
            if validation_result["valid"]:
                break

            if retry_count >= RETRY_LIMIT:
                break

            error_feedback = validation_result["errors"]
            retry_count += 1

        has_warnings   = len(validation_result.get("warnings", [])) > 0
        refinement     = not validation_result["valid"] and retry_count > RETRY_LIMIT

        return {
            "synthesis":                synthesis,
            "valid":                    validation_result["valid"],
            "validation":               {
                "score":    validation_result.get("score", 0),
                "errors":   validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "checks":   validation_result.get("checks", {}),
            },
            "retry_count":              retry_count,
            "context":                  context,
            "aspects_used":             aspects_used,
            "human_review_recommended": has_warnings,
            "refinement_needed":        refinement,
            "timestamp":                datetime.now(timezone.utc).isoformat(),
        }

    # ── Vault ─────────────────────────────────────────────────────────────────

    def get_vault_context(self) -> str:
        """
        Charge et retourne le contenu concaténé des 3 fichiers vault doctrinaux.
        Met en cache en mémoire après le premier chargement (I/O unique par process).

        Fichiers chargés dans l'ordre :
            karmic_vault/00_MASTER_CONTEXT.md
            karmic_vault/01_output_rules.md
            karmic_vault/02_planet_keywords.md

        Si un fichier est absent, il est ignoré silencieusement avec un warning log.

        Retourne une string concaténée avec séparateurs de sections.
        """
        if self._vault_cache is not None:
            return self._vault_cache

        vault_files = [
            "00_MASTER_CONTEXT.md",
            "01_output_rules.md",
            "02_planet_keywords.md",
        ]
        sections = []
        for filename in vault_files:
            path = VAULT_PATH / filename
            try:
                content = path.read_text(encoding="utf-8")
                sections.append(f"=== {filename} ===\n{content}")
            except FileNotFoundError:
                import logging
                logging.warning("Vault file manquant : %s", path)

        self._vault_cache = "\n\n".join(sections)
        return self._vault_cache

    # ── Construction du prompt ────────────────────────────────────────────────

    def build_gemma_prompt(
        self,
        aspects_dict: list[dict],
        vault_context: str,
        user_data: dict,
        context: str,
        error_feedback: list[str] | None = None,
    ) -> str:
        """
        Construit le prompt complet envoyé à Gemma.

        Structure :
            [VAULT]         — doctrine complète (@siderealAstro13)
            [ASPECTS]       — aspects dominants sélectionnés
            [USER CONTEXT]  — pseudo, langue, données natales si disponibles
            [INSTRUCTIONS]  — format attendu selon context
            [RETRY FEEDBACK]— erreurs du pass précédent si retry > 0

        Input :
            aspects_dict  — liste d'aspects (output de select_dominant_aspects_ranked)
            vault_context — contenu vault (get_vault_context())
            user_data     — {"pseudo": str, "lang": str, "name": str, ...}
            context       — "hook" | "calendar" | "synthesis"
            error_feedback— liste d'erreurs du validateur (pour retry)

        Output :
            str — prompt complet prêt à envoyer à Gemma.

        Exemples de blocs générés :

            [ASPECTS ACTIFS]
            - Saturne → Chiron (H12) · conjonction · orbe 0.8° · Shatabhisha/Revati
            - Soleil → Lilith (H5) · carré · orbe 1.2°

            [INSTRUCTIONS — hook]
            Écris 3 phrases. Pas de titre. Pas d'introduction.
            Phrase 1 : mémoire karmique réactivée aujourd'hui.
            ...

            [CORRECTION REQUISE — retry 2/3]
            Erreurs détectées dans la version précédente :
            - Section "Alternative de Conscience" absente
            Corrige ces points dans la nouvelle version.
        """
        pseudo = user_data.get("pseudo", user_data.get("name", "l'utilisateur"))
        lang   = user_data.get("lang", "fr")

        # Bloc aspects
        aspects_lines = []
        for a in aspects_dict:
            natal_display   = a.get("natal_display", "")
            transit_display = a.get("transit_display", "")
            line = (
                f"- {a.get('transit_planet', '?')} → {a.get('natal_planet', '?')} "
                f"({natal_display}) · {a.get('aspect', '?')} · orbe {a.get('orb', '?')}°"
            )
            if a.get("transit_nak"):
                line += f" · {a['transit_nak']}"
                if a.get("natal_nak"):
                    line += f"/{a['natal_nak']}"
            aspects_lines.append(line)
        aspects_block = "\n".join(aspects_lines) if aspects_lines else "(aucun aspect sous le seuil d'orbe)"

        # Bloc instructions selon contexte
        instructions_block = self._instructions_for_context(context, pseudo, lang)

        # Bloc retry feedback
        feedback_block = ""
        if error_feedback:
            retry_n = len(error_feedback)
            feedback_block = (
                f"\n[CORRECTION REQUISE]\n"
                f"Erreurs détectées dans la version précédente :\n"
                + "\n".join(f"- {e}" for e in error_feedback)
                + "\nCorrige ces points dans la nouvelle version. Ne répète pas les erreurs."
            )

        prompt = (
            f"[VAULT DOCTRINAL]\n{vault_context}\n\n"
            f"[ASPECTS ACTIFS — {context.upper()}]\n{aspects_block}\n\n"
            f"[CONTEXTE UTILISATEUR]\n"
            f"Pseudo : {pseudo}\n"
            f"Langue : {lang}\n\n"
            f"[INSTRUCTIONS]\n{instructions_block}"
            f"{feedback_block}"
        )
        return prompt

    def _instructions_for_context(self, context: str, pseudo: str, lang: str) -> str:
        """
        Retourne le bloc d'instructions Gemma selon le contexte demandé.

        hook :      3 phrases · pas de titre · mémoire/blessure/alternative
        calendar :  résumé journalier · 4-5 phrases · énergie du jour
        synthesis : 4 sections complètes · min 300 mots · Alternative de Conscience obligatoire
        """
        if context == "hook":
            return (
                f"Écris un hook de 3 phrases pour {pseudo}. Pas de titre. Pas d'introduction.\n"
                "Phrase 1 : ce qui se réactive dans la mémoire karmique aujourd'hui.\n"
                "Phrase 2 : ce que ça touche dans la blessure profonde.\n"
                "Phrase 3 : l'amorce de l'Alternative de Conscience.\n"
                "INTERDIT : noms de signes zodiacaux. Utilise H1-H12 et noms de planètes."
            )
        elif context == "calendar":
            return (
                f"Écris un résumé karmique du jour pour {pseudo}. 4-5 phrases max.\n"
                "Décris l'énergie dominante du transit, ce qu'elle active dans le thème natal,\n"
                "et une action concrète possible. Ton : dense, direct, oraculaire.\n"
                "INTERDIT : noms de signes zodiacaux."
            )
        else:  # synthesis
            return (
                f"Écris la synthèse karmique complète pour {pseudo}.\n"
                "Structure obligatoire (dans cet ordre) :\n"
                "## 1. LA MÉMOIRE KARMIQUE\n"
                "## 2. LA BLESSURE EN TRAITEMENT\n"
                "## 3. L'ÉPREUVE KARMIQUE\n"
                "## 4. ALTERNATIVE DE CONSCIENCE\n"
                "Minimum 300 mots. Section 4 obligatoire avec une phrase finale actionnable.\n"
                "INTERDIT : noms de signes zodiacaux. Utilise H1-H12 et noms de planètes."
            )

    # ── Appel Gemma ───────────────────────────────────────────────────────────

    def call_gemma_api(self, prompt: str, context: str = "hook") -> str:
        """
        Envoie le prompt à Gemma et retourne le texte généré.

        Deux modes selon GEMMA_ENDPOINT :
          - "local" ou vide → stub (retourne placeholder pour dev/test)
          - URL HTTP        → POST JSON vers l'endpoint configuré

        Payload envoyé :
            {
                "model":      GEMMA_MODEL,
                "prompt":     prompt,
                "max_tokens": GEMMA_MAX_TOKENS_HOOK | _SYNTHESIS | _CALENDAR,
                "temperature": 0.7
            }

        Réponse attendue :
            {"text": "...", "model": "...", "tokens_used": 123}
            ou
            {"choices": [{"text": "..."}]}   (format OpenAI-compatible)

        En cas d'erreur réseau ou timeout : lève une RuntimeError avec le détail.

        Config env vars :
            GEMMA_ENDPOINT  — URL de l'endpoint (ex: "http://localhost:8080/generate")
            GEMMA_AUTH      — token Bearer si requis
            GEMMA_MODEL     — nom du modèle

        Exemple (stub local) :
            os.environ["GEMMA_ENDPOINT"] = ""
            result = pipeline.call_gemma_api(prompt, "hook")
            # → "[STUB] Gemma non configuré — prompt reçu (456 chars)"
        """
        max_tokens_map = {
            "hook":      GEMMA_MAX_TOKENS_HOOK,
            "calendar":  GEMMA_MAX_TOKENS_CALENDAR,
            "synthesis": GEMMA_MAX_TOKENS_SYNTHESIS,
        }
        max_tokens = max_tokens_map.get(context, GEMMA_MAX_TOKENS_HOOK)

        endpoint = GEMMA_ENDPOINT.strip()

        # Mode stub (dev/test)
        if not endpoint or endpoint == "local":
            return (
                f"[STUB] Gemma non configuré — prompt reçu ({len(prompt)} chars), "
                f"context={context}, max_tokens={max_tokens}."
            )

        import requests

        headers = {"Content-Type": "application/json"}
        if GEMMA_AUTH:
            headers["Authorization"] = f"Bearer {GEMMA_AUTH}"

        payload = {
            "model":       GEMMA_MODEL,
            "prompt":      prompt,
            "max_tokens":  max_tokens,
            "temperature": 0.7,
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Support format natif et format OpenAI-compatible
            if "text" in data:
                return data["text"]
            elif "choices" in data and data["choices"]:
                return data["choices"][0].get("text", "")
            else:
                raise RuntimeError(f"Format de réponse Gemma inattendu : {list(data.keys())}")

        except requests.Timeout:
            raise RuntimeError(f"Timeout Gemma après 30s (endpoint: {endpoint})")
        except requests.RequestException as exc:
            raise RuntimeError(f"Erreur réseau Gemma : {exc}")


# ── Fonction standalone ───────────────────────────────────────────────────────

def run_pipeline(
    calc_result: dict,
    user_data: dict,
    context: str = "hook",
) -> dict:
    """
    Raccourci fonctionnel — instancie SynthesisPipeline et génère la synthèse.

    Input :
        calc_result — output complet de calculate_transits()
                      doit contenir "natal", "transits", "aspects"
        user_data   — {"pseudo": str, "lang": str, ...}
        context     — "hook" | "calendar" | "synthesis"

    Output :
        dict (cf. SynthesisPipeline.generate_synthesis)

    Exemple :
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        output = run_pipeline(result, {"pseudo": "alice", "lang": "fr"}, context="hook")
        print(output["synthesis"])
    """
    pipeline = SynthesisPipeline()
    return pipeline.generate_synthesis(
        natal_pos=calc_result.get("natal", {}),
        transit_pos=calc_result.get("transits", {}),
        aspects_list=calc_result.get("aspects", []),
        user_data=user_data,
        context=context,
    )
