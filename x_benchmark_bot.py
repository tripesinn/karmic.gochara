#!/usr/bin/env python3
"""
x_benchmark_bot.py — Benchmark Interactif des IA pour l'Astrologie Karmique

Flow :
  1) Parse les mentions au format : @Bot MM/DD/YYYY HH:MM Ville
  2) Calcule le thème karmique
  3) Génère l'interprétation via 3-4 providers en parallèle (Gemini, Claude, Grok, local)
  4) Envoie le comparatif en DM avec les labels A/B/C/D
  5) Collecte les votes (l'utilisateur reply avec sa préférence)
  6) Sauvegarde dans benchmark_votes.json → alimente la page /benchmark

Utilisation :
  python3 x_benchmark_bot.py          # mode continu (polling toutes les 2 min)
  python3 x_benchmark_bot.py --once   # un seul cycle (pour cron)

Dépendances : tweepy, python-dotenv, geopy, timezonefinder
"""

import datetime
import json
import os
import re
import sys
import time
import threading
import urllib.request
import base64
import urllib.parse

import tweepy
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astro_calc import calculate_transits
from karmic_lite import TRANSIT_LOC, generate_prompt
import gemini_api

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
LOCAL_API_URL = "http://127.0.0.1:8000/v1/chat/completions"
LOCAL_MODEL = "phi-4-4bit"
LOCAL_API_KEY = "dummy"

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

LAST_SEEN_FILE = "benchmark_last_seen_id.txt"
VOTES_FILE = "benchmark_votes.json"
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Providers disponibles ──────────────────────────────────────────────────────
PROVIDERS = []

if GEMINI_API_KEY:
    PROVIDERS.append({
        "id": "gemini",
        "name": "Google Gemini",
        "emoji": "\U0001f7e2",  # 🟢
        "available": True
    })
if ANTHROPIC_KEY:
    PROVIDERS.append({
        "id": "claude",
        "name": "Anthropic Claude",
        "emoji": "\U0001f451",  # 👑
        "available": True
    })
if XAI_API_KEY:
    PROVIDERS.append({
        "id": "grok",
        "name": "xAI Grok",
        "emoji": "\u26a1",  # ⚡
        "available": True
    })
# Toujours disponible si le serveur local tourne
PROVIDERS.append({
    "id": "local",
    "name": "Phi-4 Local",
    "emoji": "\U0001f4bb",  # 💻
    "available": True
})


# ── Helpers X hérités ────────────────────────────────────────────────────────
def setup_x_client():
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("❌ Clés X.com manquantes.")
        sys.exit(1)
    # Générer un Bearer Token à partir des clés OAuth2
    bearer_token = None
    try:
        b64 = base64.b64encode(f"{X_API_KEY}:{X_API_SECRET}".encode()).decode()
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
        req = urllib.request.Request(
            "https://api.twitter.com/oauth2/token",
            data=data,
            headers={
                "Authorization": f"Basic {b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )
        resp = urllib.request.urlopen(req)
        token_data = json.loads(resp.read())
        bearer_token = token_data.get("access_token")
    except Exception as e:
        print(f"⚠ Impossible de générer le Bearer Token: {e}")
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    me = client.get_me()
    print(f"✓ Connecté à X.com en tant que @{me.data.username}")
    return client, me.data.id


def get_last_seen_id():
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE) as f:
            c = f.read().strip()
            if c.isdigit():
                return c
    return None


def save_last_seen_id(tweet_id):
    with open(LAST_SEEN_FILE, "w") as f:
        f.write(str(tweet_id))


# ── Parsing (identique à x_grok_bot.py) ─────────────────────────────────────
def parse_user_request(text):
    """Extrait MM/DD/YYYY HH:MM Ville depuis le texte du tweet."""
    pattern = r"(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+(?P<city>.+)"
    match = re.search(pattern, text)
    if not match:
        return None
    data = match.groupdict()
    try:
        month, day, year = int(data['month']), int(data['day']), int(data['year'])
        hour, minute = int(data['hour']), int(data['minute'])
        city = data['city'].strip()
        if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2026):
            return None
        return {"month": month, "day": day, "year": year, "hour": hour, "minute": minute, "location": city}
    except ValueError:
        return None


def geocode_location(city):
    geolocator = Nominatim(user_agent="karmic_gochara_benchmark")
    tf = TimezoneFinder()
    location = geolocator.geocode(city)
    if location:
        lat, lon = location.latitude, location.longitude
        tz = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        return lat, lon, tz
    return None, None, None


def generate_karmic_data(user_data):
    """Calcule et génère le prompt karmique à partir des données utilisateur."""
    lat, lon, tz = geocode_location(user_data["location"])
    if not lat:
        raise ValueError(f"Ville introuvable : {user_data['location']}")
    natal_info = {
        "year": user_data["year"], "month": user_data["month"], "day": user_data["day"],
        "hour": user_data["hour"], "minute": user_data["minute"],
        "location": user_data["location"], "lat": lat, "lon": lon, "tz": tz
    }
    now = datetime.datetime.now()
    data = calculate_transits(
        natal_info, TRANSIT_LOC,
        now.year, now.month, now.day, now.hour, now.minute
    )
    return generate_prompt(data, natal_info=natal_info), natal_info


# ── Appels aux providers en parallèle ───────────────────────────────────────
_SYSTEM_PROMPT = (
    "Tu es siderealAstro13, experte en Astrologie Karmique Védique Sidérale (Chandra Lagna). "
    "Tu vas recevoir un état des lieux de transits astrologiques karmiques. "
    "Rédige une interprétation personnalisée en français, percutante, d'environ 200 mots. "
    "Structure : 1) Point chaud du moment, 2) Action recommandée, 3) Horizon temporel. "
    "Sois précise, sans jargon excessif. Parle directement à la personne."
)


def _call_grok(prompt: str) -> dict:
    from openai import OpenAI
    start = time.time()
    client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")
    resp = client.chat.completions.create(
        model="grok-4.3",
        messages=[{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        max_tokens=600, temperature=0.7
    )
    text = resp.choices[0].message.content.strip()
    elapsed = time.time() - start
    return {"text": text, "speed": round(elapsed, 2), "tokens": resp.usage.completion_tokens if resp.usage else 0, "provider": "grok"}


def _call_claude(prompt: str) -> dict:
    import anthropic
    start = time.time()
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    resp = client.messages.create(
        model="claude-3-5-sonnet-latest",
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600, temperature=0.7
    )
    text = resp.content[0].text.strip()
    elapsed = time.time() - start
    return {"text": text, "speed": round(elapsed, 2), "tokens": resp.usage.output_tokens if resp.usage else 0, "provider": "claude"}


def _call_gemini(prompt: str) -> dict:
    start = time.time()
    text = gemini_api.generate(
        system=_SYSTEM_PROMPT,
        prompt=prompt,
        max_tokens=600,
        model="gemini-2.0-flash",
        user_key=GEMINI_API_KEY
    )
    elapsed = time.time() - start
    # Estimation du nombre de tokens (approximatif)
    tokens = max(1, len(text.split()))
    return {"text": text, "speed": round(elapsed, 2), "tokens": tokens, "provider": "gemini"}


def _call_local(prompt: str) -> dict:
    import json as _json
    start = time.time()
    payload = _json.dumps({
        "model": LOCAL_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }).encode()
    req = urllib.request.Request(
        LOCAL_API_URL, data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {LOCAL_API_KEY}"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = _json.loads(resp.read())
        text = result["choices"][0]["message"]["content"].strip()
        elapsed = time.time() - start
        usage = result.get("usage", {})
        tokens = usage.get("completion_tokens", 0)
        return {"text": text, "speed": round(elapsed, 2), "tokens": tokens, "provider": "local"}
    except Exception as e:
        return {"text": f"[Erreur serveur local : {e}]", "speed": 0, "tokens": 0, "provider": "local", "error": str(e)}


def call_all_providers(prompt: str) -> list[dict]:
    """Lance tous les providers en parallèle et retourne les résultats."""
    threads = []
    results = {}
    lock = threading.Lock()

    targets = []

    if XAI_API_KEY:
        targets.append(("grok", _call_grok, prompt))
    if ANTHROPIC_KEY:
        targets.append(("claude", _call_claude, prompt))
    if GEMINI_API_KEY:
        targets.append(("gemini", _call_gemini, prompt))
    # Toujours tenter le local
    targets.append(("local", _call_local, prompt))

    def run(provider_id, func, arg):
        try:
            result = func(arg)
        except Exception as e:
            result = {"text": f"[Erreur {provider_id}: {e}]", "speed": 0, "tokens": 0, "provider": provider_id, "error": str(e)}
        with lock:
            results[provider_id] = result

    for pid, func, arg in targets:
        t = threading.Thread(target=run, args=(pid, func, arg), daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=130)  # timeout global 130s

    return [results.get(pid) for pid in ["gemini", "claude", "grok", "local"] if pid in results]


# ── DM & Vote ────────────────────────────────────────────────────────────────
_LABELS = ["A", "B", "C", "D"]
_EMOJIS = ["\U0001f7e2", "\U0001f451", "\u26a1", "\U0001f4bb"]  # 🟢 👑 ⚡ 💻
_PROVIDER_NAMES = {"gemini": "Gemini", "claude": "Claude", "grok": "Grok", "local": "Phi-4"}


def format_comparison_dm(results: list[dict], natal_info: dict) -> str:
    """Construit le message DM avec les 3-4 interprétations côte à côte."""
    lines = [
        "\u2728 ANALYSE KARMIQUE MULTI-IA \u2728",
        f"Thème : {natal_info['location']}",
        f"Date   : {natal_info['day']:02d}/{natal_info['month']:02d}/{natal_info['year']}",
        f"Heure : {natal_info['hour']:02d}:{natal_info['minute']:02d}",
        "",
        "3 IA ont interprété ton karma. Chacune a son style.",
        "Laquelle te parle le plus ?",
        ""
    ]
    for i, r in enumerate(results):
        label = _LABELS[i]
        emoji = _EMOJIS[i] if i < len(_EMOJIS) else "\u2b50"
        prov_name = _PROVIDER_NAMES.get(r.get("provider", ""), r.get("provider", ""))
        speed = r.get("speed", 0)
        lines.append(f"{emoji} {label} — {prov_name} ({speed}s)")
        lines.append("")
        # Texte tronqué à ~350 caractères pour rester dans les limites DM
        text = r["text"][:350]
        if len(r["text"]) > 350:
            text += "..."
        lines.append(text)
        lines.append("")
        lines.append("\u2500" * 30)
        lines.append("")

    lines.append("")
    lines.append("Réponds A, B ou C (ou D si 4 modèles) pour voter !")
    lines.append("Ton vote aide à améliorer l'oracle \u2728")
    return "\n".join(lines)


def save_vote(user_id: str, choice: str, results: list[dict], natal_info: dict):
    """Sauvegarde un vote dans benchmark_votes.json."""
    votes = []
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE) as f:
                votes = json.load(f)
        except (json.JSONDecodeError, Exception):
            votes = []

    chosen_idx = ord(choice.upper()) - ord("A")
    chosen_provider = results[chosen_idx]["provider"] if chosen_idx < len(results) else "unknown"

    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": str(user_id),
        "choice": choice.upper(),
        "chosen_provider": chosen_provider,
        "natal": {
            "location": natal_info["location"],
            "date": f"{natal_info['year']}-{natal_info['month']:02d}-{natal_info['day']:02d}",
            "time": f"{natal_info['hour']:02d}:{natal_info['minute']:02d}"
        },
        "results": [
            {"provider": r["provider"], "speed": r.get("speed"), "tokens": r.get("tokens", 0)}
            for r in results
        ]
    }
    votes.append(record)
    with open(VOTES_FILE, "w") as f:
        json.dump(votes, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Vote sauvegardé : {choice} → {chosen_provider}")


def generate_benchmark_html():
    """Génère une page HTML statique avec les résultats du benchmark."""
    if not os.path.exists(VOTES_FILE):
        return
    with open(VOTES_FILE) as f:
        votes = json.load(f)

    if not votes:
        return

    # Stats
    total = len(votes)
    provider_counts = {}
    for v in votes:
        p = v.get("chosen_provider", "unknown")
        provider_counts[p] = provider_counts.get(p, 0) + 1

    provider_names = {"gemini": "Gemini", "claude": "Claude", "grok": "Grok", "local": "Phi-4 Local"}
    stats_html = ""
    for pid, count in sorted(provider_counts.items(), key=lambda x: -x[1]):
        pct = round(count / total * 100)
        name = provider_names.get(pid, pid)
        stats_html += f"""
        <div style="margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;font-family:monospace;font-size:0.85rem;">
            <span style="color:var(--gold);">{name}</span>
            <span>{count} votes ({pct}%)</span>
          </div>
          <div style="height:8px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;background:var(--gold);border-radius:4px;"></div>
          </div>
        </div>"""

    # Derniers votes
    recent_html = ""
    for v in votes[-5:]:
        p = provider_names.get(v.get("chosen_provider", ""), v.get("chosen_provider", ""))
        loc = v.get("natal", {}).get("location", "?")
        when = v.get("timestamp", "")[:10]
        recent_html += f"<tr><td style='padding:4px 8px;color:var(--gold-dim);'>{when}</td><td style='padding:4px 8px;'>{loc}</td><td style='padding:4px 8px;color:var(--gold);'>{p}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Benchmark IA — Quelle IA comprend le mieux ton karma ?</title>
  <meta name="description" content="Comparatif interactif des intelligences artificielles pour l'interprétation de l'astrologie karmique védique. Gemini, Claude, Grok et Phi-4 évalués par les utilisateurs réels.">
  <meta property="og:title" content="✦ Benchmark des Oracles IA — Karmic Gochara">
  <meta property="og:description" content="{total} utilisateurs ont déjà voté. Quelle IA interprète le mieux ton karma ?">
  <meta property="og:type" content="website">
  <style>
    :root {{ --bg: #0a0a1a; --gold: #c9a84c; --gold-dim: #a8862c; --text: #e0d5c0; --text-dim: #8a7e6a; --border: rgba(201,168,76,0.2); }}
    body {{ background:var(--bg); color:var(--text); font-family:'Georgia',serif; margin:0; padding:2rem 1rem; line-height:1.6; }}
    .container {{ max-width:720px; margin:0 auto; }}
    h1 {{ font-family:'Cinzel',serif; color:var(--gold); font-weight:400; font-size:1.5rem; text-align:center; letter-spacing:0.15em; }}
    h2 {{ font-family:'Cinzel',serif; color:var(--gold); font-weight:400; font-size:1.1rem; margin-top:2rem; }}
    .subtitle {{ text-align:center; color:var(--text-dim); font-style:italic; margin-bottom:2rem; }}
    .stats-card {{ background:rgba(255,255,255,0.02); border:1px solid var(--border); border-radius:8px; padding:1.5rem; margin-bottom:1.5rem; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
    th {{ text-align:left; color:var(--gold-dim); font-family:monospace; font-size:0.75rem; text-transform:uppercase; padding:4px 8px; border-bottom:1px solid var(--border); }}
    .footer {{ text-align:center; margin-top:3rem; font-size:0.75rem; color:var(--text-dim); }}
    .cta {{ display:inline-block; background:var(--gold); color:var(--bg); padding:0.6rem 1.5rem; border-radius:4px; text-decoration:none; font-family:'Cinzel',serif; margin:1rem auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>✦ Benchmark des Oracles IA</h1>
    <p class="subtitle">{total} utilisateurs ont voté — Quelle IA résonne avec ton karma ?</p>

    <div class="stats-card">
      <h2>Classement</h2>
      {stats_html}
    </div>

    <div class="stats-card">
      <h2>Derniers votes</h2>
      <table>
        <tr><th>Date</th><th>Thème</th><th>Préférée</th></tr>
        {recent_html}
      </table>
    </div>

    <div style="text-align:center;">
      <p style="color:var(--text-dim);">Participe au benchmark :</p>
      <p style="font-family:monospace;background:rgba(255,255,255,0.03);padding:0.8rem;border-radius:4px;border:1px solid var(--border);">
        Tweet <strong>@karmicgochara 15/03/1990 14:30 Paris</strong><br>
        <span style="font-size:0.75rem;color:var(--text-dim);">Reçois 3 interprétations et vote pour ta préférée ✨</span>
      </p>
    </div>

    <div class="footer">
      <p>Karmic Gochara — Astrologie Védique Sidérale · Chandra Lagna · DK Ayanamsa</p>
      <p>@siderealAstro13</p>
    </div>
  </div>
</body>
</html>"""
    path = os.path.join(RESULTS_DIR, "index.html")
    with open(path, "w") as f:
        f.write(html)
    print(f"  ✓ Page benchmark générée : {path}")


# ── Traitement des mentions ──────────────────────────────────────────────────
def process_benchmark_vote(client, mention, results_map):
    """Vérifie si une mention est un vote (A/B/C/D) dans les 24h suivant une analyse."""
    text = mention.text.strip().upper()
    # Ignorer le tweet original qui contient les dates
    if parse_user_request(mention.text):
        return False

    # Cherche A, B, C ou D dans le texte
    valid_choices = {"A", "B", "C", "D"}
    words = set(text.split())
    # Enlève le @mention du début
    mention_parts = text.split()
    clean_words = {w for w in mention_parts if not w.startswith("@")}

    for choice in valid_choices:
        if choice in clean_words or choice.lower() in clean_words:
            # Chercher si cet utilisateur a une analyse récente
            user_id = mention.author_id
            user_dir = os.path.join(RESULTS_DIR, str(user_id))
            pending_file = os.path.join(user_dir, "pending.json")
            if os.path.exists(pending_file):
                with open(pending_file) as f:
                    data = json.load(f)
                if datetime.datetime.fromisoformat(data["expires"]) > datetime.datetime.now():
                    save_vote(user_id, choice, data["results"], data["natal_info"])
                    # Répondre publiquement pour le remercier
                    chosen_provider = _PROVIDER_NAMES.get(data["results"][ord(choice) - ord("A")]["provider"], "?")
                    public_reply = (
                        f"Merci pour ton vote {choice} → {chosen_provider} ! \u2728\u2728\u2728\n"
                        "Ton préférence aide à améliorer l'oracle. "
                        "Les résultats sont visibles ici : karmicgochara.app/benchmark\n"
                        "#BenchmarkIA #AstrologieKarmique #GocharaKarmique"
                    )
                    try:
                        client.create_tweet(text=public_reply, in_reply_to_tweet_id=mention.id)
                        print(f"  ✓ Réponse publique postée pour le vote {choice}")
                    except Exception as e:
                        print(f"  ⚠ Impossible de répondre au vote : {e}")
                    os.remove(pending_file)
                    generate_benchmark_html()
                    return True
    return False


def process_mentions(client, my_user_id):
    """Vérifie les nouvelles mentions : soit demande d'analyse, soit vote."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Vérification des mentions...")
    last_id = get_last_seen_id()

    try:
        mentions = client.get_users_mentions(
            id=my_user_id,
            since_id=last_id,
            tweet_fields=["author_id", "created_at"]
        )
        if not mentions.data:
            return

        new_last_id = mentions.data[0].id

        for mention in reversed(mentions.data):
            print(f"\n📩 Mention de {mention.author_id}: {mention.text[:80]}...")

            # 1) Essayer de voter d'abord (réponse à une analyse existante)
            if process_benchmark_vote(client, mention, {}):
                continue

            # 2) Sinon, parser comme nouvelle demande d'analyse
            user_data = parse_user_request(mention.text)
            if user_data:
                print(f"  ✓ Demande valide : {user_data}")
                try:
                    prompt, natal_info = generate_karmic_data(user_data)
                    print("  ✓ Thème calculé, appel aux providers...")

                    results = call_all_providers(prompt)
                    print(f"  ✓ {len(results)} interprétations reçues")

                    # Filtrer les résultats valides (éliminer les erreurs)
                    valid_results = [r for r in results if r.get("text") and not r.get("error")]
                    if not valid_results:
                        raise Exception("Aucun provider n'a répondu correctement.")

                    # Envoyer le DM
                    dm_text = format_comparison_dm(valid_results, natal_info)
                    try:
                        client.create_direct_message(participant_id=mention.author_id, text=dm_text)
                        print("  ✓ DM envoyé avec le comparatif !")
                    except Exception as e:
                        print(f"  ⚠ DM impossible (l'utilisateur suit-il le bot ?) : {e}")
                        # Fallback : réponse publique avec un lien
                        fallback = f"Ton analyse est prête ! Suis-nous et DM ouvert pour la recevoir \u2728 karmicgochara.app"
                        client.create_tweet(text=fallback, in_reply_to_tweet_id=mention.id)
                        continue

                    # Sauvegarder le pending pour 24h (pour collecter le vote)
                    user_dir = os.path.join(RESULTS_DIR, str(mention.author_id))
                    os.makedirs(user_dir, exist_ok=True)
                    with open(os.path.join(user_dir, "pending.json"), "w") as f:
                        json.dump({
                            "results": valid_results,
                            "natal_info": natal_info,
                            "expires": (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
                        }, f, indent=2, ensure_ascii=False)

                    # Tweet public
                    public_reply = (
                        "Ton analyse karmique multi-IA vient de t'être envoyée en DM ! \u2728\n"
                        "Réponds A, B ou C pour dire quelle interprétation te parle le plus !\n"
                        "#BenchmarkIA #AstrologieKarmique #GocharaKarmique"
                    )
                    client.create_tweet(text=public_reply, in_reply_to_tweet_id=mention.id)
                    print("  ✓ Analyse envoyée + réponse publique postée !")

                except Exception as e:
                    print(f"  ❌ Erreur : {e}")
                    error_msg = f"Désolé, erreur lors de l'analyse : {e}"
                    client.create_tweet(text=error_msg, in_reply_to_tweet_id=mention.id)
            else:
                print("  ! Format invalide (ignoré)")

        save_last_seen_id(new_last_id)

    except tweepy.errors.TooManyRequests:
        print("⚠️ Rate limit X atteint.")
    except Exception as e:
        print(f"❌ Erreur polling : {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=== Karmic Gochara — Benchmark IA Multi-Provider ===")
    print(f"  Providers dispo : {[p['id'] for p in PROVIDERS if p['available']]}")

    client, my_user_id = setup_x_client()
    generate_benchmark_html()  # Régénère la page au démarrage

    once = "--once" in sys.argv
    print(f"\\n{'Run unique' if once else 'Écoute continue (Ctrl+C pour arrêter)...'}")

    try:
        while True:
            process_mentions(client, my_user_id)
            if once:
                break
            time.sleep(120)  # 2 min entre les polls
    except KeyboardInterrupt:
        print("\nArrêt du bot benchmark.")


if __name__ == "__main__":
    main()
