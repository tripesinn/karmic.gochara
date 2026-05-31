import sys

sys.path.append("/Users/jero87/karmic.gochara")
from ai_interpret import generate_ai

name = "TestUser"
natal_ctx = "Chandra Lagna H1: Aries\nKetu H4\nRahu H10"

system = (
    "Tu es @siderealAstro13. Lecteur d'âme karmique védique. "
    "Style : chirurgical, dense, percutant. Tutoiement. "
    "INTERDIT ABSOLU : noms de signes zodiacaux. "
    "Utilise uniquement maisons (H1, H3…) et noms de planètes."
)
prompt = (
    f"Thème natal de {name} :\n{natal_ctx}\n\n"
    f"En 100 mots maximum, révèle L'Alternative de Conscience de {name}.\n"
    f"C'est l'insight transformateur central — le pivot entre la prison "
    f"de la Porte Invisible et la libération de la Porte Visible.\n"
    f"Sois chirurgical, personnel, percutant.\n"
    f"Aucun lien. Aucun titre. Texte seul."
)
user_params = {"user_provider": "local", "user_key": None, "user_model": None}

try:
    content = generate_ai(system, prompt, user=user_params, max_tokens=1024)
    print("Content:", content)
    print("Length:", len(content))
except Exception as e:
    print("Exception:", e)
