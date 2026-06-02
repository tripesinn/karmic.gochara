"""
blueprints/geocode.py — Geocoding via Nominatim/Photon
"""
from flask import Blueprint, jsonify, request

import requests as req

geocode_bp = Blueprint("geocode_bp", __name__)


@geocode_bp.route("/geocode")
def geocode():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    try:
        r = req.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5},
            headers={"User-Agent": "Karmic.Gochara/1.0"},
            timeout=5,
        )
        return jsonify(r.json())
    except Exception:
        try:
            r2 = req.get(
                "https://photon.komoot.io/api/",
                params={"q": q, "limit": 5},
                headers={"User-Agent": "Karmic.Gochara/1.0"},
                timeout=5,
            )
            features = r2.json().get("features", [])
            results = []
            for f in features:
                p = f.get("properties", {})
                g = f.get("geometry", {}).get("coordinates", [None, None])
                results.append({
                    "display_name": f"{p.get('name','')}, {p.get('country','')}",
                    "lat": str(g[1]), "lon": str(g[0]),
                })
            return jsonify(results)
        except Exception as exc2:
            return jsonify({"error": str(exc2)}), 500
