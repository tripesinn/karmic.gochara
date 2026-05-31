import json
import re

import requests


def extract_json(content):
    # 1. Try finding markdown code blocks: ```json ... ``` or ``` ... ```
    blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if blocks:
        for block in reversed(blocks):
            try:
                return json.loads(block)
            except Exception:
                pass

    # 2. Try finding any JSON block by matching braces '{' and '}'
    # We trace from the first '{' and find matching '}' using a brace counter
    for i in range(len(content)):
        if content[i] == '{':
            brace_count = 0
            in_string = False
            escape = False
            for j in range(i, len(content)):
                char = content[j]
                if char == '\\' and in_string:
                    escape = not escape
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                escape = False
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            candidate = content[i:j+1]
                            try:
                                return json.loads(candidate)
                            except Exception:
                                break # try next outer brace or next '{'

    # 3. Fallback to simple first { and last }
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1:
        try:
            return json.loads(content[start_idx:end_idx+1])
        except Exception:
            pass

    raise ValueError("Could not extract valid JSON from response")

def get_translations_from_local_ai():
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy"
    }
    
    prompt = """
Tu es un traducteur expert. Traduis le dictionnaire suivant en Anglais (en), Espagnol (es), Portugais (pt), Allemand (de), Néerlandais (nl), et Italien (it).
Renvoie UNIQUEMENT un objet JSON valide, avec les codes de langue comme clés principales, et les clés de traduction à l'intérieur. Pas de texte avant ou après.

Dictionnaire français original :
{
  "ai_settings_title": "Paramètres IA (Optionnel)",
  "ai_settings_desc": "Utilise ta propre clé API pour des calculs illimités sans restriction de quota.",
  "ai_provider": "Provider (Fournisseur)",
  "ai_provider_default": "Défaut serveur",
  "ai_provider_local": "Serveur Local",
  "ai_api_key": "Clé API",
  "ai_model_pref": "Modèle Préféré"
}
"""
    
    payload = {
        "model": "Qwen3.5-9B-MLX-4bit",
        "messages": [
            {"role": "system", "content": "You are a precise JSON translation machine. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    
    print("Demande de traduction à l'IA locale (Qwen3.5)...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # Extraction robuste du JSON (élimine le Thinking Process ou les blocs markdown)
        translations = extract_json(content)
        
        print("\n--- TRADUCTIONS GÉNÉRÉES PAR L'IA LOCALE ---\n")
        print(json.dumps(translations, indent=2, ensure_ascii=False))
        
        # Sauvegarde dans un fichier pour qu'Antigravity puisse les lire
        with open("local_ai_translations.json", "w", encoding="utf-8") as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        print("\nTraductions sauvegardées dans local_ai_translations.json")
            
    except Exception as e:
        print(f"Erreur lors de la communication avec l'IA locale : {e}")
        if 'content' in locals():
            print("\n--- RAW LLM RESPONSE CONTENT ---")
            print(content)
            print("--------------------------------")

if __name__ == "__main__":
    get_translations_from_local_ai()
