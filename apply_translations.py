import json

with open("local_ai_translations.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Helper to inject keys
def inject_keys(content, lang_code, new_keys):
    # Find the dictionary for the language
    marker = f'"{lang_code}": {{'
    if marker not in content:
        print(f"Marker {marker} not found")
        return content
        
    parts = content.split(marker, 1)
    
    # We want to insert the new keys right after the marker
    lines = []
    for k, v in new_keys.items():
        v_escaped = v.replace('"', '\\"')
        lines.append(f'        "{k}": "{v_escaped}",')
        
    insertion = "\n" + "\n".join(lines)
    
    return parts[0] + marker + insertion + parts[1]

# Apply for all languages
for lang, keys in translations.items():
    content = inject_keys(content, lang, keys)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Traductions appliquées à app.py !")
