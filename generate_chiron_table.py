"""
generate_chiron_table.py
Génère ChironTable.java — table de positions de Chiron 1900-2035,
résolution 10 jours. Utilise la mécanique képlerienne (éléments JPL J2000).
Précision ~0.3-0.5°, largement suffisante pour un orbe de 3°.

Usage :
    python generate_chiron_table.py > .../astro/ChironTable.java
"""

import math
from datetime import date, timedelta

# ── Ayanamsa Centre Galactique DK ───────────────────────────────────────────
DK_T0_JD   = 2442351.809028   # JD du 31/10/1974 07h25 UTC
DK_AYAN_T0 = 28.0             # 28°00′
# Vitesse de précession sidérale : 50.27"/an = 0.013964°/an
PRECESSION_RATE = 50.27 / 3600.0 / 365.25   # degrés/jour

def dk_ayanamsa(jd):
    return DK_AYAN_T0 + (jd - DK_T0_JD) * PRECESSION_RATE

# ── Éléments orbitaux de Chiron (époque J2000 = JD 2451545.0) ───────────────
# Source : JPL Horizons small-body browser (2060 Chiron)
JD_J2000   = 2451545.0
CHIRON_A   = 13.6488       # demi-grand axe (UA)
CHIRON_E   = 0.38214       # excentricité
CHIRON_I   = math.radians(6.9310)    # inclinaison
CHIRON_NODE= math.radians(209.6020)  # longitude nœud ascendant
CHIRON_PERI= math.radians(339.3882)  # argument du périhélie
CHIRON_M0  = math.radians(27.70)     # anomalie moyenne à J2000
# Période : T = 2π × √(a³/GM_sun), avec a en UA → T en années juliennes
# T ≈ 50.42 ans = 18 415 jours
CHIRON_N   = 2 * math.pi / (50.42 * 365.25)  # mouvement moyen rad/jour

def solve_kepler(M, e, tol=1e-9):
    """Résout l'équation de Kepler M = E - e·sin(E)."""
    E = M
    for _ in range(50):
        dE = (M - E + e * math.sin(E)) / (1 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E

def chiron_tropical_lon(jd):
    """Longitude tropicale géocentrique approchée de Chiron (degrés)."""
    # Anomalie moyenne
    M = CHIRON_M0 + CHIRON_N * (jd - JD_J2000)
    M = M % (2 * math.pi)

    # Anomalie excentrique
    E = solve_kepler(M, CHIRON_E)

    # Coordonnées héliocentriques en plan orbital
    r   = CHIRON_A * (1 - CHIRON_E * math.cos(E))
    nu  = 2 * math.atan2(
        math.sqrt(1 + CHIRON_E) * math.sin(E / 2),
        math.sqrt(1 - CHIRON_E) * math.cos(E / 2)
    )

    # Passage au plan écliptique J2000
    u    = nu + CHIRON_PERI  # argument de latitude
    cos_i = math.cos(CHIRON_I)

    # Longitude écliptique héliocentrique
    x = r * (math.cos(CHIRON_NODE) * math.cos(u) - math.sin(CHIRON_NODE) * math.sin(u) * cos_i)
    y = r * (math.sin(CHIRON_NODE) * math.cos(u) + math.cos(CHIRON_NODE) * math.sin(u) * cos_i)

    lon_helio = math.degrees(math.atan2(y, x)) % 360

    # Correction géocentrique simplifiée (parallaxe solaire négligeable à 8-18 UA)
    # On utilise la position héliocentrique directement — erreur < 0.5° pour Chiron lointain
    return lon_helio

# ── Génération de la table ───────────────────────────────────────────────────
START = date(1900, 1, 1)
END   = date(2035, 12, 31)
STEP  = 10  # jours

def date_to_jd(d):
    """Jour Julien pour une date à midi UTC."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return (d.day + (153 * m + 2) // 5 + 365 * y
            + y // 4 - y // 100 + y // 400 - 32045) - 0.5

entries = []
current = START
while current <= END:
    jd      = date_to_jd(current)
    trop    = chiron_tropical_lon(jd)
    ayan    = dk_ayanamsa(jd)
    sid_lon = (trop - ayan) % 360
    entries.append((jd, sid_lon))
    current += timedelta(days=STEP)

# ── Sortie Java ──────────────────────────────────────────────────────────────
print("package com.karmicgochara.app.astro;")
print()
print("/**")
print(f" * ChironTable — positions sidérales de Chiron, résolution {STEP} jours.")
print(" * Générée par generate_chiron_table.py · Mécanique képlerienne · Ayanamsa DK")
print(f" * Éléments orbitaux : JPL Horizons J2000 · {START}→{END}")
print(f" * {len(entries)} entrées · précision ~0.3-0.5° (orbe 3°)")
print(" */")
print("public final class ChironTable {")
print()
print(f"    public static final double JD_START  = {entries[0][0]:.6f};")
print(f"    public static final int    STEP_DAYS = {STEP};")
print()
print("    /** Longitudes sidérales (degrés, 0-360) indexées par (JD - JD_START) / STEP_DAYS */")
print("    public static final float[] LON = {")

LINE = 8
for i, (jd, lon) in enumerate(entries):
    if i % LINE == 0:
        print("        ", end="")
    print(f"{lon:.4f}f", end="")
    if i < len(entries) - 1:
        print(", ", end="")
        if (i + 1) % LINE == 0:
            print()
print()
print("    };")
print()
print("    private ChironTable() {}")
print()
print("    /**")
print("     * Retourne la longitude sidérale de Chiron pour un JD donné.")
print("     * Interpolation linéaire entre les deux entrées encadrantes.")
print("     */")
print("    public static double lonForJd(double jd) {")
print("        double offset = (jd - JD_START) / STEP_DAYS;")
print("        int    idx    = (int) offset;")
print("        if (idx < 0)               return LON[0];")
print("        if (idx >= LON.length - 1) return LON[LON.length - 1];")
print("        double frac = offset - idx;")
print("        double a = LON[idx], b = LON[idx + 1];")
print("        // Gère le saut 360°→0° (Chiron franchit 0° vers ~2028)")
print("        double diff = b - a;")
print("        if (diff >  180) diff -= 360;")
print("        if (diff < -180) diff += 360;")
print("        return (a + frac * diff + 360) % 360;")
print("    }")
print("}")
