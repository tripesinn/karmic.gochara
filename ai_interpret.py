"""
ai_interpret.py — Gochara Karmique [FIXED]
Intelligence siderealAstro13 | Astrologie védique sidérale (Chandra Lagna)
Doctrine centralisée dans doctrine.py — ce fichier ne contient que la logique d'appel API.

Vault Karpathy (karmic_vault/) injecté dans _build_system_prompt().
Fallback automatique vers doctrine.py si vault absent.

Hooks :
  get_hook_natal(user)              → 3-4 phrases dès le login (natal seul)
  get_hook_transit(chart_data, user)→ 3-4 phrases dès la date choisie (aspects du jour)
  get_synthesis(chart_data, user)   → synthèse complète ~4000 tokens (payant)
  build_prompt_only(chart_data, user) → prompt Gemma sans appel API
"""

import json
import os
import threading

import requests

import gemini_api
from astro_calc import NAKSHATRA_LORDS, NAKSHATRAS
from rag_memory import retrieve_context, save_reading

# ── Router Multi-Provider ────────────────────────────────────────────────────
_SERVER_ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_SERVER_GROK_KEY = os.environ.get("GROK_API_KEY", "")

import re
import time

_GROK_MODEL_CACHE = {
    "model": None,
    "last_fetched": 0
}

def _get_grok_model() -> str:
    """
    Délivre dynamiquement le meilleur modèle Grok disponible.
    Priorise GROK_MODEL de l'environnement s'il est spécifié.
    Sinon, interroge l'API x.ai pour lister les modèles et sélectionne le plus récent (avec cache de 12 heures).
    En cas de problème, fallback sur 'grok-4.3'.
    """
    env_model = os.environ.get("GROK_MODEL", "").strip()
    if env_model and env_model != "auto":
        return env_model

    now = time.time()
    if _GROK_MODEL_CACHE["model"] and (now - _GROK_MODEL_CACHE["last_fetched"] < 43200):
        return _GROK_MODEL_CACHE["model"]

    default_fallback = "grok-4.3"
    api_key = _SERVER_GROK_KEY or os.environ.get("GROK_API_KEY", "")
    if not api_key:
        return default_fallback

    try:
        url = "https://api.x.ai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            models_data = r.json().get("data", [])
            valid_models = []
            for m in models_data:
                model_id = m.get("id", "")
                is_reasoning = "reasoning" in model_id and "non-reasoning" not in model_id
                if (model_id.startswith("grok-") and 
                    "imagine" not in model_id and 
                    "build" not in model_id and 
                    "multi-agent" not in model_id and 
                    not is_reasoning):
                    valid_models.append(model_id)

            if valid_models:
                def model_sort_key(name):
                    numbers = re.findall(r'\d+', name)
                    return [int(num) for num in numbers] if numbers else [0]

                valid_models.sort(key=model_sort_key)
                best_model = valid_models[-1]
                
                _GROK_MODEL_CACHE["model"] = best_model
                _GROK_MODEL_CACHE["last_fetched"] = now
                print(f"[GROK AUTO-ROUTING] Dynamic search selected: {best_model} (Available: {valid_models})", flush=True)
                return best_model
    except Exception as e:
        print(f"[GROK AUTO-ROUTING] Error fetching dynamic model, fallback to {default_fallback}: {e}", flush=True)

    _GROK_MODEL_CACHE["model"] = default_fallback
    _GROK_MODEL_CACHE["last_fetched"] = now
    return default_fallback


def _call_grok(system: str, prompt: str, model: str, api_key: str, max_tokens: int) -> str:
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or "grok-beta",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _call_claude(system: str, prompt: str, model: str, api_key: str, max_tokens: int) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": model or "claude-3-5-sonnet-latest",
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def _enforce_plan_provider(user: dict):
    """Enforce provider routing based on plan or custom user settings."""
    cust_prov = user.get("user_provider")
    cust_key = user.get("user_key")
    cust_model = user.get("user_model")
    
    # Si l'utilisateur a configuré son propre fournisseur
    if cust_prov:
        if cust_prov == "local" or cust_key:
            return cust_prov, cust_key or "dummy", cust_model or "phi-4-4bit"

    plan = user.get("plan", "free").lower().replace("é", "e")
    if plan in ("illimite", "subscription", "pro", "test", "lecture", "essential"):
        return "local", "dummy", "phi-4-4bit"
    else:
        return "grok", _SERVER_GROK_KEY, _get_grok_model()


def generate_ai(system: str, prompt: str, user: dict, max_tokens: int = 1024) -> str:
    """Route la requête vers le provider choisi par l'utilisateur."""
    provider, user_key, model = _enforce_plan_provider(user)

    # Si pas de provider, ou si on a un provider externe mais pas de clé
    if not provider or (not user_key and provider not in ["local", "claude", "gemini"]):
        if model and model.startswith("claude") and _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, model, _SERVER_ANTHROPIC_KEY, max_tokens)
        if model and model.startswith("grok") and _SERVER_GROK_KEY:
            return _call_grok(system, prompt, model, _SERVER_GROK_KEY, max_tokens)
        # Fallback sur Gemini sans modèle custom pour éviter un 404
        return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=None, user_key=user_key)

    try:
        if provider == "gemini":
            gemini_model = model if model and not model.startswith("claude") else None
            return gemini_api.generate(system, prompt, max_tokens=max_tokens, model=gemini_model, user_key=user_key)

        elif provider == "claude":
            return _call_claude(system, prompt, model or "claude-3-5-sonnet-latest", user_key, max_tokens)
            
        elif provider == "grok":
            return _call_grok(system, prompt, model or "grok-4.3", user_key, max_tokens)
            
        elif provider == "local":
            url = "http://127.0.0.1:8000/v1/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }
            if user_key:
                user_key = user_key.strip()
                if user_key.startswith("http"):
                    url = f"{user_key.rstrip('/')}/chat/completions"
                    headers["Authorization"] = "Bearer dummy"
                else:
                    headers["Authorization"] = f"Bearer {user_key}"
            
            # oMLX multi-model : le nom du modèle dans le répertoire ~/.omlx/models/
            local_model = "phi-4-4bit"
            if model and not (model.startswith("claude") or model.startswith("gemini")):
                local_model = model
                
            payload = {
                "model": local_model,
                "messages": [
                    {"role": "system", "content": system + "\n\nCRITICAL: Never repeat the same phrase or sentence twice. If you have nothing new to say, finish your response immediately."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "frequency_penalty": 0.5,
                "presence_penalty": 0.5
            }
            print("--- DEBUG VLLM ---", flush=True)
            print(f"URL VLLM: {url}", flush=True)
            print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}", flush=True)
            print("------------------", flush=True)
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
            
        elif provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {user_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model or "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens
            }
            r = requests.post(url, headers=headers, json=payload, timeout=90)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
            
        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {user_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://karmicgochara.app",
                "X-Title": "Karmic Gochara"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens
            }
            r = requests.post(url, headers=headers, json=payload, timeout=90)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
            
    except Exception as e:
        print(f"Erreur provider {provider}: {e}")
        # Si c'est l'IA locale ou un fournisseur personnalisé de l'utilisateur qui a échoué,
        # on ne fait PAS de repli sur l'API payante du serveur afin de protéger les quotas de facturation !
        if provider == "local":
            return (
                "✦ **Impossible de se connecter à votre IA Locale (MLX).**\n\n"
                "Pour corriger cela :\n"
                "1. Assurez-vous que votre serveur local MLX est bien démarré sur votre machine (port 8888).\n"
                "2. Si vous êtes sur le Web Cloud (karmicgochara.app), configurez votre URL de tunnel public ngrok dans les Paramètres (rouage en haut à droite).\n"
                "3. Vous pouvez également sélectionner un autre fournisseur (Gemini, Claude, Groq) dans les Paramètres et renseigner votre propre clé d'API personnelle pour utiliser vos propres jetons (tokens).\n\n"
                "👉 **Nouveau :** Besoin d'aide pour choisir le meilleur moteur ? [Consulter le Comparatif des IA 📊](#open-benchmark)"
            )
        
        # Si c'est un fournisseur tiers individuel configuré par l'utilisateur
        if user.get("user_provider"):
            return f"✦ Erreur avec votre fournisseur d'IA personnel ({provider}) : {str(e)}\n\nVeuillez vérifier vos clés API et quotas de facturation dans les Paramètres (rouage)."

        # Fallback de secours uniquement pour le serveur par défaut (ex: Freemium)
        if _SERVER_GROK_KEY:
            try:
                return _call_grok(system, prompt, _get_grok_model(), _SERVER_GROK_KEY, max_tokens)
            except Exception as e2:
                print(f"Fallback Grok échoué : {e2}")
        if _SERVER_ANTHROPIC_KEY:
            try:
                return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
            except Exception as e2:
                print(f"Fallback Claude échoué : {e2}")
        return "Erreur lors de la génération (serveur non configuré)."
        
    # Provider inconnu et pas de configuration personnalisée -> serveur par défaut (Freemium)
    if not user.get("user_provider"):
        if _SERVER_GROK_KEY:
            return _call_grok(system, prompt, _get_grok_model(), _SERVER_GROK_KEY, max_tokens)
        elif _SERVER_ANTHROPIC_KEY:
            return _call_claude(system, prompt, "claude-3-5-sonnet-latest", _SERVER_ANTHROPIC_KEY, max_tokens)
    return "Erreur de configuration (fournisseur inconnu)."
    return "Erreur lors de la génération (aucun provider valide)."



def stream_ai(system: str, prompt: str, user: dict, max_tokens: int = 1024):
    """Route la requête stream vers le provider. 
    Pour Gemini (avec clé), on utilise le vrai stream SSE. 
    Pour les autres (y compris Grok par défaut), on fait un appel bloquant puis on yield des mots pour simuler le stream."""
    provider, user_key, model = _enforce_plan_provider(user)

    # Si l'utilisateur a explicitement configuré Gemini avec sa propre clé
    if provider == "gemini" and user_key:
        for chunk in gemini_api.stream(system, prompt, max_tokens=max_tokens, model=model, user_key=user_key):
            yield chunk
        return

    # Pour tous les autres cas (Serveur par défaut Grok/Claude, VLLM local, Groq, OpenRouter), 
    # on utilise generate_ai() qui gère déjà parfaitement le routage et les fallbacks.
    try:
        full_text = generate_ai(system, prompt, user=user, max_tokens=max_tokens)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
    except Exception as e:
        yield f"[ERROR] {str(e)}"

# ── Import doctrine centralisée ───────────────────────────────────────────────
from doctrine import (
    NAKSHATRA_KARMA,
    NODAL_CYCLES,
    _detect_friction_axis,
    get_system_prompt,
)

# ══════════════════════════════════════════════════════════════════════════════
# VAULT KARPATHY — chargement des fichiers Markdown doctrinaux
# ══════════════════════════════════════════════════════════════════════════════

_VAULT_DIR = os.path.join(os.path.dirname(__file__), "karmic_vault")


def _load_vault(include_keywords: bool = True) -> str | None:
    """
    Charge le vault doctrinal Markdown compressé (~800-1300 tokens).
    Fallback silencieux vers doctrine.get_system_prompt() si vault absent.
    include_keywords=False → 00 + 01 seulement (hooks, budget réduit).
    """
    try:
        master = open(os.path.join(_VAULT_DIR, "00_MASTER_CONTEXT.md"), encoding="utf-8").read()
        rules  = open(os.path.join(_VAULT_DIR, "01_output_rules.md"),   encoding="utf-8").read()
        vault  = master + "\n\n---\n\n" + rules
        if include_keywords:
            kw_path = os.path.join(_VAULT_DIR, "02_planet_keywords.md")
            if os.path.exists(kw_path):
                vault += "\n\n---\n\n" + open(kw_path, encoding="utf-8").read()
        import logging
        logging.getLogger(__name__).info("VAULT chargé — %d tokens estimés", len(vault.split()))

        return vault
    except FileNotFoundError:
        return None


# ── Configuration Gemini ──────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
# MODEL ASSIGNMENT — Router par cas d'usage
# ══════════════════════════════════════════════════════════════════════════════
HOOK_MODEL = os.environ.get("HOOK_MODEL", "grok-beta")        # Hook gratuit — rapide, cheap
SYNTHESIS_MODEL = os.environ.get("SYNTHESIS_MODEL", "claude-3-opus-latest")     # Synthèse payante — meilleure qualité doctrinal

# ══════════════════════════════════════════════════════════════════════════════
# HOOK PROMPTS — Mirror → Wound → Friction → Open Door
# ══════════════════════════════════════════════════════════════════════════════

HOOK_PROMPT_FR = """Tu ES @siderealAstro13. Génère un hook de 4 phrases EXACTEMENT.

Structure obligatoire :
1. MIROIR : Ce que {name} vit concrètement EN CE MOMENT — comportement reconnaissable, pas de jargon astro.
2. BLESSURE : Ce que cette période réveille dans sa blessure profonde — sensation, pas mécanique.
3. FRICTION : Ce que la période rend insupportable ou répétitif — l'endroit qui frotte le plus.
4. PORTE OUVERTE : Révèle l'Alternative de Conscience.
   La phrase doit être complète et donner une clé de compréhension concrète.
   Format : "Ce que tu dois comprendre sur [thème central], c'est..." et tu termines la phrase.

RÈGLES ABSOLUES :
- 4 phrases. Pas 3. Pas 5.
- Tutoiement direct.
- Zéro jargon astro (pas de "ton Ketu", "ta Porte Invisible", "ton Chiron").
- La phrase 4 CONCLUT. Elle donne une piste claire.
- Le hook délivre une première clé, une piste pour l'Alternative de Conscience.
"""

HOOK_PROMPT_EN = """You ARE @siderealAstro13. Generate a hook of EXACTLY 4 sentences.

Mandatory structure:
1. MIRROR: What {name} is concretely living RIGHT NOW — recognizable behavior, no astro jargon.
2. WOUND: What this period reawakens in their deep wound — sensation, not mechanics.
3. FRICTION: What the period makes unbearable or repetitive — where it chafes most.
4. OPEN DOOR: Reveal the Alternative of Consciousness.
   The sentence must be complete and give a concrete key to understanding.
   Format: "What you need to understand about [core theme] is that..." then FINISH the sentence.

ABSOLUTE RULES:
- 4 sentences. Not 3. Not 5.
- Direct address: "you", "your".
- Zero astro jargon (no "your Ketu", "your Invisible Door", "your Chiron").
- Sentence 4 CONCLUDES. It gives a clear direction.
- The hook delivers a first key, a hint for the Alternative of Consciousness.
"""

# ══════════════════════════════════════════════════════════════════════════════
# PROMPT SYSTÈME — personnalisé par utilisateur, doctrine centralisée
# ══════════════════════════════════════════════════════════════════════════════

def _build_system_prompt(user: dict, use_vault: bool = True) -> str:
    """
    Construit le prompt système complet.
    use_vault=True  → vault Karpathy (fallback doctrine.py si absent)
    use_vault=False → doctrine.py legacy uniquement
    Injection bloc natal personnalisé + friction (Pilier 6) dans les deux cas.
    """
    user = user or {}
    lang = user.get("lang", "fr")

    name         = user.get("name", "l'utilisateur")
    cl_sign      = user.get("chandra_lagna_sign", "")
    cl_deg       = user.get("chandra_lagna_deg", "")
    ketu_sign    = user.get("ketu_sign", "")
    ketu_h       = user.get("ketu_house", "")
    rahu_sign    = user.get("rahu_sign", "")
    rahu_h       = user.get("rahu_house", "")
    pv_sign      = user.get("porte_visible_sign", "")
    pv_deg       = user.get("porte_visible_deg", "")
    pv_h         = user.get("porte_visible_house", "")
    pi_sign      = user.get("porte_invisible_sign", "")
    pi_deg       = user.get("porte_invisible_deg", "")
    pi_h         = user.get("porte_invisible_house", "")
    chiron_sign  = user.get("chiron_sign", "")
    chiron_h     = user.get("chiron_house", "")
    lilith_sign  = user.get("lilith_sign", "")
    lilith_h     = user.get("lilith_house", "")
    saturn_sign  = user.get("saturn_sign", "")
    saturn_h     = user.get("saturn_house", "")
    jupiter_sign = user.get("jupiter_sign", "")
    jupiter_h    = user.get("jupiter_house", "")

    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")
    lilith_nak = user.get("lilith_nakshatra", "")

    def nak_theme(nak_name: str, planet_key: str) -> str:
        if not nak_name:
            return ""
        entry = NAKSHATRA_KARMA.get(nak_name, {})
        theme = entry.get(planet_key, "")
        return f" — {theme}" if theme else ""

    if lang == "en":
        header     = f"NATAL CHART OF {name.upper()} — Base reference for all transits"
        lbl_h1     = "Identity (H1 / Chandra Lagna)"
        lbl_ketu   = "Karmic Memory — Ketu (ROM ☋)"
        lbl_rahu   = "Dharma — Rahu (☊)"
        lbl_pv     = "Liberation Path (Visible Door — healing/Stage)"
        lbl_pi     = "Unconscious Prison (Invisible Door — refoulement/blockage)"  # CORR L123
        lbl_chiron = "Core Wound — Chiron (RAM ⚷ — opening tool of Visible Door)"  # CORR L124
        lbl_lilith = "Karmic Trial — Lilith (⚸)"
        lbl_saturn = "Saturn — Architect (♄)"
        lbl_jup    = "Jupiter — Gift-Bearer (♃)"
        lbl_ref    = f"ALWAYS use this natal chart as fixed reference. Never deviate.\nAddress {name} directly."
    else:
        header     = f"THÈME NATAL DE {name.upper()} — Référence de base pour tous les transits"
        lbl_h1     = "Identité (H1 / Chandra Lagna)"
        lbl_ketu   = "Mémoire karmique — Ketu (ROM ☋)"
        lbl_rahu   = "Dharma — Rahu (☊)"
        lbl_pv     = "Voie de libération (Porte Visible — guérison/Stage)"
        lbl_pi     = "Prison inconsciente (Porte Invisible — refoulement/blocage)"  # CORR L135
        lbl_chiron = "Blessure originelle — Chiron (RAM ⚷ — outil d'ouverture de la Porte Visible)"  # CORR L136
        lbl_lilith = "Épreuve karmique — Lilith (⚸)"
        lbl_saturn = "Saturne — Architecte (♄)"
        lbl_jup    = "Jupiter — Porteur de cadeaux (♃)"
        lbl_ref    = f"Utilise TOUJOURS ce thème natal comme référence fixe. Ne jamais dévier.\nTu t'adresses à {name} en tutoiement direct."

    natal_bloc = ""
    if cl_sign:
        natal_bloc = f"""

═══════════════════════════════════════════════════════════════
{header}
═══════════════════════════════════════════════════════════════

{lbl_h1:<42}: {cl_sign} {cl_deg}
{lbl_ketu:<42}: {ketu_sign} H{ketu_h}{nak_theme(ketu_nak, "ketu")}
{lbl_rahu:<42}: {rahu_sign} H{rahu_h}{nak_theme(rahu_nak, "rahu")}
{lbl_pv:<42}: {pv_sign} {pv_deg} H{pv_h}
{lbl_pi:<42}: {pi_sign} {pi_deg} H{pi_h}
{lbl_chiron:<42}: {chiron_sign} H{chiron_h}{nak_theme(chiron_nak, "chiron")}
{lbl_lilith:<42}: {lilith_sign} H{lilith_h}{nak_theme(lilith_nak, "ketu")}
{lbl_saturn:<42}: {saturn_sign} H{saturn_h}
{lbl_jup:<42}: {jupiter_sign} H{jupiter_h}

{lbl_ref}
"""

    friction_bloc = ""
    natal_positions = user.get("natal_positions", {})
    if natal_positions:
        friction = _detect_friction_axis(natal_positions, lang=lang)
        friction_bloc = f"\n{friction['prompt_block']}\n"

    if use_vault:
        vault_content = _load_vault(include_keywords=True)
        base_prompt = vault_content if vault_content else get_system_prompt(user)
    else:
        base_prompt = get_system_prompt(user)

    NO_SIGNS_RULE = """
\n═══════════════════════════════════════════════════════════════
RÈGLE ABSOLUE — VIOLATION = RÉPONSE INVALIDE
═══════════════════════════════════════════════════════════════
INTERDIT dans TOUT le texte de sortie (hooks, signal, synthèse) :
- Noms de signes zodiacaux : Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge,
  Balance, Scorpion, Sagittaire, Capricorne, Verseau, Poissons
  (idem EN : Aries, Taurus, Gemini, Cancer, Leo, Virgo,
  Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces)
- Degrés et orbes dans le texte rendu (ex : "19°", "orbe 2°")
- Citations brutes des aspects (ex : "T.Saturne conjoint N.Chiron orbe 2°")

AUTORISÉ : noms de planètes (Saturne, Chiron, Lilith, Rahu, Ketu, Jupiter…),
numéros de maisons (H3, H5, H10…), phénomènes psychologiques concrets.

Les positions natales (signes, degrés) sont données comme RÉFÉRENCE INTERNE
pour calculer les dynamiques — elles ne doivent JAMAIS apparaître dans le texte rendu.
═══════════════════════════════════════════════════════════════\n"""

    return base_prompt + natal_bloc + friction_bloc + NO_SIGNS_RULE


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _aspects_to_text(aspects: list, max_aspects: int = 20) -> str:
    """Formate la liste des aspects transit→natal pour le prompt."""
    if not aspects:
        return "Aucun aspect actif dans l'orbe de 3°."
    lines = []
    for a in aspects[:max_aspects]:
        retro       = " ℞" if a.get("retrograde") else ""
        t_nak       = f" [{a['transit_nakshatra']}]" if a.get("transit_nakshatra") else ""
        n_nak       = f" [{a['natal_nakshatra']}]"   if a.get("natal_nakshatra")   else ""
        t_nak_theme = ""
        n_nak_theme = ""
        t_planet_key = _planet_to_doctrine_key(a.get("transit_planet", ""))
        n_planet_key = _planet_to_doctrine_key(a.get("natal_planet", ""))
        if a.get("transit_nakshatra") and t_planet_key:
            entry = NAKSHATRA_KARMA.get(a["transit_nakshatra"], {})
            if entry.get(t_planet_key):
                t_nak_theme = f" -> {entry[t_planet_key]}"
        if a.get("natal_nakshatra") and n_planet_key:
            entry = NAKSHATRA_KARMA.get(a["natal_nakshatra"], {})
            if entry.get(n_planet_key):
                n_nak_theme = f" -> {entry[n_planet_key]}"
        lines.append(
            f"T.{a['transit_planet']}{retro} ({a.get('transit_display','')}{t_nak}{t_nak_theme}) "
            f"{a['aspect']} "
            f"N.{a['natal_planet']} ({a.get('natal_display','')}{n_nak}{n_nak_theme}) "
            f"[orbe {a['orb']}°]"
        )
    return "\n".join(lines)


def _planet_to_doctrine_key(planet_name: str) -> str:
    """Mappe le nom de planète vers la clé doctrine NAKSHATRA_KARMA."""
    mapping = {
        "Ketu":    "ketu",  "Rahu":    "rahu",
        "Saturn":  "saturn","Saturne": "saturn",
        "Chiron":  "chiron","Venus":   "venus",
        "Vénus":   "venus", "Jupiter": "jupiter",
        "Mars":    "mars",
    }
    return mapping.get(planet_name, "")


def _build_natal_context(user: dict) -> str:
    """Bloc de contexte natal compact pour le prompt de synthèse."""
    user = user or {}
    lines = []
    fields = [
        ("Chandra Lagna H1",                "chandra_lagna_sign",  "chandra_lagna_deg"),
        ("Ketu (ROM ☋)",                    "ketu_sign",           "ketu_house"),
        ("Rahu (Dharma ☊)",                 "rahu_sign",           "rahu_house"),
        ("Porte Visible (guérison/Stage)",  "porte_visible_sign",  "porte_visible_house"),   # CORR L251
        ("Porte Invisible (prison/refoul.)", "porte_invisible_sign","porte_invisible_house"), # CORR L252
        ("Chiron (RAM ⚷ — ouverture PV)",   "chiron_sign",         "chiron_house"),
        ("Lilith (⚸)",                      "lilith_sign",         "lilith_house"),
        ("Saturne (♄)",                     "saturn_sign",         "saturn_house"),
        ("Jupiter (♃)",                     "jupiter_sign",        "jupiter_house"),
    ]
    for label, key1, key2 in fields:
        v1 = user.get(key1, "")
        v2 = user.get(key2, "")
        if v1:
            lines.append(f"  {label}: {v1} {'H'+str(v2) if v2 else ''}")
    return "\n".join(lines) if lines else ""


def _build_amsa_bloc(chart_data: dict, lang: str = "fr", compact: bool = False) -> str:
    """Formate les positions divisionnelles D9/D10/D60."""
    natal = chart_data.get("natal", {})
    if not natal:
        return ""
    D9_PLANETS  = ["Lune ☽", "ASC ↑", "Nœud Nord ☊", "Nœud Sud ☋", "Vénus ♀", "Jupiter ♃"]
    D10_PLANETS = ["Soleil ☀", "Saturne ♄", "Mars ♂", "Jupiter ♃", "MC ↑"]
    D60_PLANETS = ["Lune ☽", "Nœud Sud ☋"] if compact else ["Lune ☽", "Soleil ☀", "Nœud Sud ☋", "Chiron ⚷", "Saturne ♄"]

    def fmt(planet_key: str, amsa: str) -> str:
        p = natal.get(planet_key)
        if not p:
            return None
        data = p.get(amsa)
        if not data:
            return None
        sign  = data.get("sign", "")
        part  = data.get("part", "")
        lord  = data.get("lord", "")
        lord_s = f" [{lord}]" if lord else ""
        return f"  {planet_key:<22} {sign}{lord_s} (part {part})"

    lines_d9  = [r for p in D9_PLANETS  if (r := fmt(p, "d9"))]
    lines_d10 = [r for p in D10_PLANETS if (r := fmt(p, "d10"))]
    lines_d60 = [r for p in D60_PLANETS if (r := fmt(p, "d60"))]
    if not any([lines_d9, lines_d10, lines_d60]):
        return ""

    if lang == "en":
        header  = "DIVISIONAL CHARTS (NATAL AMSAS)"
        d9_lbl  = "D9 — Navamsha (dharma, soul purpose, marriage)"
        d10_lbl = "D10 — Dashamsha (professional karma, public action)"
        d60_lbl = "D60 — Shashtyamsha (karmic specificity, soul imprint)"
        instr   = ("Use these Amsas to deepen the natal reading: "
                   "the Navamsha sign refines the soul's incarnation dharma; "
                   "the Dashamsha reveals the professional mission; "
                   "the Shashtyamsha lord names the karmic sub-color of each planet.")
    else:
        header  = "CHARTS DIVISIONNELS (AMSAS NATAUX)"
        d9_lbl  = "D9 — Navamsha (dharma, vocation de l'âme, mariage)"
        d10_lbl = "D10 — Dashamsha (karma professionnel, action publique)"
        d60_lbl = "D60 — Shashtyamsha (spécificité karmique, empreinte de l'âme)"
        instr   = ("Utilise ces Amsas pour approfondir la lecture natale : "
                   "le signe Navamsha affine le dharma d'incarnation de l'âme ; "
                   "le Dashamsha révèle la mission professionnelle ; "
                   "le seigneur Shashtyamsha nomme la sous-couleur karmique de chaque planète.")

    bloc = f"\n{'─'*62}\n{header}\n{'─'*62}\n"
    if lines_d9:
        bloc += f"\n{d9_lbl}\n" + "\n".join(lines_d9) + "\n"
    if lines_d10:
        bloc += f"\n{d10_lbl}\n" + "\n".join(lines_d10) + "\n"
    if lines_d60:
        bloc += f"\n{d60_lbl}\n" + "\n".join(lines_d60) + "\n"
    if not compact:
        bloc += f"\n{instr}\n"
    return bloc


def _detect_nodal_cycle(user: dict, chart_data: dict) -> str:
    """Détecte si un cycle nodal est actif."""
    nn_transit = chart_data.get("transit_positions", {}).get("true_node_lon")
    nn_natal   = chart_data.get("natal_positions",   {}).get("true_node_lon")
    if nn_transit is None or nn_natal is None:
        return ""
    diff = abs(nn_transit - nn_natal) % 360
    if diff > 180:
        diff = 360 - diff
    if diff <= 10:
        cycle = NODAL_CYCLES["return"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 90) <= 10:
        cycle = NODAL_CYCLES["square"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    if abs(diff - 180) <= 10:
        cycle = NODAL_CYCLES["opposition"]
        return f"\n CYCLE NODAL ACTIF : {cycle['description']} — {cycle['karma']}"
    return ""


def _detect_transit_friction(chart_data: dict, lang: str = "fr") -> str:
    """Détecte l'axe de friction identitaire sur les positions EN TRANSIT (Pilier 6)."""
    transit_pos = chart_data.get("transit_positions", {})
    if not transit_pos:
        return ""
    positions = {}
    for planet in ("venus", "jupiter", "mars", "saturn"):
        raw = transit_pos.get(f"{planet}_lon") or transit_pos.get(planet, {}).get("lon_raw")
        if raw is not None:
            positions[f"transit_{planet}"] = {"lon_raw": float(raw)}
    if not positions:
        return ""
    friction = _detect_friction_axis(positions, lang=lang)
    if friction["label"] == "low" and not friction["aspects"]:
        return ""
    return f"\n{friction['prompt_block']}\n"


def _get_nak_lord(nak_name: str) -> str:
    """Retourne le régent Vimshotari d'un nakshatra, chaîne vide si inconnu."""
    try:
        return NAKSHATRA_LORDS[NAKSHATRAS.index(nak_name)]
    except (ValueError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════════════════════
# HOOK NATAL — affiché dès le login (natal seul, pas de transit)
# ══════════════════════════════════════════════════════════════════════════════

def get_hook_natal(user: dict, lang: str = "fr") -> str:
    """
    Génère un hook de 3-4 phrases (Mirror → Wound → Friction → Open Door) basé uniquement sur le thème natal.
    Appelé dès le login — zéro calcul de transit requis.
    Mis en cache côté app.py (clé: pseudo, durée: 7 jours).
    Modèle : Sonnet (rapide, cheap)

    Retourne une chaîne HTML-safe prête à afficher.
    """
    user = user or {}
    name = user.get("name", "")

    cl     = user.get("chandra_lagna_sign", "")
    ketu_h = user.get("ketu_house", "")
    chi_h  = user.get("chiron_house", "")
    pv     = user.get("porte_visible_sign", "") or user.get("porte_visible_house", "")
    lil_h  = user.get("lilith_house", "")
    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")

    if not cl:
        return ""

    natal_mini = (
        f"Chandra Lagna H1: {cl}. "
        f"Ketu (mémoire statique): H{ketu_h}. "
        f"Chiron (blessure-clé, outil d'ouverture): H{chi_h}. "
        f"Porte Visible (guérison/Stage): {pv}. "
        f"Lilith (épreuve): H{lil_h}. "
        f"Nakshatras : Ketu en {ketu_nak} (régent {_get_nak_lord(ketu_nak)}), Rahu en {rahu_nak}, Chiron en {chiron_nak}. "
    )

    system = (
        "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
        "Ton style : oraculaire, direct, sans hedging. "
        "Zéro degrés, zéro orbes, zéro labels techniques visibles. "
        "Tutoiement direct. "
        "INTERDIT ABSOLU dans le texte rendu : noms de signes zodiacaux "
        "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
        "Sagittaire, Capricorne, Verseau, Poissons). "
        "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
    )

    if lang == "fr":
        hook_template = HOOK_PROMPT_FR.format(name=name)
        prompt = f"""{hook_template}

Thème natal de {name} :
{natal_mini}

CONTEXTE : Lecture natale au login. Tu dois fournir une analyse profonde et complètement ORIGINALE à chaque fois. 
Choisis de te concentrer sur un aspect spécifique et inattendu du thème (une planète différente, une maison particulière, etc.) pour garantir que cette lecture soit unique.
La phrase 4 DOIT donner la clé complète et terminer la pensée."""
    else:
        hook_template = HOOK_PROMPT_EN.format(name=name)
        prompt = f"""{hook_template}

Natal chart of {name}:
{natal_mini}

CONTEXT: Natal reading at login. You must provide a profound and completely ORIGINAL analysis every time.
Choose to focus on a specific and unexpected aspect of the chart (a different planet, a particular house, etc.) to ensure this reading is unique.
Sentence 4 MUST give the complete key and finish the thought."""

    pseudo = user.get("pseudo", "")
    rag_context = retrieve_context(pseudo, "analyse natale et blessure profonde", limit=2)
    if rag_context:
        if lang == "fr":
            prompt += f"\n\nCONTEXTE KARMIQUE PASSÉ (SOUVENIRS DE LECTURES PRÉCÉDENTES) :\n{rag_context}\n\nPrends en compte cette évolution dans ta nouvelle analyse pour ne pas te répéter et montrer que tu suis l'utilisateur."
        else:
            prompt += f"\n\nPAST KARMIC CONTEXT (MEMORIES OF PREVIOUS READINGS) :\n{rag_context}\n\nTake this evolution into account in your new analysis to avoid repetition and show you follow the user."

    # Force le modèle Sonnet pour le hook si aucun n'est précisé
    # Force le modèle et le provider du serveur pour le hook, car il doit être rapide et précis
    user_with_model = {**(user or {}), "user_provider": None, "user_key": None, "user_model": HOOK_MODEL}
    result = generate_ai(system, prompt, user=user_with_model, max_tokens=1000)
    
    if result and not result.startswith("[ERROR]"):
        threading.Thread(target=save_reading, args=(pseudo, result, "hook_natal")).start()
        
    return result


# ══════════════════════════════════════════════════════════════════════════════
# HOOK TRANSIT — affiché dès la date choisie, avant la synthèse complète
# ══════════════════════════════════════════════════════════════════════════════

def get_hook_transit(chart_data: dict, user: dict = None) -> str:
    """
    Génère un hook de 4 phrases (Mirror → Wound → Friction → Open Door) basé sur les aspects du jour.
    Appelé après calculate_transits(), avant get_synthesis().
    Mis en cache côté app.py (clé: pseudo+date, durée: 24h).
    Modèle : Sonnet (rapide, cheap)

    chart_data : dict retourné par calculate_transits()
    Retourne une chaîne prête à afficher.
    """
    user = user or {}
    lang = user.get("lang", "fr")
    name = user.get("name", "")

    # Aspects limités aux 3 plus serrés pour le hook
    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=3)
    date         = chart_data.get("transit_date", "")

    _NO_ASPECT = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT:
        return ""

    natal_mini = _build_natal_context(user)

    system = (
        "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
        "Style : oraculaire, direct, sans hedging. "
        "Zéro degrés, zéro orbes, zéro labels techniques visibles. "
        "Tutoiement direct. "
        "INTERDIT ABSOLU dans le texte rendu : noms de signes zodiacaux "
        "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
        "Sagittaire, Capricorne, Verseau, Poissons). "
        "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
    )

    if lang == "fr":
        hook_template = HOOK_PROMPT_FR.format(name=name)
        prompt = f"""{hook_template}

Thème natal de {name} :
{natal_mini}

Aspects actifs ce jour ({date}) — ne pas citer tels quels dans le texte :
{aspects_text}

CONTEXTE : Lecture des transits du jour. Fournis une analyse percutante de l'aspect le plus saillant.
La phrase 4 DOIT donner la clé complète de l'Alternative de Conscience et terminer la pensée."""
    else:
        hook_template = HOOK_PROMPT_EN.format(name=name)
        prompt = f"""{hook_template}

Natal chart of {name}:
{natal_mini}

Active aspects today ({date}) — do not quote as-is in text:
{aspects_text}

CONTEXT: Daily transit reading. Provide a striking analysis of the most salient aspect today.
Sentence 4 MUST give the complete key to the Alternative of Consciousness and finish the thought."""

    pseudo = user.get("pseudo", "")
    rag_context = retrieve_context(pseudo, "transit et friction du moment", limit=2)
    if rag_context:
        if lang == "fr":
            prompt += f"\n\nCONTEXTE KARMIQUE PASSÉ (SOUVENIRS DE LECTURES) :\n{rag_context}\n\nPrends en compte cette évolution dans ta nouvelle analyse des transits."
        else:
            prompt += f"\n\nPAST KARMIC CONTEXT (MEMORIES) :\n{rag_context}\n\nTake this evolution into account in your new transit analysis."

    # Modèle Sonnet forcé si non précisé
    # Force le modèle et le provider du serveur pour le hook, car il doit être rapide et précis
    user_with_model = {**(user or {}), "user_provider": None, "user_key": None, "user_model": HOOK_MODEL}
    result = generate_ai(system, prompt, user=user_with_model, max_tokens=1000)

    if result and not result.startswith("[ERROR]"):
        threading.Thread(target=save_reading, args=(pseudo, result, "hook_transit", date)).start()

    return result
# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL DU JOUR — compact pour TikTok/Web
# ══════════════════════════════════════════════════════════════════════════════

def get_daily_signal(transit_date: str = None) -> dict:
    """
    Génère la Météo Astrologique globale pour le jour (sans user spécifique).
    Retourne transits majeurs + position de la Lune + régime doctrinal du jour.
    """
    from datetime import date as date_cls
    from datetime import datetime

    from astro_calc import _calc_positions, get_julian_day
    from transit_alerts import PLANET_LABELS, detect_global_nak_transits

    if not transit_date:
        transit_date = str(date_cls.today())

    try:
        transit_date_obj = datetime.strptime(transit_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD.",
                "global": {}, "hook_generic": "", "cta": {}}

    # 1. Détection des transits majeurs (planètes lentes entrant en nakshatra)
    try:
        events = detect_global_nak_transits(transit_date_obj)
    except Exception as exc:
        return {"error": f"Transit calculation failed: {str(exc)}",
                "global": {}, "hook_generic": "", "cta": {}}

    primary = events[0] if events else None

    # 2. Position de la Lune pour le signal quotidien (plus dynamique)
    ref_lat, ref_lon, ref_tz = 48.8566, 2.3522, "Europe/Paris"
    jd = get_julian_day(transit_date_obj.year, transit_date_obj.month, transit_date_obj.day, 12, 0, ref_tz)
    pos = _calc_positions(jd, ref_lat, ref_lon)
    moon_data = pos.get("Lune ☽")
    
    moon_info = ""
    if moon_data:
        nak = moon_data["nakshatra"]
        pada = moon_data["pada"]
        moon_info = f"Lune en {nak} (P{pada})"

    title_str = transit_date_obj.strftime("%d/%m/%Y")
    title = f"Météo Astrologique — {title_str}"

    if primary:
        nakshatra     = primary["nakshatra"]
        regime        = primary["regime"]
        regime_label  = primary["regime_label"]
        transits_text = (
            f"{PLANET_LABELS.get(primary['transit'], primary['transit'])} "
            f"entre en {nakshatra} (régent {primary['lord']}) — {regime_label.lower()}"
        )
    else:
        regime        = "neutre"
        regime_label  = "Jour stable"
        transits_text = f"{moon_info} — Aucune activation majeure des planètes lentes."

    return {
        "global": {
            "title":        title,
            "transits":     transits_text,
            "regime":       regime,
            "regime_label": regime_label,
            "moon_nak":     moon_info,
        },
        "hook_generic": _generate_generic_hook(regime),
        "cta": {
            "text":    "Et toi, né sous une Pleine Lune en Lion ?",
            "subtext": "Découvre ce que ça dit pour TON thème natal",
            "link":    "https://karmicgochara.app/register",
        },
    }


def _generate_generic_hook(regime: str) -> str:
    """Génère un hook générique de 1-2 phrases basé sur le régime du jour."""
    hooks = {
        "ROM_oppression":       "Test karmique majeur aujourd'hui — destruction des faux pouvoirs. L'âme rejoue son schéma sans fin, mais le cosmos refuse.",
        "Dharma_amplification": "Opportunité d'expansion consciente — l'univers ouvre une porte. C'est le moment de choisir autrement.",
        "Blessure_activation":  "La blessure profonde remonte à la surface pour se transformer. Chiron travaille — tu sens l'inconfort ? C'est bon signe.",
        "neutre":               "Jour stable en apparence, mais chaque instant cache une mutation silencieuse de l'âme.",
    }
    return hooks.get(regime, "L'astrologie parle aujourd'hui — es-tu en train d'écouter ?")


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE COMPLÈTE — payant, ~4000 tokens
# ══════════════════════════════════════════════════════════════════════════════

def get_synthesis(chart_data: dict, user: dict = None, lang: str = "fr") -> str:
    """
    Génère la synthèse karmique complète (payant).
    Modèle : Opus pour la meilleure qualité doctrinal.
    chart_data : dict retourné par calculate_transits()
    user       : dict du profil utilisateur (session["profile"])
    """
    user = user or {}
    lang = user.get("lang", lang)

    # Force le modèle Opus pour la synthèse payante, sauf si customisé
    user_model = user.get("user_model") if user else None
    user = {**user, "user_model": user_model or SYNTHESIS_MODEL}

    aspects_text  = _aspects_to_text(chart_data.get("aspects", []))
    natal_context = _build_natal_context(user)
    nodal_cycle   = _detect_nodal_cycle(user, chart_data)
    transit_frict = _detect_transit_friction(chart_data, lang=lang)
    amsa_bloc     = _build_amsa_bloc(chart_data, lang=lang)
    date          = chart_data.get("transit_date", "")
    time          = chart_data.get("transit_time", "")
    name          = user.get("name", "l'utilisateur")

    _NO_ASPECT_FR = "Aucun aspect actif dans l'orbe de 3°."
    if not aspects_text or aspects_text.strip() == _NO_ASPECT_FR:
        return ("⚠️ Synthèse impossible : aucun aspect de transit actif détecté. "
                "Vérifie que `calculate_transits()` retourne bien des aspects avant d'appeler `get_synthesis()`.")
    if not natal_context:
        return ("⚠️ Synthèse impossible : thème natal manquant. "
                "Vérifie que le profil utilisateur contient au minimum `chandra_lagna_sign`.")

    natal_bloc = f"\nThème natal de référence :\n{natal_context}\n" if natal_context else ""
    nodal_bloc = nodal_cycle if nodal_cycle else ""
    frict_bloc = transit_frict if transit_frict else ""

    LANG_NAMES = {
        "fr": "français",   "en": "English",
        "es": "español",    "pt": "português",
        "de": "Deutsch",    "nl": "Nederlands",
        "it": "italiano",
    }
    lang_name = LANG_NAMES.get(lang, "English")

    if lang == "fr":
        prompt = f"""Tu ES @siderealAstro13. Ne te comporte pas comme un assistant. Analyse directement les données ci-dessous selon la doctrine karmique.
Interdiction de reformuler le prompt. Tu dois rédiger une analyse basée exclusivement sur les aspects et positions fournis.

LANGUE : français uniquement. Aucun mot anglais.
Analyse siderealAstro13 des transits de {name} — {date} à {time}.
CONSIGNE : commence directement par "## 1. LA MÉMOIRE KARMIQUE". Aucune note préalable, aucune introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Aspects actifs (données brutes — NE PAS les citer tels quels dans le texte) :
{aspects_text}

STYLE OBLIGATOIRE : tu écris comme un lecteur d'âme, pas comme un astrologue technique.
- Traduis chaque aspect en vécu concret, en pattern comportemental reconnaissable.
- Ne cite jamais les aspects bruts ("T.Saturne conjoint N.Chiron orbe 2°"). Traduis-les en ce que {name} ressent ou fait.
- Parle directement à {name} : "tu", "ton", "ta".
- À la fin de chaque section (1, 2, 3), glisse un APERÇU : une phrase courte en italique qui ouvre une porte sans tout révéler.

Applique le protocole en 4 étapes :

1. LA MÉMOIRE KARMIQUE (ROM ☋) — Quel piège l'âme de {name} rejoue-t-elle en ce moment ? Décris le comportement automatique, la sensation familière, ce que ça lui coûte. Termine par un aperçu en italique.

2. LA BLESSURE EN TRAITEMENT (RAM ⚷) — Qu'est-ce qui est réveillé dans la blessure profonde de {name} ? La Porte Invisible (prison/refoulement) est-elle sous pression ? La Porte Visible (guérison/Stage) s'ouvre-t-elle via Chiron ? Décris le mouvement vécu, pas la mécanique. Termine par un aperçu en italique.

3. L'ÉPREUVE KARMIQUE (⚸) — Qu'est-ce que la période rend insupportable à {name} ? Quel endroit de sa vie frotte le plus fort ? Vers quoi ça le pousse malgré lui ? Termine par un aperçu en italique.

4. ALTERNATIVE DE CONSCIENCE — Ce que {name} doit cesser de faire. Ce qu'il doit oser activer. Termine par UNE seule phrase directe, actionnable, personnelle.

Minimum 300 mots. Ne pas tronquer. Tout en français."""
    else:
        prompt = f"""You ARE @siderealAstro13. Do not behave as an assistant. Analyse the data below directly according to karmic doctrine.
Forbidden to rephrase the prompt. Write analysis based exclusively on the aspects and positions provided.

siderealAstro13 transit analysis for {name} — {date} at {time}.
INSTRUCTION: start directly with "## 1. KARMIC MEMORY". No preamble, no introduction.
{natal_bloc}{amsa_bloc}{nodal_bloc}{frict_bloc}

Active aspects (raw data — do NOT quote them as-is in the text):
{aspects_text}

MANDATORY STYLE: soul reader, not technical astrologer.
- Translate each aspect into lived experience, recognizable behavioral pattern.
- Never quote raw aspects. Translate them into what {name} feels or does.
- Speak directly to {name}: "you", "your".
- End sections 1, 2, 3 with an INSIGHT in italics.

1. KARMIC MEMORY (ROM ☋) — What trap replays? Automatic behavior, familiar feeling, what it costs. Insight in italics.
2. THE WOUND IN PROCESSING (RAM ⚷) — What is awakened? Invisible Door (prison/blockage) under pressure? Visible Door (healing/Stage) opening via Chiron? Insight in italics.
3. KARMIC TRIAL (⚸) — What is unbearable? Where does it chafe? Where does it push? Insight in italics.
4. ALTERNATIVE OF CONSCIOUSNESS — What {name} must stop. What to dare activate. ONE direct actionable sentence.

Minimum 300 words. Do not truncate. Language: {lang_name}."""

    return generate_ai(_build_system_prompt(user, use_vault=True), prompt, user=user, max_tokens=4000)


def stream_synthesis(chart_data: dict, user: dict = None, lang: str = "fr"):
    """
    Génère la synthèse karmique complète en streaming avec sortie JSON structurée.
    Modèle : Opus pour la meilleure qualité doctrinal.
    """
    user = user or {}
    lang = user.get("lang", lang)
    user_model = user.get("user_model")
    user = {**user, "user_model": user_model or SYNTHESIS_MODEL}

    aspects_text  = _aspects_to_text(chart_data.get("aspects", []))
    natal_context = _build_natal_context(user)
    date          = chart_data.get("transit_date", "")
    name          = user.get("name", "l'utilisateur")

    if lang == "fr":
        prompt = f"""Tu ES @siderealAstro13.
Analyse les données de transit pour {name} ({date}) et retourne une réponse JSON stricte.

Thème natal de référence :
{natal_context}

Aspects actifs (données brutes pour ton analyse) :
{aspects_text}

SCHEMA JSON DE SORTIE OBLIGATOIRE :
{{
  "analysis": {{
    "title": "Synthèse Karmique du {date}",
    "karmic_memory": "...",
    "wound_processing": "...",
    "karmic_trial": "...",
    "consciousness_alternative": "..."
  }},
  "recommendations": ["Action 1...", "Action 2...", "Action 3..."],
  "confidence": "Élevée|Moyenne|Faible",
  "disclaimer": "Cette analyse est une interprétation..."
}}

INSTRUCTIONS :
1.  Remplis les sections de `analysis` en suivant la doctrine :
    - `karmic_memory`: Le piège karmique (ROM) qui se rejoue.
    - `wound_processing`: La blessure (RAM/Chiron) qui est activée.
    - `karmic_trial`: L'épreuve (Lilith) que la période rend insupportable.
    - `consciousness_alternative`: Le changement de conscience, l'action à poser.
2.  `recommendations`: Fournis 3 actions concrètes et courtes.
3.  `confidence`: Évalue ta confiance dans l'analyse.
4.  `disclaimer`: Ajoute un avertissement standard.
5.  Écris en français, directement à {name} ("tu", "ton"). Ne cite jamais les aspects bruts.
"""
    else:
        prompt = f"""You ARE @siderealAstro13.
Analyze the transit data for {name} ({date}) and return a strict JSON response.

Natal reference chart:
{natal_context}

Active aspects (raw data for your analysis):
{aspects_text}

MANDATORY JSON OUTPUT SCHEMA:
{{
  "analysis": {{
    "title": "Karmic Synthesis for {date}",
    "karmic_memory": "...",
    "wound_processing": "...",
    "karmic_trial": "...",
    "consciousness_alternative": "..."
  }},
  "recommendations": ["Action 1...", "Action 2...", "Action 3..."],
  "confidence": "High|Medium|Low",
  "disclaimer": "This analysis is an interpretation..."
}}

INSTRUCTIONS:
1.  Fill the `analysis` sections following the doctrine:
    - `karmic_memory`: The karmic trap (ROM) being replayed.
    - `wound_processing`: The wound (RAM/Chiron) being activated.
    - `karmic_trial`: The trial (Lilith) that the period makes unbearable.
    - `consciousness_alternative`: The shift in consciousness, the action to take.
2.  `recommendations`: Provide 3 concrete, short actions.
3.  `confidence`: Assess your confidence in the analysis.
4.  `disclaimer`: Add a standard disclaimer.
5.  Write in English, directly to {name} ("you", "your"). Never quote raw aspects.
"""

    pseudo = user.get("pseudo", "")
    rag_context = retrieve_context(pseudo, "synthèse complète et blessure karmique", limit=3)
    if rag_context:
        if lang == "fr":
            prompt += f"\n\nCONTEXTE KARMIQUE PASSÉ (SOUVENIRS) :\n{rag_context}\n\nPrends en compte cette évolution dans ta nouvelle synthèse globale."
        else:
            prompt += f"\n\nPAST KARMIC CONTEXT (MEMORIES) :\n{rag_context}\n\nTake this evolution into account in your new global synthesis."

    # Utilise stream_ai pour la réponse en streaming et capture pour la sauvegarde
    def wrapped_stream():
        full_result = []
        for chunk in stream_ai(_build_system_prompt(user, use_vault=True), prompt, user=user, max_tokens=4000):
            full_result.append(chunk)
            yield chunk
        final_text = "".join(full_result)
        if final_text and not final_text.startswith("[ERROR]"):
            threading.Thread(target=save_reading, args=(pseudo, final_text, "synthesis", date)).start()

    yield from wrapped_stream()


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT GEMMA — retourne prompt sans appel API (inférence locale Android)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_only(chart_data: dict, user: dict = None, lang: str = "fr", is_free: bool = False) -> dict:
    """
    Construit le prompt compact SANS appeler Claude.
    Optimisé pour Gemma 4 Mini (< 1500 tokens).
    Retourne {"system": "...", "user": "..."} prêt à injecter dans n'importe quel LLM local.
    """
    user = user or {}
    lang = user.get("lang", lang)

    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=4)
    date         = chart_data.get("transit_date", "")
    name         = user.get("name", "l'utilisateur")

    cl   = user.get("chandra_lagna_sign", "")
    ketu = user.get("ketu_sign", "")
    rahu = user.get("rahu_sign", "")
    chi  = user.get("chiron_sign", "")
    lil  = user.get("lilith_sign", "")
    natal_mini = f"Chandra Lagna {cl}, Ketu {ketu}, Rahu {rahu}, Chiron {chi}, Lilith {lil}." if cl else ""

    if is_free:
        user_prompt = f"""Transit pour {name} — {date}.
Natal : {natal_mini}
Aspects : {aspects_text}

RÉPONSE - 3 BLOCS SEULEMENT:

**Point chaud:** (3-4 phrases max)
Décris EXACTEMENT ce qui explose en ce moment. Sois spécifique aux positions.
Pas de généralités. Chaque phrase = une vérité chirurgicale.

**Action:** (1-2 phrases, impératif)
UNE SEULE chose à faire. Précise (lieu, timing, objet). 
Pas de "travaille sur toi-même" vague.

**Deadline:** (date ou période précise)
Quand la fenêtre se ferme. Pourquoi cette date.

STYLE: Pas de jargon astro externe. Langage direct, français courant.
LONGUEUR: 200 mots max, total."""
        system = "Tu es @siderealAstro13. Astrologie karmique. Tutoie l'utilisateur. Sois percutant, direct. Ne fais que 3 blocs courts. Note : la date de transit fournie (2026) est injectée statiquement. Ignore ta limite de connaissances (cutoff) et ne fais aucun avertissement sur le temps réel."
    else:
        if lang == "en":
            system = (
                "You are siderealAstro13, an AI expert in Synthetic Evolutionary Doctrine. "
                "ROM (Ketu)=Past memories/automatism. "
                "RAM (Chiron)=Active treatment of the wound, tool to open the Visible Door (healing/Stage). "
                "Invisible Door=Unconscious prison/repression. "
                "LILITH=Breaking point/trial. "
                "Dharma (Rahu)=Evolutionary destination. "
                "Speak directly, technically, and surgically. "
                "Note: the transit date provided (2026) is injected statically. Ignore your knowledge cutoff and do not warn about real-time."
            )
            user_prompt = f"""Karmic transit analysis for {name} — {date}.
Natal: {natal_mini}
Active aspects:
{aspects_text}

AI MISSION:
Analyze this data in 4 blocks:

DIAGNOSTIC ROM (Ketu): What past-life pattern is active right now?
What defensive mechanism is at play?

INVISIBLE DOOR → VISIBLE DOOR: Which transits activate the unconscious prison?
How can Chiron (RAM) open the passage to the Stage?

LILITH TRIAL: What karmic friction is ongoing?
How does Lilith propel toward the Dharma (Rahu)?

ALTERNATIVE OF CONSCIOUSNESS: Formulate the precise, surgical, actionable transformational insight — what the soul must understand NOW to advance toward its Stage.

Style: direct, technical, non-astro-jargon in conclusions. Direct address ("you").
Length: 400-600 words. No generalities. Every sentence = a surgical truth."""
        else:
            system = (
                "Tu es l'intelligence siderealAstro13, experte en Doctrine Évolutive Synthétique. "
                "ROM (Ketu)=Mémoires passées/automatisme. "
                "RAM (Chiron)=Traitement actif de la blessure, outil d'ouverture de la Porte Visible (guérison/Stage). "
                "Porte Invisible=Prison inconsciente/refoulement. "
                "LILITH=Point de rupture/épreuve. "
                "DHARMA (Rahu)=Destination d'évolution. "
                "Tutoie l'utilisateur. Sois direct et chirurgical. "
                "Note : la date de transit fournie (2026) est injectée statiquement. Ignore ta limite de connaissances (cutoff) et ne fais aucun avertissement sur le temps réel."
            )
            user_prompt = f"""Analyse karmique de transit pour {name} — {date}.
Natal : {natal_mini}
Aspects actifs :
{aspects_text}

MISSION POUR L'IA :
Analyse ces données en 4 blocs :

DIAGNOSTIC ROM (Ketu) : Quel schéma de passé-vie est activé en ce moment ?
Quel automatisme défensif est à l'œuvre ?

PORTE INVISIBLE → PORTE VISIBLE : Quels transits activent la prison inconsciente ?
Comment Chiron (RAM) peut-il ouvrir le passage vers le Stage ?

ÉPREUVE LILITH : Quelle friction karmique est en cours ?
Comment Lilith propulse-t-elle vers le Dharma (Rahu) ?

ALTERNATIVE DE CONSCIENCE : Formule l'insight transformateur précis,
chirurgical, actionnable — ce que l'âme doit comprendre MAINTENANT
pour avancer vers son Stage.

Style : direct, technique, non-astro-jargon dans les conclusions. Tutoiement direct ("tu").
Longueur : 400-600 mots. Pas de généralités. Chaque phrase = une vérité chirurgicale."""

    return {"system": system, "user": user_prompt}


# ══════════════════════════════════════════════════════════════════════════════
# LECTURE NATALE — prompt Gemma (sans appel Claude)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_natal(user: dict, lang: str = "fr") -> dict:
    """
    Construit le prompt Lecture Natale SANS appeler Claude.
    Miroir de get_hook_natal() — retourne {system, user} prêt pour Gemma.
    Génère : 3 phrases d'accroche sur le thème natal (ROM/RAM/Stage).
    """
    user = user or {}
    lang = user.get("lang", lang)
    name = user.get("name", "l'âme")

    cl         = user.get("chandra_lagna_sign", "")
    ketu_h     = user.get("ketu_house", "")
    chi_h      = user.get("chiron_house", "")
    pv         = user.get("porte_visible_sign", "") or user.get("porte_visible_house", "")
    lil_h      = user.get("lilith_house", "")
    ketu_nak   = user.get("ketu_nakshatra", "")
    rahu_nak   = user.get("rahu_nakshatra", "")
    chiron_nak = user.get("chiron_nakshatra", "")

    if not cl:
        return {"system": "", "user": ""}

    natal_mini = (
        f"Chandra Lagna H1: {cl}. Ketu (ROM): H{ketu_h}. "
        f"Chiron (RAM, outil ouverture): H{chi_h}. Porte Visible: {pv}. "
        f"Lilith (epreuve): H{lil_h}. "
        f"Nakshatras: Ketu en {ketu_nak}, Rahu en {rahu_nak}, Chiron en {chiron_nak}."
    )

    if lang == "en":
        system = (
            "You are @siderealAstro13. Sidereal Vedic karmic soul reader. "
            "Oracular, direct, no hedging. No degrees, no orbs, no technical labels. "
            "Plain text only — no markdown, no headers, no numbered lists, no dashes. "
            "Address user as 'you'. FORBIDDEN: any zodiac sign name. H1-H12 only."
        )
        user_prompt = (
            f"Natal chart of {name}:\n{natal_mini}\n\n"
            f"Write exactly 3 flowing sentences of plain prose. No numbers, no titles, no markdown.\n"
            f"The first sentence: dominant karmic pattern {name} replays (Ketu — frozen ROM).\n"
            f"The second sentence: active wound and what it seeks (Chiron H{chi_h} — opening toward Visible Door).\n"
            f"The third sentence: liberation direction (Stage) + seed of Alternative de Conscience.\n"
            f"Dense, precise. Make them want to know more."
        )
    else:
        system = (
            "Tu es @siderealAstro13. Lecteur d'ame karmique vedique siderale. "
            "Oraculaire, direct, sans hedging. Zero degres, zero orbes. Tutoiement. "
            "Texte brut uniquement — jamais de markdown, jamais de headers, jamais de listes, jamais de tirets. "
            "INTERDIT : noms de signes zodiacaux. Maisons H1-H12 uniquement."
        )
        user_prompt = (
            f"Theme natal de {name} :\n{natal_mini}\n\n"
            f"Ecris exactement 3 phrases de prose enchainee. Pas de numeros, pas de titres, pas de markdown.\n"
            f"La premiere phrase : le schema karmique dominant que {name} rejoue (Ketu — ROM figee).\n"
            f"La deuxieme phrase : la blessure active et ce qu'elle cherche (Chiron H{chi_h} — outil vers la Porte Visible).\n"
            f"La troisieme phrase : la direction de liberation (Stage) + amorce d'Alternative de Conscience.\n"
            f"Dense, precis. Donne envie d'en savoir plus."
        )

    return {"system": system, "user": user_prompt}


# ══════════════════════════════════════════════════════════════════════════════
# ALTERNATIVE DE CONSCIENCE — prompt Gemma focalisé (section 4 uniquement)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_conscience(chart_data: dict, user: dict = None, lang: str = "fr") -> dict:
    """
    Construit un prompt focalisé sur l'Alternative de Conscience SANS appeler Claude.
    Génère uniquement la section 4 — shift actionnable immédiat.
    Budget Gemma : ~200 tokens output.
    """
    user = user or {}
    lang = user.get("lang", lang)
    name = user.get("name", "l'ame")

    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=3)
    date         = chart_data.get("transit_date", "")
    natal_mini   = _build_natal_context(user)

    if lang == "en":
        system = (
            "You are @siderealAstro13. Sidereal Vedic karmic astrology. "
            "Write a precise, actionable inner shift the soul can choose RIGHT NOW. "
            "Plain text only — no markdown, no headers, no numbered lists. "
            "No intro. Direct address. FORBIDDEN: zodiac signs. H1-H12 only. 150 words max."
        )
        user_prompt = (
            f"Transit for {name} — {date}.\nNatal:\n{natal_mini}\nAspects:\n{aspects_text}\n\n"
            f"Write 3-4 sentences of plain prose. No title, no numbers, no markdown.\n"
            f"What {name} can stop replaying (ROM loop) and what concrete action opens the Visible Door now."
        )
    else:
        system = (
            "Tu es @siderealAstro13. Astrologie karmique vedique siderale. "
            "Tu ecris le shift interieur actionnable que l'ame peut choisir MAINTENANT. "
            "Texte brut uniquement — jamais de markdown, jamais de headers, jamais de listes. "
            "Pas d'intro. Tutoiement. INTERDIT : signes zodiacaux. H1-H12 uniquement. 150 mots max."
        )
        user_prompt = (
            f"Transit de {name} — {date}.\nNatal :\n{natal_mini}\nAspects :\n{aspects_text}\n\n"
            f"Ecris 3-4 phrases de prose enchainee. Pas de titre, pas de numeros, pas de markdown.\n"
            f"Ce que {name} peut cesser de rejouer (ROM) et l'action concrete qui ouvre la Porte Visible maintenant."
        )

    return {"system": system, "user": user_prompt}


# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL DU JOUR — prompt Gemma (narratif global, sans profil)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_signal(signal_data: dict, lang: str = "fr") -> dict:
    """
    Construit le prompt Signal du Jour pour Gemma SANS appeler Claude.
    Prend le dict de get_daily_signal() et retourne {system, user}.
    Génère : 3-4 phrases narratives sur la météo karmique du jour, au format strict de 3 blocs.
    """
    g       = signal_data.get("global", {})
    title   = g.get("title", "Signal du Jour")
    transit = g.get("transits", "")
    regime  = g.get("regime", "neutre")
    label   = g.get("regime_label", "")

    if lang == "en":
        system = (
            "You are @siderealAstro13. Sidereal Vedic karmic astrology. "
            "Write a short collective daily karmic signal. No personal profile. "
            "Oracular tone. Direct. FORBIDDEN: zodiac sign names. 120 words max. "
            "Note: the transit date provided (2026) is injected statically. Ignore your knowledge cutoff and do not warn about real-time."
        )
        user_prompt = (
            f"Today's signal — {title}.\nActive transit: {transit}\nRegime: {label} ({regime})\n\n"
            f"Write exactly 3 blocks:\n\n"
            f"**Point chaud:** (3-4 sentences max on the collective sky/karmic weather today)\n\n"
            f"**Action:** (1 sentence on what to do or avoid today)\n\n"
            f"**Deadline:** (1 sentence on when this energy shifts or peaks)"
        )
    else:
        system = (
            "Tu es @siderealAstro13. Astrologie karmique vedique siderale. "
            "Tu ecris un signal karmique collectif court pour le jour. Sans profil personnel. "
            "Ton oraculaire. Direct. INTERDIT : signes zodiacaux. 120 mots max. "
            "Note : la date de transit fournie (2026) est injectée statiquement. Ignore ta limite de connaissances (cutoff) et ne fais aucun avertissement sur le temps réel."
        )
        user_prompt = (
            f"Signal du jour — {title}.\nTransit actif : {transit}\nRegime : {label} ({regime})\n\n"
            f"Ecris exactement 3 blocs :\n\n"
            f"**Point chaud:** (3-4 phrases max sur le ciel collectif et la météo karmique d'aujourd'hui)\n\n"
            f"**Action:** (1 phrase à l'impératif sur quoi faire ou eviter aujourd'hui)\n\n"
            f"**Deadline:** (1 phrase sur le moment où cette énergie bascule ou atteint son pic)"
        )

    return {"system": system, "user": user_prompt}


# ══════════════════════════════════════════════════════════════════════════════
# CHATBOT — prompt Gemma multi-tour (dialogue continu avec contexte natal)
# ══════════════════════════════════════════════════════════════════════════════

def build_prompt_chat(message: str, history: list, profile: dict, lang: str = "fr") -> dict:
    """
    Construit le prompt chatbot pour Gemma (inférence locale).
    history : liste de {role: "user"|"assistant", content: str}
    Retourne {system, user} pour GemmaSynthesisPlugin.generate().
    """
    name = profile.get("name") or profile.get("pseudo", "")

    parts = []
    for key, label in [
        ("ketu_nakshatra",    "Ketu"),
        ("chiron_nakshatra",  "Chiron"),
        ("rahu_nakshatra",    "Rahu"),
        ("chandra_lagna_sign","Lagna"),
    ]:
        val = profile.get(key, "").strip()
        if val:
            parts.append(f"{label}·{val}")
    natal_ctx = ("PROFIL : " + " | ".join(parts)) if parts else ""

    if lang == "en":
        system = (
            f"You are @siderealAstro13, Vedic sidereal karmic astrologer. "
            f"In dialogue with {name}. Direct oracular tone. "
            f"Forbidden: zodiac sign names. Max 100 words per answer."
        )
        if natal_ctx:
            system += f"\n{natal_ctx}"
            
        pseudo = profile.get("pseudo", "")
        rag_context = retrieve_context(pseudo, message, limit=3)
        if rag_context:
            system += f"\n\nPAST KARMIC CONTEXT (RAG) :\n{rag_context}\nUse these memories if relevant."

        hist_lines = []
        for turn in (history or [])[-6:]:
            prefix = name if turn.get("role") == "user" else "@siderealAstro13"
            hist_lines.append(f"{prefix}: {turn.get('content','').strip()}")
        hist_lines.append(f"{name}: {message}")
    else:
        system = (
            f"Tu es @siderealAstro13, astrologue karmique vedique sideral. "
            f"En dialogue avec {name}. Ton direct, oraculaire. "
            f"Interdit : signes zodiacaux. Max 100 mots par reponse."
        )
        if natal_ctx:
            system += f"\n{natal_ctx}"
        
        pseudo = profile.get("pseudo", "")
        rag_context = retrieve_context(pseudo, message, limit=3)
        if rag_context:
            system += f"\n\nSOUVENIRS KARMIQUES (RAG) :\n{rag_context}\nSers-toi de ces souvenirs si cela est pertinent pour répondre."

        hist_lines = []
        for turn in (history or [])[-6:]:
            prefix = name if turn.get("role") == "user" else "@siderealAstro13"
            hist_lines.append(f"{prefix} : {turn.get('content','').strip()}")
        hist_lines.append(f"{name} : {message}")

    return {"system": system, "user": "\n".join(hist_lines)}
