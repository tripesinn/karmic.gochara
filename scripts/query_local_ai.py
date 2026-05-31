import sys

import requests


def query_local_ai(prompt):
    url = "http://127.0.0.1:8000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy"
    }
    
    payload = {
        "model": "Qwen3.5-9B-MLX-4bit",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 2048
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        print(content)
    except Exception as e:
        print(f"Error querying local AI: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_local_ai.py \"<prompt>\"", file=sys.stderr)
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    query_local_ai(user_prompt)
