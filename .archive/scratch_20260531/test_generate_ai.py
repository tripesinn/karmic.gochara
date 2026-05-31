import sys
import os
sys.path.append('.')
from ai_interpret import generate_ai
user = {"plan": "free"}
res = generate_ai("hello", "hello", user)
print(f"Result: {repr(res)}")
