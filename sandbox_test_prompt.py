#!/usr/bin/env python3
"""
SANDBOX — VALIDATEUR NU du prompt X Bot (Karmic Gochara).
Importe SYSTEM_INSTRUCTION / DOMI_HINTS / cl_house depuis prompt_xbot_v2.py
(le terrain de jeu de Jérôme, reviewable par AGY).

RÔLE : appeler Grok (cible réelle X Bot) OU gemma local (fallback dev),
mesurer tokens/temps, et montrer le rendu live (truncate pour simuler la
contrainte DM X ≤200). NE FAIT PLUS AUCUNE ÉCRITURE DATASET — le fine-tuning
est géré séparément avec un guard corrigé (rejet si cut / anti-jargon).

Usage:
  .venv/bin/python3 sandbox_test_prompt.py            # Grok (réel)
  .venv/bin/python3 sandbox_test_prompt.py --local    # gemma oMLX (dev)
  .venv/bin/python3 sandbox_test_prompt.py --rich     # mode riche 4 blocs

Aucune modif de x_grok_bot.py / karmic_lite.py.
"""
import sys, os, time, datetime

from dotenv import load_dotenv
load_dotenv(".env", override=True)

from karmic_lite import NATAL, TRANSIT_LOC, generate_prompt
from astro_calc import calculate_transits
from prompt_xbot_v2 import (SYSTEM_INSTRUCTION, DOMI_HINTS, cl_house, sign_of,
                            MAX_CHARS, build_system_instruction,
                            build_nakshatra_hints, PONDÉRATION,
                            validate_response, build_ton_posture, _sade_sati)


# ─── INJECTION DOMIFICATION (miroir de prompt_xbot_v2.cl_house) ────────────
def inject_domination(user_prompt: str, data: dict) -> str:
    """Injecte 'Maison X' après chaque planète clé du bloc natal/transit."""
    moon_disp = data["natal"].get("Lune ☽", {}).get("display", "")
    def repl(line):
        if ":" not in line:
            return line
        head, _, body = line.partition(":")
        for pname in ["Lune natale ☽", "Ketu ☋", "Rahu ☊", "Chiron ⚷", "Lilith ⚸",
                      "Porte Visible ⊙", "PV ⊙", "Porte Invisible ⊗", "PI ⊗",
                      "Saturne ♄", "Uranus ♅", "Jupiter ♃"]:
            if pname in head:
                h = cl_house(body, moon_disp)
                if h:
                    return f"{line.rstrip()}  [Maison {h}]"
        return line
    return "\n".join(repl(ln) for ln in user_prompt.split("\n"))


def call_grok(system, user):
    import requests
    v = os.getenv("GROK_API_KEY")
    if not v:
        raise RuntimeError("GROK_API_KEY absent")
    r = requests.post("https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {v}", "Content-Type": "application/json"},
        json={"model": "grok-4.3", "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}],
            "max_tokens": 300, "temperature": 0.5},
        timeout=60)
    r.raise_for_status()
    resp = r.json()["choices"][0]["message"]["content"]
    # Passe 2 : si la réponse finit en plein milieu de phrase, demande une conclusion
    if not resp.rstrip().endswith((".", "!", "?")):
        fix = requests.post("https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {v}", "Content-Type": "application/json"},
            json={"model": "grok-4.3", "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": resp},
                {"role": "user", "content": "Termine la dernière phrase avec 2-4 mots MAX qui clôturent net, suivis d'un point final. Réponds UNIQUEMENT par ces mots, rien d'autre."}],
                "max_tokens": 60, "temperature": 0.4},
            timeout=60)
        fix.raise_for_status()
        add = fix.json()["choices"][0]["message"]["content"].strip()
        resp = resp.rstrip() + " " + add
    return resp


def call_local(system, user):
    sys.path.insert(0, "scripts")
    from query_local_ai import query_local_ai
    return query_local_ai(user, system)


def truncate(resp, limit=MAX_CHARS):
    """Simule la contrainte live DM X (≤200). GARDE le format 3 lignes.
    Note: ceci est une SIMULATION d'affichage — le dataset ne doit jamais
    recevoir de réponse tronquée (voir prompt_xbot_v2.py + guard séparé)."""
    if len(resp) <= limit:
        return resp, False
    lines = resp.split("\n")
    kept = []
    used = 0
    for ln in lines:
        if used + len(ln) + 1 <= limit:
            kept.append(ln)
            used += len(ln) + 1
        else:
            remain = limit - used
            if remain > 10:
                c = ln.rfind(" ", 0, remain)
                piece = ln[:c if c > 0 else remain].rstrip(" ,;:")
                # On NE ré-injecte PAS de '.' : un fragment coupé reste visiblement incomplet.
                kept.append(piece.rstrip())
            break
    return "\n".join(kept), True


def main():
    use_local = "--local" in sys.argv
    rich_mode = "--rich" in sys.argv
    now = datetime.datetime.now()
    data = calculate_transits(NATAL, TRANSIT_LOC, now.year, now.month, now.day, now.hour, now.minute)

    user = generate_prompt(data, natal_info=NATAL, rich=rich_mode)
    user = inject_domination(user, data)

    # ─── INJECTION CHIRURGICALE NAKSHATRA + MAISON + TON (Playground v2.2) ─
    # moon_nak = Lune natale (Chandra Lagna) = filtre d'incarnation (point 1, 20%).
    # transit_nak = NAKSHATRA DE LA PLANETE LA PLUS TENDUE (orbe min, applying) :
    # c'est la texture du mental active dans le champ de vie (point 3 / 50% Friction).
    # transit_house = cl_house de cette planète -> ancre la maison 50% (Option B+).
    moon_nak = data["natal"].get("Lune ☽", {}).get("nakshatra", "")
    moon_disp = data["natal"].get("Lune ☽", {}).get("display", "")
    aspects = data.get("aspects", [])
    tense = [a for a in aspects if a.get("applying")] or aspects
    top = tense[0] if tense else None  # deja trie par orb croissant dans astro_calc
    transit_nak = top.get("transit_nak", "") if top else ""
    transit_house = cl_house(top.get("transit_display", ""), moon_disp) if top else ""
    # Sade Sati : Saturne transit dans le Nakshatra lunaire ±1 (catégoriel)
    sat_nak = data["transits"].get("Saturne ♄", {}).get("nakshatra", "")
    sade_sati = _sade_sati(moon_nak, sat_nak)
    # Dasha courant (Pilier 5) -> posture
    dasha_lord = ""
    for d in data.get("dashas", []):
        try:
            if datetime.datetime.strptime(d.get("end_date", ""), "%d/%m/%Y") >= now:
                dasha_lord = d.get("lord", ""); break
        except ValueError:
            pass
    ton_hint = build_ton_posture(dasha_lord, sade_sati)
    moon_hint, transit_hint = build_nakshatra_hints(moon_nak, transit_nak, transit_house)
    system = build_system_instruction(moon_hint, transit_hint, ton_hint)

    n_in = len(user) // 4
    target = "GROK (x.ai)" if not use_local else "gemma oMLX (local)"

    if moon_nak or transit_nak:
        print("NAKSHATRA INJECT (chirurgical, Option B) :")
        if moon_hint:
            print("  • " + moon_hint)
        if transit_hint:
            src = (f"{top['transit_planet']} {top['aspect']} {top['natal_planet']} "
                   f"orbe {top['orb']}°" if top else "?")
            print(f"  • {transit_hint}  [source: {src}]")
        if transit_house:
            print(f"  • MAISON TRANSIT CALCULÉE : {transit_house}  (cl_house)")
        print(f"  • TON : {dasha_lord or '?'}{' + SADE SATI' if sade_sati else ''}")
        print("─" * 60)

    print("=" * 60)
    print(f"TARGET: {target} | PROMPT ~ {n_in} tok ({len(user)} chars)")
    print("=" * 60)
    print("\n" + "─" * 60)
    print("PROMPT USER GÉNÉRÉ (avec domification CL):")
    print("─" * 60)
    print(user)

    t0 = time.time()
    try:
        resp = call_local(system, user) if use_local else call_grok(system, user)
    except Exception as e:
        print(f"ERREUR: {e}")
        sys.exit(1)
    dt = time.time() - t0

    # Nettoyage espaces trailing (Grok en émet parfois) pour l'affichage
    resp_clean = "\n".join(ln.rstrip() for ln in resp.split("\n"))
    resp2, cut = truncate(resp_clean)
    n_out = len(resp2) // 4

    # ─── GUARD READ-ONLY (validate_only) : VALIDE/REJET + densité ──────────
    ok, reasons = validate_response(resp_clean, user)
    print(f"\nGUARD : {'✅ VALIDE' if ok else '❌ REJET'}" +
          ("" if ok else " → " + " ; ".join(reasons)))
    words = resp_clean.split()
    FILLER = {"de", "le", "la", "les", "un", "une", "des", "du", "au", "aux", "et",
              "ou", "pour", "que", "qui", "dans", "sur", "ton", "ta", "tes", "en",
              "à", "par", "vers", "avec", "sans", "ce", "cet", "cette", "son",
              "sa", "ses", "se", "tu", "te", "toi", "mais", "donc", "car", "ne",
              "pas", "plus", "moins", "y", "jusqu", "lors", "dont"}
    dense = len([w for w in words if w.lower().strip(".,!?;:") not in FILLER])
    ratio = dense / max(1, len(words))
    print(f"DENSITÉ : {ratio:.2f} ({dense}/{len(words)} mots chargés)")

    print("\n" + "-" * 60)
    print("RÉPONSE BRUTE (espaces trailing nettoyés):")
    print("-" * 60)
    print(resp_clean)
    if cut:
        print(f"\n[⚠️ simulé ≤{MAX_CHARS}]")
        print("-" * 60)
        print(resp2)
    print("\n" + "=" * 60)
    print(f"Temps: {dt:.1f}s | out ~ {n_out} tok | chars={len(resp2)}/{MAX_CHARS} | truncated={cut}")
    print("=" * 60)
    print("\nℹ️ Validateur nu : aucune écriture dataset. Pour fine-tuner, voir guard séparé.")


if __name__ == "__main__":
    main()
