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

# ── Définition complète et ordonnée de toutes les colonnes ───────────────────
# Bloc 1 — Profil de base (A–V, indices 0–21)
COLS = [
    "pseudo",               # A  0
    "email",                # B  1
    "name",                 # C  2
    "year",                 # D  3
    "month",                # E  4
    "day",                  # F  5
    "hour",                 # G  6
    "minute",               # H  7
    "lat",                  # I  8
    "lon",                  # J  9
    "tz",                   # K  10
    "city",                 # L  11
    "transit_city",         # M  12
    "transit_lat",          # N  13
    "transit_lon",          # O  14
    "transit_tz",           # P  15
    "transit_date",         # Q  16
    "syntheses_count",      # R  17
    "syntheses_reset_date", # S  18
    "alerts_enabled",       # T  19
    "plan",                 # U  20
    "plan_syntheses",       # V  21
    "stripe_customer_id",   # W  22
]

# Bloc 2 — Données natales calculées (X–AT, indices 23–45)
NATAL_COLS = [
    "chandra_lagna_sign",    # X  23
    "ketu_sign",             # Y  24
    "ketu_house",            # Z  25
    "ketu_nakshatra",        # AA 26
    "rahu_sign",             # AB 27
    "rahu_house",            # AC 28
    "rahu_nakshatra",        # AD 29
    "chiron_sign",           # AE 30
    "chiron_house",          # AF 31
    "chiron_nakshatra",      # AG 32
    "lilith_sign",           # AH 33
    "lilith_house",          # AI 34
    "saturn_sign",           # AJ 35
    "saturn_house",          # AK 36
    "jupiter_sign",          # AL 37
    "jupiter_house",         # AM 38
    "porte_visible_sign",    # AN 39
    "porte_visible_house",   # AO 40
    "porte_visible_deg",     # AP 41
    "porte_invisible_sign",  # AQ 42
    "porte_invisible_house", # AR 43
    "moon_longitude_sid",    # AS 44
    "chandra_lagna_degree",  # AT 45
]

# Bloc 3 — Quotas chatbot et alertes (AU–AW, indices 46–48)
QUOTA_COLS = [
    "chat_remaining",        # AU 46
    "chat_reset_month",      # AV 47
    "alert_sent",            # AW 48
]

# Liste maître — toutes les colonnes dans l'ordre
ALL_COLS = COLS + NATAL_COLS + QUOTA_COLS

# Index nommés pour éviter les nombres magiques
C = {name: i for i, name in enumerate(ALL_COLS)}

SYNTHESIS_QUOTA = 3  # max synthèses par mois (plan free)

_sheet = None


def _col(idx: int) -> str:
    """Convertit un index 0-based en lettre(s) de colonne Sheets (A, B, …, AA, …)."""
    idx += 1
    result = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


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
            except Exception:
                ws = spreadsheet.add_worksheet(title="gochara-profiles", rows=1000, cols=len(ALL_COLS) + 5)

    # Créer l'en-tête si la feuille est vide
    if ws and not ws.row_values(1):
        ws.append_row(ALL_COLS)

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
        data.get("transit_date", ""),  # transit_date
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
            def _pick(key, idx, default=""):
                return data.get(key) if key in data and data.get(key) is not None else (row[idx] if len(row) > idx else default)

            # Préserve les colonnes quota existantes
            sc  = C["syntheses_count"]
            srd = C["syntheses_reset_date"]
            ae  = C["alerts_enabled"]
            existing_count      = row[sc]  if len(row) > sc  else "0"
            existing_reset_date = row[srd] if len(row) > srd else _current_month_str()
            existing_alerts     = row[ae]  if len(row) > ae  else "0"

            new_row = [
                _pick("pseudo",       0),
                row[1],  # email immuable
                _pick("name",         2),
                str(_pick("year",     3)),
                str(_pick("month",    4)),
                str(_pick("day",      5)),
                str(_pick("hour",     6)),
                str(_pick("minute",   7)),
                str(_pick("lat",      8)),
                str(_pick("lon",      9)),
                _pick("tz",           10, "Europe/Paris"),
                _pick("city",         11),
                _pick("transit_city", 12),
                str(_pick("transit_lat", 13)),
                str(_pick("transit_lon", 14)),
                _pick("transit_tz",   15, "Europe/Paris"),
                _pick("transit_date", 16),
                existing_count,
                existing_reset_date,
                existing_alerts,
            ]
            # Inclure les données natales existantes pour le retour
            if len(row) > len(new_row):
                new_row.extend(row[len(new_row):])

            end_col = _col(C["alerts_enabled"])
            ws.update(f"A{i}:{end_col}{i}", [new_row[:C["alerts_enabled"] + 1]])
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
        c1 = _col(C[NATAL_COLS[0]])
        c2 = _col(C[NATAL_COLS[-1]])
        ws.update(f"{c1}{i}:{c2}{i}", [natal_row])
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

        sc = C["syntheses_count"]; srd = C["syntheses_reset_date"]
        try:
            count = int(row[sc]) if len(row) > sc and row[sc] else 0
        except ValueError:
            count = 0

        reset_date = row[srd] if len(row) > srd and row[srd] else ""

        if reset_date != current_month:
            count = 0
            reset_date = current_month

        if count >= SYNTHESIS_QUOTA:
            return {"allowed": False, "remaining": 0}

        new_count = count + 1
        ws.update(f"{_col(sc)}{i}:{_col(srd)}{i}", [[str(new_count), current_month]])

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
        ws.update(f"{_col(C['alerts_enabled'])}{i}", [[str(int(enabled))]])
        return True
    return False


# ── Gestion plans Stripe ───────────────────────────────────────────────────────

PLAN_SYNTHESES = {
    "lecture":  1,    # one-shot → 1 synthèse + 3 questions chatbot
    "essential": 1,   # legacy name for lecture
    "illimite": -1,   # illimité
    "illimité": -1,   # legacy/manual name with accent
    "free":     0,
}

PLAN_CHAT_LIMITS = {
    "lecture":  3,    # 3 questions chatbot one-shot
    "essential": 3,
    "illimite": 10,   # 10/mois via serveur (Gemini) — illimité si IA local
    "illimité": 10,
    "free":     0,
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
        ws.update(f"{_col(C['plan'])}{i}:{_col(C['plan_syntheses'])}{i}", [[plan, str(syntheses)]])
        if stripe_customer_id:
            ws.update(f"{_col(C['stripe_customer_id'])}{i}", [[stripe_customer_id]])
        current_month = _current_month_str()[:7]
        cr = _col(C["chat_remaining"])
        cm = _col(C["chat_reset_month"])
        ws.update(f"{cr}{i}:{cm}{i}", [[str(chat_limit), current_month]])
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
        ws.update(f"{_col(C['plan'])}{i}:{_col(C['plan_syntheses'])}{i}", [["free", "0"]])
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
        plan = row[C["plan"]] if len(row) > C["plan"] else "free"
        plan_normalized = plan.lower().replace("é", "e")
        try:
            remaining = int(row[C["chat_remaining"]]) if len(row) > C["chat_remaining"] and row[C["chat_remaining"]] else 0
        except ValueError:
            remaining = 0
        if plan_normalized in ("illimite", "subscription"):
            reset_month = row[C["chat_reset_month"]] if len(row) > C["chat_reset_month"] else ""
            if reset_month != current_month:
                remaining = PLAN_CHAT_LIMITS.get(plan, 10)
        return {
            "plan": plan, "remaining": remaining,
            "limit": PLAN_CHAT_LIMITS.get(plan, 0),
            "local_unlimited": plan_normalized in ("illimite", "subscription"),
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
        plan = row[C["plan"]] if len(row) > C["plan"] else "free"
        plan_normalized = plan.lower().replace("é", "e")
        cr_col = _col(C["chat_remaining"])
        cm_col = _col(C["chat_reset_month"])

        if plan_normalized in ("illimite", "subscription"):
            if local:
                return {"ok": True, "remaining": -1, "local": True}
            try:
                remaining = int(row[C["chat_remaining"]]) if len(row) > C["chat_remaining"] and row[C["chat_remaining"]] else 0
            except ValueError:
                remaining = 0
            reset_month = row[C["chat_reset_month"]] if len(row) > C["chat_reset_month"] else ""
            if reset_month != current_month:
                remaining = PLAN_CHAT_LIMITS.get(plan, 10)
                ws.update(f"{cm_col}{i}", [[current_month]])
            if remaining <= 0:
                return {"ok": False, "remaining": 0, "local": False}
            ws.update(f"{cr_col}{i}", [[str(remaining - 1)]])
            return {"ok": True, "remaining": remaining - 1, "local": False}

        if plan_normalized not in ("test", "lecture", "essential"):
            return {"ok": False, "remaining": 0, "local": False}
        try:
            remaining = int(row[C["chat_remaining"]]) if len(row) > C["chat_remaining"] and row[C["chat_remaining"]] else 0
        except ValueError:
            remaining = 0
        if remaining <= 0:
            return {"ok": False, "remaining": 0, "local": False}
        ws.update(f"{cr_col}{i}", [[str(remaining - 1)]])
        return {"ok": True, "remaining": remaining - 1, "local": False}
    return {"ok": False, "remaining": 0, "local": False}


def get_and_consume_alert(pseudo: str, plan: str) -> dict:
    """
    Gère le quota d'alertes selon le plan.
    - free        → refusé
    - test/lecture→ 1 alerte one-shot (col AV, index 47)
    - illimite    → illimité

    Retourne {"ok": bool, "is_last": bool}
    is_last=True si c'est la dernière alerte disponible (test plan).
    """
    plan_normalized = plan.lower().replace("é", "e")
    if plan_normalized == "free":
        return {"ok": False, "is_last": False}
    if plan_normalized in ("illimite", "subscription"):
        return {"ok": True, "is_last": False}

    # plan == "test" ou "lecture" → 1 alerte max
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()
    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        try:
            sent = int(row[C["alert_sent"]]) if len(row) > C["alert_sent"] and row[C["alert_sent"]] else 0
        except ValueError:
            sent = 0
        if sent >= 1:
            return {"ok": False, "is_last": False}
        ws.update(f"{_col(C['alert_sent'])}{i}", [["1"]])
        return {"ok": True, "is_last": True}
    return {"ok": False, "is_last": False}


def consume_plan_synthesis(pseudo: str) -> bool:
    """
    Décrémente le compteur plan_syntheses d'un utilisateur si applicable.
    Retourne True si autorisé (illimité ou compteur > 0), False sinon.
    """
    ws = _get_sheet()
    records = ws.get_all_values()
    pseudo_lower = pseudo.strip().lower()

    for i, row in enumerate(records[1:], start=2):
        if not row or row[0].strip().lower() != pseudo_lower:
            continue
        
        plan = row[19] if len(row) > 19 else "free"
        plan_normalized = plan.lower().replace("é", "e")
        if plan_normalized in ("illimite", "subscription"):
            return True  # Illimité pour les abonnés

        try:
            count = int(row[20]) if len(row) > 20 and row[20] else 0
        except ValueError:
            count = 0
            
        if count <= 0:
            return False
            
        ws.update(f"{_col(C['plan_syntheses'])}{i}", [[str(count - 1)]])
        return True
    return False