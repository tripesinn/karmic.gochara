import requests

try:
    print("Testing /synthesis/prompt locally...")
    # This must fail due to 401 Unauthorized if no session profile
    res = requests.post("http://127.0.0.1:5000/synthesis/prompt", json={"context": "hook_transit", "date": "2026-05-25"})
    print(res.status_code)
except Exception as e:
    print(e)
