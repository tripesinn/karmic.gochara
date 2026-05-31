import json
import astro_calc

natal = {
    "year": 1985, "month": 3, "day": 15, "hour": 14, "minute": 30,
    "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"
}
transit_loc = {"lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"}

results = []
for day in range(1, 366):
    month = 1
    d = day
    if day > 31: month = 2; d = day - 31
    if day > 59: month = 3; d = day - 59
    if day > 90: month = 4; d = day - 90
    if day > 120: month = 5; d = day - 120
    # rough enough just for testing
    if month > 12: month = 12
    if d > 28: d = 28
    
    try:
        res = astro_calc.calculate_transits(natal, transit_loc, 2026, month, d, 12, 0)
        results.append(res)
    except Exception as e:
        pass

payload = json.dumps(results)
print(f"Size of 365 days of transits: {len(payload) / 1024:.2f} KB")
