import time
from app import app
from flask import json

with app.test_request_context('/api/prefetch_year', method='POST', json={"year": 2026, "transit_loc": {"lat": 48.8, "lon": 2.3, "tz": "Europe/Paris"}}):
    from flask import session
    session["profile"] = {"name": "Test", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0, "lat": 48.8, "lon": 2.3, "tz": "Europe/Paris", "city": "Paris", "lang": "fr"}
    start = time.time()
    res = app.full_dispatch_request()
    end = time.time()
    print(f"Status: {res.status_code}")
    print(f"Time taken: {end - start:.2f} seconds")
