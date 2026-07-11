#!/usr/bin/env python3
"""
Bot X.com (Twitter) Interactif pour Gochara Karmique
Utilise l'API Grok (xAI) et répond aux mentions.
Format attendu: @BotHandle MM/DD/YYYY HH:MM Ville
"""

import datetime
import os
import re
import sys
import time

import tweepy
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from openai import OpenAI
from timezonefinder import TimezoneFinder

# Importer la logique existante
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astro_calc import calculate_transits
from karmic_lite import TRANSIT_LOC, generate_prompt

# Charger les variables d'environnement
load_dotenv()

# Configuration
XAI_API_KEY = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

LAST_SEEN_FILE = "last_seen_id.txt"

def setup_x_client():
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("❌ Erreur : Clés d'API X.com manquantes.")
        sys.exit(1)
        
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    
    # Tester l'authentification
    me = client.get_me()
    print(f"✓ Connecté à X.com en tant que @{me.data.username}")
    return client, me.data.id

def get_last_seen_id():
    if os.path.exists(LAST_SEEN_FILE):
        with open(LAST_SEEN_FILE) as f:
            content = f.read().strip()
            if content.isdigit():
                return content
    return None

def save_last_seen_id(tweet_id):
    with open(LAST_SEEN_FILE, 'w') as f:
        f.write(str(tweet_id))

def parse_user_request(text):
    """
    Extrait les données natales depuis le format: 
    @Handle MM/DD/YYYY HH:MM City
    """
    # Pattern US Date: MM/DD/YYYY HH:MM City
    pattern = r"(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+(?P<city>.+)"
    match = re.search(pattern, text)
    
    if not match:
        return None
        
    data = match.groupdict()
    
    # Conversion types
    try:
        month = int(data['month'])
        day = int(data['day'])
        year = int(data['year'])
        hour = int(data['hour'])
        minute = int(data['minute'])
        city = data['city'].strip()
        
        # Validations basiques
        if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2026):
            return None
            
        return {
            "month": month,
            "day": day,
            "year": year,
            "hour": hour,
            "minute": minute,
            "location": city
        }
    except ValueError:
        return None

def geocode_location(city):
    """Trouve la latitude, longitude et le fuseau horaire d'une ville."""
    geolocator = Nominatim(user_agent="karmic_gochara_bot")
    tf = TimezoneFinder()
    
    location = geolocator.geocode(city)
    if location:
        lat = location.latitude
        lon = location.longitude
        tz = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        return lat, lon, tz
    return None, None, None

def generate_karmic_data(user_data):
    """Calcule les transits pour l'utilisateur spécifique."""
    lat, lon, tz = geocode_location(user_data["location"])
    
    if not lat:
        raise ValueError(f"Ville introuvable : {user_data['location']}")
        
    natal_info = {
        "year": user_data["year"],
        "month": user_data["month"],
        "day": user_data["day"],
        "hour": user_data["hour"],
        "minute": user_data["minute"],
        "location": user_data["location"],
        "lat": lat,
        "lon": lon,
        "tz": tz
    }
    
    now = datetime.datetime.now()
    data = calculate_transits(
        natal_info, TRANSIT_LOC,
        now.year, now.month, now.day,
        now.hour, now.minute
    )
    return generate_prompt(data, natal_info=natal_info)

def call_grok(prompt):
    """Envoie le prompt à Grok pour générer le fil de discussion."""
    if not XAI_API_KEY:
        print("❌ Erreur : Clé XAI_API_KEY manquante.")
        sys.exit(1)
        
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )
    
    system_instruction = """
Tu es un astrologue karmique brut et direct sur X (Twitter), expert en "Doctrine Évolutive". Ton but est de forcer l'évolution de l'âme de la personne.
RÈGLE ABSOLUE : Tu dois baser ton analyse UNIQUEMENT sur l'aspect fourni dont l'orbe est le plus proche de 0.00°. Ignore le reste.
Tes prédictions s'adressent au grand public (PAS de jargon astrologique : interdit de parler de "conjonction", de "degrés", ou du nom des planètes).
Traduite l'énergie de cet aspect précis en un avertissement psychologique tranchant, sans concession, mais orienté vers l'évolution et la libération.
Interdiction absolue d'utiliser des termes "horoscope" ou vagues. 
Tes réponses font moins de 250 caractères.

Format obligatoire :
🎯 Le Mur: [Quel est le schéma destructeur qui bloque l'évolution de son âme aujourd'hui ?].
⚡ L'Éveil: [L'action courageuse et radicale à faire dans les 24h pour se libérer et grandir].
⏳ L'Ouverture: [Date. Pourquoi c'est EXACTEMENT le moment de saisir cette opportunité d'évolution].
"""
    
    response = client.chat.completions.create(
        model="grok-4.3",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        max_tokens=800,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def send_dm(client, text, participant_id):
    """Envoie la réponse en Message Privé (DM) à l'utilisateur."""
    # Les DMs peuvent contenir jusqu'à 10 000 caractères, pas besoin de les couper.
    client.create_direct_message(participant_id=participant_id, text=text)

def process_mentions(client, my_user_id):
    """Vérifie les nouvelles mentions et y répond."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Vérification des mentions...")
    
    last_id = get_last_seen_id()
    
    try:
        # Récupérer les mentions
        mentions = client.get_users_mentions(
            id=my_user_id, 
            since_id=last_id,
            tweet_fields=['author_id', 'created_at'],
            user_auth=True
        )
        
        if not mentions.data:
            return
            
        # Mettre à jour le last_id avec le plus récent
        new_last_id = mentions.data[0].id
        
        for mention in reversed(mentions.data):
            # Traiter de la plus ancienne à la plus récente
            print(f"\n📩 Nouvelle mention de l'utilisateur {mention.author_id}: {mention.text}")
            
            user_data = parse_user_request(mention.text)
            
            if user_data:
                print(f"  ✓ Format valide détecté : {user_data}")
                try:
                    prompt = generate_karmic_data(user_data)
                    print("  ✓ Thème calculé, appel à Grok...")
                    ai_response = call_grok(prompt)
                    send_dm(client, ai_response, mention.author_id)
                    
                    # Tweet public pour le référencement (SEO Twitter)
                    public_reply = "Votre diagnostic karmique vient de vous être envoyé en message privé ! 🌌✨\n\n#GocharaKarmique #AstrologieKarmique #Astrologie"
                    client.create_tweet(text=public_reply, in_reply_to_tweet_id=mention.id)
                    
                    print("  ✓ DM envoyé et réponse publique publiée !")
                except Exception as e:
                    print(f"  ❌ Erreur lors du traitement : {e}")
                    # Optionnel: Répondre à l'utilisateur qu'il y a eu une erreur (ex: ville non trouvée)
                    error_msg = "Désolé, une erreur est survenue lors du calcul de votre carte karmique. Assurez-vous que la ville est bien orthographiée."
                    client.create_tweet(text=error_msg, in_reply_to_tweet_id=mention.id)
            else:
                print("  ! Format invalide ignoré.")
                
        save_last_seen_id(new_last_id)
        
    except tweepy.errors.TooManyRequests:
        print("⚠️ Rate limit atteint. Attente nécessaire.")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des mentions : {e}")

def main():
    print("=== Démarrage du Bot Interactif X.com (Grok) Karmic Lite ===")
    
    client, my_user_id = setup_x_client()
    
    print("\nÉcoute en cours... (Appuyez sur Ctrl+C pour arrêter)")
    
    try:
        while True:
            process_mentions(client, my_user_id)
            # Attendre 2 minutes entre chaque vérification pour ne pas épuiser l'API
            time.sleep(120)
    except KeyboardInterrupt:
        print("\nArrêt du bot.")

if __name__ == "__main__":
    main()
