#!/usr/bin/env python3
"""
Gemma Batch Runner — exécute les 6 prompts boilerplate Astro
automatiquement via l'API OpenAI-compatible de Gemma locale.

Usage:
  python3 run_gemma_batch.py              # Exécute tous les prompts
  python3 run_gemma_batch.py --prompt 1   # Un seul prompt
  python3 run_gemma_batch.py --dry-run    # Affiche les prompts sans exécuter

Prérequis :
  - Serveur oMLX tournant sur 127.0.0.1:8888 (gemma-4-E4B)
  - curl disponible
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
GEMMA_API = "http://127.0.0.1:8888/v1/chat/completions"
GEMMA_API_KEY = "omlx_12345678910111213abcDEF"
ASTRO_DIR = Path.home() / "karmic.gochara/astro"
PROMPTS_FILE = Path.home() / "karmic.gochara/.hermes/prompts/GEMMA-BATCH-SESSION-1.md"
LOG_FILE = Path.home() / "karmic.gochara/.hermes/gemma_batch_log.json"
MODEL = "unsloth--gemma-4-E4B-it-UD-MLX-4bit"
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds

# ── Prompt → Fichier mapping ────────────────────────────────────────
# Les prompts sont extraits du fichier markdown par parsing
# Les fichiers générés sont déduits du contenu de la réponse

PROMPT_TITLES = {
    1: "BaseLayout.astro + global.css",
    2: "tailwind.config.mjs + astro.config.mjs",
    3: "index.astro + 404.astro",
    4: "types.ts + env.d.ts",
    5: "HeroSection.astro + LoginCardLayout.astro",
    6: "package.json + .env.example",
}

# ── Helpers ─────────────────────────────────────────────────────────

def parse_prompts_from_md(path: Path) -> list[dict]:
    """Extrait les prompts du fichier markdown structuré."""
    content = path.read_text()
    prompts = []
    current_title = ""
    current_text = []
    in_prompt = False
    
    for line in content.split("\n"):
        if line.startswith("## Prompt "):
            if current_text:
                prompts.append({
                    "title": current_title,
                    "text": "\n".join(current_text).strip()
                })
            current_title = line.strip("## ").strip()
            current_text = []
            in_prompt = True
        elif line.startswith("---") or line.startswith("## 📋") or line.startswith("## 📝"):
            if current_text:
                prompts.append({
                    "title": current_title,
                    "text": "\n".join(current_text).strip()
                })
            current_text = []
            in_prompt = False
        elif in_prompt:
            current_text.append(line)
    
    if current_text:
        prompts.append({
            "title": current_title,
            "text": "\n".join(current_text).strip()
        })
    
    return prompts


def call_gemma(prompt_text: str, timeout: int = 300) -> str:
    """Appelle Gemma via API OpenAI-compatible. Retourne le texte de réponse."""
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Tu génères du code Astro + TypeScript + Python. "
                           "Réponds UNIQUEMENT avec les fichiers demandés, "
                           "séparés par des séparateurs markdown. "
                           "Pas d'explications, pas de bavardage."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
        "stream": False
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(
                ["curl", "-s", "-X", "POST", GEMMA_API,
                 "-H", "Content-Type: application/json",
                 "-H", f"Authorization: Bearer {GEMMA_API_KEY}",
                 "-d", json.dumps(payload)],
                capture_output=True, text=True, timeout=timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"curl failed: {result.stderr}")
            
            response = json.loads(result.stdout)
            
            if "choices" not in response or not response["choices"]:
                raise RuntimeError(f"Unexpected response: {response}")
            
            content = response["choices"][0]["message"]["content"]
            return content
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, RuntimeError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️ Tentative {attempt+1} échouée: {e}. Nouvel essai dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                raise
        
    raise RuntimeError("Toutes les tentatives ont échoué")


def extract_files_from_response(response: str, prompt_num=None):
    """Extrait les fichiers des blocs de code Gemma.
    
    Stratégie : repère les blocs ```...```, court le chemin depuis
    les commentaires // ou # en début de bloc, ou depuis le nom de section.
    """
    files = []
    lines = response.split("\n")
    
    in_code = False
    current_lang = ""
    current_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                current_lang = stripped[3:].strip()
                current_lines = []
            else:
                in_code = False
                # Analyse du bloc
                if current_lines:
                    content = "\n".join(current_lines)
                    filepath = infer_filepath(current_lines, current_lang, prompt_num)
                    if filepath:
                        files.append({
                            "path": filepath,
                            "language": current_lang,
                            "content": content
                        })
                current_lines = []
        elif in_code:
            current_lines.append(line)
    
    return files


def infer_filepath(lines: list, lang: str, prompt_num=None):
    """Infère le chemin d'un fichier depuis les commentaires du code."""
    
    # 1. Chercher // src/... ou # src/... ou /* src/... en début de bloc
    for line in lines[:5]:
        stripped = line.strip()
        # typescript: // src/path/to/file.ts
        if stripped.startswith("// "):
            path = stripped[3:].strip()
            if "/" in path and "." in path:
                return path
        # python/bash: # src/path/to/file.py  
        if stripped.startswith("# "):
            path = stripped[2:].strip()
            if "/" in path and "." in path:
                return path
        # CSS: /* src/path/to/file.css */ ou /* src/path */
        if stripped.startswith("/* ") and stripped.endswith(" */"):
            path = stripped[3:-3].strip()
            if "/" in path and "." in path:
                return path
        if stripped.startswith("/* "):
            path = stripped[3:].strip().rstrip("*/").strip()
            if "/" in path and "." in path:
                return path
        # Just a bare path
        if stripped.startswith("src/") or stripped.startswith("astro/") or \
           stripped.startswith("tailwind") or stripped.startswith("astro.config") or \
           stripped.startswith("package.json") or stripped.startswith(".env") or \
           stripped.startswith("tsconfig"):
            return stripped.strip("`*:")
    
    # 2. Fallback : nommer par ordre si on connaît le prompt
    file_map = {
        1: ["src/layouts/BaseLayout.astro", "src/styles/global.css"],
        2: ["tailwind.config.mjs", "astro.config.mjs"],
        3: ["src/pages/index.astro", "src/pages/404.astro"],
        4: ["src/types.ts", "src/env.d.ts"],
        5: ["src/components/HeroSection.astro", "src/components/LoginCardLayout.astro"],
        6: ["package.json", ".env.example"],
    }
    
    if prompt_num and prompt_num in file_map:
        # Count how many files we've seen so far in this prompt (global counter)
        # This is a simplification — we assume order matches
        pass  # Will be handled by caller
    
    return None


def save_generated_files(files: list[dict]):
    """Sauvegarde chaque fichier généré dans le bon répertoire."""
    saved = []
    for f in files:
        path = ASTRO_DIR / f["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.exists():
            # Backup existing file
            backup = path.with_suffix(path.suffix + ".bak")
            path.rename(backup)
        
        path.write_text(f["content"])
        saved.append(str(path.relative_to(ASTRO_DIR.parent)))
    
    return saved


def check_gemma_server() -> bool:
    """Vérifie que le serveur Gemma répond."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-H", f"Authorization: Bearer {GEMMA_API_KEY}",
             "http://127.0.0.1:8888/v1/models"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout == "200"
    except:
        pass
    
    # Fallback: essayer models endpoint
    try:
        result = subprocess.run(
            ["curl", "-s", GEMMA_API.replace("/chat/completions", "/models")],
            capture_output=True, text=True, timeout=5
        )
        return "gemma" in result.stdout.lower()
    except:
        return False


def log_progress(prompt_num: int, title: str, status: str, detail: str = ""):
    """Log l'avancement dans un fichier JSON."""
    log = {}
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
    
    log[f"prompt_{prompt_num}"] = {
        "title": title,
        "status": status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "detail": detail
    }
    log["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, indent=2))


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("✦  GEMMA BATCH RUNNER  ✦")
    print("=" * 60)
    
    # Parse args
    single_prompt = None
    dry_run = False
    for arg in sys.argv[1:]:
        if arg.startswith("--prompt="):
            single_prompt = int(arg.split("=")[1])
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--help":
            print("Usage: python3 run_gemma_batch.py [--prompt=N] [--dry-run]")
            return 0
    
    # Check server
    print("\n🔍 Vérification du serveur Gemma...")
    if not check_gemma_server():
        print("❌ Serveur Gemma (127.0.0.1:8888) ne répond pas.")
        print("   Lance d'abord : ssh ... ou démarre le serveur local")
        return 1
    print("✅ Serveur OK")
    
    # Parse prompts
    print("\n📋 Parsing des prompts...")
    prompts = parse_prompts_from_md(PROMPTS_FILE)
    print(f"   → {len(prompts)} prompts trouvés")
    
    if single_prompt:
        if single_prompt < 1 or single_prompt > len(prompts):
            print(f"❌ Prompt {single_prompt} invalide. Prompts disponibles: 1-{len(prompts)}")
            return 1
        prompts = [prompts[single_prompt - 1]]
    
    if dry_run:
        print("\n🏃 DRY RUN — Prompts à exécuter :")
        for i, p in enumerate(prompts, 1):
            title = p["title"][:60]
            chars = len(p["text"])
            print(f"   {i}. {title} ({chars} chars)")
        return 0
    
    # Execute each prompt
    total = len(prompts)
    successes = 0
    
    for i, prompt in enumerate(prompts, 1):
        num = single_prompt or i
        title = prompt["title"]
        print(f"\n{'='*50}")
        print(f"📝 Prompt {num}/{total}: {title}")
        print(f"{'='*50}")
        
        log_progress(num, title, "running", "Envoi à Gemma...")
        
        try:
            print("   ⏳ Appel Gemma (temps max 5 min)...")
            start = time.time()
            response = call_gemma(prompt["text"])
            elapsed = time.time() - start
            print(f"   ✅ Réponse reçue ({elapsed:.0f}s, {len(response)} chars)")
            
            # Sauvegarder la réponse raw
            raw_dir = ASTRO_DIR / ".gemma_raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_path = raw_dir / f"prompt_{num}_response.md"
            raw_path.write_text(response)
            print(f"   💾 Réponse sauvegardée: {raw_path}")
            
            # Extraire et sauvegarder les fichiers
            files = extract_files_from_response(response, prompt_num=num)
            if files:
                saved = save_generated_files(files)
                if saved:
                    print("   📂 Fichiers créés:")
                    for s in saved:
                        print(f"      ✓ {s}")
                else:
                    print("   ⚠️ Aucun fichier extrait de la réponse")
            else:
                print("   ⚠️ Parsing échoué — sauvegardé raw pour review manuelle")
            
            log_progress(num, title, "success", f"{elapsed:.0f}s, {len(response)} chars")
            successes += 1
            
            # Pause entre les prompts pour laisser la RAM refroidir
            if i < total:
                pause = min(30, 10 + i * 5)
                print(f"\n   ⏸️  Pause {pause}s avant prochain prompt (RAM)...")
                time.sleep(pause)
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            log_progress(num, title, "error", str(e))
    
    # Summary
    print(f"\n{'='*60}")
    if successes == total:
        print(f"✅ Batch terminé: {successes}/{total} prompts réussis")
        print(f"📂 Fichiers dans {ASTRO_DIR}")
        print(f"📝 Log: {LOG_FILE}")
        print("\nProchaine étape: revue Hermes pour valider les fichiers")
    else:
        print(f"⚠️ Batch partiel: {successes}/{total} prompts réussis")
        print(f"   Consulte le log pour les erreurs: {LOG_FILE}")
    
    return 0 if successes == total else 1


if __name__ == "__main__":
    sys.exit(main())
