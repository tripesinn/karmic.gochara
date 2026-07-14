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
MONTHS = {m: i+1 for i, m in enumerate(_FR)}
MONTHS.update({m: i+1 for i, m in enumerate(_EN)})

_SIGN = "@siderealAstro13"
_APP = "https://karmicgochara.app"
_TAGS = "#KarmicGochara #VedicAstrology #SiderealAstro"
_OUT = "/tmp/karmic_biorhythm.png"


def parse_target_date(text: str, now: date | None = None) -> date | None:
    """Parse '17 juillet' / 'Jul 17' / 'mon pic du 10 sep' -> date (futur seul).
    None si rien trouve ou date passee."""
    if not text:
        return None
    now = now or date.today()
    low = text.lower()
    # pattern : chiffre (1-2) + mois  OU  mois + chiffre
    m = re.search(r"\b(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", low)
    if not m:
        m = re.search(r"\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})\b", low)
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


def _label(e: dict) -> str:
    """Libelle court d'un point de biorythme."""
    node = " ◆" if e.get("has_node") else ""
    return f"{e['date'][5:]} (H{e['house']}, d{e['natal_density']}{node})"


def build_biorhythm_tweet(biorhythm: list[dict], now: date | None = None,
                          n_pics: int = 3) -> str:
    """Tweet public 280c : signe les pics + lien app.
    biorhythm = courbe brute (tous jours) de transit_alerts.chandra_biorhythm."""
    now = now or date.today()
    future = [e for e in biorhythm if e["date"] >= now.isoformat()]
    if not future:
        return f"Ton biorythme lunaire est calme. Reviens bientôt ⌁ {_SIGN} {_APP} {_TAGS}"
    # sommets : has_node d'abord, puis density
    future.sort(key=lambda e: (not e["has_node"], -e["natal_density"], e["date"]))
    pics = future[:n_pics]
    pic_txt = " · ".join(_label(e) for e in pics)
    head = "Ton biorythme lunaire :"
    body = f"Prochains pics -> {pic_txt}"
    tail = f"Courbe complete -> {_APP} {_TAGS}"
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
    Texte court, injecte dans transit_hint du system prompt (pas du DM brut)."""
    if not point:
        return ""
    node = " (nœud Rahu/Ketu actif)" if point.get("has_node") else ""
    return (f"Biorythme: le {point['date']}, Lune en H{point['house']} "
            f"({point['nakshatra']}), densite {point['natal_density']}{node}. "
            f"Cible ce jour-ci.")
