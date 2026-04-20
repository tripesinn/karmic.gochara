# Skill: Configuration du Développement Local

Ce skill décrit comment installer et exécuter le projet en local pour le développement.

## Dépendances Système
- **Python 3.10+**
- **Node.js 18+** & **npm** (pour le frontend Capacitor)

## Installation Backend
1. **Créer un environnement virtuel** :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
   ```
2. **Installer les packages** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Fichiers DLL (Swiss Ephemeris)** :
   Assurez-vous que `swedll64.dll` est à la racine du projet pour les calculs astrologiques.

## Installation Frontend
```bash
npm install
```

## Exécution
1. **Lancer le backend Flask** :
   ```bash
   python app.py
   ```
   L'API sera disponible sur `http://localhost:5000`.

2. **Lancer le Web View (si applicable)** :
   Ouvrez `www/index.html` ou utilisez un serveur local (`npx serve www`).

## Variables .env
Copiez `.env.example` vers `.env` et remplissez :
- `ANTHROPIC_API_KEY` (optionnel pour les tests locaux sans Gemma).
- `SECRET_KEY` (pour les sessions Flask).
