package com.karmicgochara.app.astro;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import swisseph.SweConst;
import swisseph.SwissEph;

// Chiron calculé via table képlerienne — pas de fichier .se1 requis
// Les autres planètes utilisent SE4J + éphémérides sepl/semo.

/**
 * AstroEngine — Port Java de astro_calc.py
 * Nécessite swisseph.jar dans android/app/libs/
 * et les fichiers d'éphémérides dans le répertoire passé au constructeur.
 */
public class AstroEngine {

    // ── Ayanamsa Centre Galactique Djwhal Khul ───────────────────────────────
    private static final double DK_T0_JD   = 2442351.809028;  // 31/10/1974 07h25 UTC
    private static final double DK_AYAN_T0 = 28.0;            // 28°00′

    // ── IDs planétaires SE ────────────────────────────────────────────────────
    private static final int[][] PLANET_IDS = {
        // { seId, nameIndex } — les noms sont dans PLANET_NAMES
        { SweConst.SE_SUN,        0 },
        { SweConst.SE_MOON,       1 },
        { SweConst.SE_MERCURY,    2 },
        { SweConst.SE_VENUS,      3 },
        { SweConst.SE_MARS,       4 },
        { SweConst.SE_JUPITER,    5 },
        { SweConst.SE_SATURN,     6 },
        { SweConst.SE_URANUS,     7 },
        { SweConst.SE_NEPTUNE,    8 },
        { SweConst.SE_PLUTO,      9 },
        { SweConst.SE_CHIRON,    10 },
        { SweConst.SE_TRUE_NODE, 11 },
        { SweConst.SE_OSCU_APOG, 12 },
    };

    public static final String[] PLANET_NAMES = {
        "Soleil ☀", "Lune ☽", "Mercure ☿", "Vénus ♀", "Mars ♂",
        "Jupiter ♃", "Saturne ♄", "Uranus ♅", "Neptune ♆", "Pluton ♇",
        "Chiron ⚷", "Nœud Nord ☊", "Lilith ⚸"
    };

    private static final double ORB = 3.0;

    private static final int[][] ASPECTS = {
        // { angle_deg × 100 }  — on stocke × 100 pour rester en entiers
        {     0 }, // Conjonction ☌
        { 18000 }, // Opposition ☍
        { 12000 }, // Trigone △
        {  9000 }, // Carré □
        {  6000 }, // Sextile ✶
    };
    private static final String[] ASPECT_NAMES = {
        "Conjonction ☌", "Opposition ☍", "Trigone △", "Carré □", "Sextile ✶"
    };

    private final SwissEph se;

    public AstroEngine(String ephePath) {
        se = new SwissEph(ephePath);
        se.swe_set_sid_mode(SweConst.SE_SIDM_USER, DK_T0_JD, DK_AYAN_T0);
    }

    public void close() {
        se.swe_close();
    }

    // ── getJulianDay ─────────────────────────────────────────────────────────
    /** Convertit une date/heure locale en Jour Julien (UTC). */
    public static double getJulianDay(int year, int month, int day,
                                      int hour, int minute, String tzStr) {
        ZoneId zone = ZoneId.of(tzStr);
        ZonedDateTime local = ZonedDateTime.of(year, month, day, hour, minute, 0, 0, zone);
        ZonedDateTime utc   = local.withZoneSameInstant(ZoneOffset.UTC);
        // JD epoch = 1 Jan 4713 BC noon = Unix epoch 1 Jan 1970 → JD 2440587.5
        long epochMillis = utc.toInstant().toEpochMilli();
        return 2440587.5 + epochMillis / 86400000.0;
    }

    // ── calcPositions ─────────────────────────────────────────────────────────
    /** Calcule toutes les positions planétaires sidérales pour un JD donné. */
    public Map<String, NakshatraCalc.PlanetPosition> calcPositions(double jd, double lat, double lon) {
        int flags = SweConst.SEFLG_SIDEREAL | SweConst.SEFLG_SPEED | SweConst.SEFLG_MOSEPH;
        Map<String, NakshatraCalc.PlanetPosition> positions = new LinkedHashMap<>();

        double[] coords = new double[6];
        StringBuffer err = new StringBuffer();

        for (int[] entry : PLANET_IDS) {
            int seId    = entry[0];
            String name = PLANET_NAMES[entry[1]];

            double planetLon, speed;

            if (seId == SweConst.SE_CHIRON) {
                // Chiron via table képlerienne — pas de seas_18.se1 requis
                planetLon = ChironTable.lonForJd(jd);
                speed     = 0;  // vitesse non utilisée pour Chiron (pas rétrograde dans nos aspects)
            } else {
                err.setLength(0);
                int ret = se.swe_calc_ut(jd, seId, flags, coords, err);
                if (ret < 0) {
                    positions.put(name, null);
                    continue;
                }
                planetLon = coords[0] % 360;
                speed     = coords[3];
            }

            NakshatraCalc.NakshatraResult nak = NakshatraCalc.lonToNakshatra(planetLon);
            positions.put(name, new NakshatraCalc.PlanetPosition(
                planetLon,
                NakshatraCalc.lonToDisplay(planetLon),
                nak.nakshatra, nak.pada, nak.lord, nak.degInNak,
                NakshatraCalc.lonToD9(planetLon),
                NakshatraCalc.lonToD10(planetLon),
                NakshatraCalc.lonToD60(planetLon),
                speed, speed < 0
            ));
        }

        // ── Nœud Sud = Nœud Nord + 180° ──────────────────────────────────────
        NakshatraCalc.PlanetPosition nn = positions.get("Nœud Nord ☊");
        if (nn != null) {
            double ksLon = (nn.lon + 180) % 360;
            NakshatraCalc.NakshatraResult nak = NakshatraCalc.lonToNakshatra(ksLon);
            positions.put("Nœud Sud ☋", new NakshatraCalc.PlanetPosition(
                ksLon, NakshatraCalc.lonToDisplay(ksLon),
                nak.nakshatra, nak.pada, nak.lord, nak.degInNak,
                NakshatraCalc.lonToD9(ksLon),
                NakshatraCalc.lonToD10(ksLon),
                NakshatraCalc.lonToD60(ksLon),
                0, false
            ));
        }

        // ── Moonrise Chart : ASC = début du signe de la Lune ─────────────────
        NakshatraCalc.PlanetPosition moon = positions.get("Lune ☽");
        if (moon != null) {
            double moonSignStart = (int)(moon.lon / 30) * 30.0;
            NakshatraCalc.NakshatraResult nak = NakshatraCalc.lonToNakshatra(moonSignStart);
            positions.put("ASC ↑", new NakshatraCalc.PlanetPosition(
                moonSignStart, NakshatraCalc.lonToDisplay(moonSignStart),
                nak.nakshatra, nak.pada, nak.lord, nak.degInNak,
                NakshatraCalc.lonToD9(moonSignStart),
                NakshatraCalc.lonToD10(moonSignStart),
                NakshatraCalc.lonToD60(moonSignStart),
                0, false
            ));
        }

        // ── MC (Placidus, sidéral) ────────────────────────────────────────────
        double[] cusps = new double[13];
        double[] ascmc = new double[10];
        int ret = se.swe_houses(jd, 0, lat, lon, (int)'P', cusps, ascmc);
        if (ret >= 0) {
            // swe_houses retourne tropical → soustraire ayanamsa DK pour sidéral
            double ayan  = DK_AYAN_T0 + (jd - DK_T0_JD) * (50.27 / 3600.0 / 365.25);
            double mcLon = ((ascmc[1] - ayan) % 360 + 360) % 360;
            NakshatraCalc.NakshatraResult nak = NakshatraCalc.lonToNakshatra(mcLon);
            positions.put("MC ↑", new NakshatraCalc.PlanetPosition(
                mcLon, NakshatraCalc.lonToDisplay(mcLon),
                nak.nakshatra, nak.pada, nak.lord, nak.degInNak,
                NakshatraCalc.lonToD9(mcLon),
                NakshatraCalc.lonToD10(mcLon),
                NakshatraCalc.lonToD60(mcLon),
                0, false
            ));
        }

        return positions;
    }

    // ── calculateTransits ────────────────────────────────────────────────────
    public TransitResult calculateTransits(
            int natalYear, int natalMonth, int natalDay, int natalHour, int natalMinute,
            double natalLat, double natalLon, String natalTz,
            int year, int month, int day, int hour, int minute,
            double transitLat, double transitLon, String transitTz) {

        double natalJd   = getJulianDay(natalYear, natalMonth, natalDay, natalHour, natalMinute, natalTz);
        double transitJd = getJulianDay(year, month, day, hour, minute, transitTz);

        Map<String, NakshatraCalc.PlanetPosition> natalPos   = calcPositions(natalJd,   natalLat,   natalLon);
        Map<String, NakshatraCalc.PlanetPosition> transitPos = calcPositions(transitJd, transitLat, transitLon);

        // ── Portes natales ────────────────────────────────────────────────────
        addPortes(natalPos, "Saturne ♄", "Uranus ♅");

        // ── Portes de transit ─────────────────────────────────────────────────
        addPortes(transitPos, "Saturne ♄", "Uranus ♅");

        // ── Aspects ───────────────────────────────────────────────────────────
        List<AspectEntry> aspects = new ArrayList<>();

        for (Map.Entry<String, NakshatraCalc.PlanetPosition> te : transitPos.entrySet()) {
            if (te.getValue() == null || "Nœud Sud ☋".equals(te.getKey())) continue;
            double tLon = te.getValue().lon;

            for (Map.Entry<String, NakshatraCalc.PlanetPosition> ne : natalPos.entrySet()) {
                if (ne.getValue() == null) continue;
                double nLon = ne.getValue().lon;

                double diff = Math.abs(tLon - nLon) % 360;
                if (diff > 180) diff = 360 - diff;

                for (int i = 0; i < ASPECTS.length; i++) {
                    double aspAngle  = ASPECTS[i][0] / 100.0;
                    double orbActual = Math.abs(diff - aspAngle);
                    if (orbActual <= ORB) {
                        aspects.add(new AspectEntry(
                            te.getKey(), te.getValue().display,
                            te.getValue().nakshatra, te.getValue().pada,
                            ne.getKey(), ne.getValue().display,
                            ne.getValue().nakshatra,
                            ASPECT_NAMES[i],
                            Math.round(orbActual * 100.0) / 100.0,
                            te.getValue().retrograde
                        ));
                    }
                }
            }
        }

        aspects.sort((a, b) -> Double.compare(a.orb, b.orb));

        String transitDate = String.format("%02d/%02d/%04d", day, month, year);
        String transitTime = String.format("%02dh%02d", hour, minute);

        return new TransitResult(aspects, natalPos, transitPos, transitDate, transitTime);
    }

    // ── addPortes ─────────────────────────────────────────────────────────────
    private void addPortes(Map<String, NakshatraCalc.PlanetPosition> pos,
                           String satKey, String uraKey) {
        NakshatraCalc.PlanetPosition sat = pos.get(satKey);
        NakshatraCalc.PlanetPosition ura = pos.get(uraKey);
        if (sat == null || ura == null) return;

        NakshatraCalc.PortesResult portes = NakshatraCalc.calcPortes(sat.lon, ura.lon);
        pos.put("Porte Visible ⊙",   portes.porteVisible);
        pos.put("Porte Invisible ⊗", portes.porteInvisible);
    }

    // ── Value objects ─────────────────────────────────────────────────────────

    public static class AspectEntry {
        public final String  transitPlanet, transitDisplay, transitNak;
        public final int     transitPada;
        public final String  natalPlanet, natalDisplay, natalNak;
        public final String  aspect;
        public final double  orb;
        public final boolean retrograde;

        AspectEntry(String transitPlanet, String transitDisplay, String transitNak, int transitPada,
                    String natalPlanet, String natalDisplay, String natalNak,
                    String aspect, double orb, boolean retrograde) {
            this.transitPlanet = transitPlanet; this.transitDisplay = transitDisplay;
            this.transitNak = transitNak; this.transitPada = transitPada;
            this.natalPlanet = natalPlanet; this.natalDisplay = natalDisplay;
            this.natalNak = natalNak; this.aspect = aspect;
            this.orb = orb; this.retrograde = retrograde;
        }
    }

    public static class TransitResult {
        public final List<AspectEntry>                          aspects;
        public final Map<String, NakshatraCalc.PlanetPosition> natal;
        public final Map<String, NakshatraCalc.PlanetPosition> transits;
        public final String                                     transitDate;
        public final String                                     transitTime;

        TransitResult(List<AspectEntry> aspects,
                      Map<String, NakshatraCalc.PlanetPosition> natal,
                      Map<String, NakshatraCalc.PlanetPosition> transits,
                      String transitDate, String transitTime) {
            this.aspects = aspects; this.natal = natal; this.transits = transits;
            this.transitDate = transitDate; this.transitTime = transitTime;
        }
    }
}
