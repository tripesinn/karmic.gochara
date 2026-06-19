
with open('/Users/jero87/karmic.gochara/ai_interpret.py') as f:
    content = f.read()

# 1. Add _SERVER_GROK_KEY and _call_grok
new_headers = """_SERVER_ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_SERVER_GROK_KEY = os.environ.get("GROK_API_KEY", "")

def _call_grok(system: str, prompt: str, model: str, api_key: str, max_tokens: int) -> str:
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or "grok-beta",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]"""
content = content.replace('_SERVER_ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")', new_headers)


# 2. Update generate_ai provider routing
old_provider_check = """        if model and model.startswith("claude") and _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, model, _SERVER_ANTHROPIC_KEY, max_tokens)
        # Fallback sur Gemini sans modèle custom pour éviter un 404
        return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=None, user_key=user_key)"""
new_provider_check = """        if model and model.startswith("claude") and _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, model, _SERVER_ANTHROPIC_KEY, max_tokens)
        if model and model.startswith("grok") and _SERVER_GROK_KEY:
            return _call_grok(system, prompt, model, _SERVER_GROK_KEY, max_tokens)
        # Fallback sur Gemini sans modèle custom pour éviter un 404
        return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=None, user_key=user_key)"""
content = content.replace(old_provider_check, new_provider_check)


# 3. Update generate_ai fallback exceptions
old_exception = """        print(f"Erreur provider {provider}: {e}")
        if _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
        return "Erreur lors de la génération (serveur non configuré)."
        
    # Provider inconnu -> serveur par défaut
    if _SERVER_ANTHROPIC_KEY:
        return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
    return "Erreur lors de la génération (aucun provider valide).\""""
new_exception = """        print(f"Erreur provider {provider}: {e}")
        if _SERVER_GROK_KEY:
            return _call_grok(system, prompt, "grok-beta", _SERVER_GROK_KEY, max_tokens)
        elif _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
        return "Erreur lors de la génération (serveur non configuré)."
        
    # Provider inconnu -> serveur par défaut
    if _SERVER_GROK_KEY:
        return _call_grok(system, prompt, "grok-beta", _SERVER_GROK_KEY, max_tokens)
    elif _SERVER_ANTHROPIC_KEY:
        return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
    return "Erreur lors de la génération (aucun provider valide).\""""
content = content.replace(old_exception, new_exception)

# 4. Update HOOK_MODEL definition
content = content.replace(
    'HOOK_MODEL = os.environ.get("HOOK_MODEL", "claude-3-5-sonnet-latest")',
    'HOOK_MODEL = os.environ.get("HOOK_MODEL", "grok-beta")'
)

with open('/Users/jero87/karmic.gochara/ai_interpret.py', 'w') as f:
    f.write(content)
