import sys
import requests

# ── Configuration ──────────────────────────────────────────
LOCAL_AI_URL  = "http://127.0.0.1:8888/v1/chat/completions"
LOCAL_AI_AUTH = "Bearer omlx_12345678910111213abcDEF"

# Modèle léger quantisé — tient en mémoire malgré les limites
# Remplace l'ancien unsloth--gemma-4-E4B (4B params, trop lourd)
LOCAL_AI_MODEL = "gemma-4-E2B-it-qat-oQ4-fp16"

# Séquence de repli sur OOM (507) : réduit les tokens
MAX_TOKENS_STEPS = [1024, 512, 256]
# ───────────────────────────────────────────────────────────


def query_local_ai(prompt: str, system: str = "") -> str:
    """
    Envoie un prompt à l'IA locale (oMLX, port 8888).
    Retente automatiquement avec moins de tokens si OOM (507).

    Args:
        prompt : Message utilisateur.
        system : Prompt système optionnel (défaut : vide).

    Returns:
        Texte de réponse de l'IA.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": LOCAL_AI_AUTH,
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    last_error = None
    for max_tokens in MAX_TOKENS_STEPS:
        payload = {
            "model": LOCAL_AI_MODEL,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(
                LOCAL_AI_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )
            if resp.status_code == 507:
                # Mémoire insuffisante → retente avec moins de tokens
                last_error = f"507 OOM (max_tokens={max_tokens})"
                print(
                    f"[localAI] ⚠️  507 OOM — retry avec {max_tokens // 2} tokens",
                    file=sys.stderr,
                )
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            last_error = "timeout (120s)"
            break
        except requests.exceptions.ConnectionError:
            last_error = "connexion refusée — oMLX démarré ?"
            break
        except Exception as exc:
            last_error = str(exc)
            break

    raise RuntimeError(f"IA locale indisponible : {last_error}")


if __name__ == "__main__":
    # Usage :
    #   python query_local_ai.py "mon prompt"
    #   python query_local_ai.py "mon prompt" "system prompt optionnel"
    if len(sys.argv) < 2:
        print(
            "Usage: python query_local_ai.py \"<prompt>\" [\"<system>\"]",
            file=sys.stderr,
        )
        sys.exit(1)

    user_prompt = sys.argv[1]
    system_prompt = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        result = query_local_ai(user_prompt, system_prompt)
        print(result)
    except RuntimeError as err:
        print(f"Erreur : {err}", file=sys.stderr)
        sys.exit(1)
