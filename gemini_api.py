"""
gemini_api.py — Appels REST Gemini sans SDK Google.
Utilise uniquement `requests` (déjà dans requirements.txt).
"""
import json
import os
import requests

_DEFAULT_MODEL = os.environ.get("HOOK_MODEL", "gemini-2.5-flash")
_DEFAULT_SYNTH  = os.environ.get("SYNTHESIS_MODEL", "gemini-2.5-flash")
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def _api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "")


def generate(system: str, prompt: str, model: str = "", max_tokens: int = 4096) -> str:
    """Appel non-streaming, retourne le texte brut."""
    model = model or _DEFAULT_MODEL
    url = f"{_BASE_URL}/{model}:generateContent?key={_api_key()}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def stream(system: str, prompt: str, model: str = "", max_tokens: int = 4096):
    """Générateur streaming — yield de morceaux de texte."""
    model = model or _DEFAULT_MODEL
    url = f"{_BASE_URL}/{model}:streamGenerateContent?key={_api_key()}&alt=sse"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    with requests.post(url, json=payload, stream=True, timeout=120) as r:
        r.raise_for_status()
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
