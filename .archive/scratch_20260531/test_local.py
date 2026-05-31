import requests

try:
    print("Testing /expand locally...")
    res = requests.post("http://127.0.0.1:5000/expand", json={"pseudo": "tester_123", "topic": "alternative_conscience"})
    print(res.status_code)
except Exception as e:
    print(e)
