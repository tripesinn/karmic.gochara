from profiles import create_profile, check_and_consume_daily_signal
import random

pseudo = f"tester_{random.randint(10000,99999)}"
data = {
    "pseudo": pseudo,
    "email": f"{pseudo}@test.com",
    "name": pseudo,
    "year": 1990,
    "month": 1,
    "day": 1,
    "hour": 12,
    "minute": 0,
    "lat": 48.8566,
    "lon": 2.3522
}
print("Creating profile...")
prof = create_profile(data)
print("Profile created!")

print("Checking daily signal...")
res = check_and_consume_daily_signal(pseudo)
print(f"Result: {res}")
