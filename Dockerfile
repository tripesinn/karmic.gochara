# Utiliser une image Python officielle légère
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires (ex: pour compiler certains paquets ou pour les fuseaux horaires)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port sur lequel l'application s'exécute (Cloud Run utilise 8080 par défaut)
EXPOSE 8080

# Commande pour démarrer l'application avec Gunicorn
# Cloud Run injecte la variable d'environnement PORT (par défaut 8080)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
