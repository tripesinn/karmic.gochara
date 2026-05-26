with open('/Users/jero87/karmic.gochara/ai_interpret.py', 'r') as f:
    content = f.read()

# For get_hook_natal
old_natal = '    user_model = user.get("user_model") if user else None\n    user_with_model = {**(user or {}), "user_model": user_model or HOOK_MODEL}'
new_natal = '    # Force le modèle et le provider du serveur pour le hook, car il doit être rapide et précis\n    user_with_model = {**(user or {}), "user_provider": None, "user_key": None, "user_model": HOOK_MODEL}'
content = content.replace(old_natal, new_natal)

# For get_hook_transit
old_transit = '    user_model = user.get("user_model") if user else None\n    user_with_model = {**(user or {}), "user_model": user_model or HOOK_MODEL}'
new_transit = '    # Force le modèle et le provider du serveur pour le hook transit\n    user_with_model = {**(user or {}), "user_provider": None, "user_key": None, "user_model": HOOK_MODEL}'
content = content.replace(old_transit, new_transit)

with open('/Users/jero87/karmic.gochara/ai_interpret.py', 'w') as f:
    f.write(content)
