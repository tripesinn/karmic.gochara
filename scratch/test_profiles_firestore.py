import sys
import os

# Insert path to load local modules
sys.path.insert(0, '/Users/jero87/karmic.gochara')

from dotenv import load_dotenv
load_dotenv('/Users/jero87/karmic.gochara/.env')

import profiles

def run_tests():
    print("🧪 Démarrage des tests d'intégration Firestore...")
    
    # 1. Test get_profile_by_email
    email = "tripes.inn@gmail.com"
    print(f"🔍 Test get_profile_by_email for '{email}'...")
    p = profiles.get_profile_by_email(email)
    if p:
        print(f"✅ Profil trouvé ! Pseudo: {p.get('pseudo')}, Ville: {p.get('city')}")
    else:
        print("❌ Profil non trouvé via email !")
        sys.exit(1)
        
    # 2. Test get_profile_by_pseudo
    pseudo = p.get('pseudo')
    print(f"🔍 Test get_profile_by_pseudo for '{pseudo}'...")
    p2 = profiles.get_profile_by_pseudo(pseudo)
    if p2:
        print(f"✅ Profil trouvé ! Email: {p2.get('email')}")
    else:
        print("❌ Profil non trouvé via pseudo !")
        sys.exit(1)
        
    # 3. Test check_and_increment_synthesis
    print("🔄 Test check_and_increment_synthesis...")
    res = profiles.check_and_increment_synthesis(pseudo)
    print(f"✅ Quota checked: allowed={res.get('allowed')}, remaining={res.get('remaining')}")
    
    # 4. Test create and delete test profile
    test_data = {
        "pseudo": "test_agent_verify",
        "email": "verifyagent@example.com",
        "name": "Verify Agent",
        "year": 1985,
        "month": 5,
        "day": 12,
        "hour": 14,
        "minute": 30,
        "lat": 48.8566,
        "lon": 2.3522,
        "tz": "Europe/Paris",
        "city": "Paris"
    }
    
    print("➕ Test create_profile...")
    new_p = profiles.create_profile(test_data)
    print(f"✅ Profil créé ! Pseudo: {new_p.get('pseudo')}, Email: {new_p.get('email')}")
    
    print("❌ Test delete_profile...")
    success = profiles.delete_profile(new_p.get('pseudo'))
    if success:
        print("✅ Profil supprimé !")
    else:
        print("❌ Échec de la suppression du profil !")
        sys.exit(1)
        
    print("🎉 Tous les tests d'intégration Firestore ont réussi !")

if __name__ == '__main__':
    run_tests()
