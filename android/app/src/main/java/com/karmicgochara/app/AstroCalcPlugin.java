package com.karmicgochara.app;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import com.karmicgochara.app.astro.AstroEngine;
import com.karmicgochara.app.astro.EphemerisSetup;
import com.karmicgochara.app.astro.NakshatraCalc;

import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * AstroCalcPlugin — Capacitor bridge pour AstroEngine.
 *
 * Méthodes exposées :
 *   calculateTransits({ natal, date, hour, minute, transit_lat, transit_lon, transit_city, transit_tz })
 *     → { aspects[], natal{}, transits{}, transit_date, transit_time }
 *
 * Le format JSON retourné est identique à celui du serveur Python (/calculate).
 */
@CapacitorPlugin(name = "AstroCalc")
public class AstroCalcPlugin extends Plugin {

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private AstroEngine engine;

    @Override
    public void load() {
        executor.execute(() -> {
            try {
                String path = EphemerisSetup.getEphemerisPath(getContext());
                engine = new AstroEngine(path);
            } catch (Exception e) {
                // Rendre totalement silencieux pour éviter le rouge au démarrage
                // Fallback Moshier en cas d'erreur d'extraction
                engine = new AstroEngine(null);
            }
        });
    }

    @PluginMethod
    public void calculateTransits(PluginCall call) {
        if (engine == null) {
            call.reject("ENGINE_NOT_READY", "Moteur astral non initialisé. Éphémérides manquantes ?");
            return;
        }

        // ── Natal ─────────────────────────────────────────────────────────────
        JSObject natal   = call.getObject("natal");
        String   dateStr = call.getString("date", "");
        int      hour    = call.getInt("hour",   12);
        int      minute  = call.getInt("minute",  0);

        if (natal == null || dateStr.isEmpty()) {
            call.reject("INVALID_PARAMS", "Paramètres manquants : natal et date sont requis.");
            return;
        }

        // Coordonnées de transit (fallback : lieu de naissance)
        double transitLat  = call.getDouble("transit_lat",  natal.optDouble("lat",  0.0));
        double transitLon  = call.getDouble("transit_lon",  natal.optDouble("lon",  0.0));
        String transitCity = call.getString("transit_city", natal.getString("city"));
        String transitTz   = call.getString("transit_tz",  natal.getString("tz"));

        executor.execute(() -> {
            try {
                String[] dateParts = dateStr.split("-");
                int year  = Integer.parseInt(dateParts[0]);
                int month = Integer.parseInt(dateParts[1]);
                int day   = Integer.parseInt(dateParts[2]);

                AstroEngine.TransitResult result = engine.calculateTransits(
                    natal.getInteger("year"),  natal.getInteger("month"), natal.getInteger("day"),
                    natal.getInteger("hour"),  natal.getInteger("minute"),
                    natal.getDouble("lat"),    natal.getDouble("lon"),    natal.getString("tz"),
                    year, month, day, hour, minute,
                    transitLat, transitLon, transitTz
                );

                JSObject out = new JSObject();
                out.put("aspects",      aspectsToJson(result.aspects));
                out.put("natal",        positionsToJson(result.natal));
                out.put("transits",     positionsToJson(result.transits));
                out.put("transit_date", result.transitDate);
                out.put("transit_time", result.transitTime);
                call.resolve(out);

            } catch (Exception e) {
                call.reject("CALC_ERROR", "Erreur calcul : " + e.getMessage(), e);
            }
        });
    }

    // ── Sérialiseurs JSON ─────────────────────────────────────────────────────

    private JSArray aspectsToJson(java.util.List<AstroEngine.AspectEntry> aspects) {
        JSArray arr = new JSArray();
        for (AstroEngine.AspectEntry a : aspects) {
            JSObject o = new JSObject();
            o.put("transit_planet",  a.transitPlanet);
            o.put("transit_display", a.transitDisplay);
            o.put("transit_nak",     a.transitNak);
            o.put("transit_pada",    a.transitPada);
            o.put("natal_planet",    a.natalPlanet);
            o.put("natal_display",   a.natalDisplay);
            o.put("natal_nak",       a.natalNak);
            o.put("aspect",          a.aspect);
            o.put("orb",             a.orb);
            o.put("retrograde",      a.retrograde);
            arr.put(o);
        }
        return arr;
    }

    private JSObject positionsToJson(Map<String, NakshatraCalc.PlanetPosition> positions) {
        JSObject out = new JSObject();
        for (Map.Entry<String, NakshatraCalc.PlanetPosition> e : positions.entrySet()) {
            NakshatraCalc.PlanetPosition p = e.getValue();
            if (p == null) continue;
            JSObject o = new JSObject();
            o.put("display",    p.display);
            o.put("retrograde", p.retrograde);
            o.put("nakshatra",  p.nakshatra);
            o.put("pada",       p.pada);
            o.put("nak_lord",   p.nakLord);
            o.put("lon_raw",    p.lon);
            o.put("d9",         divisionalToJson(p.d9));
            o.put("d10",        divisionalToJson(p.d10));
            o.put("d60",        divisionalToJson(p.d60));
            out.put(e.getKey(), o);
        }
        return out;
    }

    private JSObject divisionalToJson(NakshatraCalc.DivisionalResult d) {
        if (d == null) return new JSObject();
        JSObject o = new JSObject();
        o.put("sign",    d.sign);
        o.put("symbol",  d.symbol);
        o.put("display", d.symbol + " " + d.sign);
        o.put("part",    d.part);
        if (d.lord != null) o.put("lord", d.lord);
        return o;
    }
}
