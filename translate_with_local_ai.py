import requests
import json

def get_translations_from_local_ai():
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
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
        "model": "mlx-community/phi-4-4bit",
        "messages": [
            {"role": "system", "content": "You are a precise JSON translation machine. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    print("Demande de traduction à l'IA locale (phi-4)...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # Nettoyage si l'IA ajoute des balises markdown
        content = content.replace("```json", "").replace("```", "").strip()
        
        translations = json.loads(content)
        print("\n--- TRADUCTIONS GÉNÉRÉES PAR L'IA LOCALE ---\n")
        print(json.dumps(translations, indent=2, ensure_ascii=False))
        
        # Sauvegarde dans un fichier pour qu'Antigravity puisse les lire
        with open("local_ai_translations.json", "w", encoding="utf-8") as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        print("\nTraductions sauvegardées dans local_ai_translations.json")
            
    except Exception as e:
        print(f"Erreur lors de la communication avec l'IA locale : {e}")

if __name__ == "__main__":
    get_translations_from_local_ai()
