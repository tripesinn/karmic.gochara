# -*- coding: utf-8 -*-
"""
Couche B — Formatage du BIORYTHME LUNAIRE (Chandra Lagna) pour X.
Texte DETERMINE (aucun appel LLM) : parse la date demandee dans la mention
et formate le tweet public (280c) + le hint DM.

Axe unique (density/has_node) vient de transit_alerts. Ici on ne fait que
formater. Single-source reviewable par AGY.
"""
import re
from datetime import date, timedelta

# Mois FR + abrevs EN (insensible a la casse)
_FR = ["janvier","février","mars","avril","mai","juin","juillet","août",
       "septembre","octobre","novembre","décembre"]
_EN = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
_EN_FULL = ["january","february","march","april","may","june","july","august",
            "september","october","november","december"]
MONTHS = {m: i+1 for i, m in enumerate(_FR)}
MONTHS.update({m: i+1 for i, m in enumerate(_EN)})
MONTHS.update({m: i+1 for i, m in enumerate(_EN_FULL)})
# Alternation des noms de mois (FR + EN abrégé + EN complet) pour le parsing.
_MONTH_ALT = "|".join(_FR + _EN + _EN_FULL)

_SIGN = "@siderealAstro13"
_APP = "https://karmicgochara.app"
_TAGS = "#ChandraLagna #SiderealAstrology #KarmicAstrology #karma #astrology"
_OUT = "/tmp/karmic_biorhythm.png"


def parse_target_date(text: str, now: date | None = None) -> date | None:
    """Parse '17 juillet' / 'Jul 17' / 'mon pic du 10 sep' -> date (futur seul).
    None si rien trouve ou date passee."""
    if not text:
        return None
    now = now or date.today()
    low = text.lower()
    # chiffre + mois  OU  mois + chiffre  (FR + EN abrégé + EN complet)
    m = re.search(rf"\b(\d{{1,2}})\s+({_MONTH_ALT})\b", low)
    if not m:
        m = re.search(rf"\b({_MONTH_ALT})\s+(\d{{1,2}})\b", low)
        if not m:
            return None
        mo, dd = m.group(1), int(m.group(2))
    else:
        dd, mo = int(m.group(1)), m.group(2)
    mo_i = MONTHS.get(mo)
    if not mo_i or dd < 1 or dd > 31:
        return None
    try:
        d = date(now.year, mo_i, dd)
    except ValueError:
        return None
    if d < now:
        return None   # anti-retro : on ne genere pas pour le passe
    return d


def _phase_short(e: dict) -> str:
    """Phase courte du jour pour le label tweet (EN, cohérent avec le hint)."""
    if e.get("has_node"):
        return "introspection"
    d = e.get("natal_density", 0) or 0
    if d >= 5:
        return "peak"
    if d >= 3:
        return "action"
    if d == 2:
        return "build"
    return "rest"


def _label(e: dict) -> str:
    """Libelle court d'un point de biorythme (EN)."""
    node = " ◆" if e.get("has_node") else ""
    return f"{e['date'][5:]} (H{e['house']}, d{e['natal_density']}{node} · {_phase_short(e)})"


def build_biorhythm_tweet(biorhythm: list[dict], now: date | None = None,
                          n_pics: int = 3) -> str:
    """Tweet public 280c (EN) : signe les pics + lien app.
    biorhythm = courbe brute (tous jours) de transit_alerts.chandra_biorhythm."""
    now = now or date.today()
    future = [e for e in biorhythm if e["date"] >= now.isoformat()]
    if not future:
        return f"Your lunar biorhythm is calm. Check back soon ⌁ {_SIGN} {_APP} {_TAGS}"
    # sommets : has_node d'abord, puis density
    future.sort(key=lambda e: (not e["has_node"], -e["natal_density"], e["date"]))
    pics = future[:n_pics]
    pic_txt = " · ".join(_label(e) for e in pics)
    head = "Your lunar biorhythm:"
    body = f"Next peaks -> {pic_txt}"
    tail = f"Full curve -> {_APP} {_TAGS}"
    tweet = f"{head}\n{body}\n{tail}"
    # tronque si depasse 280 (rare : 3 pics max, labels courts)
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    return tweet


def build_biorhythm_image(biorhythm: list[dict], out_path: str = _OUT,
                          now: date | None = None) -> str:
    """Infographie locale (matplotlib, 0€) : courbe natal_density 90j,
    pics has_node en rouge ◆, signature @siderealAstro13 en footer.
    Retourne le chemin du PNG (ou '' si echec)."""
    now = now or date.today()
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
    except Exception:
        return ""
    try:
        xs = [datetime.fromisoformat(e["date"]) for e in biorhythm]
        ys = [e["natal_density"] for e in biorhythm]
        nodes = [(x, y) for x, y, e in zip(xs, ys, biorhythm) if e["has_node"]]
        fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(xs, ys, color="#d29922", lw=2, zorder=2)
        ax.fill_between(xs, ys, color="#d29922", alpha=0.12, zorder=1)
        if nodes:
            nx, ny = zip(*nodes)
            ax.scatter(nx, ny, color="#f85149", s=60, zorder=3,
                       marker="D", label="Nœud Rahu/Ketu ◆")
        ax.set_ylim(0, max(ys) + 1)
        ax.set_ylabel("densité natale", color="#c9d1d9")
        ax.set_title("Ton biorythme lunaire — Chandra Lagna",
                     color="#f0f6fc", fontsize=13, fontweight="bold")
        ax.tick_params(colors="#8b949e")
        ax.spines["bottom"].set_color("#30363d")
        ax.spines["left"].set_color("#30363d")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.legend(facecolor="#0d1117", edgecolor="#30363d", labelcolor="#c9d1d9",
                  loc="upper right", fontsize=8)
        fig.text(0.01, 0.02,
                 f"{_SIGN}  ·  courbe complete sur {_APP}",
                 color="#58a6ff", fontsize=8)
        fig.tight_layout(rect=[0, 0.04, 1, 1])
        fig.savefig(out_path, facecolor=fig.get_facecolor())
        plt.close(fig)
        return out_path
    except Exception:
        return ""


def build_biorhythm_hint(point: dict | None) -> str:
    """Hint pour le DM Soul Debug : le jour choisi (ou None -> sommet auto).
    Texte court EN (colle au system prompt Grok), 1 ligne condensée : phase du
    jour + sig maison + digest EN du Nakshatra du jour (ni FR, ni dict brut)."""
    if not point:
        return ""
    house = str(point.get("house", ""))
    nak = point.get("nakshatra", "")
    density = point.get("natal_density", 0) or 0
    has_node = bool(point.get("has_node", False))
    node = " (Rahu/Ketu node active)" if has_node else ""
    # Phase — bandes fines calées sur l'échelle 0-7 + seuil perso min_density=2.
    if has_node:
        phase = "INTROSPECTION (karmic node window)"
    elif density >= 5:
        phase = "PEAK ACTION (maximum activation)"
    elif density >= 3:
        phase = "ACTION (building momentum)"
    elif density == 2:
        phase = "BUILD (personal-relevance threshold)"
    else:
        phase = "REST / OBSERVE (low density)"
    # Signification de maison (Chandra Lagna) — EN pour coller au system prompt.
    HOUSE_SIG = {
        "1": "vital drive & new beginning", "2": "resources & stability",
        "3": "courage & communication", "4": "home & inner peace",
        "5": "creativity & joy", "6": "challenges & health",
        "7": "relationships & partnerships", "8": "transformation & intuition",
        "9": "wisdom & luck", "10": "career & alignment",
        "11": "gains & network", "12": "letting go & dreams",
    }
    sig = HOUSE_SIG.get(house, "general sensitivity")
    # Règle Nakshatra DIGÉRÉE en EN (1 phrase, pas le dict FR brut) — coherent
    # avec STYLE_NO_VERBATIM du system prompt (Grok doit assimiler, pas recopier).
    NAK_EN = {
        "Ashwini": "initiative healing vs reflexive rush to dodge depth",
        "Bharani": "creative rebirth vs guilt-driven control",
        "Krittika": "clear vision vs harsh rejection",
        "Rohini": "conscious abundance vs possessive clinging",
        "Mrigashira": "focused curiosity vs restless fleeing",
        "Ardra": "resilience after storm vs crisis-seeking",
        "Punarvasu": "cyclic renewal vs nostalgic withdrawal",
        "Pushya": "balanced care vs worn-out self-sacrifice",
        "Ashlesha": "lucid trust vs controlling distrust",
        "Magha": "humble leadership vs ancestral-power ego",
        "Purva Phalguni": "sacred creativity vs addictive seduction",
        "Uttara Phalguni": "stable service vs approval-seeking",
        "Hasta": "creative mastery vs paralyzing perfectionism",
        "Chitra": "architecture of meaning vs surface beauty",
        "Swati": "shared freedom vs flight from commitment",
        "Vishakha": "ethical focus vs win-at-all-costs",
        "Anuradha": "soul loyalty vs blind devotion",
        "Jyeshtha": "wise protection vs lonely control",
        "Mula": "spiritual rooting vs destructive unraveling",
        "Purva Ashadha": "inner invincibility vs sterile strife",
        "Uttara Ashadha": "collective leadership vs isolated delay",
        "Shravana": "active listening vs silent invisibility",
        "Dhanishtha": "shared prosperity vs defensive hoarding",
        "Shatabhisha": "collective soul-medicine vs isolated healing",
        "Purva Bhadrapada": "channeled idealism vs bitter fanaticism",
        "Uttara Bhadrapada": "embodied wisdom vs passive dissolution",
        "Revati": "protective guidance vs abandonment-solving sacrifice",
    }
    nak_part = f" Nakshatra theme of the day ({nak}): {NAK_EN[nak]}." if nak in NAK_EN else ""
    return (
        f"BIORYTHM TARGET DAY: {point['date']}, transiting Moon in Chandra Lagna "
        f"House {house} ({sig}), Nakshatra {nak}, density {density}{node}. "
        f"Phase: {phase}.{nak_part} Speak to THIS specific day as the active window "
        f"of the Soul Debug."
    )
