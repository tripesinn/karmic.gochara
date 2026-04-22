"""
profiles.py — Gestion des profils utilisateurs via Google Sheets
Gochara Karmique — Architecture multi-utilisateurs
"""

import os
import json
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Colonnes du Google Sheet (ordre fixe)
COLS = [
    "pseudo",               # A
    "email",                # B
    "name",                 # C
    "year",                 # D
    "month",                # E
    "day",                  # F
    "hour",                 # G
    "minute",               # H
    "lat",                  # I
    "lon",                  # J
    "tz",                   # K
    "city",                 # L
    "transit_city",         # M
    "transit_lat",          # N
    "transit_lon",          # O
    "transit_tz",           # P
    "syntheses_count",      # Q
    "syntheses_reset_date", # R
    "alerts_enabled",       # S
    "plan",                 # T : "free" | "sub" | "essential" | "complete"
    "plan_syntheses",       # U : nombre de synthèses restantes sur plan payant
    "stripe_customer_id",   # V
]

# Colonnes natales — à partir de W (index 22)
NATAL_COLS = [
    "chandra_lagna_sign",    # W  (22)
    "ketu_sign",             # X  (23)
    "ketu_house",            # Y  (24)
    "ketu_nakshatra",        # Z  (25)
    "rahu_sign",             # AA (26)
    "rahu_house",            # AB (27)
    "rahu_nakshatra",        # AC (28)
    "chiron_sign",           # AD (29)
    "chiron_house",          # AE (30)
    "chiron_nakshatra",      # AF (31)
    "lilith_sign",           # AG (32)
    "lilith_house",          # AH (33)
    "saturn_sign",           # AI (34)
    "saturn_house",          # AJ (35)
    "jupiter_sign",          # AK (36)
    "jupiter_house",         # AL (37)
    "porte_visible_sign",    # AM (38)
    "porte_visible_house",   # AN (39)
    "porte_visible_deg",     # AO (40)
    "porte_invisible_sign",  # AP (41)
    "porte_invisible_house", # AQ (42)
    "moon_longitude_sid",    # AR (43)
    "chandra_lagna_degree",  # AS (44)
]

SYNTHESIS_QUOTA = 3  # max synthèses par mois (plan free)

_sheet = None


def _current_month_str() -> str:
    """Retourne le 1er du mois courant au format YYYY-MM-01."""
    today = date.today()
    return f"{today.year}-{today.month:02d}-01"


def _get_sheet():
    global _sheet
    if _sheet is not None:
        return _sheet

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    sheet_id   = os.environ.get("SHEET_ID")

    if not creds_json or not sheet_id:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON ou SHEET_ID manquant dans les variables d'environnement.")

    creds_data = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
    gc = gspread.authorize(creds)
    spreadsheet = gc.open_by_key(sheet_id)

    ws = None
    try:
        ws = spreadsheet.worksheet("gochara-profiles")
    except gspread.WorksheetNotFound:
        try:
            ws = spreadsheet.worksheet("profiles")
        except gspread.WorksheetNotFound:
            try:
                ws = spreadsheet.sheet1
            except Exception: # Can be WorksheetNotFound if no sheets
                ws = spreadsheet.add_worksheet(title="gochara-profiles", rows=1000, cols=len(COLS))

    # Créer l'en-tête si la feuille est vide
    if ws and not ws.row_values(1):
        ws.append_row(COLS)

    _sheet = ws
    return _sheet


def _row_to_profile(row: list) -> dict:
    """Convertit une ligne Sheets en dict profil."""
    def _safe(i, cast=str, default=""):
        try:
            v = row[i].strip() if isinstance(row[i], str) else str(row[i])
            return cast(v) if v else default
        except (IndexError, ValueError):
            return default

    return {
        "pseudo":               _safe(0),
        "email":                _safe(1),
        "name":                 _safe(2),
        "year":                 _safe(3, int, 1990),
        "month":                _safe(4, int, 1),
        "day":                  _safe(5, int, 1),
        "hour":                 _safe(6, int, 12),
        "minute":               _safe(7, int, 0),
        "lat":                  _safe(8, float, 48.8566),
        "lon":                  _safe(9, float, 2.3522),
        "tz":                   _safe(10) or "Europe/Paris",
        "city":                 _safe(11) or "Paris, France",
        "transit_city":         _safe(12) or "Paris, France",
        "transit_lat":          _safe(13, float, 48.8566),
        "transit_lon":          _safe(14, float, 2.3522),
        "transit_tz":           _safe(15) or "Europe/Paris",
        # Quota — fallback 0 / mois courant pour anciens profils
        "syntheses_count":      _safe(16, int, 0),
        "syntheses_reset_date": _safe(17) or _current_month_str(),
        "alerts_enabled":       _safe(18, int, 0),
        "plan":                 _safe(19) or "free",
        "plan_syntheses":       _safe(20, int, 0),
        "stripe_customer_id":   _safe(21) or "",
        # Données natales (colonnes W→AQ, indices 22→42)
        "chandra_lagna_sign":    _safe(22),
        "ketu_sign":             _safe(23),
        "ketu_house":            _safe(24),
        "ketu_nakshatra":        _safe(25),
        "rahu_sign":             _safe(26),
        "rahu_house":            _safe(27),
        "rahu_nakshatra":        _safe(28),
        "chiron_sign":           _safe(29),
        "chiron_house":          _safe(30),
        "chiron_nakshatra":      _safe(31),
        "lilith_sign":           _safe(32),
        "lilith_house":          _safe(33),
        "saturn_sign":           _safe(34),
        "saturn_house":          _safe(35),
        "jupiter_sign":          _safe(36),
        "jupiter_house":         _safe(37),
        "porte_visible_sign":    _safe(38),
        "porte_visible_house":   _safe(39),
        "porte_visible_deg":     _safe(40),
        "porte_invisible_sign":  _safe(41),
        "porte_invisible_house": _safe(42),
        "moon_longitude_sid":    _safe(43),
        "chandra_lagna_degree":  _safe(44),
    }


def get_all_profiles() -> list[dict]:
    """Retourne tous les profils de la feuille."""
    ws = _get_sheet()
    rows = ws.get_all_values()
    return [_row_to_profile(row) for row in rows[1:] if row and row[0]]


def get_profile_by_email(email: str) -> dict | None:
    ws = _get_sheet()
    records = ws.get_all_values()
    email_lower = email.strip().lower()
    for row in records[1:]:
        if len(row) > 1 and row[1].strip().lower() == email_lower:
            return _row_to_profile(row)
    return None


def _clean_pseudo(s: str) -> str:
    """Supprime espaces insécables, caractères invisibles, BOM — pour comparaison robuste."""
    import unicodedata
    s = "".join(c for c in s if not unicodedata.category(c).startswith("C"))
    return s.strip().replace("\u00a0", "").replace("\u200b", "").replace("\ufeff", "").lower()


def get_profile_by_pseudo(pseudo: str) -> dict | None:
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_clean = _clean_pseudo(pseudo)

    for row in records[1:]:
        if row and _clean_pseudo(row[0]) == pseudo_clean:
            return _row_to_profile(row)
    return None


def save_email_by_pseudo(pseudo: str, email: str) -> bool:
    """Met à jour uniquement la colonne email (B) pour un pseudo donné."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_clean = _clean_pseudo(pseudo)
    for i, row in enumerate(records[1:], start=2):
        if row and _clean_pseudo(row[0]) == pseudo_clean:
            ws.update(f"B{i}", [[email.strip().lower()]])
            return True
    return False


def create_profile(data: dict) -> dict:
    """Crée un nouveau profil et retourne le profil créé."""
    ws = _get_sheet()
    row = [
        data.get("pseudo", ""),
        data.get("email", ""),
        data.get("name", ""),
        str(data.get("year", "")),
        str(data.get("month", "")),
        str(data.get("day", "")),
        str(data.get("hour", "")),
        str(data.get("minute", "")),
        str(data.get("lat", "")),
        str(data.get("lon", "")),
        data.get("tz", "Europe/Paris"),
        data.get("city", ""),
        data.get("transit_city", ""),
        str(data.get("transit_lat", "")),
        str(data.get("transit_lon", "")),
        data.get("transit_tz", "Europe/Paris"),
        "0",                      # syntheses_count
        _current_month_str(),     # syntheses_reset_date
        "0",                      # alerts_enabled
        "free",                   # plan
        "0",                      # plan_syntheses
        "",                       # stripe_customer_id
    ]
    ws.append_row(row)
    return _row_to_profile(row)


def update_profile(email: str, data: dict) -> dict | None:
    """Met à jour le profil d'un utilisateur existant."""
    ws = _get_sheet()
    records = ws.get_all_values()
    email_lower = email.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if len(row) > 1 and row[1].strip().lower() == email_lower:
            # Préserve les colonnes quota existantes
            existing_count      = row[16] if len(row) > 16 else "0"
            existing_reset_date = row[17] if len(row) > 17 else _current_month_str()
            existing_alerts     = row[18] if len(row) > 18 else "0"

            new_row = [
                data.get("pseudo") if "pseudo" in data and data.get("pseudo") is not None else (row[0] if len(row) > 0 else ""),
                row[1],  # email immuable
                data.get("name") if "name" in data and data.get("name") is not None else (row[2] if len(row) > 2 else ""),
                str(data.get("year") if "year" in data and data.get("year") is not None else (row[3] if len(row) > 3 else "")),
                str(data.get("month") if "month" in data and data.get("month") is not None else (row[4] if len(row) > 4 else "")),
                str(data.get("day") if "day" in data and data.get("day") is not None else (row[5] if len(row) > 5 else "")),
                str(data.get("hour") if "hour" in data and data.get("hour") is not None else (row[6] if len(row) > 6 else "")),
                str(data.get("minute") if "minute" in data and data.get("minute") is not None else (row[7] if len(row) > 7 else "")),
                str(data.get("lat") if "lat" in data and data.get("lat") is not None else (row[8] if len(row) > 8 else "")),
                str(data.get("lon") if "lon" in data and data.get("lon") is not None else (row[9] if len(row) > 9 else "")),
                data.get("tz") if "tz" in data and data.get("tz") is not None else (row[10] if len(row) > 10 else "Europe/Paris"),
                data.get("city") if "city" in data and data.get("city") is not None else (row[11] if len(row) > 11 else ""),
                data.get("transit_city") if "transit_city" in data and data.get("transit_city") is not None else (row[12] if len(row) > 12 else ""),
                str(data.get("transit_lat") if "transit_lat" in data and data.get("transit_lat") is not None else (row[13] if len(row) > 13 else "")),
                str(data.get("transit_lon") if "transit_lon" in data and data.get("transit_lon") is not None else (row[14] if len(row) > 14 else "")),
                data.get("transit_tz") if "transit_tz" in data and data.get("transit_tz") is not None else (row[15] if len(row) > 15 else "Europe/Paris"),
                existing_count,
                existing_reset_date,
                existing_alerts,
            ]
            # Reconstruire la ligne complète pour le retour afin d'inclure les données natales calculées
            if len(row) > 19:
                new_row.extend(row[19:])

            ws.update(f"A{i}:S{i}", [new_row[:19]])
            return _row_to_profile(new_row)
    return None


def save_natal_to_sheet(pseudo: str, profile: dict) -> bool:
    """
    Sauvegarde les données natales calculées dans les colonnes W→AS.
    Appelée après calcul natal à l'inscription ou au premier login.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        natal_row = [str(profile.get(col, "")) for col in NATAL_COLS]
        ws.update(f"W{i}:AS{i}", [natal_row])
        return True
    return False


def check_and_increment_synthesis(pseudo: str) -> dict:
    """
    Vérifie le quota mensuel de synthèses pour un utilisateur.
    - Si quota dépassé  → retourne {"allowed": False, "remaining": 0}
    - Sinon             → incrémente le compteur et retourne {"allowed": True, "remaining": N}
    Gère le reset automatique en début de mois.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    current_month = _current_month_str()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue

        try:
            count = int(row[16]) if len(row) > 16 and row[16] else 0
        except ValueError:
            count = 0

        reset_date = row[17] if len(row) > 17 and row[17] else ""

        if reset_date != current_month:
            count = 0
            reset_date = current_month

        if count >= SYNTHESIS_QUOTA:
            return {"allowed": False, "remaining": 0}

        new_count = count + 1
        ws.update(f"Q{i}:R{i}", [[str(new_count), current_month]])

        return {"allowed": True, "remaining": SYNTHESIS_QUOTA - new_count}

    return {"allowed": False, "remaining": 0}


def delete_profile(pseudo: str) -> bool:
    """Supprime définitivement le profil. Retourne True si supprimé."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for i, row in enumerate(records[1:], start=2):
        if row and row[0].strip().lower() == pseudo_lower:
            ws.delete_rows(i)
            return True
    return False


def pseudo_exists(pseudo: str) -> bool:
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for row in records[1:]:
        if row and row[0].strip().lower() == pseudo_lower:
            return True
    return False


def set_alerts(pseudo: str, enabled: bool) -> bool:
    """Active ou désactive les alertes transit pour un utilisateur."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        ws.update(f"S{i}", [[str(int(enabled))]])
        return True
    return False


# ── Gestion plans Stripe ───────────────────────────────────────────────────────

PLAN_SYNTHESES = {
    "test":         1,    # one-shot → 1 synthèse + 3 questions chatbot
    "subscription": 10,   # 10/mois via serveur (Haiku) — illimité si Gemma local (managé côté Edge AI)
    "free":         0,
}

PLAN_CHAT_LIMITS = {
    "test":         3,    # 3 questions chatbot one-shot
    "subscription": 10,   # 10/mois via serveur (Haiku) — illimité si Gemma local
    "free":         0,
}


def upgrade_plan(pseudo: str, plan: str, stripe_customer_id: str = "") -> bool:
    """
    Met à jour le plan d'un utilisateur après paiement Stripe confirmé.
    Crédite le nombre de synthèses correspondant au plan.
    Sauvegarde le stripe_customer_id si fourni.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    syntheses = PLAN_SYNTHESES.get(plan, 0)

    chat_limit = PLAN_CHAT_LIMITS.get(plan, 0)

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        ws.update(f"T{i}:U{i}", [[plan, str(syntheses)]])
        if stripe_customer_id:
            ws.update(f"V{i}", [[stripe_customer_id]])
        current_month = _current_month_str()[:7]
        ws.update(f"AT{i}:AU{i}", [[str(chat_limit), current_month]])
        return True
    return False


def downgrade_plan(pseudo: str) -> bool:
    """Remet le plan à "free" après annulation abonnement Stripe."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        ws.update(f"T{i}:U{i}", [["free", "0"]])
        return True
    return False


def get_chat_quota(pseudo: str) -> dict:
    """Retourne {plan, remaining, limit, local_unlimited}."""
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    current_month = _current_month_str()[:7]
    for row in records[1:]:
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        plan = row[19] if len(row) > 19 else "free"
        try:
            remaining = int(row[45]) if len(row) > 45 and row[45] else 0
        except ValueError:
            remaining = 0
        if plan == "subscription":
            reset_month = row[46] if len(row) > 46 else ""
            if reset_month != current_month:
                remaining = PLAN_CHAT_LIMITS["subscription"]
        return {
            "plan": plan, "remaining": remaining,
            "limit": PLAN_CHAT_LIMITS.get(plan, 0),
            "local_unlimited": plan == "subscription",
        }
    return {"plan": "free", "remaining": 0, "limit": 0, "local_unlimited": False}


def consume_chat_question(pseudo: str, local: bool = False) -> dict:
    """
    Consomme 1 question chatbot.
    subscription + local=True  → illimité, pas de décrément
    subscription + local=False → 10/mois Haiku, reset mensuel col AU
    test                       → 3 one-shot col AT
    free                       → refusé
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    current_month = _current_month_str()[:7]

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        plan = row[19] if len(row) > 19 else "free"

        if plan == "subscription":
            if local:
                return {"ok": True, "remaining": -1, "local": True}
            try:
                remaining = int(row[45]) if len(row) > 45 and row[45] else 0
            except ValueError:
                remaining = 0
            reset_month = row[46] if len(row) > 46 else ""
            if reset_month != current_month:
                remaining = PLAN_CHAT_LIMITS["subscription"]
                ws.update(f"AU{i}", [[current_month]])
            if remaining <= 0:
                return {"ok": False, "remaining": 0, "local": False}
            ws.update(f"AT{i}", [[str(remaining - 1)]])
            return {"ok": True, "remaining": remaining - 1, "local": False}

        if plan != "test":
            return {"ok": False, "remaining": 0, "local": False}
        try:
            remaining = int(row[45]) if len(row) > 45 and row[45] else 0
        except ValueError:
            remaining = 0
        if remaining <= 0:
            return {"ok": False, "remaining": 0, "local": False}
        ws.update(f"AT{i}", [[str(remaining - 1)]])
        return {"ok": True, "remaining": remaining - 1, "local": False}
    return {"ok": False, "remaining": 0, "local": False}


def get_and_consume_alert(pseudo: str, plan: str) -> dict:
    """
    Gère le quota d'alertes selon le plan.
    - free        → refusé
    - test        → 1 alerte one-shot (col AV, index 47)
    - subscription → illimité

    Retourne {"ok": bool, "is_last": bool}
    is_last=True si c'est la dernière alerte disponible (test plan).
    """
    if plan == "free":
        return {"ok": False, "is_last": False}
    if plan == "subscription":
        return {"ok": True, "is_last": False}

    # plan == "test" → 1 alerte max
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        try:
            sent = int(row[47]) if len(row) > 47 and row[47] else 0
        except ValueError:
            sent = 0
        if sent >= 1:
            return {"ok": False, "is_last": False}
        ws.update(f"AV{i}", [["1"]])
        return {"ok": True, "is_last": True}
    return {"ok": False, "is_last": False}


def consume_plan_synthesis(pseudo: str) -> bool:
    """
    Décrémente le compteur plan_syntheses d'un utilisateur.
    Retourne True si autorisé (compteur > 0), False sinon.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        try:
            count = int(row[20]) if len(row) > 20 and row[20] else 0
        except ValueError:
            count = 0
        if count <= 0:
            return False
        ws.update(f"U{i}", [[str(count - 1)]])
        return True
    return False