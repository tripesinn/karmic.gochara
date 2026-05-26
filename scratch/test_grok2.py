import os
import requests
import json

api_key = os.environ.get("SERVER_GROK_KEY", "")
url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = {
    "model": "grok-2-latest",
    "max_tokens": 100,
    "messages": [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Hello"}
    ],
}
r = requests.post(url, headers=headers, json=payload)
print(r.status_code)
print(r.text)
