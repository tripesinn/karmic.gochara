"""
app.py — Gochara Karmique
Application Flask — Architecture multi-utilisateurs
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-secret-2024")
app.config["JSON_AS_ASCII"] = False

TRANSIT_LOC_DEFAULT = {
    "city": "Paris, France",
    "lat":  48.8566,
    "lon":  2.3522,
    "tz":   "Europe/Paris",
}

# ── Labels multilingues ───────────────────────────────────────────────────────
LANGS = {
    "fr": {
        "code": "fr", "label": "🇫🇷 FR",
        "title": "Gochara Karmique",
        "login": "Connexion",
        "create_profile": "Créer un profil",
        "connect": "Connexion »",
        "pseudo": "Pseudo :",
        "pseudo_ph": "Ton pseudo…",
        "karmic_profile": "✦ Créer un profil karmique",
        "firstname": "Prénom :",
        "email": "Email :",
        "birthdate": "Date naissance :",
        "birthtime": "Heure naissance :",
        "birthcity": "Ville naissance :",
        "city_ph": "Cherche ta ville…",
        "back": "← Retour",
        "create": "Créer mon profil »",
        "logout": "Déconnexion",
        "settings": "RÉGLAGES",
        "date": "Date :",
        "hour": "Heure :",
        "min": "min",
        "transit_ph": "Lieu de transit…",
        "calculate": "✦ Calculer »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Carte Karmique",
        "synthesis_title": "✦ Synthèse karmique — @siderealAstro13",
        "synthesis_wait": "Lance un calcul pour obtenir ta synthèse karmique védique…",
        "aspects_title": "✦ Aspects actifs (orbe < 3°)",
        "aspects_wait": "Lance un calcul pour voir les aspects…",
        "carte_title": "✦ Carte Karmique — Zodiaque Sidéral",
        "map_wait": "Lance un calcul…",
        "listen": "▶ Écouter",
        "stop": "■ Stop",
        "send_email": "📧 Recevoir par email",
        "sending": "Envoi…",
        "sent_ok": "✓ Envoyé !",
        "sent_err": "⚠ Erreur envoi",
        "ready": "Prêt",
        "no_calc": "Lance d'abord un calcul.",
        "select_transit": "⚠ Sélectionne un lieu de transit dans la liste.",
        "select_date": "⚠ Sélectionne une date.",
        "calc_ephem": "Calcul des éphémérides…",
        "calc_sideral": "Calcul sidéral Djwhal Khul…",
        "calc_karmic": "Interprétation karmique védique en cours…",
        "transit_title": "⏱ Transits — Date de consultation",
        "support_title": "☕ Soutenir le projet",
        "support_label": "Buy me a coffee",
    },
    "en": {
        "code": "en", "label": "🇬🇧 EN",
        "title": "Karmic Gochara",
        "login": "Login",
        "create_profile": "Create a profile",
        "connect": "Login »",
        "pseudo": "Username:",
        "pseudo_ph": "Your username…",
        "karmic_profile": "✦ Create a karmic profile",
        "firstname": "First name:",
        "email": "Email:",
        "birthdate": "Birth date:",
        "birthtime": "Birth time:",
        "birthcity": "Birth city:",
        "city_ph": "Search your city…",
        "back": "← Back",
        "create": "Create my profile »",
        "logout": "Logout",
        "settings": "SETTINGS",
        "date": "Date:",
        "hour": "Hour:",
        "min": "min",
        "transit_ph": "Transit location…",
        "calculate": "✦ Calculate »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Karmic Chart",
        "synthesis_title": "✦ Karmic Synthesis — @siderealAstro13",
        "synthesis_wait": "Run a calculation to get your Vedic karmic synthesis…",
        "aspects_title": "✦ Active Aspects (orb < 3°)",
        "aspects_wait": "Run a calculation to see aspects…",
        "carte_title": "✦ Karmic Chart — Sidereal Zodiac",
        "map_wait": "Run a calculation…",
        "listen": "▶ Listen",
        "stop": "■ Stop",
        "send_email": "📧 Receive by email",
        "sending": "Sending…",
        "sent_ok": "✓ Sent!",
        "sent_err": "⚠ Send error",
        "ready": "Ready",
        "no_calc": "Run a calculation first.",
        "select_transit": "⚠ Select a transit location from the list.",
        "select_date": "⚠ Select a date.",
        "calc_ephem": "Calculating ephemeris…",
        "calc_sideral": "Sidereal calculation Djwhal Khul…",
        "calc_karmic": "Vedic karmic interpretation in progress…",
        "transit_title": "⏱ Transits — Consultation date",
        "support_title": "☕ Support the project",
        "support_label": "Buy me a coffee",
    },
    "es": {
        "code": "es", "label": "🇪🇸 ES",
        "title": "Gochara Kármico",
        "login": "Conexión",
        "create_profile": "Crear un perfil",
        "connect": "Conectar »",
        "pseudo": "Seudónimo:",
        "pseudo_ph": "Tu seudónimo…",
        "karmic_profile": "✦ Crear un perfil kármico",
        "firstname": "Nombre:",
        "email": "Email:",
        "birthdate": "Fecha de nacimiento:",
        "birthtime": "Hora de nacimiento:",
        "birthcity": "Ciudad de nacimiento:",
        "city_ph": "Busca tu ciudad…",
        "back": "← Volver",
        "create": "Crear mi perfil »",
        "logout": "Desconexión",
        "settings": "AJUSTES",
        "date": "Fecha:",
        "hour": "Hora:",
        "min": "min",
        "transit_ph": "Lugar de tránsito…",
        "calculate": "✦ Calcular »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Carta Kármica",
        "synthesis_title": "✦ Síntesis kármica — @siderealAstro13",
        "synthesis_wait": "Lanza un cálculo para obtener tu síntesis kármica védica…",
        "aspects_title": "✦ Aspectos activos (orbe < 3°)",
        "aspects_wait": "Lanza un cálculo para ver los aspectos…",
        "carte_title": "✦ Carta Kármica — Zodiaco Sideral",
        "map_wait": "Lanza un cálculo…",
        "listen": "▶ Escuchar",
        "stop": "■ Parar",
        "send_email": "📧 Recibir por email",
        "sending": "Enviando…",
        "sent_ok": "✓ ¡Enviado!",
        "sent_err": "⚠ Error de envío",
        "ready": "Listo",
        "no_calc": "Lanza primero un cálculo.",
        "select_transit": "⚠ Selecciona un lugar de tránsito de la lista.",
        "select_date": "⚠ Selecciona una fecha.",
        "calc_ephem": "Calculando efemérides…",
        "calc_sideral": "Cálculo sideral Djwhal Khul…",
        "calc_karmic": "Interpretación kármica védica en curso…",
        "transit_title": "⏱ Tránsitos — Fecha de consulta",
        "support_title": "☕ Apoyar el proyecto",
        "support_label": "Invítame a un café",
    },
    "pt": {
        "code": "pt", "label": "🇧🇷 PT",
        "title": "Gochara Kármico",
        "login": "Conexão",
        "create_profile": "Criar um perfil",
        "connect": "Entrar »",
        "pseudo": "Pseudónimo:",
        "pseudo_ph": "Seu pseudónimo…",
        "karmic_profile": "✦ Criar um perfil kármico",
        "firstname": "Nome:",
        "email": "Email:",
        "birthdate": "Data de nascimento:",
        "birthtime": "Hora de nascimento:",
        "birthcity": "Cidade de nascimento:",
        "city_ph": "Procure sua cidade…",
        "back": "← Voltar",
        "create": "Criar meu perfil »",
        "logout": "Sair",
        "settings": "CONFIGURAÇÕES",
        "date": "Data:",
        "hour": "Hora:",
        "min": "min",
        "transit_ph": "Local de trânsito…",
        "calculate": "✦ Calcular »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Carta Kármica",
        "synthesis_title": "✦ Síntese kármica — @siderealAstro13",
        "synthesis_wait": "Execute um cálculo para obter sua síntese kármica védica…",
        "aspects_title": "✦ Aspectos ativos (orbe < 3°)",
        "aspects_wait": "Execute um cálculo para ver os aspectos…",
        "carte_title": "✦ Carta Kármica — Zodíaco Sideral",
        "map_wait": "Execute um cálculo…",
        "listen": "▶ Ouvir",
        "stop": "■ Parar",
        "send_email": "📧 Receber por email",
        "sending": "Enviando…",
        "sent_ok": "✓ Enviado!",
        "sent_err": "⚠ Erro de envio",
        "ready": "Pronto",
        "no_calc": "Execute primeiro um cálculo.",
        "select_transit": "⚠ Selecione um local de trânsito da lista.",
        "select_date": "⚠ Selecione uma data.",
        "calc_ephem": "Calculando efemérides…",
        "calc_sideral": "Cálculo sideral Djwhal Khul…",
        "calc_karmic": "Interpretação kármica védica em andamento…",
        "transit_title": "⏱ Trânsitos — Data de consulta",
        "support_title": "☕ Apoiar o projeto",
        "support_label": "Me pague um café",
    },
    "de": {
        "code": "de", "label": "🇩🇪 DE",
        "title": "Karmisches Gochara",
        "login": "Anmeldung",
        "create_profile": "Profil erstellen",
        "connect": "Anmelden »",
        "pseudo": "Benutzername:",
        "pseudo_ph": "Dein Benutzername…",
        "karmic_profile": "✦ Karmisches Profil erstellen",
        "firstname": "Vorname:",
        "email": "Email:",
        "birthdate": "Geburtsdatum:",
        "birthtime": "Geburtszeit:",
        "birthcity": "Geburtsstadt:",
        "city_ph": "Stadt suchen…",
        "back": "← Zurück",
        "create": "Mein Profil erstellen »",
        "logout": "Abmelden",
        "settings": "EINSTELLUNGEN",
        "date": "Datum:",
        "hour": "Stunde:",
        "min": "min",
        "transit_ph": "Transitort…",
        "calculate": "✦ Berechnen »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Karmische Karte",
        "synthesis_title": "✦ Karmische Synthese — @siderealAstro13",
        "synthesis_wait": "Starte eine Berechnung für deine vedische karmische Synthese…",
        "aspects_title": "✦ Aktive Aspekte (Orb < 3°)",
        "aspects_wait": "Starte eine Berechnung für die Aspekte…",
        "carte_title": "✦ Karmische Karte — Sideraler Tierkreis",
        "map_wait": "Starte eine Berechnung…",
        "listen": "▶ Anhören",
        "stop": "■ Stop",
        "send_email": "📧 Per Email erhalten",
        "sending": "Wird gesendet…",
        "sent_ok": "✓ Gesendet!",
        "sent_err": "⚠ Sendefehler",
        "ready": "Bereit",
        "no_calc": "Starte zuerst eine Berechnung.",
        "select_transit": "⚠ Wähle einen Transitort aus der Liste.",
        "select_date": "⚠ Wähle ein Datum.",
        "calc_ephem": "Ephemeriden berechnen…",
        "calc_sideral": "Siderale Berechnung Djwhal Khul…",
        "calc_karmic": "Vedische karmische Interpretation läuft…",
        "transit_title": "⏱ Transite — Beratungsdatum",
        "support_title": "☕ Projekt unterstützen",
        "support_label": "Kauf mir einen Kaffee",
    },
    "nl": {
        "code": "nl", "label": "🇳🇱 NL",
        "title": "Karmische Gochara",
        "login": "Inloggen",
        "create_profile": "Profiel aanmaken",
        "connect": "Inloggen »",
        "pseudo": "Gebruikersnaam:",
        "pseudo_ph": "Jouw gebruikersnaam…",
        "karmic_profile": "✦ Karmisch profiel aanmaken",
        "firstname": "Voornaam:",
        "email": "Email:",
        "birthdate": "Geboortedatum:",
        "birthtime": "Geboortetijd:",
        "birthcity": "Geboortestad:",
        "city_ph": "Zoek je stad…",
        "back": "← Terug",
        "create": "Mijn profiel aanmaken »",
        "logout": "Uitloggen",
        "settings": "INSTELLINGEN",
        "date": "Datum:",
        "hour": "Uur:",
        "min": "min",
        "transit_ph": "Transitlocatie…",
        "calculate": "✦ Berekenen »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Karmische Kaart",
        "synthesis_title": "✦ Karmische Synthese — @siderealAstro13",
        "synthesis_wait": "Start een berekening voor je vedische karmische synthese…",
        "aspects_title": "✦ Actieve Aspecten (orb < 3°)",
        "aspects_wait": "Start een berekening om aspecten te zien…",
        "carte_title": "✦ Karmische Kaart — Sideraal Zodiac",
        "map_wait": "Start een berekening…",
        "listen": "▶ Beluisteren",
        "stop": "■ Stop",
        "send_email": "📧 Per email ontvangen",
        "sending": "Verzenden…",
        "sent_ok": "✓ Verzonden!",
        "sent_err": "⚠ Verzendfout",
        "ready": "Klaar",
        "no_calc": "Start eerst een berekening.",
        "select_transit": "⚠ Selecteer een transitlocatie uit de lijst.",
        "select_date": "⚠ Selecteer een datum.",
        "calc_ephem": "Efemeridenberekening…",
        "calc_sideral": "Siderale berekening Djwhal Khul…",
        "calc_karmic": "Vedische karmische interpretatie bezig…",
        "transit_title": "⏱ Transieten — Consultatiedatum",
        "support_title": "☕ Project steunen",
        "support_label": "Koop me een koffie",
    },
    "it": {
        "code": "it", "label": "🇮🇹 IT",
        "title": "Gochara Karmico",
        "login": "Accesso",
        "create_profile": "Crea un profilo",
        "connect": "Accedi »",
        "pseudo": "Pseudonimo:",
        "pseudo_ph": "Il tuo pseudonimo…",
        "karmic_profile": "✦ Crea un profilo karmico",
        "firstname": "Nome:",
        "email": "Email:",
        "birthdate": "Data di nascita:",
        "birthtime": "Ora di nascita:",
        "birthcity": "Città di nascita:",
        "city_ph": "Cerca la tua città…",
        "back": "← Indietro",
        "create": "Crea il mio profilo »",
        "logout": "Disconnetti",
        "settings": "IMPOSTAZIONI",
        "date": "Data:",
        "hour": "Ora:",
        "min": "min",
        "transit_ph": "Luogo di transito…",
        "calculate": "✦ Calcola »",
        "tab_gochara": "◆ Gochara",
        "tab_carte": "✦ Carta Karmica",
        "synthesis_title": "✦ Sintesi karmica — @siderealAstro13",
        "synthesis_wait": "Avvia un calcolo per ottenere la tua sintesi karmica vedica…",
        "aspects_title": "✦ Aspetti attivi (orbe < 3°)",
        "aspects_wait": "Avvia un calcolo per vedere gli aspetti…",
        "carte_title": "✦ Carta Karmica — Zodiaco Siderale",
        "map_wait": "Avvia un calcolo…",
        "listen": "▶ Ascolta",
        "stop": "■ Stop",
        "send_email": "📧 Ricevere per email",
        "sending": "Invio…",
        "sent_ok": "✓ Inviato!",
        "sent_err": "⚠ Errore invio",
        "ready": "Pronto",
        "no_calc": "Avvia prima un calcolo.",
        "select_transit": "⚠ Seleziona un luogo di transito dalla lista.",
        "select_date": "⚠ Seleziona una data.",
        "calc_ephem": "Calcolo effemeridi…",
        "calc_sideral": "Calcolo siderale Djwhal Khul…",
        "calc_karmic": "Interpretazione karmica vedica in corso…",
        "transit_title": "⏱ Transiti — Data di consultazione",
        "support_title": "☕ Supporta il progetto",
        "support_label": "Offrimi un caffè",
    },
}


def get_lang():
    code = session.get("lang", "fr")
    return LANGS.get(code, LANGS["fr"])


# ── Routes publiques ──────────────────────────────────────────────────────────
@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    user = session.get("profile")
    lang = get_lang()
    return render_template(
        "index.html",
        user=user,
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
        lang=lang,
        all_langs=list(LANGS.values()),
    )


@app.route("/set_lang", methods=["POST"])
def set_lang():
    data = request.get_json() or {}
    code = data.get("lang", "fr")
    if code in LANGS:
        session["lang"] = code
    return jsonify({"ok": True, "lang": code})


@app.route("/login", methods=["POST"])
def login():
    from profiles import get_profile_by_pseudo
    data   = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip()
    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400
    try:
        profile = get_profile_by_pseudo(pseudo)
    except Exception as exc:
        app.logger.error("Erreur Sheets login : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500
    if not profile:
        return jsonify({"ok": False, "error": f"Pseudo '{pseudo}' introuvable. Crée ton profil d'abord."}), 404
    session["profile"] = profile
    return jsonify({"ok": True, "pseudo": pseudo, "profile": profile})


@app.route("/register", methods=["POST"])
def register():
    from profiles import get_profile_by_email, pseudo_exists, create_profile
    data   = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip()
    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400
    try:
        if pseudo_exists(pseudo):
            return jsonify({"ok": False, "error": "Pseudo déjà pris"}), 409
        email = (data.get("email") or "").strip().lower()
        if email and get_profile_by_email(email):
            return jsonify({"ok": False, "error": "Email déjà enregistré"}), 409
        profile = create_profile(data)
    except Exception as exc:
        app.logger.error("Erreur Sheets register : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500
    session["profile"] = profile
    return jsonify({"ok": True, "pseudo": pseudo, "profile": profile})


@app.route("/logout", methods=["POST"])
def logout():
    lang = session.get("lang", "fr")
    session.clear()
    session["lang"] = lang
    return jsonify({"ok": True})


@app.route("/geocode")
def geocode():
    import time, requests as req
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    try:
        r = req.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5},
            headers={"User-Agent": "Karmic.Gochara/1.0"},
            timeout=5,
        )
        time.sleep(1)
        return jsonify(r.json())
    except Exception:
        try:
            r2 = req.get(
                "https://photon.komoot.io/api/",
                params={"q": q, "limit": 5},
                headers={"User-Agent": "Karmic.Gochara/1.0"},
                timeout=5,
            )
            features = r2.json().get("features", [])
            results = []
            for f in features:
                p = f.get("properties", {})
                g = f.get("geometry", {}).get("coordinates", [None, None])
                results.append({
                    "display_name": f"{p.get('name','')}, {p.get('country','')}",
                    "lat": str(g[1]), "lon": str(g[0]),
                })
            return jsonify(results)
        except Exception as exc2:
            return jsonify({"error": str(exc2)}), 500


# ── Routes protégées ──────────────────────────────────────────────────────────
@app.route("/calculate", methods=["POST"])
def calculate():
    from astro_calc import calculate_transits
    from ai_interpret import get_synthesis

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    natal = {
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

    data = request.get_json() or {}
    date_str = data.get("date", "")
    hour     = int(data.get("hour", 12))
    minute   = int(data.get("minute", 0))

    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  float(data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
        "lon":  float(data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }

    lang = session.get("lang", "fr")

    try:
        import time as _time
        year, month, day = map(int, date_str.split("-"))
        result = calculate_transits(natal, transit_loc, year, month, day, hour, minute)

        # Retry 3x sur surcharge Anthropic (529 / overloaded_error)
        synthesis = None
        last_exc  = None
        for attempt in range(3):
            try:
                synthesis = get_synthesis(result, profile, lang=lang)
                break
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                if "529" in msg or "overload" in msg:
                    app.logger.warning("Anthropic surchargé (tentative %d/3) : %s", attempt + 1, exc)
                    _time.sleep(3 * (attempt + 1))
                else:
                    raise

        if synthesis is None:
            raise Exception("L'oracle est temporairement surchargé — réessaie dans quelques secondes.")

        result["synthesis"] = synthesis
        return jsonify(result)
    except Exception as exc:
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


@app.route("/send_synthesis", methods=["POST"])
def send_synthesis():
    """Envoie la synthèse karmique par email via Resend."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    email = (profile.get("email") or "").strip()
    if not email:
        return jsonify({"ok": False, "error": "Aucun email dans ton profil"}), 400

    data      = request.get_json() or {}
    synthesis = (data.get("synthesis") or "").strip()
    date_str  = data.get("date", "")
    if not synthesis:
        return jsonify({"ok": False, "error": "Aucune synthèse à envoyer"}), 400

    resend_key = os.environ.get("RESEND_API_KEY", "")
    if not resend_key:
        return jsonify({"ok": False, "error": "Resend non configuré (RESEND_API_KEY manquant)"}), 500

    lang   = get_lang()
    pseudo = profile.get("pseudo") or profile.get("name", "")

    # Corps HTML de l'email
    html_body = f"""
<!DOCTYPE html>
<html lang="{lang['code']}">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; background: #0a0a1a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 680px; margin: 0 auto; background: #0f0f2a; border: 1px solid #4b0082;
                border-radius: 4px; padding: 30px; }}
  h1 {{ color: #d4a017; font-size: 20px; border-bottom: 1px solid #4b0082; padding-bottom: 10px; }}
  .meta {{ color: #9090b0; font-size: 12px; margin-bottom: 20px; }}
  .synthesis {{ white-space: pre-wrap; line-height: 1.7; font-size: 14px; color: #e0d8f0; }}
  .synthesis h2 {{ color: #d4a017; font-size: 16px; margin-top: 24px; }}
  .synthesis h3 {{ color: #c090e0; font-size: 14px; }}
  .footer {{ margin-top: 30px; padding-top: 16px; border-top: 1px solid #4b0082;
             font-size: 11px; color: #606080; text-align: center; }}
  .support {{ margin-top: 20px; text-align: center; }}
  .support a {{
    background: #d4a017; color: #000; text-decoration: none;
    padding: 8px 20px; border-radius: 4px; font-weight: bold; font-size: 13px;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>✦ Karmic Gochara — @siderealAstro13</h1>
  <div class="meta">
    {pseudo} · {date_str} · Jyotish · Djwhal Khul · Chandra Lagna · Whole sign
  </div>
  <div class="synthesis">{synthesis}</div>
  <div class="support">
    <a href="https://buymeacoffee.com/PLACEHOLDER">☕ {lang['support_label']}</a>
  </div>
  <div class="footer">
    Généré par Karmic Gochara · karmic.gochara.onrender.com<br>
    Ayanamsa Djwhal Khul · Chandra Lagna · True Nodes · Whole sign
  </div>
</div>
</body>
</html>
"""

    import requests as req
    try:
        r = req.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
            },
           json={
                "from": "Gochara Karmique <karmic.gochara@astro.jeromemalige.fr>",
                "reply_to": "astro@jeromemalige.fr",
                "to": [email],
                "subject": f"✦ Karmic Gochara Synthesis {date_str}",
                "html": html_body,
            },
            timeout=10,
        )
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        else:
            app.logger.error("Resend error %s : %s", r.status_code, r.text)
            return jsonify({"ok": False, "error": f"Resend {r.status_code}"}), 500
    except Exception as exc:
        app.logger.error("Resend exception : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
