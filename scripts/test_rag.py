import sys

sys.path.append("/Users/jero87/karmic.gochara")
from rag_memory import retrieve_context, save_reading

print("Testing RAG memory...")

pseudo = "TestUser"

print("\nSaving readings...")
save_reading(pseudo, "L'utilisateur a une grande difficulté à lâcher prise sur le contrôle matériel (Saturne H2).", "synthesis", "2026-01-01")
save_reading(pseudo, "La blessure originelle de rejet est fortement activée par le transit de Mars.", "hook_transit", "2026-03-15")
save_reading(pseudo, "Rahu en Maison 10 demande de briller publiquement, mais la peur de l'échec bloque.", "hook_natal", "2026-05-01")

print("\nRetrieving context for query 'lâcher prise'...")
ctx = retrieve_context(pseudo, "difficulté à lâcher prise", limit=2)
print("\n--- Retrieved Context ---")
print(ctx)

print("\nRetrieving context for query 'public et carrière'...")
ctx2 = retrieve_context(pseudo, "public et carrière", limit=2)
print("\n--- Retrieved Context ---")
print(ctx2)
