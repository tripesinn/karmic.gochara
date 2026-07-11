import os
import shutil
import sys

import requests


def apply_local_ai(file_path, instruction):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    # Read the original file content
    with open(file_path, encoding='utf-8') as f:
        original_content = f.read()
        
    url = "http://127.0.0.1:8889/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer omlx_12345678910111213abcDEF"
    }
    
    system_prompt = (
        "Tu es un agent d'écriture automatique de code de niveau Sénior.\n"
        "Ton but est de modifier ou corriger le code fourni selon les instructions de l'utilisateur.\n"
        "Règles CRITIQUES :\n"
        "1. Ne fournis AUCUNE explication, AUCUN texte d'introduction ou de conclusion.\n"
        "2. Retourne UNIQUEMENT le code complet, corrigé et prêt à être écrit directement dans le fichier.\n"
        "3. N'utilise PAS de blocs de code markdown (comme ```python et ```) pour envelopper le code. Retourne le code sous forme de texte brut."
    )
    
    user_prompt = f"Fichier original :\n```\n{original_content}\n```\n\nInstructions de modification :\n{instruction}"
    
    payload = {
        "model": "gemma-4-E2B-it-qat-oQ4-fp16",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,  # Low temperature for highly deterministic code generation
        "max_tokens": 4096
    }
    
    print(f"Refactorisation de '{os.path.basename(file_path)}' en cours par l'IA locale (Phi-4)...")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # Clean up code block formatting if the model didn't follow instructions perfectly
        clean_content = content.strip()
        if clean_content.startswith("```"):
            lines = clean_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_content = "\n".join(lines).strip()
            
        # Create a backup of the original file
        backup_path = file_path + ".bak"
        shutil.copy2(file_path, backup_path)
        print(f"-> Sauvegarde de sécurité créée : {os.path.basename(backup_path)}")
        
        # Write the new content to the original file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
            
        print(f"[OK] Le fichier '{os.path.basename(file_path)}' a été modifié de manière effective !")
        
    except Exception as e:
        print(f"Error querying local AI: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python apply_local_ai.py <file_path> \"<instruction>\"", file=sys.stderr)
        sys.exit(1)
        
    target_file = sys.argv[1]
    instructions = sys.argv[2]
    apply_local_ai(target_file, instructions)
