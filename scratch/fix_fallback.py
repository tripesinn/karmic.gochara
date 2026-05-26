with open('/Users/jero87/karmic.gochara/ai_interpret.py', 'r') as f:
    content = f.read()

old_fallback = """    except Exception as e:
        # En cas d'erreur de clé ou d'API, log et fallback sur Gemini avec le modèle par défaut
        print(f"Erreur provider {provider}: {e}")
        return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=None, user_key=None)
        
    return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=None, user_key=None)"""

new_fallback = """    except Exception as e:
        # En cas d'erreur de clé ou d'API, log et fallback sur le serveur (Claude par défaut)
        print(f"Erreur provider {provider}: {e}")
        if _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, "claude-sonnet-4-6", _SERVER_ANTHROPIC_KEY, max_tokens)
        return "Erreur lors de la génération (serveur non configuré)."
        
    # Provider inconnu -> serveur par défaut
    if _SERVER_ANTHROPIC_KEY:
        return _call_claude(system, prompt, "claude-sonnet-4-6", _SERVER_ANTHROPIC_KEY, max_tokens)
    return "Erreur lors de la génération (aucun provider valide)."
"""

if old_fallback in content:
    content = content.replace(old_fallback, new_fallback)

with open('/Users/jero87/karmic.gochara/ai_interpret.py', 'w') as f:
    f.write(content)
