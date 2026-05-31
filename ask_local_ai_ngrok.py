
import requests


def ask_local_ai_about_ngrok():
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy"
    }
    
    prompt = """
L'utilisateur est sur macOS. Il a besoin d'installer et de configurer `ngrok` pour exposer le port 8000 (où tourne son IA locale vLLM) sur internet.
Explique-lui en 3 étapes simples, en français, comment :
1. Installer ngrok (via Homebrew)
2. Connecter son compte ngrok (avec le token d'authentification)
3. Lancer la commande pour exposer le port 8000

Sois très concis, donne juste les commandes à taper dans le terminal. Pas de blabla inutile.
"""
    
    payload = {
        "model": "Qwen3.5-9B-MLX-4bit",
        "messages": [
            {"role": "system", "content": "Tu es un ingénieur système très direct. Tu donnes uniquement les commandes exactes à exécuter, formatées en Markdown."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }
    
    print("Demande de tutoriel ngrok à l'IA locale (Qwen3.5)...\n")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        print("--- RÉPONSE DE L'IA LOCALE ---\n")
        print(content)
        print("\n------------------------------")
            
    except Exception as e:
        print(f"Erreur lors de la communication avec l'IA locale : {e}")

if __name__ == "__main__":
    ask_local_ai_about_ngrok()
