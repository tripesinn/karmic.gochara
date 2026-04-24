"""
gemini_api.py — Appels REST Gemini sans SDK Google.
Utilise uniquement `requests` (déjà dans requirements.txt).
"""
import json
import logging
import os
import time
import requests

# ── Configuration ─────────────────────────────────────────────────────────────
_DEFAULT_MODEL = os.environ.get("HOOK_MODEL", "gemini-1.5-flash")
_DEFAULT_SYNTH = os.environ.get("SYNTHESIS_MODEL", "gemini-1.5-flash")
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# ── Mécanisme de Retry ────────────────────────────────────────────────────────
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # en secondes

def _make_request(url: str, payload: dict, stream: bool = False, timeout: int = 60) -> requests.Response:
    """Effectue une requête POST avec une logique de retry pour les erreurs 5xx."""
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(url, json=payload, stream=stream, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as e:
            last_exception = e
            # Réessayer uniquement pour les erreurs serveur (5xx)
            if 500 <= e.response.status_code < 600:
                backoff = INITIAL_BACKOFF * (2 ** attempt)
                logging.warning(
                    f"Erreur serveur {e.response.status_code}. "
                    f"Tentative {attempt + 1}/{MAX_RETRIES} dans {backoff}s..."
                )
                time.sleep(backoff)
            else:
                # Ne pas réessayer pour les erreurs client (4xx)
                raise e
        except requests.exceptions.RequestException as e:
            # Pour les erreurs réseau (timeout, etc.)
            last_exception = e
            backoff = INITIAL_BACKOFF * (2 ** attempt)
            logging.warning(
                f"Erreur réseau. Tentative {attempt + 1}/{MAX_RETRIES} dans {backoff}s..."
            )
            time.sleep(backoff)
            
    # Si toutes les tentatives ont échoué
    raise last_exception


def _api_key(override: str = None) -> str:
    return override or os.environ.get("GEMINI_API_KEY", "")


def generate(system: str, prompt: str, model: str = "", max_tokens: int = 8192, user_key: str = None) -> str:
    """Appel non-streaming, retourne le texte brut."""
    model = model or _DEFAULT_SYNTH
    url = f"{_BASE_URL}/{model}:generateContent?key={_api_key(user_key)}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }
    r = _make_request(url, payload, timeout=90)
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def stream(system: str, prompt: str, model: str = "", max_tokens: int = 4096, user_key: str = None):
    """Générateur streaming — yield de morceaux de texte."""
    model = model or _DEFAULT_MODEL
    url = f"{_BASE_URL}/{model}:streamGenerateContent?key={_api_key(user_key)}&alt=sse"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.8},
    }
    with _make_request(url, payload, stream=True, timeout=120) as r:
        for line in r.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                if text:
                    yield text
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
