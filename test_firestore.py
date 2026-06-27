import sys
import os
sys.path.append(os.getcwd())
from profiles import get_profile_by_pseudo
try:
    p = get_profile_by_pseudo("TestUser")
    print(p.get("tz"))
except Exception as e:
    print(f"Error: {e}")
