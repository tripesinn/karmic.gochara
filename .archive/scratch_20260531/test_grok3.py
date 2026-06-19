import os

import requests

api_key = os.environ.get("SERVER_GROK_KEY", "")
url = "https://api.x.ai/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
r = requests.get(url, headers=headers)
print(r.status_code)
print(r.text)
