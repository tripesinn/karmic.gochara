
import requests

key = ""
with open(".env") as f:
    for line in f:
        if line.startswith("GROK_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")

url = "https://api.x.ai/v1/models"
headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}
r = requests.get(url, headers=headers)
print(r.status_code)
for m in r.json().get("data", []):
    print(m["id"])
