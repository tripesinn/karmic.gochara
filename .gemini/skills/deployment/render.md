# Skill: Déploiement sur Render

Ce skill décrit les étapes pour déployer le backend Flask de Gochara Karmique sur la plateforme Render.

## Prérequis
- Compte GitHub avec le dépôt du projet.
- Compte Render (plan gratuit possible).
- Une clé API Anthropic (si l'interprétation cloud est activée).

## Configuration Render
1. **New → Web Service**.
2. Connecter le dépôt GitHub.
3. Paramètres détectés via `render.yaml` :
   - **Environment** : `Python`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

## Variables d'Environnement
Ajouter dans l'onglet **Environment** de Render :
- `ANTHROPIC_API_KEY` : Votre clé `sk-ant-...`
- `PORT` : 5000 (standard Render).

## Notes sur le Plan Gratuit
- **Démarrage à froid** : L'application s'endort après 15 minutes d'inactivité. Le premier accès peut prendre ~30 secondes.
- **Fichiers éphémères** : Toute écriture sur le disque local est perdue au redémarrage. Les fichiers `.task` générés à la volée ne sont pas affectés car ils sont servis en flux (streaming).

## Fichiers critiques pour le déploiement
- `render.yaml` : Configuration infrastructure-as-code.
- `requirements.txt` : Liste des dépendances Python.
- `Procfile.txt` : Instruction pour les serveurs de process (Heroku/Render).
