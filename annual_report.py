"""
annual_report.py — Rapport PDF annuel des transits karmiques
Gochara Karmique

Génère un PDF avec :
  - Page de couverture (profil, année)
  - Calendrier mensuel des transits importants (12 mois)
  - Synthèse karmique annuelle via Claude
"""

import io
from datetime import date

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from calendar_calc import get_monthly_transits

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = HexColor("#0c0a08")
GOLD     = HexColor("#c9a84c")
VIOLET   = HexColor("#4b0082")
TEXT     = HexColor("#e8e0d0")
DIM      = HexColor("#9090b0")
LIGHT_BG = HexColor("#0f0f2a")

MONTH_NAMES_FR = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

MONTH_NAMES = {
    "fr": MONTH_NAMES_FR,
    "en": ["", "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "es": ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    "pt": ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
           "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
    "de": ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
           "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "it": ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
           "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
    "nl": ["", "Januari", "Februari", "Maart", "April", "Mei", "Juni",
           "Juli", "Augustus", "September", "Oktober", "November", "December"],
}


def _styles():
    return {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=22,
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=12,
            textColor=DIM, alignment=TA_CENTER, spaceAfter=4,
        ),
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=13,
            textColor=GOLD, spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10,
            textColor=TEXT, leading=15, spaceAfter=6,
        ),
        "dim": ParagraphStyle(
            "dim", fontName="Helvetica", fontSize=9,
            textColor=DIM, leading=13,
        ),
        "month": ParagraphStyle(
            "month", fontName="Helvetica-Bold", fontSize=11,
            textColor=GOLD, spaceBefore=10, spaceAfter=4,
        ),
    }


def _add_page_bg(canvas, doc):
    """Fond sombre sur chaque page."""
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Bordure or subtile
    canvas.setStrokeColor(VIOLET)
    canvas.setLineWidth(0.5)
    canvas.rect(1*cm, 1*cm, A4[0] - 2*cm, A4[1] - 2*cm, fill=0, stroke=1)
    canvas.restoreState()


def _get_annual_synthesis(profile: dict, all_transits: dict, lang: str = "fr") -> str:
    """Appelle Claude pour une synthèse karmique de l'année."""
    import os

    import anthropic

    client    = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    name      = profile.get("name") or profile.get("pseudo", "")
    year      = date.today().year

    # Résumer les transits actifs par mois
    transit_summary = ""
    for month in range(1, 13):
        month_key = f"{year}-{month:02d}"
        month_events = {k: v for k, v in all_transits.items() if k.startswith(month_key)}
        if month_events:
            transit_summary += f"\n{MONTH_NAMES_FR[month]} :\n"
            seen = set()
            for events in month_events.values():
                for e in events:
                    pair = (e["transit"], e["natal"])
                    if pair not in seen:
                        seen.add(pair)
                        transit_summary += f"  - {e['transit_label']} ⊕ {e['natal_label']}\n"

    if not transit_summary:
        transit_summary = "Aucun transit majeur calculé pour cette année."

    prompt = f"""Tu es un astrologue védique expert en système Djwhal Khul, Chandra Lagna et Gochara.

Voici les transits karmiques importants de l'année {year} pour {name} :
{transit_summary}

Rappel des 3 piliers du système :
- Ketu (Nœud Sud) = ROM = Mémoire karmique passée, résistances, prison
- Chiron = RAM = Blessure originelle, clé de la Porte Invisible
- Rahu (Nœud Nord) = Stage = Dharma, mission de vie, libération

Rédige une synthèse karmique annuelle en {lang}. Structure :
1. Thème dominant de l'année (2-3 lignes)
2. Par trimestre (T1/T2/T3/T4) : les mouvements clés et leur signification karmique (3-4 lignes chacun)
3. Message de clôture : conseil pour l'année (2-3 lignes)

Ton sobre, profond, poétique. Utilise des marqueurs Markdown (##, **gras**) pour structurer."""

    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def generate_annual_pdf(profile: dict, lang: str = "fr") -> bytes:
    """Génère le PDF annuel et retourne les bytes."""
    year     = date.today().year
    name     = profile.get("name") or profile.get("pseudo", "")
    month_names = MONTH_NAMES.get(lang, MONTH_NAMES_FR)
    s        = _styles()

    # ── 1. Calcul des transits pour les 12 mois ───────────────────────────────
    all_transits = {}
    for month in range(1, 13):
        monthly = get_monthly_transits(profile, year, month)
        all_transits.update(monthly)

    # ── 2. Synthèse IA ────────────────────────────────────────────────────────
    try:
        synthesis_text = _get_annual_synthesis(profile, all_transits, lang)
    except Exception as exc:
        synthesis_text = f"[Synthèse indisponible : {exc}]"

    # ── 3. Construction du PDF ────────────────────────────────────────────────
    buf = io.BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="bg", frames=frame, onPage=_add_page_bg)])

    story = []

    # ── Couverture ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("✦ Karmic Gochara", s["title"]))
    story.append(Paragraph(f"Rapport annuel {year}", s["subtitle"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(name, s["subtitle"]))
    city = profile.get("city", "")
    if city:
        story.append(Paragraph(city, s["dim"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Astrologie Védique Sidérale · Chandra Lagna · DK Ayanamsa · Orbe &lt; 3°",
        s["dim"],
    ))
    story.append(PageBreak())

    # ── Calendrier mensuel ────────────────────────────────────────────────────
    story.append(Paragraph(f"Calendrier des transits — {year}", s["section"]))
    story.append(Paragraph(
        "Conjonctions actives (orbe &lt; 3°) entre planètes lentes et points natals clés.",
        s["dim"],
    ))
    story.append(Spacer(1, 0.4*cm))

    for month in range(1, 13):
        month_key    = f"{year}-{month:02d}"
        month_events = {k: v for k, v in all_transits.items() if k.startswith(month_key)}

        story.append(Paragraph(month_names[month], s["month"]))

        if not month_events:
            story.append(Paragraph("— Aucun transit majeur ce mois-ci.", s["dim"]))
            story.append(Spacer(1, 0.2*cm))
            continue

        # Tableau : Date | Transit | Point natal | Orbe
        table_data = [
            [
                Paragraph("<b>Jour</b>", s["dim"]),
                Paragraph("<b>Planète transit</b>", s["dim"]),
                Paragraph("<b>Point natal</b>", s["dim"]),
                Paragraph("<b>Orbe</b>", s["dim"]),
            ]
        ]

        seen_pairs = set()
        for day_key in sorted(month_events.keys()):
            day_num = day_key.split("-")[2]
            for e in month_events[day_key]:
                pair = (e["transit"], e["natal"])
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                retro = " ℞" if e.get("retrograde") else ""
                table_data.append([
                    Paragraph(f"{day_num}", s["body"]),
                    Paragraph(f"{e['transit_label']}{retro}", s["body"]),
                    Paragraph(e["natal_label"], s["body"]),
                    Paragraph(f"{e['orb']}°", s["body"]),
                ])

        col_widths = [1.5*cm, 5*cm, 6.5*cm, 2*cm]
        tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  HexColor("#1a1a30")),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  GOLD),
            ("GRID",        (0, 0), (-1, -1), 0.3, HexColor("#2a2a40")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#0f0f22"), HexColor("#121228")]),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # ── Synthèse karmique annuelle ────────────────────────────────────────────
    story.append(Paragraph(f"Synthèse karmique — {year}", s["section"]))
    story.append(Spacer(1, 0.3*cm))

    # Convertir le markdown basique en paragraphes
    for line in synthesis_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2*cm))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], s["section"]))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], s["section"]))
        else:
            # Convertir **bold** → <b>bold</b> pour ReportLab
            import re
            line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
            line = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", line)
            story.append(Paragraph(line, s["body"]))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Généré par Karmic Gochara · {date.today().strftime('%d/%m/%Y')} · "
        "Astrologie Védique Sidérale · @siderealAstro13",
        s["dim"],
    ))

    doc.build(story)
    return buf.getvalue()
