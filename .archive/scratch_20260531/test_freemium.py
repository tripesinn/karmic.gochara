import random

import requests

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

pseudo = f"tester_{random.randint(10000,99999)}"
print(f"Registering/Logging in pseudo: {pseudo}")
res = session.post(f"{BASE_URL}/register", json={
    "pseudo": pseudo,
    "birth_date": "1990-01-01T12:00",
    "birth_place": "Paris, France",
    "lat": 48.8566,
    "lng": 2.3522
})
print(f"Login status: {res.status_code}")

if res.status_code == 200:
    print("\nCalling /hook/transit...")
    res_hook = session.post(f"{BASE_URL}/hook/transit", json={
        "date": "2026-05-25",
        "hour": 12,
        "minute": 0,
        "transit_city": "Paris, France",
        "transit_lat": 48.8566,
        "transit_lon": 2.3522,
        "transit_tz": "Europe/Paris"
    }, stream=True)
    print(f"Hook Transit Status: {res_hook.status_code}")
    for line in res_hook.iter_lines():
        if line:
            print(line.decode('utf-8'))
