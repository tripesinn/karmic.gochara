"""
blueprints/chat.py — Chatbot endpoints : statut, question, résumé
"""
from flask import Blueprint, current_app, jsonify, request, session

from app_common import UNLIMITED_PSEUDOS, _enrich_profile_with_natal

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/chat")


@chat_bp.route("/status", methods=["GET"])
def chat_status():
    """Retourne le plan et le quota chatbot restant pour l'utilisateur connecté."""
    from profiles import get_chat_quota
    profile = session.get("profile")
    if not profile:
        return jsonify({"plan": "free", "remaining": 0, "limit": 0})
    pseudo = profile.get("pseudo", "")
    if pseudo.lower() in UNLIMITED_PSEUDOS:
        return jsonify({"plan": "subscription", "remaining": 999, "limit": 999})
    return jsonify(get_chat_quota(pseudo))


@chat_bp.route("/ask", methods=["POST"])
def chat_ask():
    """
    Valide le quota chatbot, consomme 1 question si plan test,
    et retourne {system, user} pour que Gemma génère la réponse localement.

    Body JSON :
        message : str       — question de l'utilisateur
        history : list      — [{role, content}, ...] (derniers échanges)
    """
    from ai_interpret import build_prompt_chat
    from profiles import consume_chat_question

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    data    = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])
    local   = bool(data.get("local", False))
    lang    = session.get("lang", "fr")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    pseudo = profile.get("pseudo", "")

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    if pseudo.lower() not in UNLIMITED_PSEUDOS and not user_key:
        result = consume_chat_question(pseudo, local=local)
        if not result["ok"]:
            return jsonify({"error": "quota_exceeded",
                            "message": "Tu as utilisé toutes tes questions chatbot.",
                            "upgrade_url": "/stripe/checkout?product=subscription"}), 429
        remaining = result["remaining"]
    else:
        remaining = -1

    enriched = _enrich_profile_with_natal(profile, {})

    if user_key:
        enriched["user_key"] = user_key
    if user_model:
        enriched["user_model"] = user_model
    if user_provider:
        enriched["user_provider"] = user_provider

    prompts  = build_prompt_chat(message, history, enriched, lang=lang)

    if local:
        return jsonify({
            "ok":        True,
            "system":    prompts["system"],
            "user":      prompts["user"],
            "remaining": remaining,
        })

    # Génération AI côté serveur
    from ai_interpret import generate_ai
    try:
        answer = generate_ai(prompts["system"], prompts["user"], user=enriched, max_tokens=1024).strip()

        # Sauvegarde asynchrone dans RAG
        if pseudo:
            import threading

            from rag_memory import save_reading
            content_to_save = f"User: {message}\nAssistant: {answer}"
            threading.Thread(target=save_reading, args=(pseudo, content_to_save, "chat")).start()

    except Exception as e:
        current_app.logger.error("Chat AI error: %s", e)
        return jsonify({"error": "generation_failed", "message": str(e)}), 500

    return jsonify({
        "ok":        True,
        "answer":    answer,
        "remaining": remaining,
    })


@chat_bp.route("/summarize", methods=["POST"])
def summarize_chat():
    """
    Crée un résumé d'une conversation pour la sauvegarde locale.
    Réservé au plan "illimite".
    (Route original: /summarize_chat → migrée vers /chat/summarize)
    """
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    # Normalise le nom du plan pour la vérification
    plan = (profile.get("plan", "free") or "free").lower().replace("é", "e")
    if plan != "illimite":
        return jsonify({"ok": False, "error": "Fonctionnalité réservée au plan Illimité"}), 403

    data    = request.get_json() or {}
    history = data.get("history", [])
    if not history:
        return jsonify({"ok": False, "error": "Historique de chat vide"}), 400

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    enriched = {
        "user_key": user_key,
        "user_model": user_model,
        "user_provider": user_provider
    }

    lang = session.get("lang", "fr")
    # Construit une version texte simple de l'historique
    transcript = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    if lang == "fr":
        system_prompt = (
            "Tu es un expert en synthèse. Résume la conversation suivante en une seule phrase (15-20 mots max). "
            "Ce résumé servira de contexte pour une future conversation. "
            "Capture l'intention principale et les thèmes clés de manière concise."
        )
        user_prompt = f"Voici la conversation à résumer :\n\n{transcript}"
    else:
        system_prompt = (
            "You are a synthesis expert. Summarize the following conversation in a single sentence (15-20 words max). "
            "This summary will be used as context for a future conversation. "
            "Capture the main intent and key themes concisely."
        )
        user_prompt = f"Here is the conversation to summarize:\n\n{transcript}"

    try:
        from ai_interpret import generate_ai
        summary = generate_ai(system_prompt, user_prompt, user=enriched, max_tokens=100)
        return jsonify({"ok": True, "summary": summary.strip()})
    except Exception as exc:
        current_app.logger.error("Erreur summarize_chat : %s", exc)
        return jsonify({"ok": False, "error": "Erreur lors de la génération du résumé"}), 500
