import os

import requests

api_key = os.environ.get("SERVER_GROK_KEY", "")
print("KEY length:", len(api_key))

url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = {
    "model": "grok-beta",
    "max_tokens": 1024,
    "messages": [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Hello"}
    ],
}
print("Requesting...")
r = requests.post(url, headers=headers, json=payload)
print(r.status_code)
print(r.text)
