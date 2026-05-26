import sys
import os
sys.path.append('.')
from ai_interpret import generate_ai

system = "Test system"
prompt = "Test prompt"

tests = [
    {"user_provider": "local", "user_key": "dummy", "user_model": "test-local-model"},
    {"user_provider": "groq", "user_key": "dummy-key", "user_model": "test-groq-model"},
    {"user_provider": "gemini", "user_key": "dummy-key", "user_model": "test-gemini-model"}
]

for t in tests:
    print(f"Testing {t['user_provider']}...")
    try:
        generate_ai(system, prompt, user=t, max_tokens=10)
    except Exception as e:
        print(f"Exception for {t['user_provider']}: {type(e).__name__}: {e}")

