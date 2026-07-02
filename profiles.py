"""
profiles.py — Gestion des profils utilisateurs via Cloud Firestore
Gochara Karmique — Architecture multi-utilisateurs
"""

import json
import os
from datetime import date
from google.cloud import firestore

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

# Bloc 3 — Quotas chatbot et alertes (AU–AX, indices 46–49)
QUOTA_COLS = [
    "chat_remaining",        # AU 46
    "chat_reset_month",      # AV 47
    "alert_sent",            # AW 48
    "last_signal_date",      # AX 49
]

# Liste maître — toutes les colonnes dans l'ordre
ALL_COLS = COLS + NATAL_COLS + QUOTA_COLS

# Index nommés pour éviter les nombres magiques
C = {name: i for i, name in enumerate(ALL_COLS)}

SYNTHESIS_QUOTA = 3  # max synthèses par mois (plan free)

_db = None

def _get_db():
    global _db
    if _db is not None:
        return _db
    project_id = os.environ.get("PROJECT_ID", "karmic-gochara-cloud")
    
    # 🧪 Configuration spéciale pour l'émulateur local pour éviter les timeouts de credentials GCP
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        from google.auth.credentials import AnonymousCredentials
        _db = firestore.Client(project=project_id, credentials=AnonymousCredentials())
    else:
        _db = firestore.Client(project=project_id)
    return _db

def _current_month_str() -> str:
    """Retourne le 1er du mois courant au format YYYY-MM-01."""
    today = date.today()
    return f"{today.year}-{today.month:02d}-01"

def _clean_pseudo(s: str) -> str:
    """Supprime espaces insécables, caractères invisibles, BOM — pour comparaison robuste."""
    import unicodedata
    s = "".join(c for c in s if not unicodedata.category(c).startswith("C"))
    return s.strip().replace("\u00a0", "").replace("\u200b", "").replace("\ufeff", "").lower()

def _doc_to_profile(doc) -> dict | None:
    """Convertit un document snapshot Firestore en dictionnaire profil."""
    if not doc.exists:
        return None
    data = doc.to_dict()
    
    def _safe(key, cast=str, default=""):
        try:
            val = data.get(key)
            if val is None or val == "":
                return default
            return cast(val)
        except (ValueError, TypeError):
            return default

    return {
        "pseudo":                _safe("pseudo"),
        "email":                 _safe("email"),
        "name":                  _safe("name"),
        "year":                  _safe("year", int, 1990),
        "month":                 _safe("month", int, 1),
        "day":                   _safe("day", int, 1),
        "hour":                  _safe("hour", int, 12),
        "minute":                _safe("minute", int, 0),
        "lat":                   _safe("lat", float, 48.8566),
        "lon":                   _safe("lon", float, 2.3522),
        "tz":                    _safe("tz") or "Europe/Paris",
        "city":                  _safe("city") or "Paris, France",
        "transit_city":          _safe("transit_city") or "Paris, France",
        "transit_lat":           _safe("transit_lat", float, 48.8566),
        "transit_lon":           _safe("transit_lon", float, 2.3522),
        "transit_tz":            _safe("transit_tz") or "Europe/Paris",
        "transit_date":          _safe("transit_date") or "",
        "syntheses_count":       _safe("syntheses_count", int, 0),
        "syntheses_reset_date":  _safe("syntheses_reset_date") or _current_month_str(),
        "alerts_enabled":        _safe("alerts_enabled", int, 0),
        "plan":                  _safe("plan") or "free",
        "plan_syntheses":        _safe("plan_syntheses", int, 0),
        "stripe_customer_id":    _safe("stripe_customer_id") or "",
        "chandra_lagna_sign":    _safe("chandra_lagna_sign"),
        "ketu_sign":             _safe("ketu_sign"),
        "ketu_house":            _safe("ketu_house"),
        "ketu_nakshatra":        _safe("ketu_nakshatra"),
        "rahu_sign":             _safe("rahu_sign"),
        "rahu_house":            _safe("rahu_house"),
        "rahu_nakshatra":        _safe("rahu_nakshatra"),
        "chiron_sign":           _safe("chiron_sign"),
        "chiron_house":          _safe("chiron_house"),
        "chiron_nakshatra":      _safe("chiron_nakshatra"),
        "lilith_sign":           _safe("lilith_sign"),
        "lilith_house":          _safe("lilith_house"),
        "saturn_sign":           _safe("saturn_sign"),
        "saturn_house":          _safe("saturn_house"),
        "jupiter_sign":          _safe("jupiter_sign"),
        "jupiter_house":         _safe("jupiter_house"),
        "porte_visible_sign":    _safe("porte_visible_sign"),
        "porte_visible_house":   _safe("porte_visible_house"),
        "porte_visible_deg":     _safe("porte_visible_deg"),
        "porte_invisible_sign":  _safe("porte_invisible_sign"),
        "porte_invisible_house": _safe("porte_invisible_house"),
        "moon_longitude_sid":    _safe("moon_longitude_sid"),
        "chandra_lagna_degree":  _safe("chandra_lagna_degree"),
        "last_signal_date":      _safe("last_signal_date"),
        "chat_remaining":        _safe("chat_remaining", int, 0),
        "chat_reset_month":      _safe("chat_reset_month"),
        "alert_sent":            _safe("alert_sent", int, 0),
    }

def get_all_profiles() -> list[dict]:
    """Retourne tous les profils de la base."""
    db = _get_db()
    docs = db.collection("users").stream()
    profiles = []
    for doc in docs:
        p = _doc_to_profile(doc)
        if p:
            profiles.append(p)
    return profiles

def get_profile_by_email(email: str) -> dict | None:
    """Récupère un profil par son email."""
    db = _get_db()
    email_clean = email.strip().lower()
    doc = db.collection("users").document(email_clean).get()
    if doc.exists:
        return _doc_to_profile(doc)
    
    # Query fallback en cas d'indexation différente
    query = db.collection("users").where("email", "==", email_clean).limit(1).get()
    if query:
        return _doc_to_profile(query[0])
    return None

def get_profile_by_pseudo(pseudo: str) -> dict | None:
    """Récupère un profil par son pseudo (insensible à la casse)."""
    db = _get_db()
    pseudo_clean = _clean_pseudo(pseudo)
    
    # Query directe par le champ pseudo
    query = db.collection("users").where("pseudo", "==", pseudo_clean).limit(1).get()
    if query:
        return _doc_to_profile(query[0])
    
    query = db.collection("users").where("pseudo", "==", pseudo.strip()).limit(1).get()
    if query:
        return _doc_to_profile(query[0])
        
    # Parcours fallback pour robustesse sur pseudos mal formatés
    docs = db.collection("users").stream()
    for doc in docs:
        p = _doc_to_profile(doc)
        if p and _clean_pseudo(p.get("pseudo", "")) == pseudo_clean:
            return p
    return None

def save_email_by_pseudo(pseudo: str, email: str) -> bool:
    """Met à jour l'email pour un pseudo donné."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if p:
        old_email = p.get("email").strip().lower()
        new_email = email.strip().lower()
        p["email"] = new_email
        
        if old_email == new_email:
            db.collection("users").document(new_email).update({"email": new_email})
        else:
            db.collection("users").document(new_email).set(p)
            db.collection("users").document(old_email).delete()
        return True
    return False

def create_profile(data: dict) -> dict:
    """Crée un nouveau profil dans Firestore."""
    db = _get_db()
    pseudo = data.get("pseudo", "")
    email = data.get("email", "").strip().lower()
    
    profile_data = {
        "pseudo":                pseudo,
        "email":                 email,
        "name":                  data.get("name", pseudo),
        "year":                  int(data.get("year", 1990)),
        "month":                 int(data.get("month", 1)),
        "day":                   int(data.get("day", 1)),
        "hour":                  int(data.get("hour", 12)),
        "minute":                int(data.get("minute", 0)),
        "lat":                   float(data.get("lat", 48.8566)),
        "lon":                   float(data.get("lon", 2.3522)),
        "tz":                    data.get("tz", "Europe/Paris"),
        "city":                  data.get("city", ""),
        "transit_city":          data.get("transit_city", data.get("city", "")),
        "transit_lat":           float(data.get("transit_lat", data.get("lat", 48.8566))),
        "transit_lon":           float(data.get("transit_lon", data.get("lon", 2.3522))),
        "transit_tz":            data.get("transit_tz", data.get("tz", "Europe/Paris")),
        "transit_date":          data.get("transit_date", ""),
        "syntheses_count":       0,
        "syntheses_reset_date":  _current_month_str(),
        "alerts_enabled":        0,
        "plan":                  "pro",
        "plan_syntheses":        0,
        "stripe_customer_id":    "",
        "chat_remaining":        0,
        "chat_reset_month":      "",
        "alert_sent":            0
    }
    
    doc_ref = db.collection("users").document(email)
    doc_ref.set(profile_data)
    return _doc_to_profile(doc_ref.get())

def update_profile(email: str, data: dict) -> dict | None:
    """Met à jour un profil existant dans Firestore."""
    db = _get_db()
    email_clean = email.strip().lower()
    doc_ref = db.collection("users").document(email_clean)
    doc = doc_ref.get()
    if not doc.exists:
        return None
        
    updates = {}
    for k, v in data.items():
        if v is not None:
            if k in ("year", "month", "day", "hour", "minute", "syntheses_count", "plan_syntheses", "alerts_enabled", "chat_remaining", "alert_sent"):
                try: updates[k] = int(v)
                except: pass
            elif k in ("lat", "lon", "transit_lat", "transit_lon"):
                try: updates[k] = float(v)
                except: pass
            else:
                updates[k] = v
                
    if updates:
        doc_ref.update(updates)
        
    return _doc_to_profile(doc_ref.get())

def save_natal_to_sheet(pseudo: str, profile: dict) -> bool:
    """Sauvegarde les données natales calculées dans Firestore (conserve le nom historique)."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if p:
        email = p.get("email").strip().lower()
        doc_ref = db.collection("users").document(email)
        
        updates = {}
        for col in NATAL_COLS:
            if col in profile:
                updates[col] = profile[col]
        if updates:
            doc_ref.update(updates)
        return True
    return False

def check_and_increment_synthesis(pseudo: str) -> dict:
    """Vérifie le quota mensuel de synthèses."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return {"allowed": False, "remaining": 0}
        
    email = p.get("email").strip().lower()
    doc_ref = db.collection("users").document(email)
    
    current_month = _current_month_str()
    count = p.get("syntheses_count", 0)
    reset_date = p.get("syntheses_reset_date", "")
    
    if reset_date != current_month:
        count = 0
        reset_date = current_month
        
    if count >= SYNTHESIS_QUOTA:
        return {"allowed": False, "remaining": 0}
        
    new_count = count + 1
    doc_ref.update({
        "syntheses_count": new_count,
        "syntheses_reset_date": reset_date
    })
    return {"allowed": True, "remaining": SYNTHESIS_QUOTA - new_count}

def delete_profile(pseudo: str) -> bool:
    """Supprime définitivement un profil dans Firestore."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if p:
        email = p.get("email").strip().lower()
        db.collection("users").document(email).delete()
        return True
    return False

def pseudo_exists(pseudo: str) -> bool:
    """Vérifie si un pseudo existe."""
    p = get_profile_by_pseudo(pseudo)
    return p is not None

def set_alerts(pseudo: str, enabled: bool) -> bool:
    """Active ou désactive les alertes de transit."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if p:
        email = p.get("email").strip().lower()
        db.collection("users").document(email).update({
            "alerts_enabled": int(enabled)
        })
        return True
    return False

# ── Gestion plans Stripe ───────────────────────────────────────────────────────

PLAN_SYNTHESES = {
    "test":     1,
    "lecture":  1,
    "essential": 1,
    "subscription": -1,
    "illimite": -1,
    "illimité": -1,
    "free":     0,
}

PLAN_CHAT_LIMITS = {
    "test":     3,
    "lecture":  3,
    "essential": 3,
    "subscription": 10,
    "illimite": 10,
    "illimité": 10,
    "free":     0,
}

def upgrade_plan(pseudo: str, plan: str, stripe_customer_id: str = "") -> bool:
    """Met à jour le plan d'un utilisateur après paiement Stripe."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return False
        
    email = p.get("email").strip().lower()
    doc_ref = db.collection("users").document(email)
    
    syntheses = PLAN_SYNTHESES.get(plan, 0)
    chat_limit = PLAN_CHAT_LIMITS.get(plan, 0)
    current_month = _current_month_str()[:7]
    
    updates = {
        "plan": plan,
        "plan_syntheses": syntheses,
        "chat_remaining": chat_limit,
        "chat_reset_month": current_month
    }
    if stripe_customer_id:
        updates["stripe_customer_id"] = stripe_customer_id
        
    doc_ref.update(updates)
    return True

def downgrade_plan(pseudo: str) -> bool:
    """Rétrograde le plan à free."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if p:
        email = p.get("email").strip().lower()
        db.collection("users").document(email).update({
            "plan": "free",
            "plan_syntheses": 0
        })
        return True
    return False

def get_chat_quota(pseudo: str) -> dict:
    """Retourne l'état des quotas de chat pour un utilisateur."""
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return {"plan": "free", "remaining": 0, "limit": 0, "local_unlimited": False}
        
    plan = p.get("plan", "free")
    plan_normalized = plan.lower().replace("é", "e")
    remaining = p.get("chat_remaining", 0)
    current_month = _current_month_str()[:7]
    
    if plan_normalized in ("illimite", "subscription"):
        reset_month = p.get("chat_reset_month", "")
        if reset_month != current_month:
            remaining = PLAN_CHAT_LIMITS.get(plan, 10)
            
    return {
        "plan": plan,
        "remaining": remaining,
        "limit": PLAN_CHAT_LIMITS.get(plan, 0),
        "local_unlimited": plan_normalized in ("illimite", "subscription")
    }

def consume_chat_question(pseudo: str, local: bool = False) -> dict:
    """Consomme 1 question de chat."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return {"ok": False, "remaining": 0, "local": False}
        
    email = p.get("email").strip().lower()
    doc_ref = db.collection("users").document(email)
    
    plan = p.get("plan", "free")
    plan_normalized = plan.lower().replace("é", "e")
    current_month = _current_month_str()[:7]
    
    if plan_normalized in ("illimite", "subscription"):
        if local:
            return {"ok": True, "remaining": -1, "local": True}
        remaining = p.get("chat_remaining", 0)
        reset_month = p.get("chat_reset_month", "")
        if reset_month != current_month:
            remaining = PLAN_CHAT_LIMITS.get(plan, 10)
            doc_ref.update({"chat_reset_month": current_month})
        if remaining <= 0:
            return {"ok": False, "remaining": 0, "local": False}
        doc_ref.update({"chat_remaining": remaining - 1})
        return {"ok": True, "remaining": remaining - 1, "local": False}
        
    if plan_normalized not in ("test", "lecture", "essential"):
        return {"ok": False, "remaining": 0, "local": False}
        
    remaining = p.get("chat_remaining", 0)
    if remaining <= 0:
        return {"ok": False, "remaining": 0, "local": False}
    doc_ref.update({"chat_remaining": remaining - 1})
    return {"ok": True, "remaining": remaining - 1, "local": False}

def get_and_consume_alert(pseudo: str, plan: str) -> dict:
    """Consomme une alerte de transit."""
    plan_normalized = plan.lower().replace("é", "e")
    if plan_normalized == "free":
        return {"ok": False, "is_last": False}
    if plan_normalized in ("illimite", "subscription"):
        return {"ok": True, "is_last": False}
        
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return {"ok": False, "is_last": False}
        
    email = p.get("email").strip().lower()
    doc_ref = db.collection("users").document(email)
    
    sent = p.get("alert_sent", 0)
    if sent >= 1:
        return {"ok": False, "is_last": False}
        
    doc_ref.update({"alert_sent": 1})
    return {"ok": True, "is_last": True}

def consume_plan_synthesis(pseudo: str) -> bool:
    """Décrémente le compteur de synthèse du plan."""
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        return False
        
    plan = p.get("plan", "free")
    plan_normalized = plan.lower().replace("é", "e")
    if plan_normalized in ("illimite", "subscription"):
        return True
        
    email = p.get("email").strip().lower()
    doc_ref = db.collection("users").document(email)
    
    count = p.get("plan_syntheses", 0)
    doc_ref.update({"plan_syntheses": count - 1})
    return True

def check_and_consume_daily_signal(pseudo: str, profile_dict: dict = None) -> bool:
    """Quota quotidien freemium."""
    if profile_dict:
        plan = profile_dict.get("plan", "free").lower().replace("é", "e")
        if plan in ("illimite", "subscription", "pro", "test", "lecture", "essential"):
            today = date.today()
            if plan == "pro" and today > date(2026, 7, 15):
                return False
            return True
            
    db = _get_db()
    p = get_profile_by_pseudo(pseudo)
    if not p:
        print("User not found in db, allowing first use", flush=True)
        return True
        
    plan = p.get("plan", "free")
    plan_normalized = plan.lower().replace("é", "e")
    if plan_normalized in ("illimite", "subscription", "pro"):
        if plan_normalized == "pro" and date.today() > date(2026, 7, 15):
            pass
        else:
            return True
            
    today_str = date.today().isoformat()
    last_date = p.get("last_signal_date", "")
    if last_date == today_str:
        return False
        
    email = p.get("email").strip().lower()
    db.collection("users").document(email).update({
        "last_signal_date": today_str
    })
    return True

# ── Voting / Benchmark ─────────────────────────────────────────────────────

def save_vote(pseudo: str, provider: str, model: str, rating: int) -> bool:
    """Enregistre un vote pour le benchmark dans Firestore."""
    db = _get_db()
    try:
        db.collection("votes").add({
            "pseudo": pseudo,
            "date": date.today().isoformat(),
            "provider": provider,
            "model": model,
            "rating": int(rating)
        })
        return True
    except Exception:
        return False

def get_benchmark() -> list:
    """Calcule le benchmark des modèles à partir de Firestore."""
    db = _get_db()
    try:
        docs = db.collection("votes").stream()
    except Exception:
        return []
        
    from collections import defaultdict
    totals = defaultdict(lambda: {"count": 0, "sum": 0})
    for doc in docs:
        row = doc.to_dict()
        prov = row.get("provider", "")
        mod = row.get("model", "")
        try:
            rat = int(row.get("rating", 0))
        except ValueError:
            continue
        key = f"{prov}/{mod}"
        totals[key]["count"] += 1
        totals[key]["sum"] += rat
        
    result = []
    for key, v in sorted(totals.items(), key=lambda x: -x[1]["count"]):
        result.append({
            "provider_model": key,
            "votes": v["count"],
            "avg_rating": round(v["sum"] / v["count"], 2),
        })
    return result