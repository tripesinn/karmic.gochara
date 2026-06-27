import sys
import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

# Insert path to load local modules
sys.path.insert(0, '/Users/jero87/karmic.gochara')

from dotenv import load_dotenv
load_dotenv('/Users/jero87/karmic.gochara/.env')

from profiles import get_all_profiles

def main():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        print("❌ GOOGLE_CREDENTIALS_JSON manquant dans l'environnement.")
        sys.exit(1)

    # Initialize Firestore client using Application Default Credentials (ADC)
    db = firestore.Client(project='karmic-gochara-cloud')

    
    print("📋 Récupération des profils depuis Google Sheets...")
    try:
        profiles = get_all_profiles()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de Google Sheets : {e}")
        sys.exit(1)
        
    print(f"✅ {len(profiles)} profils récupérés.")
    
    print("📤 Importation vers Firestore (collection 'users')...")
    batch = db.batch()
    count = 0
    for p in profiles:
        email = p.get("email")
        if not email:
            print(f"⚠️  Profil sans email ignoré : {p.get('pseudo')}")
            continue
            
        email_clean = email.strip().lower()
        doc_ref = db.collection("users").document(email_clean)
        
        # Firestore doesn't like None/empty keys or complex types in raw form sometimes,
        # but our profiles dict is flat with strings, ints, floats.
        # Let's ensure types are clean.
        cleaned_profile = {}
        for k, v in p.items():
            if v is None:
                cleaned_profile[k] = ""
            else:
                cleaned_profile[k] = v
                
        batch.set(doc_ref, cleaned_profile)
        count += 1
        
        # Commit in batches of 400
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
            print(f"   {count} profils importés...")
            
    if count % 400 != 0:
        batch.commit()
        
    print(f"🎉 Migration terminée avec succès ! {count} profils importés dans Firestore.")

if __name__ == '__main__':
    main()
