"""
blueprints/geocode.py — Geocoding via Nominatim/Photon + Timezone lookup
"""
import requests as req
from flask import Blueprint, jsonify, request
from timezonefinder import TimezoneFinder

geocode_bp = Blueprint("geocode_bp", __name__)
tf = TimezoneFinder()


@geocode_bp.route("/geocode")
def geocode():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])

    results = []
    try:
        # 1. Tentative Nominatim
        r = req.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5},
            headers={"User-Agent": "Karmic.Gochara/1.0"},
            timeout=5,
        )
        if r.status_code == 200:
            for item in r.json():
                lat = float(item["lat"])
                lon = float(item["lon"])
                results.append({
                    "display_name": item["display_name"],
                    "lat": str(lat),
                    "lon": str(lon),
                    "tz": tf.timezone_at(lng=lon, lat=lat) or "UTC"
                })
            return jsonify(results)
    except Exception:
        pass

    # 2. Fallback Photon
    try:
        r2 = req.get(
            "https://photon.komoot.io/api/",
            params={"q": q, "limit": 5},
            headers={"User-Agent": "Karmic.Gochara/1.0"},
            timeout=5,
        )
        features = r2.json().get("features", [])
        for f in features:
            p = f.get("properties", {})
            g = f.get("geometry", {}).get("coordinates", [None, None])
            if g[0] is not None:
                lat = float(g[1])
                lon = float(g[0])
                results.append({
                    "display_name": f"{p.get('name','')}, {p.get('country','')}",
                    "lat": str(lat),
                    "lon": str(lon),
                    "tz": tf.timezone_at(lng=lon, lat=lat) or "UTC"
                })
        return jsonify(results)
    except Exception as exc2:
        return jsonify({"error": str(exc2)}), 500
