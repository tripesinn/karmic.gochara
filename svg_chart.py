import math

# ── Palette ───────────────────────────────────────────────────────────────────
_BG         = "#07071a"
_GOLD       = "#c9a84c"
_GOLD_MID   = "rgba(201,168,76,0.45)"
_GOLD_DIM   = "rgba(201,168,76,0.18)"
_CYAN       = "#5ec4d4"
_CYAN_DIM   = "rgba(94,196,212,0.18)"
_PURPLE     = "#b07ed4"
_TEXT       = "#ede8df"
_TEXT_DIM   = "rgba(237,232,223,0.4)"

# Element tints (fire / earth / air / water)  — applied to 12 zodiac segments
_ELEM = [
    "rgba(180,70,35,0.22)",  # Aries   fire
    "rgba(55,125,65,0.22)",  # Taurus  earth
    "rgba(55,105,200,0.22)", # Gemini  air
    "rgba(35,75,165,0.22)",  # Cancer  water
    "rgba(180,70,35,0.22)",  # Leo     fire
    "rgba(55,125,65,0.22)",  # Virgo   earth
    "rgba(55,105,200,0.22)", # Libra   air
    "rgba(35,75,165,0.22)",  # Scorpio water
    "rgba(180,70,35,0.22)",  # Sag     fire
    "rgba(55,125,65,0.22)",  # Cap     earth
    "rgba(55,105,200,0.22)", # Aqua    air
    "rgba(35,75,165,0.22)",  # Pisces  water
]

_SIGNS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

_NAKS = [
    "Asw","Bha","Kri","Roh","Mri","Ard","Pun","Pus","Asl",
    "Mag","PPh","UPh","Has","Chi","Swa","Vis","Anu","Jye",
    "Mul","PAs","UAs","Shr","Dha","Sha","PBh","UBh","Rev",
]

# Planet name → (glyph, natal_color)
_NATAL_SYM = {
    "Soleil ☀":          ("☀", _GOLD),
    "Lune ☽":            ("☽", _GOLD),
    "Mercure ☿":         ("☿", _TEXT),
    "Vénus ♀":           ("♀", _TEXT),
    "Mars ♂":            ("♂", _TEXT),
    "Jupiter ♃":         ("♃", _GOLD),
    "Saturne ♄":         ("♄", _TEXT),
    "Uranus ♅":          ("♅", _TEXT_DIM),
    "Neptune ♆":         ("♆", _TEXT_DIM),
    "Pluton ♇":          ("♇", _TEXT_DIM),
    "Chiron ⚷":          ("⚷", _PURPLE),
    "Nœud Nord ☊":       ("☊", _CYAN),
    "Nœud Sud ☋":        ("☋", _CYAN),
    "Lilith ⚸":          ("⚸", _CYAN),
    "Porte Visible ⊙":   ("♄/♅", _GOLD),
    "Porte Invisible ⊗": ("♅/♄", _PURPLE),
}

# Transit glyph → color override (different from natal)
_TRANSIT_COLOR = {
    "Soleil ☀":    _CYAN,
    "Lune ☽":      _CYAN,
    "Mercure ☿":   "#9dd4dc",
    "Vénus ♀":     "#9dd4dc",
    "Mars ♂":      "#e07860",
    "Jupiter ♃":   _CYAN,
    "Saturne ♄":   "#aac0c8",
    "Nœud Nord ☊": "#88c4cc",
}

_IMPORTANT_NATAL = [
    "Lune ☽", "Soleil ☀", "Saturne ♄", "Jupiter ♃",
    "Nœud Nord ☊", "Nœud Sud ☋",
    "Chiron ⚷", "Lilith ⚸",
    "Porte Visible ⊙", "Porte Invisible ⊗",
    "Mars ♂", "Vénus ♀", "Mercure ☿",
]

_IMPORTANT_TRANSIT = [
    "Soleil ☀", "Lune ☽", "Mars ♂", "Vénus ♀",
    "Mercure ☿", "Jupiter ♃", "Saturne ♄", "Nœud Nord ☊",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _spread(items, min_gap=8.0, iterations=25):
    """
    items : list of [name, lon, extra]
    Returns new list with display_lon spread so no two are within min_gap°.
    """
    if len(items) <= 1:
        return [list(it) for it in items]
    result = [list(it) for it in items]
    for _ in range(iterations):
        result.sort(key=lambda x: x[1] % 360)
        changed = False
        n = len(result)
        for i in range(n):
            j = (i + 1) % n
            l1 = result[i][1] % 360
            l2 = result[j][1] % 360
            gap = (l2 - l1) % 360
            if gap < min_gap:
                push = (min_gap - gap) / 2.0
                result[i][1] -= push
                result[j][1] += push
                changed = True
        if not changed:
            break
    return result


def _coords(asc_lon, lon, radius, cx, cy):
    """Screen (x, y) for ecliptic longitude, ASC at left (180°)."""
    a = math.radians((asc_lon - lon + 180.0) % 360.0)
    return cx + radius * math.cos(a), cy + radius * math.sin(a)


def _arc_path(cx, cy, r_out, r_in, a1_deg, a2_deg):
    """
    Annular sector path from angle a1_deg to a2_deg (going CCW, sweep=0 in SVG).
    a1_deg > a2_deg because we go CCW (angles decrease).
    """
    a1 = math.radians(a1_deg)
    a2 = math.radians(a2_deg)
    # All segments are 30° → large_arc = 0
    x1o = cx + r_out * math.cos(a1)
    y1o = cy + r_out * math.sin(a1)
    x2o = cx + r_out * math.cos(a2)
    y2o = cy + r_out * math.sin(a2)
    x1i = cx + r_in  * math.cos(a1)
    y1i = cy + r_in  * math.sin(a1)
    x2i = cx + r_in  * math.cos(a2)
    y2i = cy + r_in  * math.sin(a2)
    return (f"M {x1o:.2f},{y1o:.2f} "
            f"A {r_out},{r_out} 0 0,0 {x2o:.2f},{y2o:.2f} "
            f"L {x2i:.2f},{y2i:.2f} "
            f"A {r_in},{r_in} 0 0,1 {x1i:.2f},{y1i:.2f} Z")


# ── Main generator ────────────────────────────────────────────────────────────

def generate_karmic_chart_svg(natal_positions, transit_positions=None, lang='fr', transit_date=None):
    """
    Génère une carte astrologique double-roue en SVG.
    Anneau extérieur : natal.  Anneau intérieur : transits (optionnel).
    """
    # ── Layout ────────────────────────────────────────────────────────────────
    W, H      = 600, 640
    CX, CY    = 300, 305
    R_OUT     = 270   # outer rim of zodiac band
    R_ZIN     = 218   # inner rim of zodiac band
    R_NATAL   = 190   # natal symbol radius
    R_TR_OUT  = 148   # outer boundary of transit ring
    R_TR_SYM  = 124   # transit symbol radius
    R_INNER   = 80    # innermost circle

    has_transit = bool(transit_positions)

    # ── ASC ───────────────────────────────────────────────────────────────────
    asc_data = natal_positions.get("ASC ↑") or {}
    asc_lon  = float(asc_data.get("lon_raw", 0))

    def xy(lon, r):
        return _coords(asc_lon, lon, r, CX, CY)

    def a_of(lon):
        return (asc_lon - lon + 180.0) % 360.0

    # ── SVG header + defs ─────────────────────────────────────────────────────
    svg = [
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg" style="font-family:serif;">',
        f'<rect width="{W}" height="{H}" fill="{_BG}"/>',
        '<defs>',
        # Glow filter for important glyphs
        '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">',
        '  <feGaussianBlur stdDeviation="2.5" result="b"/>',
        '  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
        # Soft center gradient
        f'<radialGradient id="cg" cx="50%" cy="50%" r="50%">',
        f'  <stop offset="0%" stop-color="#1a1050" stop-opacity="0.55"/>',
        f'  <stop offset="100%" stop-color="{_BG}" stop-opacity="0"/>',
        '</radialGradient>',
        '</defs>',
        f'<circle cx="{CX}" cy="{CY}" r="{R_OUT}" fill="url(#cg)"/>',
    ]

    # ── 1. Zodiac wheel ───────────────────────────────────────────────────────
    for i in range(12):
        lon0 = i * 30.0
        lon1 = lon0 + 30.0
        a0   = a_of(lon0)
        a1   = a_of(lon1)          # a1 = a0 - 30 (CCW)

        # Filled arc segment
        svg.append(f'<path d="{_arc_path(CX, CY, R_OUT, R_ZIN, a0, a1)}" '
                   f'fill="{_ELEM[i]}" stroke="{_GOLD_DIM}" stroke-width="0.5"/>')

        # Sign glyph at segment centre (inner half of band)
        sx, sy = xy(lon0 + 15, R_ZIN + 16)
        svg.append(f'<text x="{sx:.1f}" y="{sy:.1f}" fill="{_GOLD}" font-size="15" '
                   f'text-anchor="middle" dominant-baseline="middle">{_SIGNS[i]}</text>')

    # ── 1b. Nakshatras (27 divisions, outer half of band) ─────────────────────
    NAK_SPAN = 360.0 / 27
    for n in range(27):
        lon_s = n * NAK_SPAN
        lon_m = lon_s + NAK_SPAN / 2

        # Boundary tick on outer rim
        tx1, ty1 = xy(lon_s, R_OUT)
        tx2, ty2 = xy(lon_s, R_OUT - 8)
        svg.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
                   f'stroke="{_GOLD_DIM}" stroke-width="0.7"/>')

        # Abbreviated name (outer half of band)
        nx, ny = xy(lon_m, R_OUT - 14)
        svg.append(f'<text x="{nx:.1f}" y="{ny:.1f}" fill="{_GOLD_DIM}" font-size="6.5" '
                   f'text-anchor="middle" dominant-baseline="middle" '
                   f'font-family="monospace">{_NAKS[n]}</text>')

    # ── 2. Ring boundaries ────────────────────────────────────────────────────
    rings = [
        (R_OUT,    1.5,  _GOLD_MID),
        (R_ZIN,    1.0,  _GOLD_MID),
        (R_NATAL + 26, 0.6, _GOLD_DIM),  # natal ring outer boundary
    ]
    if has_transit:
        rings += [
            (R_TR_OUT, 0.7, _CYAN_DIM),
            (R_INNER,  0.9, _GOLD_DIM),
        ]
    else:
        rings.append((R_INNER, 0.9, _GOLD_DIM))

    for r, sw, col in rings:
        svg.append(f'<circle cx="{CX}" cy="{CY}" r="{r:.1f}" fill="none" '
                   f'stroke="{col}" stroke-width="{sw}"/>')

    # ── 3. House dividers + numbers ───────────────────────────────────────────
    inner_r = R_INNER
    for i in range(12):
        lon  = (asc_lon + i * 30.0) % 360.0
        is_angle = i in (0, 3, 6, 9)   # H1/H4/H7/H10 = ASC/IC/DSC/MC
        x1, y1 = xy(lon, R_ZIN)
        x2, y2 = xy(lon, inner_r)
        sw    = "1.4" if is_angle else "0.5"
        col   = _GOLD_MID if is_angle else _GOLD_DIM
        dash  = '' if is_angle else 'stroke-dasharray="3,3"'
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{col}" stroke-width="{sw}" {dash}/>')


    # ── 4. Axes Karma/Dharma et PI/PV ────────────────────────────────────────
    def _axis(lon_a, lon_b, color, lbl_a, lbl_b, dash="4,3"):
        x1, y1 = xy(lon_a, R_ZIN)
        x2, y2 = xy(lon_b, R_ZIN)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{color}" stroke-width="0.9" opacity="0.55" stroke-dasharray="{dash}"/>')
        for lbl, lon in ((lbl_a, lon_a), (lbl_b, lon_b)):
            lx, ly = xy(lon, R_ZIN - 14)
            svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{color}" font-size="7" '
                       f'text-anchor="middle" dominant-baseline="middle" '
                       f'font-family="monospace" opacity="0.85">{lbl}</text>')

    ketu_d = natal_positions.get("Nœud Sud ☋")
    rahu_d = natal_positions.get("Nœud Nord ☊")
    if ketu_d and rahu_d:
        _axis(float(ketu_d["lon_raw"]), float(rahu_d["lon_raw"]),
              _CYAN, "Karma", "Dharma", dash="5,3")

    pi_d = natal_positions.get("Porte Invisible ⊗")
    pv_d = natal_positions.get("Porte Visible ⊙")
    if pi_d and pv_d:
        _axis(float(pi_d["lon_raw"]), float(pv_d["lon_raw"]),
              _PURPLE, "PI", "PV", dash="2,3")

    # ── 5. Natal planets ──────────────────────────────────────────────────────
    natal_raw = []
    for name in _IMPORTANT_NATAL:
        d = natal_positions.get(name)
        if d and d.get("lon_raw") is not None:
            sym, col = _NATAL_SYM.get(name, ("?", _TEXT))
            natal_raw.append([name, float(d["lon_raw"]), (sym, col, d)])

    natal_spread = _spread(natal_raw, min_gap=9.0)

    for entry in natal_spread:
        name, disp_lon, (sym, col, orig_d) = entry
        orig_lon = float(orig_d.get("lon_raw", disp_lon))

        # Tick on inner zodiac rim at true position
        tx1, ty1 = xy(orig_lon, R_ZIN)
        tx2, ty2 = xy(orig_lon, R_ZIN - 10)
        svg.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
                   f'stroke="{col}" stroke-width="1.1" opacity="0.65"/>')

        # Connector line if spread moved symbol
        if abs((disp_lon - orig_lon + 180) % 360 - 180) > 1.5:
            lx1, ly1 = xy(orig_lon, R_ZIN - 11)
            lx2, ly2 = xy(disp_lon, R_NATAL + 14)
            svg.append(f'<line x1="{lx1:.1f}" y1="{ly1:.1f}" x2="{lx2:.1f}" y2="{ly2:.1f}" '
                       f'stroke="{_GOLD_DIM}" stroke-width="0.6"/>')

        # Glyph
        is_key = name in ("Soleil ☀", "Lune ☽", "Nœud Nord ☊", "Nœud Sud ☋",
                          "Porte Visible ⊙", "Porte Invisible ⊗")
        filt  = ' filter="url(#glow)"' if is_key else ''
        fs    = 13 if len(sym) > 1 else 21
        px, py = xy(disp_lon, R_NATAL)
        svg.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{col}" font-size="{fs}" '
                   f'text-anchor="middle" dominant-baseline="middle"{filt}>{sym}</text>')

    # ── 5. Transit planets ────────────────────────────────────────────────────
    if has_transit:
        tr_raw = []
        for name in _IMPORTANT_TRANSIT:
            d = transit_positions.get(name)
            if d and d.get("lon_raw") is not None:
                sym, _ = _NATAL_SYM.get(name, ("?", _TEXT))
                col    = _TRANSIT_COLOR.get(name, _CYAN)
                tr_raw.append([name, float(d["lon_raw"]), (sym, col, d)])

        tr_spread = _spread(tr_raw, min_gap=7.0)

        for entry in tr_spread:
            name, disp_lon, (sym, col, orig_d) = entry
            orig_lon = float(orig_d.get("lon_raw", disp_lon))

            # Outer tick
            tx1, ty1 = xy(orig_lon, R_TR_OUT + 1)
            tx2, ty2 = xy(orig_lon, R_TR_OUT + 9)
            svg.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
                       f'stroke="{col}" stroke-width="1" opacity="0.5"/>')

            # Glyph
            fs = 11 if len(sym) > 1 else 17
            px, py = xy(disp_lon, R_TR_SYM)
            svg.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="{col}" font-size="{fs}" '
                       f'text-anchor="middle" dominant-baseline="middle" opacity="0.9">{sym}</text>')

    # ── 6. ASC / DSC line + centre ────────────────────────────────────────────
    xa, ya = xy(asc_lon, R_OUT)
    xd, yd = xy(asc_lon + 180, R_OUT)
    svg.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xd:.1f}" y2="{yd:.1f}" '
               f'stroke="{_GOLD}" stroke-width="0.9" opacity="0.35" stroke-dasharray="5,3"/>')

    lx, ly = xy(asc_lon, R_OUT + 16)
    svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{_GOLD}" font-size="9" '
               f'font-weight="bold" text-anchor="middle" dominant-baseline="middle" '
               f'font-family="monospace">ASC</text>')

    svg.append(f'<circle cx="{CX}" cy="{CY}" r="2.5" fill="{_GOLD}" opacity="0.7"/>')

    # ── 7. Legend ─────────────────────────────────────────────────────────────
    ly = CY + R_OUT + 22
    svg.append(f'<text x="{CX - 80}" y="{ly}" fill="{_GOLD}" font-size="8.5" '
               f'font-family="monospace" opacity="0.65">● NATAL</text>')
    if has_transit and transit_date:
        svg.append(f'<text x="{CX + 10}" y="{ly}" fill="{_CYAN}" font-size="8.5" '
                   f'font-family="monospace" opacity="0.65">● TRANSIT {transit_date}</text>')

    # ── Close ─────────────────────────────────────────────────────────────────
    svg.append('</svg>')
    return "\n".join(svg)
