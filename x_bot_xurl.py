#!/usr/bin/env python3
"""
Bot X.com (Twitter) Karmic Gochara — via xurl CLI (PAS de tweepy).
Grok (xAI) génère la réponse EN (100% EN, marqueur 🗝️ Soul Debug :);
xurl gère mentions / DM / tweets. Format attendu :
    @BotHandle MM/DD/YYYY HH:MM Ville

Lancement (cronjob Hermes, python du .venv qui a openai OK) :
    cd ~/karmic.gochara && .venv/bin/python3 x_bot_xurl.py

Prérequis : xurl auth OK (`xurl whoami` répond le handle).
Variables : XAI_API_KEY (ou GROK_API_KEY), XURL_APP (défaut gochara),
XURL_AUTH (oauth2 | oauth1), GCS_PUBLIC_BUCKET (bucket GCS public pour
héberger l'infographie biorythme + le dataset, contourne la limite media X).
"""
import datetime
import os
import re
import sys
import json
import subprocess
import time
import traceback

from dotenv import load_dotenv
from openai import OpenAI
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astro_calc import calculate_transits
from karmic_lite import TRANSIT_LOC, generate_prompt, NATAL
from prompt_xbot_v2 import (SYSTEM_INSTRUCTION, DOMI_HINTS, cl_house, sign_of,
                            MAX_CHARS, build_system_instruction,
                            build_nakshatra_hints, PONDÉRATION,
                            validate_response, build_ton_posture, _sade_sati)
from transit_alerts import chandra_biorhythm, next_peak_biorhythm, biorhythm_at
from biorhythm_fmt import build_biorhythm_tweet, parse_target_date, build_biorhythm_hint, build_biorhythm_image

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
XURL_APP = os.getenv("XURL_APP", "gochara")
XURL_AUTH = os.getenv("XURL_AUTH", "oauth2")  # "oauth1" si OAuth 1.0a
GCS_PUBLIC_BUCKET = os.getenv("GCS_PUBLIC_BUCKET", "")
LAST_SEEN_FILE = "last_seen_id.txt"


def upload_to_gcs(local_path: str, gcs_key: str) -> str:
    """Upload un fichier vers le bucket GCS public et retourne l'URL publique.
    Utilise GOOGLE_CREDENTIALS_JSON (du .env) pour l'auth gsutil.
    Retourne '' si bucket non configuré / échec (fallback texte seul)."""
    if not GCS_PUBLIC_BUCKET:
        return ""
    creds = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    env = dict(os.environ)
    if creds:
        env["GOOGLE_CREDENTIALS_JSON"] = creds
    dst = f"gs://{GCS_PUBLIC_BUCKET}/{gcs_key}"
    r = subprocess.run(["gsutil", "-q", "cp", local_path, dst],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"  ⚠️ GCS upload échoué: {r.stderr.strip() or r.stdout.strip()}")
        return ""
    return f"https://karmicgochara.app/biorhythm/{gcs_key.split('/')[-1]}"


class CityNotFoundError(ValueError):
    """Raised when birthplace geocoding fails (city not found in Nominatim)."""


# ─── xurl wrapper (subprocess, jamais de secret inline) ──────────────────
def xurl(*args):
    cmd = ["xurl", "--app", XURL_APP] + list(args)
    if XURL_AUTH == "oauth1":
        cmd += ["--auth", "oauth1"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"xurl {args[0]} échoué: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def xurl_json(*args):
    return json.loads(xurl(*args))


def setup_x():
    # xurl gère l'auth (tokens dans ~/.xurl). On vérifie juste la portée.
    me = xurl_json("whoami")
    uname = me.get("data", {}).get("username")
    if not uname:
        raise RuntimeError("xurl non authentifié — lance `xurl auth oauth2 --app gochara`")
    print(f"✓ Connecté à X.com en tant que @{uname}")
    return uname


# ─── last seen ────────────────────────────────────────────────────────────
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


# ─── parse + geocode + thème (identique bot tweepy) ───────────────────────
def parse_user_request(text):
    pattern = r"(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+(?P<city>.+)"
    m = re.search(pattern, text)
    if not m:
        return None
    d = m.groupdict()
    try:
        month, day, year = int(d["month"]), int(d["day"]), int(d["year"])
        hour, minute = int(d["hour"]), int(d["minute"])
        city = d["city"].strip()
        if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100):
            return None
        return {"month": month, "day": day, "year": year,
                "hour": hour, "minute": minute, "location": city}
    except ValueError:
        return None


def geocode_location(city):
    geolocator = Nominatim(user_agent="karmic_gochara_bot")
    tf = TimezoneFinder()
    loc = geolocator.geocode(city)
    if loc:
        tz = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "UTC"
        return loc.latitude, loc.longitude, tz
    return None, None, None


def generate_karmic_data(user_data):
    lat, lon, tz = geocode_location(user_data["location"])
    if not lat:
        raise CityNotFoundError(f"Ville introuvable : {user_data['location']}")
    natal_info = {k: user_data[k] for k in ("year", "month", "day", "hour", "minute", "location")}
    natal_info.update(lat=lat, lon=lon, tz=tz)
    now = datetime.datetime.now()
    data = calculate_transits(natal_info, TRANSIT_LOC, now.year, now.month,
                              now.day, now.hour, now.minute)
    return generate_prompt(data, natal_info=natal_info), data, natal_info


# ─── Forward-ephemeris : prochain PIC de transit (pour le hook reply) ──────
# Plumbing astro (calendar_calc / transit_alerts) ; pas de prompt ici.
# A) peak lent×natal (orbe minimale)  + B) entree nakshatra perso.
# On prend le PLUS PROCHE des deux. Le libellé reste dans la reply
# (unguarded) — JAMAIS dans le DM Soul Debug (guard-locké).
def next_shift_date(natal_info, horizon_days=124):
    """Retourne (date_iso, label 'Nov 14', event_str) du prochain PIC futur.
    None si aucun dans l'horizon."""
    try:
        from transit_alerts import find_next_peak, find_next_nak_shift
    except Exception:
        return None, None, None
    try:
        pa, la, oa = find_next_peak(natal_info, horizon_days=horizon_days)
        pb, lb, nb = find_next_nak_shift(natal_info, horizon_days=horizon_days)
    except Exception:
        return None, None, None
    # choix du plus proche
    if pa and pb:
        if pa <= pb:
            peak, label, extra = pa, la, f" ({oa:.2f}°)"
        else:
            peak, label, extra = pb, lb, f" [{nb}]"
    elif pa:
        peak, label, extra = pa, la, f" ({oa:.2f}°)"
    elif pb:
        peak, label, extra = pb, lb, f" [{nb}]"
    else:
        return None, None, None
    return peak.isoformat(), peak.strftime("%b %d"), f"{label}{extra}"


# ─── Grok EN (openai SDK, OK en .venv) ─────────────────────────────────────
def call_grok(prompt, data=None, biorhythm_hint=None):
    if not XAI_API_KEY:
        print("❌ Erreur : Clé XAI_API_KEY manquante.")
        sys.exit(1)
    client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

    moon_nak = data["natal"].get("Lune ☽", {}).get("nakshatra", "") if data else ""
    moon_disp = data["natal"].get("Lune ☽", {}).get("display", "") if data else ""
    aspects = data.get("aspects", []) if data else []
    tense = [a for a in aspects if a.get("applying")] or aspects
    top = tense[0] if tense else None
    transit_nak = top.get("transit_nak", "") if top else ""
    transit_house = cl_house(top.get("transit_display", ""), moon_disp) if top else ""
    sat_nak = data["transits"].get("Saturne ♄", {}).get("nakshatra", "") if data else ""
    sade_sati = _sade_sati(moon_nak, sat_nak)
    dasha_lord = ""
    now = datetime.datetime.now()
    for d in (data.get("dashas", []) if data else []):
        try:
            if datetime.datetime.strptime(d.get("end_date", ""), "%d/%m/%Y") >= now:
                dasha_lord = d.get("lord", ""); break
        except ValueError:
            pass
    ton_hint = build_ton_posture(dasha_lord, sade_sati)
    moon_hint, transit_hint = build_nakshatra_hints(moon_nak, transit_nak, transit_house)
    # Couche D : si l'user a choisi un jour (biorythme), on cible CE jour-ci
    if biorhythm_hint:
        transit_hint = (transit_hint + "\n" + biorhythm_hint).strip()
    system_instruction = build_system_instruction(moon_hint, transit_hint, ton_hint)

    response = client.chat.completions.create(
        model="grok-4.3",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.5,
    )
    ai_response = response.choices[0].message.content.strip()

    ok, reasons = validate_response(ai_response, prompt)
    if ok:
        print(f"  ✓ GUARD VALIDE ({len(ai_response)} chars)")
    else:
        print(f"  ⚠️ GUARD REJET → {' ; '.join(reasons)} (réponse NON envoyée)")
    # Garde-fou : on n'envoie QUE si le guard passe (sinon DM potentiellement foireux).
    return ai_response if ok else None


# ─── X writes via xurl ─────────────────────────────────────────────────────
def send_dm(handle, text):
    h = handle if handle.startswith("@") else "@" + handle
    xurl("dm", h, text)


# ─── Feedback → dataset fine-tune ────────────────────────────────────────
FEEDBACK_STATE = "feedback_state.json"
DATASET = "dataset_finetuning.jsonl"


def _load_feedback_state():
    try:
        with open(FEEDBACK_STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_feedback_state(st):
    try:
        with open(FEEDBACK_STATE, "w") as f:
            json.dump(st, f)
    except Exception as e:
        print(f"  ⚠️ feedback state save: {e}")


def log_feedback(user_id, rating, soul_debug):
    """Ajoute une entrée feedback au dataset fine-tune + upload GCS.
    rating: +1 (👍) / -1 (👎). Ne crash jamais (best-effort)."""
    try:
        entry = {"user_id": str(user_id), "rating": rating,
                 "soul_debug": soul_debug, "ts": datetime.datetime.now().isoformat()}
        line = json.dumps(entry, ensure_ascii=False)
        with open(DATASET, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        # upload GCS si bucket configuré
        if GCS_PUBLIC_BUCKET:
            upload_to_gcs(DATASET, "dataset_finetuning.jsonl")
        print(f"  ✓ Feedback {rating:+d} loggé -> {DATASET}")
    except Exception as e:
        print(f"  ⚠️ log_feedback: {e}")


def parse_feedback(text):
    """Retourne +1 (👍/up), -1 (👎/down), ou 0 (pas un feedback)."""
    t = (text or "").lower()
    if any(k in t for k in ["👍", "up", "good", "yes", "👌", "❤️", "🔥"]):
        return 1
    if any(k in t for k in ["👎", "down", "bad", "no", "fix", "meh"]):
        return -1
    return 0


def process_mentions(my_handle):
    my_handle = (my_handle or "").lower()  # garde défensif : main() passe None sans crash
    print(f"[{datetime.datetime.now():%H:%M:%S}] Vérification des mentions...")
    last_id = get_last_seen_id()
    try:
        data = xurl_json("mentions", "-n", "20")
    except Exception as e:
        print(f"❌ mentions: {e}")
        return

    msgs = data.get("data") or []
    if not msgs:
        return
    new_last = msgs[0]["id"]

    for m in reversed(msgs):
        mid = m.get("id", "")
        if last_id and int(mid) <= int(last_id):
            continue  # déjà traité
        print(f"\n📩 Mention {mid} de {m.get('author_id')}: {m.get('text')}")
        # Feedback 👍/👎 ? (reply courte mentionnant le handle + emoji)
        fb = parse_feedback(m.get("text", ""))
        if fb != 0 and my_handle.lower() in m.get("text", "").lower():
            st = _load_feedback_state()
            soul_debug = st.get(str(m["author_id"]), "")
            if soul_debug:
                log_feedback(m["author_id"], fb, soul_debug)
                # on confirme poliment (reply courte, unguarded 280c)
                try:
                    xurl("reply", mid, "Thanks for the feedback! 🙏" if fb > 0 else "Noted — I'll sharpen it 🔧")
                except Exception:
                    pass
                continue
        ud = parse_user_request(m.get("text", ""))
        if not ud:
            print("  ! Format invalide ignoré.")
            continue
        try:
            prompt, kdata, natal_info = generate_karmic_data(ud)
            print("  ✓ Thème calculé, appel à Grok...")
        except CityNotFoundError as e:
            print(f"  ❌ GÉOCODE: ville introuvable ({e})")
            try:
                xurl("reply", mid,
                     "Sorry — I couldn't locate that birthplace. "
                     "Double-check the city spelling (e.g. 'Paris', 'London') and try again 🌍")
            except Exception:
                pass
            continue
        except Exception as e:
            print(f"  ❌ THÈME ÉCHEC: {type(e).__name__}: {e}")
            traceback.print_exc()
            continue

        # Couche D : l'user a-t-il choisi un jour via son biorythme ?
        biorhythm_hint = None
        try:
            tgt = parse_target_date(m.get("text", ""))
            if tgt:
                pt = biorhythm_at(natal_info, tgt)
                biorhythm_hint = build_biorhythm_hint(pt)
                print(f"  🌊 Jour choisi {tgt} -> hint biorythme injecté.")
            else:
                # pas de date dans la mention -> on cible le prochain sommet
                pk = next_peak_biorhythm(natal_info, days=90)
                biorhythm_hint = build_biorhythm_hint(pk)
                if pk:
                    print(f"  🌊 Sommet auto {pk['date']} -> hint biorythme injecté.")
        except Exception as e:
            print(f"  ⚠️ Biorhythm hint ignoré: {type(e).__name__}: {e}")

        try:
            ai_response = call_grok(prompt, kdata, biorhythm_hint=biorhythm_hint)
        except SystemExit as e:
            print(f"  ❌ GROK: SystemExit ({e}) — XAI_API_KEY manquante ?")
            continue
        except Exception as e:
            print(f"  ❌ GROK ÉCHEC: {type(e).__name__}: {e}")
            traceback.print_exc()
            continue
        if not ai_response:
            print("  ! Guard REJET — aucun envoi.")
            continue

        # 1) Reply publique EN — livrée si pas déjà postée (X refuse duplicate)
        # Hook de rappel (funnel fil public) + hashtags flux. DM Soul Debug reste guard-locké,
        # donc le "reviens le X" VA ICI. <date> rempli par forward-ephemeris (next_shift_date).
        try:
            _, shift_label, _ = next_shift_date(natal_info)
            shift_txt = f"~{shift_label}" if shift_label else "~soon"
            xurl("reply", mid,
                 "Your karmic Soul Debug just landed in your DMs 🌌✨\n\n"
                 f"Your next shift peaks {shift_txt} — DM me your city+time that day for a fresh one.\n\n"
                 "Did this land? 👍 or 👎 @siderealAstro13\n\n"
                 "Full app + live transits → https://karmicgochara.app\n\n"
                 "#ChandraLagna #SiderealAstrology #KarmicAstrology #karma #astrology")
            print("  ✓ Réponse publique postée.")
        except Exception as e:
            # duplicate content (déjà répondu) ou autre -> on loggue, on tente quand meme le DM
            print(f"  ⚠️ REPLY ÉCHEC (déjà posté ?): {type(e).__name__}: {e}")

        # 2) DM EN — best-effort (MP fermés = échec loggué, reply déjà tenté)
        try:
            # xurl user veut un username; l'API raw /2/users/<id> renvoie le username
            udata = xurl_json("/2/users/" + str(m["author_id"]))
            handle = udata.get("data", {}).get("username", "")
            if not handle:
                raise ValueError(f"username introuvable pour {m['author_id']}")
            send_dm(handle, ai_response)
            print("  ✓ DM envoyé.")
            # on stocke la Soul Debug pour matcher un futur 👍/👎 de cet user
            st = _load_feedback_state()
            st[str(m["author_id"])] = ai_response
            _save_feedback_state(st)
        except Exception as e:
            print(f"  ⚠️ DM ÉCHEC (MP fermés ?): {type(e).__name__}: {e}")
            traceback.print_exc()

    save_last_seen_id(new_last)


def tweet_biorhythm():
    """Couche C : poste le tweet biorythme lunaire (chart de Jérôme = contenu
    de marque @siderealAstro). L'user qui répond recoit SON biorythme en DM.
    Axe unique (density/has_node) vient de transit_alerts, format = biorhythm_fmt.
    """
    print("=== Tweet biorythme lunaire ===")
    try:
        chart = {"year": NATAL["year"], "month": NATAL["month"], "day": NATAL["day"],
                 "hour": NATAL["hour"], "minute": NATAL["minute"],
                 "lat": NATAL["lat"], "lon": NATAL["lon"], "tz": NATAL.get("tz", "Europe/Paris")}
    except Exception as e:
        print(f"  ⚠️ Profil natal illisible: {e}")
        return
    try:
        curve = chandra_biorhythm(chart, days=90)
        if not curve:
            print("  ⚠️ Courbe vide (profil incomplet).")
            return
        # infographie locale (matplotlib, 0€) -> upload GCS -> lien dans tweet
        img = build_biorhythm_image(curve)
        tweet = build_biorhythm_tweet(curve)
        posted = False
        if img and os.path.exists(img) and GCS_PUBLIC_BUCKET:
            try:
                key = f"biorhythm/chandra-biorhythm-lunaire_{datetime.datetime.now():%Y-%m-%d-%H%M}.png"
                url = upload_to_gcs(img, key)
                if url:
                    xurl("post", f"{tweet}\n\n📈 {url}")
                    print(f"  ✓ Tweet biorythme + infographie (lien GCS) postés ({len(tweet)}c, {url}).")
                    posted = True
            except Exception as e:
                print(f"  ⚠️ GCS/lien échoué ({e}), tweet texte seul.")
        if not posted:
            xurl("post", tweet)
            print(f"  ✓ Tweet biorythme posté (texte seul, {len(tweet)}c).")
    except Exception as e:
        print(f"  ⚠️ TWEET Biorhythm ÉCHEC: {type(e).__name__}: {e}")
        traceback.print_exc()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true",
                   help="single poll then exit (for cron-driven runs)")
    p.add_argument("--tweet-biorhythm", action="store_true",
                   help="post the daily lunar biorhythm tweet (Chandra Lagna)")
    args = p.parse_args()

    print("=== Démarrage Bot X.com (xurl) Karmic Gochara ===")
    uname = setup_x()
    if args.tweet_biorhythm:
        tweet_biorhythm()
        print("=== Fin tweet biorythme ===")
        return
    if args.once:
        print("\nMode one-shot (1 poll)...")
        process_mentions(uname)
        print("=== Fin du poll unique ===")
        return
    print("\nÉcoute en cours... (Ctrl+C pour arrêter)")
    try:
        while True:
            process_mentions(uname)
            time.sleep(120)
    except KeyboardInterrupt:
        print("\nArrêt du bot.")


if __name__ == "__main__":
    main()
