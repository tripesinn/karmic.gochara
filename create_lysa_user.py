from google.cloud import firestore

db = firestore.Client(project="karmic-gochara")

user_data = {
    "email": "lysa@karmic.dev",
    "name": "Lysa",
    "natal_chart": {
        "birth_date": "1994-08-15T09:15:00Z",
        "birth_place": "Lyon, France",
        "latitude": 45.7640,
        "longitude": 4.8357
    },
    "tokens": 50
}

db.collection("users").document("lysa@karmic.dev").set(user_data)
print("Lysa user created!")
