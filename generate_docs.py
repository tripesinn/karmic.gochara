import requests
import json
import os

def query_local_ai(prompt, system_prompt="Tu es un assistant IA expert."):
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "mlx-community/phi-4-4bit",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    
    # Clean potential markdown wrapping from the response
    if content.startswith("```markdown"):
        content = content[11:]
    if content.startswith("```md"):
        content = content[5:]
    if content.endswith("```"):
        content = content[:-3]
        
    return content.strip()

def main():
    print("Génération du fichier 1: Configuration Locale IA...")
    prompt_config = """
Rédige un fichier de documentation Markdown complet détaillant l'architecture locale d'IA mise en place sur le Mac de l'utilisateur.
Voici les informations à structurer de façon professionnelle :
- Moteur d'inférence : vllm-mlx (optimisé pour Apple Silicon)
- Modèle utilisé : mlx-community/phi-4-4bit
- Port d'écoute : 8000
- Commande de lancement (avec cache) : `~/.local/bin/vllm-mlx serve mlx-community/phi-4-4bit --prompt-cache-path ~/.cache/vllm-mlx-prompts.json`
- Exposition sur internet : `ngrok http 8000` (Génère une URL publique comme https://drinking-respect-research.ngrok-free.dev)
- Intégration IDE Antigravity : Création d'une compétence "localV1" via un plugin dans `~/.gemini/config/plugins/local-ai-plugin` et un script de pont `scripts/query_local_ai.py`.
Objectif du fichier : Permettre à une IA d'assimiler toute la configuration instantanément au début d'un nouveau chat. N'ajoute pas de blabla au début ou à la fin.
"""
    config_md = query_local_ai(prompt_config, "Tu es un Architecte Système Senior rédigeant de la documentation technique.")
    with open("LOCAL_AI_CONFIG.md", "w", encoding="utf-8") as f:
        f.write(config_md)


    print("Génération du fichier 2: Journal Karmic Gochara...")
    prompt_journal = """
Rédige une page de journal Markdown résumant l'état actuel du projet web karmicgochara.app.
Voici les faits récents :
- Hébergement : Google Cloud Run (service gochara-api).
- Stack : Backend Python (Flask), Frontend HTML/CSS Vanilla (thème astrologique dark/gold).
- Ajout récent 1 : Traduction en 6 langues de la modale "Paramètres IA", avec les fichiers JSON générés par l'IA locale (Phi-4).
- Ajout récent 2 : Correction de l'appel au modèle local depuis le cloud. Au lieu de taper "localhost", l'application permet à l'utilisateur de fournir son URL Ngrok pour que le Cloud Google interroge directement le Mac de l'utilisateur.
Objectif du fichier : Créer un "point de sauvegarde" pour qu'une IA reprenne le développement facilement. N'ajoute pas de blabla au début ou à la fin.
"""
    journal_md = query_local_ai(prompt_journal, "Tu es un Tech Lead rédigeant un fichier d'onboarding/journal pour un projet.")
    with open("KARMIC_GOCHARA_JOURNAL.md", "w", encoding="utf-8") as f:
        f.write(journal_md)


    print("Génération du fichier 3: Spécialisation Phi-4...")
    prompt_phi = """
Rédige un fichier Markdown nommé "phi4_system_prompt.md" (le titre du document). Ce fichier contiendra tes propres instructions de comportement (System Prompt) pour que tu deviennes un assistant parfaitement spécialisé pour l'utilisateur.
Éléments à inclure :
- Ton identité : IA locale rapide (Phi-4), résidant sur le Mac, appelée via Antigravity (Skill localV1).
- Ta mission principale : Aider au codage, formater des données (JSON), faire des revues rapides, traduire, sans limites de quotas.
- Ton ton : Ultra-concis, direct, professionnel, aucune phrase inutile d'introduction ou de conclusion, réponses toujours formatées en Markdown.
- Rôle spécifique : Capacité à comprendre le contexte de l'application karmicgochara.app (astrologie karmique) si nécessaire.
Objectif : Ce fichier servira à te donner tes instructions lors des prochaines itérations. N'ajoute pas de blabla, juste les instructions.
"""
    phi_md = query_local_ai(prompt_phi, "Tu es Phi-4, tu dois définir tes propres règles de fonctionnement pour être le meilleur outil d'aide au développement local.")
    with open("PHI4_SYSTEM_PROMPT.md", "w", encoding="utf-8") as f:
        f.write(phi_md)

    print("Terminé ! Fichiers créés : LOCAL_AI_CONFIG.md, KARMIC_GOCHARA_JOURNAL.md, PHI4_SYSTEM_PROMPT.md")

if __name__ == "__main__":
    main()
