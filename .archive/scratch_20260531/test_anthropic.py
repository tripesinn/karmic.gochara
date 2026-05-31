import os
import requests

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
url = "https://api.anthropic.com/v1/messages"
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 10,
    "system": "test",
    "messages": [{"role": "user", "content": "test"}],
}
print(f"Key present: {bool(api_key)}")
r = requests.post(url, headers=headers, json=payload)
print(r.status_code)
print(r.text)
