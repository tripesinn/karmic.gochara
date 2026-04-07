"""
app.py — Gochara Karmique
Application Flask — Architecture multi-utilisateurs
"""

import os
from datetime import datetime

import pytz
from flask import Flask, jsonify, render_template, request, session, send_from_directory
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
    enriched["natal_positions"]     = natal

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
    session["profile"] = profile
    session["pseudo"] = pseudo
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
    session["pseudo"] = pseudo
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
    from profiles import check_and_increment_synthesis  # ← AJOUT

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    # ── Vérification quota mensuel ────────────────────────────────────────────
    pseudo = profile.get("pseudo", "")
    UNLIMITED_PSEUDOS = {"jero"}
    if pseudo.lower() in UNLIMITED_PSEUDOS:
        quota = {"allowed": True, "remaining": 999}
    else:
        quota = check_and_increment_synthesis(pseudo)
    if not quota["allowed"]:
        return jsonify({
            "error": "quota_exceeded",
            "message": "Tu as atteint ta limite de 3 synthèses ce mois-ci.",
            "upgrade_url": "https://siderealastro13.com/upgrade"  # adapte l'URL
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

        result["synthesis"] = synthesis
        result["remaining"] = quota["remaining"]
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
    Utilisé par le plugin Gemma 3 / AI Core sur Android pour l'inférence locale.
    Désactivé sur prod (ENABLE_LOCAL_AI non défini).
    """
    if not os.environ.get('ENABLE_LOCAL_AI', '').lower() in ('1', 'true'):
        return jsonify({"error": "Non disponible"}), 404
    from astro_calc import calculate_transits
    from ai_interpret import build_prompt_only

    profile = session.get("profile")
    if not profile:
        return jsonify({"error": "Non connecté"}), 401

    natal = {
        "name":   profile["name"],
        "year":   profile["year"],  "month":  profile["month"],
        "day":    profile["day"],   "hour":   profile["hour"],
        "minute": profile["minute"],"lat":    profile["lat"],
        "lon":    profile["lon"],   "tz":     profile["tz"],
        "city":   profile["city"],
    }

    data      = request.get_json() or {}
    date_str  = data.get("date", "")
    hour      = int(data.get("hour", 12))
    minute    = int(data.get("minute", 0))
    transit_loc = {
        "city": data.get("transit_city") or profile.get("transit_city", TRANSIT_LOC_DEFAULT["city"]),
        "lat":  float(data.get("transit_lat") or profile.get("transit_lat", TRANSIT_LOC_DEFAULT["lat"])),
        "lon":  float(data.get("transit_lon") or profile.get("transit_lon", TRANSIT_LOC_DEFAULT["lon"])),
        "tz":   data.get("transit_tz")  or profile.get("transit_tz",  TRANSIT_LOC_DEFAULT["tz"]),
    }
    lang = session.get("lang", "fr")

    try:
        year, month, day = map(int, date_str.split("-"))
        chart_data = calculate_transits(natal, transit_loc, year, month, day, hour, minute)
        prompts    = build_prompt_only(chart_data, profile, lang=lang)
        return jsonify({
            "ok":          True,
            "system":      prompts["system"],
            "user":        prompts["user"],
            "aspects":     chart_data.get("aspects", []),
            "transit_date": chart_data.get("transit_date", ""),
        })
    except Exception as exc:
        app.logger.error("Erreur synthesis/prompt : %s", exc, exc_info=True)
        return jsonify({"error": str(exc)}), 500


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


# ── Lancement ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
