"""
app.py — Gochara Karmique
Application Flask — Architecture multi-utilisateurs
"""

import os
import time
from datetime import datetime

import pytz
from flask import Flask, jsonify, make_response, render_template, request, session, send_from_directory
from dotenv import load_dotenv

load_dotenv()

# Store des paiements en attente d'activation de session (cas navigateur externe).
# Clé : pseudo en minuscule, valeur : {"plan": str, "time": float}
_pending_plan_updates: dict = {}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gochara-secret-2024")
app.config["JSON_AS_ASCII"] = False

TRANSIT_LOC_DEFAULT = {
    "city": "Paris, France",
    "lat":  48.8566,
    "lon":  2.3522,
    "tz":   "Europe/Paris",
}

_SIGNS_FR = [
    "Bélier", "Taureau", "Gémeaux", "Cancer",
    "Lion", "Vierge", "Balance", "Scorpion",
    "Sagittaire", "Capricorne", "Verseau", "Poissons",
]

def _enrich_profile_with_natal(profile: dict, natal: dict) -> dict:
    """
    Enrichit le profil session avec les données du thème natal calculé,
    pour que get_synthesis() dispose de chandra_lagna_sign, ketu_sign, etc.
    natal = result["natal"] de calculate_transits().
    """
    def _sign(display: str) -> str:
        parts = (display or "").strip().split()
        return parts[1] if len(parts) >= 2 else ""

    def _deg(display: str) -> str:
        parts = (display or "").strip().split()
        return parts[2] if len(parts) >= 3 else ""

    def _house(planet_key: str, asc_sign: str) -> str:
        if not asc_sign or asc_sign not in _SIGNS_FR:
            return ""
        p = natal.get(planet_key) or {}
        p_sign = _sign(p.get("display", ""))
        if not p_sign or p_sign not in _SIGNS_FR:
            return ""
        return str((_SIGNS_FR.index(p_sign) - _SIGNS_FR.index(asc_sign)) % 12 + 1)

    enriched = dict(profile)

    asc = natal.get("ASC ↑") or {}
    asc_sign = _sign(asc.get("display", ""))
    enriched["chandra_lagna_sign"] = asc_sign
    enriched["chandra_lagna_deg"]  = _deg(asc.get("display", ""))

    for key, s_field, h_field, nak_field in [
        ("Nœud Sud ☋",      "ketu_sign",            "ketu_house",            "ketu_nakshatra"),
        ("Nœud Nord ☊",     "rahu_sign",            "rahu_house",            "rahu_nakshatra"),
        ("Chiron ⚷",        "chiron_sign",          "chiron_house",          "chiron_nakshatra"),
        ("Lilith ⚸",        "lilith_sign",          "lilith_house",          "lilith_nakshatra"),
        ("Saturne ♄",       "saturn_sign",          "saturn_house",          None),
        ("Jupiter ♃",       "jupiter_sign",         "jupiter_house",         None),
        ("Porte Visible ⊙", "porte_visible_sign",   "porte_visible_house",   None),
        ("Porte Invisible ⊗","porte_invisible_sign", "porte_invisible_house", None),
    ]:
        p = natal.get(key) or {}
        enriched[s_field] = _sign(p.get("display", ""))
        enriched[h_field] = _house(key, asc_sign)
        if nak_field:
            enriched[nak_field] = p.get("nakshatra", "")

    enriched["porte_visible_deg"]   = _deg((natal.get("Porte Visible ⊙")  or {}).get("display", ""))
    enriched["porte_invisible_deg"] = _deg((natal.get("Porte Invisible ⊗") or {}).get("display", ""))

    moon = natal.get("Lune ☽") or {}
    moon_lon = moon.get("lon_raw") or moon.get("lon")
    if moon_lon is not None:
        enriched["moon_longitude_sid"]   = str(round(float(moon_lon), 6))
        enriched["chandra_lagna_degree"] = str(round(float(moon_lon) % 30, 6))
    else:
        enriched["moon_longitude_sid"]   = ""
        enriched["chandra_lagna_degree"] = ""

    # Ajout de tous les degrés planétaires pour la carte SVG
    for p_key in ["Lune ☽", "Soleil ☉", "Mercure ☿", "Vénus ♀", "Mars ♂",
                  "Jupiter ♃", "Saturne ♄", "Nœud Nord ☊", "Nœud Sud ☋",
                  "Chiron ⚷", "Lilith ⚸", "Porte Visible ⊙", "Porte Invisible ⊗"]:
        planet_name = p_key.split(" ")[0].lower()
        p_data = natal.get(p_key, {})
        enriched[f"{planet_name}_deg"] = _deg(p_data.get("display", ""))

    # On ajoute natal_positions pour l'interprétation immédiate
    # ATTENTION: à supprimer avant session storage pour limiter la taille du cookie (max 4KB)
    enriched["natal_positions"] = natal

    return enriched

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
        "hero_title": "Ton", "hero_em": "Karma", "hero_sub_a": "écrit dans les étoiles",
        "hero_subtitle": "Astrologie Védique Sidérale · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Nœud Sud · mémoires passées · schémas de résistance",
        "hero_chiron": "Chiron · blessure originelle · clé de la Porte Visible",
        "hero_stage": "Dharma · lieu de libération · action incarnée",
        "hero_hook1": "Ton <strong>Ketu</strong> révèle la prison de mémoires passées.",
        "hero_hook2": "Ton <strong>Chiron</strong> est la clé qui ouvre la porte.",
        "hero_hook3": "Ton <strong>Stage</strong> est la scène qui t'attend.",
        "hero_cta": "Accéder à ta synthèse",
        "geo_auto": "Position auto ou saisir une ville…",
        "pillar1_title": "Mémoire Karmique",
        "pillar2_title": "Blessure Originelle",
        "pillar3_title": "Mise en Scène",
        # Pricing table
        "pricing_title": "✦ Accès & Tarifs",
        "pricing_free": "Gratuit",
        "pricing_lecture": "Lecture",
        "pricing_unlimited": "Illimité",
        "pricing_per_month": "/mois",
        "feat_signal": "Signal du Jour",
        "feat_natal": "Lecture natale",
        "feat_synthesis": "Synthèse karmique complète",
        "feat_chatbot": "Chatbot karmique",
        "feat_chatbot_lecture": "3 questions",
        "feat_chatbot_unlimited": "illimité si IA locale · sinon 10/mois",
        "feat_alerts": "Alertes live & mémoire",
        "feat_local_ai": "IA locale (Edge AI)",
        "feat_local_ai_note": "si présent sur l'appareil",
        # App section labels
        "section_natal": "✦ Lecture natale",
        "section_signal": "◆ Signal du jour",
        "loading_aspects": "Lecture des aspects…",
        "transit_location": "LIEU DE TRANSIT",
        "geo_use_location": "Utiliser ma position actuelle",
        "btn_signal": "◆ VOIR LE SIGNAL DU JOUR",
        "btn_reading": "✦ OBTENIR LA LECTURE COMPLÈTE",
        "btn_choose_plan": "✦ CHOISIR UN PLAN",
        "plan_lecture_desc": "Synthèse complète · 3 questions chatbot · accès immédiat",
        "plan_unlimited_desc": "Chatbot illimité si IA locale · sinon 10/mois · alertes live",
        "rating_label": "Cette lecture t'a-t-elle touché ?",
        "alerts_label": "🔔 Alertes transit par email",
        "interp_credit": "Interprétation @siderealastro13",
        # JS UI strings (injected via window.T)
        "js_err_pseudo": "Pseudo requis.",
        "js_login_loading": "Alignement des énergies…",
        "js_err_unknown": "Inconnu.",
        "js_err_network": "Erreur réseau.",
        "js_err_birth": "Champs de naissance manquants.",
        "js_err_email": "Email requis pour les alertes et l'envoi de synthèse.",
        "js_err_payment": "Erreur paiement",
        "js_badge_local": "⬡ IA LOCALE",
        "js_badge_claude": "☁ CLAUDE",
        "js_register_loading": "Création du profil…",
        "js_chat_placeholder": "Ta question…",
        "js_chat_send": "ENVOYER",
        "js_chat_unlimited": "∞ Questions illimitées",
        "js_chat_remaining": "{n}/{limit} questions",
        "js_chat_exhausted": "Questions épuisées (0/{limit})",
        "js_chat_upgrade_hint": "Passe à Illimité pour continuer.",
        "js_expand_link": "→ Révèle ton Alternative de Conscience",
        "js_expand_loading": "Lecture en cours…",
        "js_cta_label": "Lecture · 4,99€",
        "js_cta_desc": "Synthèse complète · 3 questions chatbot · accès immédiat",
        "js_cta_btn": "Débloquer la Synthèse — 4,99€",
        "js_err_select_date": "Sélectionne une date.",
        "js_err_select_loc": "Sélectionne un lieu de transit.",
        "js_transit_loading": "LECTURE EN COURS…",
        "js_transit_reread": "◆ RELIRE LE SIGNAL",
        "js_calc_loading": "CALCUL ASTRAL…",
        "js_calc_reading": "LECTURE DES ASTRES…",
        "js_no_calc_email": "Lance d'abord un calcul pour obtenir ta synthèse.",
        "js_email_sending": "Envoi en cours…",
        "js_email_sent": "✓ Synthèse envoyée par email.",
        "js_email_err": "✗ Erreur : ",
        "js_email_network_err": "✗ Erreur réseau.",
        "js_unlock_success": "✓ App débloquée",
        "js_alerts_updating": "Mise à jour…",
        "js_alerts_enabled": "✓ Alertes activées.",
        "js_alerts_disabled": "✓ Alertes désactivées.",
        "js_months": ["","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
        "js_calendar_empty": "Aucun transit majeur ce mois-ci.",
        "js_report_loading": "⏳ Génération en cours… (1-2 min)",
        "js_report_err": "Erreur réseau lors de la génération du PDF.",
        "js_modal_title": "✦ Contribuer au modèle karmique",
        "js_modal_text": "Autorises-tu l'utilisation anonyme de cette lecture pour entraîner le modèle d'astrologie karmique ?<br>Aucune donnée personnelle (nom, email) n'est transmise.",
        "js_modal_consent": "J'autorise l'utilisation anonyme de mes positions natales et de cette synthèse.",
        "js_modal_decline": "Non merci",
        "js_rating_up": "✦ Merci — feedback enregistré.",
        "js_rating_down": "✦ Noté — on s'améliore.",
        "js_geo_denied": "Permission refusée — saisir une ville",
        "js_geo_error": "Erreur GPS — saisir une ville",
        "js_geo_unsupported": "Géolocalisation non supportée — saisir une ville",
        "js_geo_locating": "Localisation…",
        "js_toggle_register": "S'INSCRIRE ET SE CONNECTER",
        "js_toggle_login": "RETOUR À LA CONNEXION",
        "js_signal_btn": "◆ VOIR LE SIGNAL DU JOUR",
        "js_gemma_loading": "GEMMA LOCAL…",
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
        "hero_title": "Your", "hero_em": "Karma", "hero_sub_a": "written in the stars",
        "hero_subtitle": "Sidereal Vedic Astrology · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "South Node · past memories · resistance patterns",
        "hero_chiron": "Chiron · original wound · key to the Visible Door",
        "hero_stage": "Dharma · place of liberation · embodied action",
        "hero_hook1": "Your <strong>Ketu</strong> reveals the prison of past memories.",
        "hero_hook2": "Your <strong>Chiron</strong> is the key that opens the door.",
        "hero_hook3": "Your <strong>Stage</strong> is the scene waiting for you.",
        "hero_cta": "Access your synthesis",
        "geo_auto": "Auto position or type a city…",
        "pillar1_title": "Karmic Memory",
        "pillar2_title": "Core Wound",
        # Pricing table
        "pricing_title": "✦ Access & Plans",
        "pricing_free": "Free",
        "pricing_lecture": "Reading",
        "pricing_unlimited": "Unlimited",
        "pricing_per_month": "/mo",
        "feat_signal": "Daily Signal",
        "feat_natal": "Natal Reading",
        "feat_synthesis": "Complete Karmic Synthesis",
        "feat_chatbot": "Karmic Chatbot",
        "feat_chatbot_lecture": "3 questions",
        "feat_chatbot_unlimited": "unlimited if local AI · otherwise 10/mo",
        "feat_alerts": "Live alerts & memory",
        "feat_local_ai": "Local AI (Edge AI)",
        "feat_local_ai_note": "if available on device",
        # App section labels
        "section_natal": "✦ Natal Reading",
        "section_signal": "◆ Daily Signal",
        "loading_aspects": "Reading aspects…",
        "transit_location": "TRANSIT LOCATION",
        "geo_use_location": "Use my current location",
        "btn_signal": "◆ SEE DAILY SIGNAL",
        "btn_reading": "✦ GET FULL READING",
        "btn_choose_plan": "✦ CHOOSE A PLAN",
        "plan_lecture_desc": "Complete synthesis · 3 chatbot questions · immediate access",
        "plan_unlimited_desc": "Unlimited chatbot if local AI · otherwise 10/mo · live alerts",
        "rating_label": "Did this reading resonate?",
        "alerts_label": "🔔 Transit alerts by email",
        "interp_credit": "Interpretation @siderealastro13",
        # JS UI strings (injected via window.T)
        "js_err_pseudo": "Username required.",
        "js_login_loading": "Aligning energies…",
        "js_err_unknown": "Unknown error.",
        "js_err_network": "Network error.",
        "js_err_birth": "Birth fields missing.",
        "js_err_email": "Email required for alerts and synthesis delivery.",
        "js_err_payment": "Payment error",
        "js_badge_local": "⬡ LOCAL AI",
        "js_badge_claude": "☁ CLAUDE",
        "js_register_loading": "Creating profile…",
        "js_chat_placeholder": "Your question…",
        "js_chat_send": "SEND",
        "js_chat_unlimited": "∞ Unlimited questions",
        "js_chat_remaining": "{n}/{limit} questions",
        "js_chat_exhausted": "Questions exhausted (0/{limit})",
        "js_chat_upgrade_hint": "Upgrade to Unlimited to continue.",
        "js_expand_link": "→ Reveal your Consciousness Alternative",
        "js_expand_loading": "Reading in progress…",
        "js_cta_label": "Reading · €4.99",
        "js_cta_desc": "Complete synthesis · 3 chatbot questions · immediate access",
        "js_cta_btn": "Unlock Synthesis — €4.99",
        "js_err_select_date": "Select a date.",
        "js_err_select_loc": "Select a transit location.",
        "js_transit_loading": "READING IN PROGRESS…",
        "js_transit_reread": "◆ RE-READ SIGNAL",
        "js_calc_loading": "ASTRAL CALCULATION…",
        "js_calc_reading": "READING THE STARS…",
        "js_no_calc_email": "Run a calculation first to get your synthesis.",
        "js_email_sending": "Sending…",
        "js_email_sent": "✓ Synthesis sent by email.",
        "js_email_err": "✗ Error: ",
        "js_email_network_err": "✗ Network error.",
        "js_unlock_success": "✓ App unlocked",
        "js_alerts_updating": "Updating…",
        "js_alerts_enabled": "✓ Alerts enabled.",
        "js_alerts_disabled": "✓ Alerts disabled.",
        "js_months": ["","January","February","March","April","May","June","July","August","September","October","November","December"],
        "js_calendar_empty": "No major transits this month.",
        "js_report_loading": "⏳ Generating… (1-2 min)",
        "js_report_err": "Network error while generating PDF.",
        "js_modal_title": "✦ Contribute to the karmic model",
        "js_modal_text": "Do you authorize the anonymous use of this reading to train the karmic astrology model?<br>No personal data (name, email) is transmitted.",
        "js_modal_consent": "I authorize the anonymous use of my natal positions and this synthesis.",
        "js_modal_decline": "No thanks",
        "js_rating_up": "✦ Thank you — feedback recorded.",
        "js_rating_down": "✦ Noted — we're improving.",
        "js_geo_denied": "Permission denied — type a city",
        "js_geo_error": "GPS error — type a city",
        "js_geo_unsupported": "Geolocation not supported — type a city",
        "js_geo_locating": "Locating…",
        "js_toggle_register": "SIGN UP AND LOG IN",
        "js_toggle_login": "BACK TO LOGIN",
        "js_signal_btn": "◆ SEE DAILY SIGNAL",
        "js_gemma_loading": "LOCAL AI…",
        "pillar3_title": "The Stage",
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
        "hero_title": "Tu", "hero_em": "Karma", "hero_sub_a": "escrito en las estrellas",
        "hero_subtitle": "Astrología Védica Sideral · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Nodo Sur · memorias pasadas · patrones de resistencia",
        "hero_chiron": "Chiron · herida original · llave de la Puerta Visible",
        "hero_stage": "Dharma · lugar de liberación · acción encarnada",
        "hero_hook1": "Tu <strong>Ketu</strong> revela la prisión de memorias pasadas.",
        "hero_hook2": "Tu <strong>Chiron</strong> es la llave que abre la puerta.",
        "hero_hook3": "Tu <strong>Stage</strong> es el escenario que te espera.",
        "hero_cta": "Acceder a tu síntesis",
        "geo_auto": "Posición auto o escribe una ciudad…",
        "pillar1_title": "Memoria Kármica",
        "pillar2_title": "Herida Original",
        "pillar3_title": "La Escena",
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
        "hero_title": "Seu", "hero_em": "Karma", "hero_sub_a": "escrito nas estrelas",
        "hero_subtitle": "Astrologia Védica Sideral · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Nodo Sul · memórias passadas · padrões de resistência",
        "hero_chiron": "Chiron · ferida original · chave da Porta Visível",
        "hero_stage": "Dharma · lugar de libertação · ação encarnada",
        "hero_hook1": "Seu <strong>Ketu</strong> revela a prisão de memórias passadas.",
        "hero_hook2": "Seu <strong>Chiron</strong> é a chave que abre a porta.",
        "hero_hook3": "Seu <strong>Stage</strong> é o palco que te espera.",
        "hero_cta": "Acessar sua síntese",
        "geo_auto": "Posição auto ou digitar uma cidade…",
        "pillar1_title": "Memória Kármica",
        "pillar2_title": "Ferida Original",
        "pillar3_title": "O Palco",
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
        "hero_title": "Dein", "hero_em": "Karma", "hero_sub_a": "in den Sternen geschrieben",
        "hero_subtitle": "Siderische Vedische Astrologie · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Südknoten · vergangene Erinnerungen · Widerstandsmuster",
        "hero_chiron": "Chiron · ursprüngliche Wunde · Schlüssel zur Sichtbaren Tür",
        "hero_stage": "Dharma · Ort der Befreiung · verkörperte Handlung",
        "hero_hook1": "Dein <strong>Ketu</strong> enthüllt das Gefängnis vergangener Erinnerungen.",
        "hero_hook2": "Dein <strong>Chiron</strong> ist der Schlüssel, der die Tür öffnet.",
        "hero_hook3": "Deine <strong>Stage</strong> ist die Bühne, die auf dich wartet.",
        "hero_cta": "Zugang zu deiner Synthese",
        "geo_auto": "Automatische Position oder Stadt eingeben…",
        "pillar1_title": "Karmisches Gedächtnis",
        "pillar2_title": "Urwunde",
        "pillar3_title": "Die Bühne",
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
        "hero_title": "Jouw", "hero_em": "Karma", "hero_sub_a": "geschreven in de sterren",
        "hero_subtitle": "Siderische Vedische Astrologie · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Zuidknoop · herinneringen uit het verleden · weerstandspatronen",
        "hero_chiron": "Chiron · oorspronkelijke wond · sleutel tot de Zichtbare Deur",
        "hero_stage": "Dharma · plek van bevrijding · belichaamde actie",
        "hero_hook1": "Jouw <strong>Ketu</strong> onthult de gevangenis van herinneringen.",
        "hero_hook2": "Jouw <strong>Chiron</strong> is de sleutel die de deur opent.",
        "hero_hook3": "Jouw <strong>Stage</strong> is het podium dat op je wacht.",
        "hero_cta": "Toegang tot je synthese",
        "geo_auto": "Auto positie of typ een stad…",
        "pillar1_title": "Karmisch Geheugen",
        "pillar2_title": "Oerwond",
        "pillar3_title": "Het Podium",
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
        "hero_title": "Il tuo", "hero_em": "Karma", "hero_sub_a": "scritto nelle stelle",
        "hero_subtitle": "Astrologia Vedica Siderale · Chandra Lagna · DK Ayanamsa",
        "hero_ketu": "Nodo Sud · memorie passate · schemi di resistenza",
        "hero_chiron": "Chiron · ferita originale · chiave della Porta Visibile",
        "hero_stage": "Dharma · luogo di liberazione · azione incarnata",
        "hero_hook1": "Il tuo <strong>Ketu</strong> rivela la prigione delle memorie passate.",
        "hero_hook2": "Il tuo <strong>Chiron</strong> è la chiave che apre la porta.",
        "hero_hook3": "Il tuo <strong>Stage</strong> è la scena che ti aspetta.",
        "hero_cta": "Accedi alla tua sintesi",
        "geo_auto": "Posizione auto o digita una città…",
        "pillar1_title": "Memoria Karmica",
        "pillar2_title": "Ferita Originale",
        "pillar3_title": "La Scena",
    },
}


def get_lang():
    if "lang" not in session:
        accept = request.headers.get("Accept-Language", "fr")
        for part in accept.replace(" ", "").split(","):
            prefix = part.split(";")[0].split("-")[0].lower()
            if prefix in LANGS:
                session["lang"] = prefix
                break
        else:
            session["lang"] = "fr"
    return LANGS.get(session["lang"], LANGS["fr"])


# ── Routes publiques ──────────────────────────────────────────────────────────
@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")


@app.route("/privacy")
def privacy():
    return render_template("privacy-policy.html")


@app.route("/.well-known/assetlinks.json")
def assetlinks():
    """Android App Links — permet au système de vérifier le domaine et rouvrir l'app."""
    data = [{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.karmicgochara.app",
            "sha256_cert_fingerprints": [
                "93:2B:A1:79:9C:2E:D7:BF:86:B2:2F:86:46:09:56:80:A8:5C:AD:56:D0:27:4D:DE:6F:53:C9:02:00:A1:DF:FE"
            ]
        }
    }]
    resp = make_response(jsonify(data))
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/")
def index():
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    user = session.get("profile")
    lang = get_lang()

    # Retour depuis Stripe : appliquer le plan si la session en a gardé la trace.
    if request.args.get("payment") == "success":
        payment_info = session.get("payment_completed")
        if payment_info and user and user.get("pseudo") == payment_info.get("pseudo"):
            user["plan"] = payment_info["plan"]
            session["profile"] = user
            session.modified = True

    return render_template(
        "index.html",
        user=user,
        today_iso=now.strftime("%Y-%m-%d"),
        now_hour=now.hour,
        now_minute=now.minute,
        lang=lang,
        ui=lang,  # On utilise 'lang' pour remplir 'ui'
        langs=LANGS,  # On envoie le dictionnaire complet pour la boucle for
        session_user=session.get('pseudo', ''),
        session_profile=session.get('profile', {}),
        enable_local_ai=os.environ.get('ENABLE_LOCAL_AI', '').lower() in ('1', 'true'),
        enable_features=os.environ.get('ENABLE_FEATURES', '').lower() in ('1', 'true'),
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

    # ── Contournement de la latence Sheets après paiement ────────────────────
    # 1. Store en mémoire (cas navigateur externe — session différente)
    pending = _pending_plan_updates.pop(pseudo.strip().lower(), None)
    if pending and time.time() - pending["time"] < 3600:
        profile["plan"] = pending["plan"]
        app.logger.info("Login post-paiement (store mémoire) : plan '%s' pour %s", pending["plan"], pseudo)
    # 2. Drapeau de session (cas WebView — même session)
    elif session.get("payment_completed"):
        payment_info = session.pop("payment_completed", None)
        if payment_info and payment_info.get("pseudo") == pseudo:
            profile["plan"] = payment_info.get("plan", profile["plan"])
            app.logger.info("Login post-paiement (session) : plan '%s' pour %s", profile["plan"], pseudo)

    session["profile"] = profile
    session["pseudo"] = pseudo

    # ── Hook natal : généré au login depuis données Sheets ───────────────────
    # Le profil contient chandra_lagna_sign si natal déjà calculé à l'inscription
    hook_natal = ""
    cache_key  = f"hook_natal_{pseudo}"
    if session.get(cache_key):
        hook_natal = session[cache_key]

    # Toujours recalculer natal_positions en session (non stocké dans le Sheet)
    try:
        from astro_calc import calculate_transits
        from profiles import save_natal_to_sheet
        from ai_interpret import get_hook_natal
        from datetime import date as _date

        natal_input = {
            "name":   profile["name"],
            "year":   profile["year"],   "month":  profile["month"],
            "day":    profile["day"],    "hour":   profile["hour"],
            "minute": profile["minute"], "lat":    profile["lat"],
            "lon":    profile["lon"],    "tz":     profile["tz"],
            "city":   profile["city"],
        }
        today = _date.today()
        transit_loc = {
            "city": profile["city"], "lat": profile["lat"],
            "lon":  profile["lon"],  "tz":  profile["tz"],
        }
        natal_result = calculate_transits(natal_input, transit_loc,
                                          today.year, today.month, today.day, 12, 0)

        enriched = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))

        user_key = data.get("user_key")
        user_model = data.get("user_model")
        user_provider = data.get("user_provider")
        if user_key: enriched["user_key"] = user_key
        if user_model: enriched["user_model"] = user_model
        if user_provider: enriched["user_provider"] = user_provider

        if not profile.get("chandra_lagna_sign"):
            save_natal_to_sheet(pseudo, enriched)

        # On garde enriched pour l'interprétation et le retour JSON
        profile = enriched
        if not hook_natal:
            hook_natal = get_hook_natal(profile)
            session[cache_key] = hook_natal

        # Mais on retire les positions lourdes pour le stockage en session (cookie 4KB)
        profile_session = profile.copy()
        profile_session.pop("natal_positions", None)
        profile_session.pop("user_key", None)
        profile_session.pop("user_model", None)
        profile_session.pop("user_provider", None)
        session["profile"] = profile_session
    except Exception as exc:
        app.logger.warning("Hook natal login échoué : %s", exc)

    return jsonify({"ok": True, "pseudo": pseudo, "profile": profile, "hook_natal": hook_natal, "hook_engine": "claude"})


@app.route("/register", methods=["POST"])
def register():
    from profiles import get_profile_by_email, pseudo_exists, create_profile
    data   = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip()
    if not pseudo:
        return jsonify({"ok": False, "error": "Pseudo requis"}), 400

    app.logger.info("REGISTER data reçue: %s", data)

    # Normalise : parse birth_date / birth_time si envoyés comme strings
    if "birth_date" in data and "year" not in data:
        try:
            parts = str(data["birth_date"]).split("-")
            data["year"], data["month"], data["day"] = int(parts[0]), int(parts[1]), int(parts[2])
        except Exception as e:
            app.logger.warning("Parse birth_date échoué: %s", e)
    if "birth_time" in data and "hour" not in data:
        try:
            tp = str(data["birth_time"]).split(":")
            data["hour"], data["minute"] = int(tp[0]), int(tp[1])
        except Exception as e:
            app.logger.warning("Parse birth_time échoué: %s", e)
    # Valeurs par défaut obligatoires
    data.setdefault("name", pseudo)
    data.setdefault("city", data.get("birth_city", ""))
    data.setdefault("lat", 48.8566)
    data.setdefault("lon", 2.3522)
    data.setdefault("tz", "Europe/Paris")
    # Transit = lieu natal par défaut
    data.setdefault("transit_city", data.get("city", ""))
    data.setdefault("transit_lat",  data.get("lat", 48.8566))
    data.setdefault("transit_lon",  data.get("lon", 2.3522))
    data.setdefault("transit_tz",   data.get("tz", "Europe/Paris"))

    try:
        if pseudo_exists(pseudo):
            return jsonify({"ok": False, "error": "Pseudo déjà pris"}), 409
        email = (data.get("email") or "").strip().lower()
        if email and get_profile_by_email(email):
            return jsonify({"ok": False, "error": "Email déjà enregistré"}), 409

        # 1. Create basic profile in sheet
        profile = create_profile(data)
        session["pseudo"] = pseudo
        session["profile"] = profile
    except Exception as exc:
        app.logger.error("Erreur Sheets register : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500

    # 2. Try to calculate natal and enrich
    hook_natal = ""
    try:
        from astro_calc import calculate_transits
        from profiles import save_natal_to_sheet
        from datetime import date as _date
        from ai_interpret import get_hook_natal

        natal_input = {
            "name":   profile["name"],
            "year":   profile["year"],   "month":  profile["month"],
            "day":    profile["day"],    "hour":   profile["hour"],
            "minute": profile["minute"], "lat":    profile["lat"],
            "lon":    profile["lon"],    "tz":     profile["tz"],
            "city":   profile["city"],
        }
        today = _date.today()
        transit_loc = {
            "city": profile["city"], "lat": profile["lat"],
            "lon":  profile["lon"],  "tz":  profile["tz"],
        }
        natal_result     = calculate_transits(natal_input, transit_loc,
                                              today.year, today.month, today.day, 12, 0)
        
        # Verify result content before enriching
        if not natal_result.get("natal"):
            app.logger.error("Calcul natal a retourné un résultat vide pour %s", pseudo)
        else:
            enriched_profile = _enrich_profile_with_natal(profile, natal_result.get("natal", {}))
            
            # 3. Save natal info to sheet and update session
            user_key = data.get("user_key")
            user_model = data.get("user_model")
            user_provider = data.get("user_provider")

            if user_key: enriched_profile["user_key"] = user_key
            if user_model: enriched_profile["user_model"] = user_model
            if user_provider: enriched_profile["user_provider"] = user_provider

            if save_natal_to_sheet(pseudo, enriched_profile):
                profile = enriched_profile
                # On retire les positions lourdes pour le stockage en session (cookie 4KB)
                profile_session = profile.copy()
                profile_session.pop("natal_positions", None)
                profile_session.pop("user_key", None)
                profile_session.pop("user_model", None)
                profile_session.pop("user_provider", None)
                session["profile"] = profile_session
                app.logger.info("Profil enrichi et sauvegardé pour %s", pseudo)
            else:
                app.logger.error("Échec de save_natal_to_sheet pour %s", pseudo)

            # 4. Generate hook
            hook_natal = get_hook_natal(profile)
    except Exception as exc:
        app.logger.error("Calcul natal register échoué pour %s : %s", pseudo, exc, exc_info=True)

    return jsonify({"ok": True, "pseudo": pseudo, "profile": profile, "hook_natal": hook_natal, "hook_engine": "claude"})



@app.route("/chart/karmic.svg")
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
            res = calculate_transits(
                profile, profile,
                profile["year"], profile["month"], profile["day"],
                profile["hour"], profile["minute"],
            )
            natal_pos = res.get("natal", {})
        except Exception as exc:
            app.logger.error("Erreur recalcul natal pour SVG: %s", exc)
            return "Erreur calcul", 500

    # ── Transit positions (optionnel — paramètres ?date=YYYY-MM-DD&hour=H) ───
    transit_pos  = None
    transit_date = None
    date_param   = request.args.get("date", "").strip()
    if date_param:
        try:
            from datetime import date as _date
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
            app.logger.warning("SVG transit calc error: %s", exc)

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
    from profiles import check_and_increment_synthesis
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
    UNLIMITED_PSEUDOS = {"jero"}

    if pseudo.lower() in UNLIMITED_PSEUDOS or user_key:
        quota = {"allowed": True, "remaining": 999}
    else:
        plan = profile.get("plan", "free")
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("test", "subscription", "lecture", "essential", "illimite"):
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
        last_exc  = None
        for attempt in range(3):
            try:
                synthesis = get_synthesis(result, enriched_profile, lang=lang)
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

        # Validation doctrinale
        validation_result = SynthesisValidator().validate(synthesis)
        if validation_result.get("warnings"):
            app.logger.warning(
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
        app.logger.error("Erreur calcul : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500



@app.route("/hook/transit", methods=["POST"])
def hook_transit():
    """
    Hook de 3 phrases basé sur les aspects du jour — streaming SSE.
    Le calcul astro se fait d'abord, puis le texte est streamé mot à mot.
    Cache 24h par pseudo+date (si déjà en cache → replay rapide streamé).

    Body JSON : {"date": "2026-04-09", "hour": 12, "minute": 0,
                 "transit_city": "...", "transit_lat": ..., "transit_lon": ..., "transit_tz": "..."}
    Retourne : text/event-stream SSE
      data: <chunk>\n\n   — tokens au fil de l'eau
      data: [DONE]\n\n   — fin du stream
      data: [ERROR] message\n\n — erreur
    """
    from astro_calc import calculate_transits
    from ai_interpret import _build_system_prompt, _aspects_to_text, _build_natal_context
    from flask import Response, stream_with_context
    import json as _json

    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data     = request.get_json() or {}
    date_str = data.get("date", "")
    if not date_str:
        return jsonify({"ok": False, "error": "Date requise"}), 400

    pseudo    = profile.get("pseudo", "")
    cache_key = f"hook_transit_{pseudo}_{date_str}"
    lang      = session.get("lang", "fr")

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
        app.logger.error("Erreur calcul hook transit : %s", exc, exc_info=True)
        def err_stream():
            yield f"data: [ERROR] {str(exc)}\n\n"
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
            app.logger.warning("update_profile hook/transit: %s", e)
    session["profile"] = {**profile, **new_transit}
    session.modified = True

    # ── Prompt ────────────────────────────────────────────────────────────────
    aspects_text = _aspects_to_text(chart_data.get("aspects", []), max_aspects=3)
    natal_mini   = _build_natal_context(enriched_profile)
    name         = enriched_profile.get("name", "")
    date_label   = chart_data.get("transit_date", date_str)

    # Activations nakshatra : planètes lentes dans le nakshatra natal de Ketu/Rahu/Chiron
    from transit_alerts import _active_nak_activations, PLANET_LABELS as _PLANET_LABELS

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

    if lang == "fr":
        system = (
            "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
            "Style : oraculaire, direct, pas de liste mécanique. "
            "Zéro degrés, zéro orbes dans le texte. Tutoiement. "
            "INTERDIT ABSOLU : noms de signes zodiacaux "
            "(Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, "
            "Sagittaire, Capricorne, Verseau, Poissons). "
            "Utilise uniquement les maisons (H1, H3…) et les noms de planètes."
        )
        prompt = (
            f"Thème natal de {name} :\n{natal_mini}\n\n"
            f"Aspects actifs ce jour ({date_label}) — ne pas citer tels quels :\n{aspects_text}\n\n"
            f"{nakshatra_context}"
            f"Écris un hook de 3 phrases. Pas de titre. Pas d'introduction.\n"
            f"Phrase 1 : ce qui se réactive dans la mémoire karmique de {name} aujourd'hui.\n"
            f"Phrase 2 : ce que ça touche dans sa blessure profonde.\n"
            f"Phrase 3 : l'amorce de l'Alternative de Conscience — ce qui change si {name} choisit autrement.\n"
            f"Donne envie d'obtenir la lecture complète. Ton dense et précis."
        )
    else:
        system = (
            "You are @siderealAstro13. Vedic karmic soul reader. "
            "Style: oracular, direct, no mechanical list. "
            "No degrees, no orbs in the text. Address as 'you'. "
            "ABSOLUTE PROHIBITION: zodiac sign names "
            "(Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, "
            "Sagittarius, Capricorn, Aquarius, Pisces). "
            "Use only house numbers (H1, H3…) and planet names."
        )
        prompt = (
            f"Natal chart of {name}:\n{natal_mini}\n\n"
            f"Active aspects ({date_label}) — do not quote as-is:\n{aspects_text}\n\n"
            f"{nakshatra_context}"
            f"Write a hook of 3 sentences. No title. No introduction.\n"
            f"Sentence 1: what reactivates in {name}'s karmic memory today.\n"
            f"Sentence 2: what this touches in their core wound.\n"
            f"Sentence 3: the seed of the Alternative of Consciousness.\n"
            f"Make them want the full reading. Dense and precise."
        )

    hook_model = os.environ.get("HOOK_MODEL", "gemini-2.5-flash")

    # ── Stream SSE ────────────────────────────────────────────────────────────
    # On capture le profil enrichi dans une var locale pour le cache post-stream
    _enriched = enriched_profile
    _cache_key = cache_key

    def generate():
        full_text = []
        from ai_interpret import stream_ai
        try:
            for text in stream_ai(system, prompt, user=_enriched, max_tokens=1024):
                if not text.startswith("[ERROR]"):
                    full_text.append(text)
                yield f"data: {_json.dumps(text)}\n\n"
            yield f"data: [DONE]\n\n"
        except Exception as exc:
            app.logger.error("Erreur stream hook transit : %s", exc)
            yield f"data: [ERROR] {str(exc)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


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
    <a href="https://buymeacoffee.com/jerome6">☕ {lang['support_label']}</a>
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


# ── Inférence locale : retourne le prompt sans appeler Claude ─────────────────
@app.route("/synthesis/prompt", methods=["POST"])
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
        build_prompt_only, build_prompt_natal,
        build_prompt_conscience, build_prompt_signal,
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
    UNLIMITED_PSEUDOS = {"jero"}

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
        from astro_calc import calculate_transits
        from ai_interpret import _aspects_to_text, _build_natal_context
        from transit_alerts import _active_nak_activations, PLANET_LABELS as _PLANET_LABELS
        date_str = data.get("date", "")
        if not date_str:
            return jsonify({"error": "Date requise"}), 400
        hour_t   = int(data.get("hour",   12))
        minute_t = int(data.get("minute", 0))
        transit_loc_t = {
            "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
            "lat":  float(data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
            "lon":  float(data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
            "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
        }
        natal_t = {
            "name": profile["name"], "year": profile["year"], "month": profile["month"],
            "day":  profile["day"],  "hour": profile["hour"], "minute": profile["minute"],
            "lat":  profile["lat"],  "lon":  profile["lon"],  "tz":     profile["tz"],
            "city": profile["city"],
        }
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
                app.logger.warning("update_profile hook_transit prompt: %s", e)
        session["profile"] = {**profile, **new_transit_t}
        session.modified = True
        return jsonify({"ok": True, "context": "hook_transit", "system": system_t, "user": user_t})

    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # Synthèse complète + Alternative de Conscience : gate paiement
    if pseudo.lower() not in UNLIMITED_PSEUDOS and not user_key:
        plan = profile.get("plan", "free")
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("test", "subscription", "lecture", "essential", "illimite"):
            from profiles import consume_plan_synthesis
            if not consume_plan_synthesis(pseudo):
                return jsonify({"error": "quota_exceeded",
                                "message": "Tu n'as plus de synthèses disponibles sur ton plan."}), 429
        else:
            return jsonify({"error": "quota_exceeded",
                            "message": "La synthèse karmique est réservée au plan Lecture.",
                            "upgrade_url": "/stripe/checkout?product=test"}), 429

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
        "lat":  float(data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
        "lon":  float(data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }

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
            prompts = build_prompt_only(chart_data, enriched_profile, lang=lang)

        return jsonify({
            "ok":           True,
            "context":      context,
            "system":       prompts["system"],
            "user":         prompts["user"],
            "aspects":      chart_data.get("aspects", []),
            "transit_date": chart_data.get("transit_date", ""),
        })
    except Exception as exc:
        app.logger.error("Erreur synthesis/prompt (%s) : %s", context, exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Chatbot karmique : quota + prompt pour Gemma local ───────────────────────

@app.route("/chat/status", methods=["GET"])
def chat_status():
    """Retourne le plan et le quota chatbot restant pour l'utilisateur connecté."""
    from profiles import get_chat_quota
    profile = session.get("profile")
    if not profile:
        return jsonify({"plan": "free", "remaining": 0, "limit": 0})
    pseudo = profile.get("pseudo", "")
    UNLIMITED_PSEUDOS = {"jero"}
    if pseudo.lower() in UNLIMITED_PSEUDOS:
        return jsonify({"plan": "subscription", "remaining": 999, "limit": 999})
    return jsonify(get_chat_quota(pseudo))


@app.route("/chat/ask", methods=["POST"])
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
    UNLIMITED_PSEUDOS = {"jero"}
    
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
    except Exception as e:
        app.logger.error("Chat AI error: %s", e)
        return jsonify({"error": "generation_failed", "message": str(e)}), 500

    return jsonify({
        "ok":        True,
        "answer":    answer,
        "remaining": remaining,
    })


# ── Alertes transit : toggle utilisateur ──────────────────────────────────────
@app.route("/toggle_alerts", methods=["POST"])
def toggle_alerts():
    from profiles import set_alerts
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data    = request.get_json() or {}
    enabled = bool(data.get("enabled", False))
    pseudo  = profile.get("pseudo", "")

    email = (profile.get("email") or "").strip()
    if enabled and not email:
        return jsonify({"ok": False, "error": "Un email est requis pour activer les alertes."}), 400

    ok = set_alerts(pseudo, enabled)
    if ok:
        profile["alerts_enabled"] = int(enabled)
        session["profile"] = profile
    return jsonify({"ok": ok, "alerts_enabled": int(enabled)})


# ── Calendrier mensuel des transits ───────────────────────────────────────────
@app.route("/calendar")
def calendar_route():
    from calendar_calc import get_monthly_transits
    from datetime import date as _date

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    today = _date.today()
    year  = int(request.args.get("year",  today.year))
    month = int(request.args.get("month", today.month))

    try:
        data = get_monthly_transits(profile, year, month)
        return jsonify({"ok": True, "year": year, "month": month, "days": data})
    except Exception as exc:
        app.logger.error("Erreur calendrier : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Rapport PDF annuel ────────────────────────────────────────────────────────
@app.route("/report/annual")
def annual_report():
    from annual_report import generate_annual_pdf
    from flask import Response

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    lang = session.get("lang", "fr")
    try:
        pdf_bytes = generate_annual_pdf(profile, lang=lang)
        from datetime import date as _date
        filename  = f"karmic_gochara_{profile.get('pseudo', 'rapport')}_{_date.today().year}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        app.logger.error("Erreur rapport PDF : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Cron quotidien : alertes transit ──────────────────────────────────────────
@app.route("/cron/daily", methods=["POST"])
def cron_daily():
    from transit_alerts import run_daily_alerts

    secret = os.environ.get("CRON_SECRET", "")
    if secret:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {secret}":
            return jsonify({"error": "Non autorisé"}), 401

    try:
        results = run_daily_alerts()
        app.logger.info("Cron alertes : %s", results)
        return jsonify({"ok": True, **results})
    except Exception as exc:
        app.logger.error("Erreur cron daily : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500



# ── Test alerte manuelle ───────────────────────────────────────────────────────
@app.route("/alert/test", methods=["POST"])
def alert_test():
    """Envoie un email d'alerte test à l'utilisateur connecté (transits réels ou synthétiques)."""
    from transit_alerts import detect_transit_events, send_alert_email

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    email = (profile.get("email") or "").strip()
    if not email:
        return jsonify({"error": "Aucun email enregistré sur ce compte."}), 400

    enriched = _enrich_profile_with_natal(profile, {})

    try:
        events = detect_transit_events(enriched)
    except Exception as exc:
        app.logger.error("alert/test detect error: %s", exc, exc_info=True)
        events = []

    if not events:
        # Événement synthétique pour valider le canal email
        events = [{
            "type":    "debut",
            "kind":    "nakshatra",
            "transit": "Saturne ♄",
            "natal":   "Ketu",
            "nakshatra": "Mula",
            "lord":    "Ketu",
            "interpretation": "ROM_oppression",
        }]

    sent = send_alert_email(enriched, events)
    if sent:
        return jsonify({"ok": True, "email": email, "events": len(events)})
    return jsonify({"error": "Échec envoi email (vérifier RESEND_API_KEY)."}), 500


# ── Capture email (pré-paiement ou suivi app) ─────────────────────────────────
@app.route("/save_email", methods=["POST"])
def save_email():
    from profiles import save_email_by_pseudo
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Email invalide"}), 400
    try:
        pseudo = profile.get("pseudo", "")
        ok = save_email_by_pseudo(pseudo, email)
        if ok:
            profile["email"] = email
            session["profile"] = profile
            session.modified = True
        return jsonify({"ok": ok})
    except Exception as exc:
        app.logger.error("Erreur save_email : %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 500


# ── Expand : Alternative de Conscience (1 clic gratuit) ──────────────────────
@app.route("/expand", methods=["POST"])
def expand():
    """
    Expansion gratuite unique — topic: alternative_conscience uniquement.
    Limité à 1 appel par session (session['expand_used']).
    """
    from ai_interpret import _build_natal_context

    data   = request.get_json() or {}
    topic  = data.get("topic", "")
    pseudo = data.get("pseudo", "")
    
    user_key = data.get("user_key")
    user_model = data.get("user_model")
    user_provider = data.get("user_provider")

    # Sécurité : 1 seul expand gratuit par session, sauf si clé perso fournie
    if session.get("expand_used") and not user_key:
        return jsonify({"content": ""}), 429

    if topic != "alternative_conscience":
        return jsonify({"content": ""}), 403

    # Récupère le profil depuis la session (ou par pseudo)
    profile = session.get("profile")
    if not profile and pseudo:
        try:
            from profiles import get_profile_by_pseudo
            profile = get_profile_by_pseudo(pseudo)
        except Exception:
            pass

    if not profile:
        return jsonify({"content": "Profil introuvable."}), 404

    session["expand_used"] = True
    session.modified = True

    natal_ctx = _build_natal_context(profile)
    name      = profile.get("name", "")

    system = (
        "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
        "Style : chirurgical, dense, percutant. Tutoiement. "
        "INTERDIT ABSOLU : noms de signes zodiacaux. "
        "Utilise uniquement maisons (H1, H3…) et noms de planètes."
    )
    prompt = (
        f"Thème natal de {name} :\n{natal_ctx}\n\n"
        f"En 100 mots maximum, révèle L'Alternative de Conscience de {name}.\n"
        f"C'est l'insight transformateur central — le pivot entre la prison "
        f"de la Porte Invisible et la libération de la Porte Visible.\n"
        f"Sois chirurgical, personnel, percutant.\n"
        f"Aucun lien. Aucun titre. Texte seul."
    )

    try:
        from ai_interpret import generate_ai
        user_params = {"user_provider": user_provider, "user_key": user_key, "user_model": user_model}
        content = generate_ai(system, prompt, user=user_params, max_tokens=1024)
        return jsonify({"content": content})
    except Exception as exc:
        app.logger.error("Erreur expand : %s", exc)
        return jsonify({"content": ""}), 500


def _fulfill_order(pseudo: str, plan: str, stripe_customer_id: str = ""):
    """Met à jour le plan d'un utilisateur après un paiement réussi."""
    from profiles import upgrade_plan
    try:
        upgrade_plan(pseudo, plan, stripe_customer_id=stripe_customer_id)
        app.logger.info("Plan upgradé : %s → %s (customer: %s)", pseudo, plan, stripe_customer_id)
        # Stocker en mémoire pour la récupération cross-session (navigateur externe).
        _pending_plan_updates[pseudo.strip().lower()] = {"plan": plan, "time": time.time()}
    except Exception as exc:
        app.logger.error("Erreur _fulfill_order pour %s : %s", pseudo, exc)
        raise


# ── Chat : Sauvegarde locale du résumé (utilisateurs Illimité) ─────────────
@app.route("/summarize_chat", methods=["POST"])
def summarize_chat():
    """
    Crée un résumé d'une conversation pour la sauvegarde locale.
    Réservé au plan "illimite".
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
        app.logger.error("Erreur summarize_chat : %s", exc)
        return jsonify({"ok": False, "error": "Erreur lors de la génération du résumé"}), 500


# ── Stripe : création session paiement ────────────────────────────────────────
@app.route("/stripe/checkout", methods=["POST"])
def stripe_checkout():
    """
    Crée une session Stripe Checkout.
    Body JSON : {"product_type": "test"|"subscription"}
    Retourne  : {"url": "https://checkout.stripe.com/..."}
    """
    from stripe_payments import create_checkout_session

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    data         = request.get_json() or {}
    product_type = data.get("product_type", "")
    if product_type not in ("test", "subscription"):
        return jsonify({"error": "product_type invalide"}), 400

    email  = profile.get("email", "")
    pseudo = profile.get("pseudo", "")
    if not email:
        return jsonify({"error": "Email requis pour le paiement"}), 400

    base_url = os.environ.get("DEEP_LINK_BASE_URL") or request.host_url.rstrip("/")
    try:
        url = create_checkout_session(product_type, email, pseudo, base_url)
        return jsonify({"url": url})
    except Exception as exc:
        app.logger.error("Stripe checkout error : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


# ── Stripe : succès paiement (page de transition) ──────────────────────────────
@app.route("/stripe/success")
def stripe_success():
    """
    Affiche une page de transition pendant que le paiement est vérifié
    et que la session utilisateur est mise à jour.
    """
    return render_template("payment_success.html")


# ── API : validation post-paiement ───────────────────────────────────────────
@app.route("/api/complete_payment", methods=["POST"])
def api_complete_payment():
    """
    Vérifie la session de paiement Stripe et met à jour le profil utilisateur.
    Appelé par le script sur la page /stripe/success.
    """
    from stripe_payments import verify_checkout_session
    from profiles import get_profile_by_pseudo

    data = request.get_json() or {}
    session_id = data.get("session_id")
    plan = data.get("plan")
    pseudo = data.get("pseudo")

    if not all([session_id, plan, pseudo]):
        return jsonify({"ok": False, "error": "Paramètres manquants"}), 400

    if not verify_checkout_session(session_id):
        app.logger.warning("Échec de vérification pour session Stripe : %s", session_id)
        return jsonify({"ok": False, "error": "Session de paiement invalide"}), 403

    try:
        _fulfill_order(pseudo, plan)

        # Mettre le plan directement en session sans relire Sheets (évite la latence de propagation).
        if "profile" in session:
            session["profile"]["plan"] = plan

        # Drapeau de secours pour le prochain login (si la session est perdue sur mobile).
        session["payment_completed"] = {"pseudo": pseudo, "plan": plan}
        session.modified = True

        return jsonify({"ok": True, "plan": plan})
    except Exception as exc:
        app.logger.error("Erreur api_complete_payment pour %s : %s", pseudo, exc)
        return jsonify({"ok": False, "error": "Erreur interne"}), 500


@app.route("/api/plan_check", methods=["POST"])
def api_plan_check():
    """
    Vérifie si un paiement est en attente pour ce pseudo (store mémoire).
    Appelé par le WebView au retour d'un navigateur externe après paiement.
    Met à jour la session si un plan en attente est trouvé.
    Body JSON : {"pseudo": "..."}
    """
    data   = request.get_json() or {}
    pseudo = (data.get("pseudo") or "").strip().lower()
    if not pseudo:
        return jsonify({"ok": False}), 400

    pending = _pending_plan_updates.pop(pseudo, None)
    if not pending or time.time() - pending["time"] >= 3600:
        return jsonify({"ok": False, "plan": None})

    plan = pending["plan"]
    # Mettre à jour la session courante si l'utilisateur est connecté
    if "profile" in session:
        session["profile"]["plan"] = plan
        session.modified = True
    app.logger.info("plan_check : plan '%s' appliqué pour %s", plan, pseudo)
    return jsonify({"ok": True, "plan": plan})


@app.route("/api/profile")
def api_profile():
    """Retourne le profil de l'utilisateur connecté."""
    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non authentifié"}), 401
    return jsonify({"ok": True, "profile": profile})


# ── Stripe : webhook (méthode de secours) ─────────────────────────────────────
@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """
    Reçoit les événements Stripe et met à jour le plan utilisateur.
    C'est la méthode de garantie si l'utilisateur ferme son navigateur.
    """
    from stripe_payments import verify_webhook, get_plan_from_price

    payload    = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = verify_webhook(payload, sig_header)
    except Exception as exc:
        app.logger.warning("Webhook Stripe invalide : %s", exc)
        return jsonify({"error": "Signature invalide"}), 400

    if event["type"] == "checkout.session.completed":
        obj_raw  = event["data"]["object"]
        obj      = obj_raw.to_dict() if hasattr(obj_raw, "to_dict") else dict(obj_raw)
        metadata = obj.get("metadata") or {}
        pseudo   = metadata.get("pseudo", "")
        plan     = metadata.get("plan", "")
        customer = obj.get("customer", "") or ""

        if pseudo and plan:
            _fulfill_order(pseudo, plan, stripe_customer_id=customer)

    elif event["type"] == "customer.subscription.deleted":
        from profiles import get_profile_by_email, downgrade_plan
        obj_raw = event["data"]["object"]
        obj     = obj_raw.to_dict() if hasattr(obj_raw, "to_dict") else dict(obj_raw)
        customer_id = obj.get("id", "")
        if customer_id:
            try:
                # La logique pour retrouver un profil par customer_id doit être implémentée
                # dans profiles.py si nécessaire. Pour l'instant, on log.
                app.logger.info("Abonnement annulé pour customer_id: %s", customer_id)
                # downgrade_plan_by_customer_id(customer_id)
            except Exception as exc:
                app.logger.error("Erreur downgrade plan : %s", exc)

    return jsonify({"ok": True})

    profile = session.get("profile")
    if profile and profile.get("pseudo") == pseudo:
        profile["plan"] = plan
        session["profile"] = profile
        session.modified = True

    lang = get_lang()
    plan_labels = {
        "test":         "Lecture débloquée — Synthèse complète + 3 questions ✓",
        "subscription": "Illimité activé ✓",
    }
    message = plan_labels.get(plan, "Paiement confirmé ✓")

    return render_template("index.html",
        user=profile,
        today_iso=datetime.now().strftime("%Y-%m-%d"),
        now_hour=datetime.now().hour,
        now_minute=datetime.now().minute,
        lang=lang,
        ui=lang,
        langs=LANGS,
        session_user=session.get("pseudo", ""),
        session_profile=session.get("profile", {}),
        enable_local_ai=os.environ.get("ENABLE_LOCAL_AI", "").lower() in ("1", "true"),
        enable_features=os.environ.get("ENABLE_FEATURES", "").lower() in ("1", "true"),
        payment_success=message,
    )
# ── Dataset : notation synthèse (👍/👎) ───────────────────────────────────────
@app.route("/rate_synthesis", methods=["POST"])
def rate_synthesis():
    """
    Collecte le feedback utilisateur sur une synthèse.
    Body JSON : {
        "rating": 1 | -1,
        "consent": true | false,
        "synthesis": "texte complet",
        "date": "2026-04-17"
    }
    Stocke dans Google Sheets onglet 'dataset' si consent=true.
    Retourne toujours {"ok": True} (non bloquant).
    """
    import json as _json
    from datetime import datetime as _dt

    profile = session.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "Non connecté"}), 401

    data     = request.get_json() or {}
    rating   = int(data.get("rating", 0))     # 1 = 👍  /  -1 = 👎
    consent  = bool(data.get("consent", False))
    synthesis = (data.get("synthesis") or "").strip()
    date_str  = data.get("date", _dt.now().strftime("%Y-%m-%d"))

    if rating not in (1, -1):
        return jsonify({"ok": False, "error": "Rating invalide"}), 400

    # Positions natales anonymisées (sans nom ni email)
    positions = {
        "chandra_lagna": profile.get("chandra_lagna_sign", ""),
        "ketu":          f"{profile.get('ketu_sign','')} H{profile.get('ketu_house','')}",
        "rahu":          f"{profile.get('rahu_sign','')} H{profile.get('rahu_house','')}",
        "chiron":        f"{profile.get('chiron_sign','')} H{profile.get('chiron_house','')}",
        "lilith":        f"{profile.get('lilith_sign','')} H{profile.get('lilith_house','')}",
        "saturn":        f"{profile.get('saturn_sign','')} H{profile.get('saturn_house','')}",
        "jupiter":       f"{profile.get('jupiter_sign','')} H{profile.get('jupiter_house','')}",
        "porte_visible": f"{profile.get('porte_visible_sign','')} H{profile.get('porte_visible_house','')}",
        "porte_invisible":f"{profile.get('porte_invisible_sign','')} H{profile.get('porte_invisible_house','')}",
    }

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
        creds_dict = _json.loads(creds_json)
        creds      = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc         = gspread.authorize(creds)

        sheet_id   = os.environ.get("GOOGLE_SHEET_ID", "")
        wb         = gc.open_by_key(sheet_id)

        # Crée l'onglet 'dataset' s'il n'existe pas
        try:
            ws = wb.worksheet("dataset")
        except gspread.exceptions.WorksheetNotFound:
            ws = wb.add_worksheet(title="dataset", rows=1000, cols=6)
            ws.append_row(["date", "positions_json", "synthesis", "rating", "consent", "lang"])

        lang = session.get("lang", "fr")

        # N'enregistre la synthèse que si consent=True
        row = [
            date_str,
            _json.dumps(positions, ensure_ascii=False),
            synthesis if consent else "",
            rating,
            1 if consent else 0,
            lang,
        ]
        ws.append_row(row)
        app.logger.info("Dataset row ajoutée : pseudo=%s rating=%s consent=%s",
                        profile.get("pseudo", "?"), rating, consent)

    except Exception as exc:
        # Non bloquant — le feedback UX est déjà affiché
        app.logger.warning("Erreur dataset write : %s", exc)

    return jsonify({"ok": True})

@app.route("/content/daily", methods=["GET"])
def content_daily():
    """
    Route publique : Météo Astrologique globale pour TikTok/Web.
    NE REQUIERT PAS de login. user_id ignoré si fourni.

    Paramètres :
      ?date=yyyy-mm-dd    (optionnel, défaut = aujourd'hui)
      ?lang=fr|en         (optionnel, défaut = fr)
    """
    from datetime import date as date_cls
    from ai_interpret import get_daily_signal

    transit_date  = request.args.get("date", str(date_cls.today()))
    lang_override = request.args.get("lang", "fr")

    signal_data = get_daily_signal(transit_date)

    if "error" in signal_data:
        return jsonify({"error": signal_data["error"]}), 400

    if lang_override == "en":
        signal_data["cta"]["text"]    = "And you, born under a Full Moon in Leo?"
        signal_data["cta"]["subtext"] = "Discover what it means for YOUR natal chart"

    return jsonify(signal_data), 200


@app.route("/generate_task")
def generate_task():
    """Génère et retourne le fichier .task pour l'utilisateur connecté."""
    from astro_calc import calculate_transits
    from build_task_file import build_task_file, extract_natal_for_task, extract_dominant_transit

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "not_authenticated"}), 401

    now = datetime.now()
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
        "city":   profile.get("city", ""),
    }

    try:
        calc_result = calculate_transits(
            natal=natal,
            transit_loc=TRANSIT_LOC_DEFAULT,
            year=now.year, month=now.month, day=now.day,
            hour=now.hour, minute=now.minute,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    user = {
        "name": profile.get("pseudo", profile.get("name", "")),
        "lang": session.get("lang", profile.get("lang", "fr")),
    }

    natal_data   = extract_natal_for_task(calc_result)
    transit_data = extract_dominant_transit(calc_result)
    task         = build_task_file(user, natal_data, transit_data)

    import json as _json
    resp = make_response(_json.dumps(task, ensure_ascii=False, indent=2))
    resp.headers["Content-Type"] = "application/json"
    resp.headers["Content-Disposition"] = f'attachment; filename="karmic_{user["name"]}.task"'
    return resp


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)