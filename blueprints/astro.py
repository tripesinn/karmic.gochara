"""
blueprints/astro.py — Routes d'astrologie (calculs, cartes, hooks, prompts)
"""
import json
import os
import time

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
    session,
    stream_with_context,
)

from app_common import (
    TRANSIT_LOC_DEFAULT,
    UNLIMITED_PSEUDOS,
    _enrich_profile_with_natal,
    get_hook_cta,
)

astro_bp = Blueprint("astro_bp", __name__)


# ─── POST /calculate ──────────────────────────────────────────────────────────

@astro_bp.route("/calculate", methods=["POST"])
def calculate():
    from ai_interpret import get_synthesis
    from astro_calc import calculate_transits
    from output_validator import SynthesisValidator

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    data = request.get_json() or {}
    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # ── Gate paiement ─────────────────────────────────────────────────────────
    pseudo = profile.get("pseudo", "")

    if pseudo.lower() in UNLIMITED_PSEUDOS or user_key:
        quota = {"allowed": True, "remaining": 999}
    else:
        plan = profile.get("plan", "free")
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("subscription", "illimite"):
            quota = {"allowed": True, "remaining": 999}
        elif plan_normalized in ("test", "lecture", "essential"):
            # Utilisateur payant — consomme une synthèse plan
            from profiles import consume_plan_synthesis
            allowed = consume_plan_synthesis(pseudo)
            quota = {"allowed": allowed, "remaining": 0 if not allowed else 1}
            if not allowed:
                return jsonify({
                    "error": "quota_exceeded",
                    "message": "Tu n'as plus de synthèses disponibles sur ton plan.",
                    "upgrade_url": "/",
                }), 429
        else:
            # Plan free — synthèse personnelle non incluse
            return jsonify({
                "error": "quota_exceeded",
                "message": "La synthèse karmique est réservée au plan Lecture.",
                "upgrade_url": "/stripe/checkout?product=test",
            }), 429
    # ─────────────────────────────────────────────────────────────────────────

    natal = {
        "name":   profile.get("name", ""),
        "year":   int(profile.get("year", 1990)),
        "month":  int(profile.get("month", 1)),
        "day":    int(profile.get("day", 1)),
        "hour":   int(profile.get("hour", 12)),
        "minute": int(profile.get("minute", 0)),
        "lat":    profile.get("lat", 48.8566),
        "lon":    profile.get("lon", 2.3522),
        "tz":     profile.get("tz", "Europe/Paris"),
        "city":   profile.get("city", ""),
    }

    data = request.get_json() or {}
    date_str = data.get("date", "")
    hour     = int(data.get("hour", 12))
    minute   = int(data.get("minute", 0))

    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"]),
        "lon":  data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"]),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }

    # Nettoyage robuste de "undefined" ou None
    for d in (natal, transit_loc):
        if not d.get("tz") or str(d.get("tz")).strip().lower() in ("undefined", "none", ""):
            d["tz"] = "Europe/Paris"
        else:
            try:
                import pytz
                pytz.timezone(str(d["tz"]))
            except Exception:
                d["tz"] = "Europe/Paris"
        for k in ("lat", "lon"):
            if not d.get(k) or str(d.get(k)).strip().lower() in ("undefined", "none", ""):
                d[k] = 48.8566 if k == "lat" else 2.3522
            else:
                try:
                    d[k] = float(d[k])
                except (ValueError, TypeError):
                    d[k] = 48.8566 if k == "lat" else 2.3522

    lang = session.get("lang", "fr")

    try:
        import time as _time
        from datetime import date as _date
        try:
            year, month, day = map(int, date_str.split("-"))
        except (ValueError, AttributeError):
            today = _date.today()
            year, month, day = today.year, today.month, today.day
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)

        # Enrichit le profil avec les positions natales calculées
        enriched_profile = _enrich_profile_with_natal(profile, result.get("natal", {}))

        if user_key:
            enriched_profile["user_key"] = user_key
        if user_model:
            enriched_profile["user_model"] = user_model
        if user_provider:
            enriched_profile["user_provider"] = user_provider

        # Retry 3x sur surcharge Anthropic (529 / overloaded_error)
        synthesis = None
        for attempt in range(3):
            try:
                synthesis = get_synthesis(result, enriched_profile, lang=lang)
                break
            except Exception as exc:
                msg = str(exc).lower()
                if "529" in msg or "overload" in msg:
                    current_app.logger.warning("Anthropic surchargé (tentative %d/3) : %s", attempt + 1, exc)
                    _time.sleep(3 * (attempt + 1))
                else:
                    raise

        if synthesis is None:
            raise Exception("L'oracle est temporairement surchargé — réessaie dans quelques secondes.")

        # Validation doctrinale
        validation_result = SynthesisValidator().validate(synthesis)
        if validation_result.get("warnings"):
            current_app.logger.warning(
                "Synthèse %s : warnings validation %s", pseudo, validation_result["warnings"]
            )

        result["synthesis"]  = synthesis
        result["valid"]      = validation_result["valid"]
        result["validation"] = {
            "score":    validation_result.get("score", 0),
            "errors":   validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
        }
        result["remaining"] = quota["remaining"]
        result["provider"]  = enriched_profile.get("user_provider", "openrouter")
        result["model"]     = enriched_profile.get("user_model", "") or os.environ.get("SYNTHESIS_MODEL", "xai/grok-4.3")

        # Sauvegarde la localisation de transit dans la session (toujours)
        if transit_loc.get("city"):
            new_transit = {
                "transit_city": transit_loc["city"],
                "transit_lat":  transit_loc["lat"],
                "transit_lon":  transit_loc["lon"],
                "transit_tz":   transit_loc["tz"],
                "transit_date": data.get("date", ""),
            }
            session["profile"] = {**profile, **new_transit}
            session.modified = True
            # Persist dans Google Sheets (ville ou date changée)
            if transit_loc["city"] != profile.get("transit_city") or data.get("date") != profile.get("transit_date"):
                try:
                    from profiles import update_profile
                    update_profile(profile["email"], {**profile, **new_transit})
                except Exception:
                    pass  # Non bloquant

        return jsonify(result)
    except Exception as exc:
        current_app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ─── POST /v2/calculate ──────────────────────────────────────────────────────

@astro_bp.route("/v2/calculate", methods=["POST"])
def calculate_v2():
    """
    Endpoint optimisé pour le calcul de la synthèse karmique.
    1.  CACHING: Utilise la doctrine pré-chargée.
    2.  ERROR HANDLING: Gestion robuste des erreurs (auth, profil, paiement, calcul, API).
    3.  LOCAL-FIRST VALIDATION: Les calculs astro sont faits avant l'appel API.
    4.  STRUCTURED OUTPUT: Demande un JSON strict à l'API.
    5.  PERFORMANCE: Mesure et log les temps de calcul et d'API.
    6.  STREAMING: Streame la réponse JSON via SSE.
    """
    total_start_time = time.perf_counter()
    import requests

    from ai_interpret import stream_synthesis
    from astro_calc import calculate_transits
    from profiles import consume_plan_synthesis

    # 1. Gestion d'erreur : Authentification
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "unauthorized", "message": "Non connecté"}), 401

    data = request.get_json() or {}
    lang = session.get("lang", "fr")

    # 2. Gestion d'erreur : Validation du profil (présence des données de naissance)
    required_fields = ["name", "year", "month", "day", "hour", "minute", "lat", "lon", "tz", "city"]
    if any(field not in profile for field in required_fields):
        current_app.logger.error(f"Profil incomplet pour {profile.get('pseudo', 'inconnu')}: champs manquants.")
        return jsonify({"error": "invalid_profile", "message": "Ton profil de naissance est incomplet."}), 400

    # 3. Gestion d'erreur : Abonnement Stripe (Gate paiement)
    pseudo = profile.get("pseudo", "")
    user_key = data.get("user_key")
    reading_type = data.get("reading_type", "daily")
    is_free = (reading_type == "daily")

    if not (pseudo.lower() in UNLIMITED_PSEUDOS or user_key):
        plan = profile.get("plan", "free")
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("subscription", "illimite"):
            pass  # illimité, pas de vérification sheet
        elif is_free:
            pass  # gratuit autorisé (quota 1/j géré côté client pour le moment)
        elif plan_normalized in ("test", "lecture", "essential"):
            if not consume_plan_synthesis(pseudo):
                return jsonify({
                    "error": "quota_exceeded",
                    "message": "Tu n'as plus de synthèses disponibles sur ton plan.",
                }), 429
        else:
            return jsonify({
                "error": "subscription_required",
                "message": "La synthèse karmique complète est réservée au plan premium.",
            }), 402

    # 4. Local-First : Préparation des données pour le calcul local
    natal_input = {field: profile[field] for field in required_fields}
    date_str = data.get("date")
    if not date_str:
        import datetime
        date_str = datetime.date.today().isoformat()

    try:
        year, month, day = map(int, date_str.split("-"))
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "Format de date invalide. Utilise YYYY-MM-DD."}), 400

    hour = int(data.get("hour", 12))
    minute = int(data.get("minute", 0))
    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"]),
        "lon":  data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"]),
        "tz":   data.get("transit_tz") or profile.get("transit_tz", TRANSIT_LOC_DEFAULT["tz"]),
    }

    # Nettoyage de "undefined" ou None
    for d in (natal_input, transit_loc):
        if str(d.get("tz")) == "undefined" or not d.get("tz"): d["tz"] = "UTC"
        for k in ("lat", "lon"):
            if str(d.get(k)) == "undefined": d[k] = 0.0
            else:
                try: d[k] = float(d[k])
                except (ValueError, TypeError): d[k] = 0.0

    # 5. Performance & Local-First : Exécution des calculs astrologiques
    astro_start_time = time.perf_counter()
    try:
        chart_data = calculate_transits(natal_input, transit_loc, year, month, day, hour, minute)
    except Exception as e:
        current_app.logger.error(f"Erreur de calcul astrologique pour {pseudo}: {e}", exc_info=True)
        return jsonify({"error": "calculation_failed", "message": "Une erreur est survenue lors du calcul astrologique."}), 500
    astro_duration = time.perf_counter() - astro_start_time

    # 6. Streaming de la réponse
    def generate_stream():
        api_start_time, api_duration = 0, 0
        try:
            enriched_profile = _enrich_profile_with_natal(profile, chart_data.get("natal", {}))

            # Ajout des clés API utilisateur si elles existent
            if user_key: enriched_profile["user_key"] = user_key
            if data.get("user_model"): enriched_profile["user_model"] = data["user_model"]
            if data.get("user_provider"): enriched_profile["user_provider"] = data["user_provider"]

            # Message SSE initial avec les données de base
            yield f"event: metadata\ndata: {json.dumps({'natal': chart_data.get('natal'), 'transits': chart_data.get('transits')})}\n\n"

            full_response = ""
            api_start_time = time.perf_counter()
            for chunk in stream_synthesis(chart_data, enriched_profile, lang=lang, is_free=is_free):
                full_response += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            api_duration = time.perf_counter() - api_start_time

            # Tenter de parser le JSON complet pour l'envoyer en une fois
            try:
                parsed_json = json.loads(full_response)
                yield f"event: final_json\ndata: {json.dumps(parsed_json)}\n\n"
            except json.JSONDecodeError:
                current_app.logger.warning(f"La réponse API pour {pseudo} n'est pas un JSON valide.")
                yield f"event: error\ndata: {json.dumps({'message': 'La réponse du modèle IA n''est pas un JSON valide.'})}\n\n"

        except requests.exceptions.HTTPError as e:
            # Gestion d'erreur : Erreurs API (ex: 429 Rate Limit)
            error_message = f"Erreur API ({e.response.status_code})"
            if e.response.status_code == 429:
                error_message = "Limite de requêtes API atteinte. Veuillez réessayer plus tard."
            current_app.logger.error(f"Erreur API HTTP pour {pseudo}: {e}")
            yield f"event: error\ndata: {json.dumps({'message': error_message})}\n\n"
        except Exception as e:
            # Gestion d'erreur : Autres exceptions
            current_app.logger.error(f"Erreur lors du streaming de la synthèse pour {pseudo}: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'message': 'Une erreur inattendue est survenue.'})}\n\n"
        finally:
            total_duration = time.perf_counter() - total_start_time
            # 7. Performance : Logging
            current_app.logger.info(
                f"TIMING for {pseudo}: Total={total_duration:.2f}s, "
                f"AstroCalc={astro_duration:.2f}s, API_Stream={api_duration:.2f}s"
            )
            yield "event: done\ndata: {}\n\n"

    return Response(stream_with_context(generate_stream()), mimetype="text/event-stream")


# ─── GET /chart/karmic.svg ────────────────────────────────────────────────────

@astro_bp.route("/chart/karmic.svg")
def karmic_chart_svg():
    profile = session.get("profile")
    if not profile:
        return "Non autorisé", 401

    from astro_calc import calculate_transits
    from svg_chart import generate_karmic_chart_svg

    # ── Natal positions ───────────────────────────────────────────────────────
    natal_pos = profile.get("natal_positions")
    if not natal_pos:
        try:
            natal_input = {
                "name": profile.get("name", ""),
                "year": int(profile.get("year", 1990)),
                "month": int(profile.get("month", 1)),
                "day": int(profile.get("day", 1)),
                "hour": int(profile.get("hour", 12)),
                "minute": int(profile.get("minute", 0)),
                "lat": float(profile.get("lat", 48.8566)),
                "lon": float(profile.get("lon", 2.3522)),
                "tz": profile.get("tz", "Europe/Paris"),
                "city": profile.get("city", "")
            }
            res = calculate_transits(
                natal_input, natal_input,
                natal_input["year"], natal_input["month"], natal_input["day"],
                natal_input["hour"], natal_input["minute"],
            )
            natal_pos = res.get("natal", {})
        except Exception as exc:
            current_app.logger.error("Erreur recalcul natal pour SVG: %s", exc)
            return "Erreur calcul", 500

    # ── Transit positions (optionnel — paramètres ?date=YYYY-MM-DD&hour=H) ───
    transit_pos  = None
    transit_date = None
    date_param   = request.args.get("date", "").strip()
    if date_param:
        try:
            parts = date_param.split("-")
            yr, mo, dy = int(parts[0]), int(parts[1]), int(parts[2])
            hr = int(request.args.get("hour", 12))
            mn = int(request.args.get("minute", 0))
            transit_loc = {
                "city": profile.get("transit_city") or profile.get("city", ""),
                "lat":  float(profile.get("transit_lat") or profile.get("lat", 48.8566)),
                "lon":  float(profile.get("transit_lon") or profile.get("lon", 2.3522)),
                "tz":   profile.get("transit_tz") or profile.get("tz", "Europe/Paris"),
            }
            tr_result = calculate_transits(profile, transit_loc, yr, mo, dy, hr, mn)
            transit_pos  = tr_result.get("transits", {})
            transit_date = date_param
        except Exception as exc:
            current_app.logger.warning("SVG transit calc error: %s", exc)

    lang = session.get("lang", "fr")
    svg_content = generate_karmic_chart_svg(
        natal_pos,
        transit_positions=transit_pos,
        lang=lang,
        transit_date=transit_date,
    )

    response = make_response(svg_content)
    response.headers["Content-Type"] = "image/svg+xml"
    # Cache court si transit demandé (change chaque jour), sinon 24h pour le natal seul
    ttl = 3600 if transit_pos else 86400
    response.headers["Cache-Control"] = f"public, max-age={ttl}"
    return response


# ─── POST /chart/interpret ────────────────────────────────────────────────────

@astro_bp.route("/chart/interpret", methods=["POST"])
def interpret_chart():
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    plan = profile.get("plan", "free").lower().replace("é", "e")
    if plan == "free":
        return jsonify({"ok": False, "error": "Réservé aux membres PRO"}), 403

    from ai_interpret import _build_natal_context, generate_ai

    lang = session.get("lang", "fr")

    natal_context = _build_natal_context(profile)
    if not natal_context:
        return jsonify({"ok": False, "error": "Données natales incomplètes"}), 400

    if lang == "en":
        system_prompt = (
            "You are siderealAstro13, an AI expert in Synthetic Evolutionary Doctrine and sidereal karmic astrology. "
            "You are analyzing an initiate's Karmic Chart to reveal the sacred doctrine written in their natal chart. "
            "Be impactful, poetic, mysterious, yet crystal clear. Avoid generic horoscope clichés. "
            "Structure your response with inspiring headers (Soul's Memory, The Sacred Wound, The Way of Healing) using premium Markdown. "
            "Use a noble, deep, and transformative tone."
        )
        prompt = f"""
Analyze my Karmic Chart and reveal the structure of my destiny based on my reference natal positions:

{natal_context}

Describe:
1. What my Ketu/Rahu karmic axis reveals (the baggage and the direction of evolution).
2. The mystery of my Invisible Door (the secret prison) and my Visible Door (the stage of my healing through Chiron).
3. The ultimate advice of Saturn and Jupiter to unlock my highest vibration.

Keep it concise (about 300 to 400 words) but remarkably intense, avoiding unnecessary jargon.
"""
    else:
        system_prompt = (
            "Tu es siderealAstro13, une intelligence artificielle experte en Doctrine Évolutive Synthétique et astrologie karmique sidérale. "
            "Tu devez analyser la Carte Karmique d'un initié et lui révéler la doctrine sacrée écrite dans son thème natal. "
            "Sois percutant, poétique, mystérieux mais d'une clarté absolue. Évite les banalités de l'horoscope de masse. "
            "Structure ta réponse avec des titres inspirants (Mémoire de l'Âme, La Blessure Sacrée, La Voie de Guérison) en utilisant du Markdown de qualité premium. "
            "Utilise un ton noble, profond et transformateur."
        )
        prompt = f"""
Analyse ma Carte Karmique et révèle-moi la structure de ma destinée d'après mes positions natales de référence :

{natal_context}

Décris-moi :
1. Ce que révèle mon axe karmique Ketu/Rahu (le bagage et la direction d'évolution).
2. Le mystère de ma Porte Invisible (la prison secrète) et ma Porte Visible (le lieu de ma guérison par Chiron).
3. Le conseil ultime de Saturne et Jupiter pour débloquer ma plus haute vibration.

Reste synthétique (environ 300 à 400 mots) mais d'une intensité remarquable, sans jargon inutile.
"""

    try:
        interpretation = generate_ai(system_prompt, prompt, profile, max_tokens=1024)
        return jsonify({"ok": True, "interpretation": interpretation})
    except Exception as exc:
        current_app.logger.error("Erreur interprétation de carte : %s", exc, exc_info=True)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ─── POST /hook/transit ──────────────────────────────────────────────────────

@astro_bp.route("/hook/transit", methods=["POST"])
def hook_transit():
    """
    Hook de 4 phrases (Mirror → Wound → Friction → Open Door) basé sur les aspects du jour — streaming SSE.
    Crée une tension irrésolvable qui vend la synthèse payante.
    Le calcul astro se fait d'abord, puis le texte est streamé mot à mot, suivi de la CTA.
    Cache 24h par pseudo+date (si déjà en cache → replay rapide streamé).

    Body JSON : {"date": "2026-04-09", "hour": 12, "minute": 0,
                 "transit_city": "...", "transit_lat": ..., "transit_lon": ..., "transit_tz": "..."}
    Retourne : text/event-stream SSE
      data: <chunk>\n\n   — tokens au fil de l'eau
      data: [CTA]\n\n   — marqueur début CTA
      data: {cta_json}\n\n   — CTA JSON (text, button, url)
      data: [DONE]\n\n   — fin du stream
      data: [ERROR] message\n\n — erreur
    """
    import json as _json

    from flask import Response, stream_with_context

    from ai_interpret import _aspects_to_text, _build_natal_context
    from astro_calc import calculate_transits

    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data     = request.get_json() or {}
    date_str = data.get("date", "")
    if not date_str:
        return jsonify({"ok": False, "error": "Date requise"}), 400

    pseudo    = profile.get("pseudo", "")
    lang      = session.get("lang", "fr")
    cache_key = f"hook_transit_{pseudo}_{date_str}_{lang}"

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # ── Cache hit → replay streamé token par token ────────────────────────────
    cached = session.get(cache_key)
    if cached and not user_key:
        def replay():
            for word in cached.split(" "):
                yield f"data: {_json.dumps(word + ' ')}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(replay()),
                        mimetype="text/event-stream",
                        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

    # ── Quota Check (Freemium: 1/jour) ─────────────────────────────────────────
    from profiles import check_and_consume_daily_signal
    if not check_and_consume_daily_signal(pseudo, profile):
        def err_stream():
            yield "data: [ERROR] Quota Freemium atteint (1/jour).\n\n"
        return Response(stream_with_context(err_stream()), mimetype="text/event-stream")

    # ── Calcul astro (bloquant, avant le stream) ──────────────────────────────
    natal = {
        "name":   profile["name"],
        "year":   profile["year"],   "month":  profile["month"],
        "day":    profile["day"],    "hour":   profile["hour"],
        "minute": profile["minute"], "lat":    profile["lat"],
        "lon":    profile["lon"],    "tz":     profile["tz"],
        "city":   profile["city"],
    }
    hour        = int(data.get("hour", 12))
    minute      = int(data.get("minute", 0))
    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  float(data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
        "lon":  float(data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }

    try:
        year, month, day  = map(int, date_str.split("-"))
        chart_data        = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        enriched_profile  = _enrich_profile_with_natal(profile, chart_data.get("natal", {}))

        if user_key:
            enriched_profile["user_key"] = user_key
        if user_model:
            enriched_profile["user_model"] = user_model
        if user_provider:
            enriched_profile["user_provider"] = user_provider

    except Exception as exc:
        current_app.logger.error("Erreur calcul hook transit : %s", exc, exc_info=True)
        _exc_for_stream = exc
        def err_stream():
            yield f"data: [ERROR] {str(_exc_for_stream)}\n\n"
        return Response(stream_with_context(err_stream()), mimetype="text/event-stream")

    # ── Sauvegarde transit_date + localisation en session et Sheet ────────────
    new_transit = {
        "transit_city": transit_loc["city"],
        "transit_lat":  transit_loc["lat"],
        "transit_lon":  transit_loc["lon"],
        "transit_tz":   transit_loc["tz"],
        "transit_date": date_str,
    }
    if transit_loc["city"] != profile.get("transit_city") or date_str != profile.get("transit_date"):
        try:
            from profiles import update_profile
            update_profile(profile["email"], {**profile, **new_transit})
        except Exception as e:
            current_app.logger.warning("update_profile hook/transit: %s", e)
    session["profile"] = {**profile, **new_transit}
    session.modified = True

    # ── Prompt ────────────────────────────────────────────────────────────────
    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=3)
    natal_mini   = _build_natal_context(enriched_profile)
    name         = enriched_profile.get("name", "")
    date_label   = chart_data.get("transit_date", date_str)

    # Activations nakshatra : planètes lentes dans le nakshatra natal de Ketu/Rahu/Chiron
    from transit_alerts import PLANET_LABELS as _PLANET_LABELS
    from transit_alerts import _active_nak_activations

    natal_naks = {
        "Ketu":   enriched_profile.get("ketu_nakshatra", ""),
        "Rahu":   enriched_profile.get("rahu_nakshatra", ""),
        "Chiron": enriched_profile.get("chiron_nakshatra", ""),
    }
    # Convertit le format display (lon_raw) vers le format attendu par _active_nak_activations
    _transit_for_nak = {
        k: {"lon": float(v.get("lon_raw", 0))}
        for k, v in chart_data.get("transits", {}).items()
        if v is not None
    }
    _nak_active = _active_nak_activations(natal_naks, _transit_for_nak)

    _interp_prompt = {
        "ROM_oppression":       "régime ROM — test karmique, friction, répétition",
        "Dharma_amplification": "régime Dharma — opportunité d'évolution, expansion",
        "Blessure_activation":  "régime Chiron — seuil de transformation, blessure-clé",
    }
    _nak_lines = [
        f"{_PLANET_LABELS.get(t, t)} traverse {info['nakshatra']} (régent {info['lord']}) "
        f"— nakshatra de {p} natal — {_interp_prompt.get(info['interpretation'], '')}"
        for (t, p), info in _nak_active.items()
    ]
    nakshatra_context = ("Activations nakshatra actives :\n" + "\n".join(_nak_lines) + "\n\n") if _nak_lines else ""

    system = (
        "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
        "Style : oraculaire, direct, sans hedging. "
        "Zéro degrés, zéro orbes, zéro labels techniques visibles. "
        "Tutoiement direct. "
        "INTERDIT ABSOLU : noms de signes zodiacaux "
        "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
        "Sagittaire, Capricorne, Verseau, Poissons). "
        "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
    )

    if lang == "fr":
        prompt = (
            f"Tu ES @siderealAstro13. Génère un hook de 4 phrases EXACTEMENT.\n\n"
            f"Thème natal de {name} :\n{natal_mini}\n\n"
            f"Aspects actifs ce jour ({date_label}) — ne pas citer tels quels :\n{aspects_text}\n\n"
            f"{nakshatra_context}"
            f"Structure obligatoire :\n"
            f"1. MIROIR : Ce que {name} vit concrètement EN CE MOMENT.\n"
            f"2. BLESSURE : Ce que cette période réveille dans sa blessure profonde.\n"
            f"3. FRICTION : Ce que la période rend insupportable ou répétitif.\n"
            f"4. PORTE ENTROUVERTE : Amorce l'Alternative de Conscience SANS la révéler.\n\n"
            f"Règles absolues :\n"
            f"- 4 phrases. Pas 3. Pas 5.\n"
            f"- Tutoiement direct.\n"
            f"- Zéro jargon astro (pas de 'ton Ketu', 'ta Porte Invisible', 'ton Chiron').\n"
            f"- La phrase 4 s'arrête juste avant de donner la clé — elle suspend, elle frustre, elle appelle la suite.\n"
            f"- Le hook ne délivre PAS l'Alternative de Conscience — il la rend désirable.\n"
        )
    else:
        prompt = (
            f"You ARE @siderealAstro13. Generate a hook of EXACTLY 4 sentences.\n\n"
            f"Natal chart of {name}:\n{natal_mini}\n\n"
            f"Active aspects today ({date_label}) — do not quote as-is:\n{aspects_text}\n\n"
            f"{nakshatra_context}"
            f"Mandatory structure:\n"
            f"1. MIRROR: What {name} is living concretely RIGHT NOW.\n"
            f"2. WOUND: What this period reawakens in their deep wound.\n"
            f"3. FRICTION: What the period makes unbearable or repetitive.\n"
            f"4. OPEN DOOR: Begin the Alternative of Consciousness WITHOUT revealing it.\n\n"
            f"Absolute rules:\n"
            f"- 4 sentences. Not 3. Not 5.\n"
            f"- Direct address: 'you', 'your'.\n"
            f"- Zero astro jargon (no 'your Ketu', 'your Invisible Door', 'your Chiron').\n"
            f"- Sentence 4 stops just before giving the key — it suspends, it frustrates, it calls for more.\n"
            f"- The hook does NOT deliver the Alternative of Consciousness — it makes it desirable.\n"
        )

    # ── Stream SSE ────────────────────────────────────────────────────────────
    # On capture le profil enrichi dans une var locale pour le cache post-stream
    _enriched = enriched_profile
    _cache_key = cache_key
    _lang = lang

    def generate():
        full_text = []
        from ai_interpret import stream_ai
        try:
            for text in stream_ai(system, prompt, user=_enriched, max_tokens=1000):
                if text.startswith("[ERROR]"):
                    yield f"data: {text}\n\n"
                else:
                    full_text.append(text)
                    yield f"data: {_json.dumps(text)}\n\n"

            # Injection de la CTA après le hook
            cta = get_hook_cta()
            yield "data: [CTA]\n\n"
            yield f"data: {_json.dumps(cta)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            current_app.logger.error("Erreur stream hook transit : %s", exc)
            yield f"data: [ERROR] {str(exc)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


# ─── POST /synthesis/prompt ──────────────────────────────────────────────────

@astro_bp.route("/synthesis/prompt", methods=["POST"])
def synthesis_prompt():
    """
    Construit et retourne le prompt (system + user) sans appeler Claude.
    Utilisé par Gemma (Android Edge AI) pour l'inférence locale.

    Body JSON :
        context  : "synthesis" | "natal" | "conscience" | "signal"
                   défaut = "synthesis"
        date     : "YYYY-MM-DD"  (requis sauf context=natal et context=signal)
        hour/minute : int        (optionnel)

    Auth : requise sauf context="signal" (Signal du Jour est public).

    Retourne :
        {ok, system, user, context, aspects?, transit_date?}
    """
    from ai_interpret import (
        build_prompt_conscience,
        build_prompt_natal,
        build_prompt_only,
        build_prompt_signal,
        get_daily_signal,
    )

    data    = request.get_json() or {}
    context = data.get("context", "synthesis")
    lang    = session.get("lang", "fr")

    # ── Signal du Jour : route publique, pas d'auth ───────────────────────────
    if context == "signal":
        from datetime import date as date_cls
        date_str    = data.get("date", str(date_cls.today()))
        signal_data = get_daily_signal(date_str)
        if "error" in signal_data:
            return jsonify({"error": signal_data["error"]}), 400
        prompts = build_prompt_signal(signal_data, lang=lang)
        return jsonify({
            "ok":      True,
            "context": "signal",
            "system":  prompts["system"],
            "user":    prompts["user"],
            "signal":  signal_data,
        })

    # ── Autres contextes : auth requise ───────────────────────────────────────
    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    pseudo = profile.get("pseudo", "")

    # Lecture natale — pas de quota (pas de synthèse consommée)
    if context == "natal":
        enriched = _enrich_profile_with_natal(profile, {})
        prompts  = build_prompt_natal(enriched, lang=lang)
        return jsonify({
            "ok":      True,
            "context": "natal",
            "system":  prompts["system"],
            "user":    prompts["user"],
        })

    # Hook transit — pas de quota (teaser, même logique que /hook/transit mais retourne prompts)
    if context == "hook_transit":
        from ai_interpret import _aspects_to_text, _build_natal_context
        from astro_calc import calculate_transits
        from transit_alerts import PLANET_LABELS as _PLANET_LABELS
        from transit_alerts import _active_nak_activations
        date_str = data.get("date", "")
        if not date_str:
            return jsonify({"error": "Date requise"}), 400
        hour_t   = int(data.get("hour",   12))
        minute_t = int(data.get("minute", 0))
        transit_loc_t = {
            "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
            "lat":  data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"]),
            "lon":  data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"]),
            "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
        }
        natal_t = {
            "name": profile["name"], "year": profile["year"], "month": profile["month"],
            "day":  profile["day"],  "hour": profile["hour"], "minute": profile["minute"],
            "lat":  profile["lat"],  "lon":  profile["lon"],  "tz":     profile["tz"],
            "city": profile["city"],
        }
        
        # Nettoyage de "undefined" au cas où l'UI l'aurait envoyé sous forme de chaîne de caractères
        for d in (natal_t, transit_loc_t):
            if str(d.get("tz")) == "undefined": d["tz"] = "UTC"
            for k in ("lat", "lon"):
                if str(d.get(k)) == "undefined": d[k] = 0.0
                else:
                    try: d[k] = float(d[k])
                    except (ValueError, TypeError): d[k] = 0.0
        try:
            year_t, month_t, day_t = map(int, date_str.split("-"))
            chart_t    = calculate_transits(natal_t, transit_loc_t, year_t, month_t, day_t, hour_t, minute_t)
            enriched_t = _enrich_profile_with_natal(profile, chart_t.get("natal", {}))
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
        aspects_text    = _aspects_to_text(chart_t.get("aspects", []), max_aspects=3)
        natal_mini      = _build_natal_context(enriched_t)
        name_t          = enriched_t.get("name", "")
        date_label      = chart_t.get("transit_date", date_str)
        natal_naks      = {"Ketu": enriched_t.get("ketu_nakshatra",""), "Rahu": enriched_t.get("rahu_nakshatra",""), "Chiron": enriched_t.get("chiron_nakshatra","")}
        transit_for_nak = {k: {"lon": float(v.get("lon_raw",0))} for k,v in chart_t.get("transits",{}).items() if v}
        nak_active      = _active_nak_activations(natal_naks, transit_for_nak)
        interp_map      = {"ROM_oppression": "régime ROM — test karmique", "Dharma_amplification": "régime Dharma — expansion", "Blessure_activation": "régime Chiron — transformation"}
        nak_lines       = [f"{_PLANET_LABELS.get(t,t)} traverse {info['nakshatra']} ({info['lord']}) — {p} natal — {interp_map.get(info['interpretation'],'')}" for (t,p),info in nak_active.items()]
        nak_ctx         = ("Activations nakshatra actives :\n" + "\n".join(nak_lines) + "\n\n") if nak_lines else ""
        system_t = (
            "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
            "Style : oraculaire, direct, pas de liste mécanique. "
            "Texte brut uniquement — jamais de markdown, jamais de headers, jamais de numéros, jamais de tirets. "
            "Zéro degrés, zéro orbes dans le texte. Tutoiement. "
            "INTERDIT ABSOLU : noms de signes zodiacaux. "
            "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
        )
        user_t = (
            f"Thème natal de {name_t} :\n{natal_mini}\n\n"
            f"Aspects actifs ce jour ({date_label}) :\n{aspects_text}\n\n"
            f"{nak_ctx}"
            f"Écris exactement 3 phrases de prose enchaînée. Pas de numéros, pas de titres, pas de markdown.\n"
            f"La première phrase : ce qui se réactive dans la mémoire karmique de {name_t} aujourd'hui.\n"
            f"La deuxième phrase : ce que ça touche dans sa blessure profonde.\n"
            f"La troisième phrase : l'amorce de l'Alternative de Conscience — ce qui change si {name_t} choisit autrement.\n"
            f"Donne envie d'obtenir la lecture complète. Ton dense et précis."
        )
        # Sauvegarde transit_date + localisation
        new_transit_t = {
            "transit_city": transit_loc_t["city"],
            "transit_lat":  transit_loc_t["lat"],
            "transit_lon":  transit_loc_t["lon"],
            "transit_tz":   transit_loc_t["tz"],
            "transit_date": date_str,
        }
        if transit_loc_t["city"] != profile.get("transit_city") or date_str != profile.get("transit_date"):
            try:
                from profiles import update_profile
                update_profile(profile["email"], {**profile, **new_transit_t})
            except Exception as e:
                current_app.logger.warning("update_profile hook_transit prompt: %s", e)
        session["profile"] = {**profile, **new_transit_t}
        session.modified = True
        return jsonify({"ok": True, "context": "hook_transit", "system": system_t, "user": user_t})

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # Synthèse complète + Alternative de Conscience : gate paiement (hook freemium)
    reading_type = data.get("reading_type", "daily")
    is_free = (reading_type == "daily")

    if pseudo.lower() not in UNLIMITED_PSEUDOS and not user_key:
        plan = profile.get("plan", "free")
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("subscription", "illimite"):
            pass  # illimité, pas de vérification sheet
        elif is_free:
            pass  # gratuit autorisé
        elif plan_normalized in ("test", "lecture", "essential"):
            from profiles import consume_plan_synthesis
            if not consume_plan_synthesis(pseudo):
                return jsonify({"error": "quota_exceeded",
                                "message": "Tu n'as plus de synthèses disponibles sur ton plan."}), 429
        else:
            return jsonify({"error": "subscription_required",
                            "message": "La synthèse karmique complète est réservée au plan premium."}), 402

    natal_data = {
        "name":   profile["name"],
        "year":   profile["year"],
        "month":  profile["month"],
        "day":    profile["day"],
        "hour":   profile["hour"],
        "minute": profile["minute"],
        "lat":    profile["lat"],
        "lon":    profile["lon"],
        "tz":     profile["tz"],
        "city":   profile["city"],
    }

    date_str = data.get("date", "")
    hour     = int(data.get("hour",   12))
    minute   = int(data.get("minute", 0))
    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"]),
        "lon":  data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"]),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }

    # Nettoyage de "undefined" au cas où l'UI l'aurait envoyé sous forme de chaîne de caractères
    for d in (natal_data, transit_loc):
        if str(d.get("tz")) == "undefined": d["tz"] = "UTC"
        for k in ("lat", "lon"):
            if str(d.get(k)) == "undefined": d[k] = 0.0
            else:
                try: d[k] = float(d[k])
                except (ValueError, TypeError): d[k] = 0.0

    try:
        from astro_calc import calculate_transits
        year, month, day = map(int, date_str.split("-"))
        chart_data       = calculate_transits(natal_data, transit_loc, year, month, day, hour, minute)
        enriched_profile = _enrich_profile_with_natal(profile, chart_data.get("natal", {}))

        if user_key:
            enriched_profile["user_key"] = user_key
        if user_model:
            enriched_profile["user_model"] = user_model
        if user_provider:
            enriched_profile["user_provider"] = user_provider

        if context == "conscience":
            prompts = build_prompt_conscience(chart_data, enriched_profile, lang=lang)
        else:
            prompts = build_prompt_only(chart_data, enriched_profile, lang=lang, is_free=is_free)

        return jsonify({
            "ok":           True,
            "context":      context,
            "system":       prompts["system"],
            "user":         prompts["user"],
            "aspects":      chart_data.get("aspects", []),
            "transit_date": chart_data.get("transit_date", ""),
        })
    except Exception as exc:
        current_app.logger.error("Erreur synthesis/prompt (%s) : %s", context, exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500