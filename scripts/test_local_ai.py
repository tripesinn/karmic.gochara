import sys
import os

sys.path.append("/Users/jero87/karmic.gochara")
from ai_interpret import generate_ai

system = "Tu es un test."
prompt = "Réponds avec le mot TEST."
user = {"user_provider": "local"}

try:
    res = generate_ai(system, prompt, user)
    print("Result:", res)
except Exception as e:
    print("Exception:", e)
