#!/usr/bin/env python3
"""Check dependencies for x_benchmark_bot.py"""
import sys

print(f"Python: {sys.version}")

try:
    import pyswisseph as swe
    print("pyswisseph: OK")
except ImportError:
    print("pyswisseph: MISSING")

try:
    from datetime import UTC
    print("datetime.UTC: OK")
except ImportError:
    print("datetime.UTC: MISSING (need Python 3.11+)")

try:
    import openai
    print("openai: OK")
except ImportError:
    print("openai: MISSING")
