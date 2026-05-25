# Journal de Projet : karmicgochara.app

## État Actuel

Le projet Karmic Gochara a atteint plusieurs jalons importants récemment. Le déploiement continu a été réussi sur Google Cloud Run, et l'intégration de l'IA locale a été complétée avec succès. Les problèmes de cache ont été résolus, et le mappage du nom de domaine a été effectué. Le projet est maintenant prêt pour une utilisation plus large et des tests supplémentaires.

## Hébergement

- **Google Cloud Run** : Déploiement réussi dans la région `europe-west1` (Belgique).
- **Mappage de nom de domaine** : `karmicgochara.app` mappé vers le service `gochara-api` dans la région `europe-west1`.

## Stack Technique

- **Google Cloud Build** : Utilisé pour le déploiement continu.
- **Docker** : Un Dockerfile propre a été ajouté sur GitHub pour corriger le build.
- **Cloudflare** : Purge de cache pour résoudre les problèmes bloquant le chargement de `style.css`.
- **Intégration IA** : vLLM avec `mlx-community/phi-4-4bit` intégré pour l'IA locale.
- **Interface Web** : Utilisation de `templates/index.html` et `static/app.js` pour gérer les requêtes vers le serveur local.

## Ajouts Récents

1. **Déploiement Continu** : Déploiement réussi sur Google Cloud Run via Cloud Build dans la région `europe-west1` (Belgique). Un Dockerfile propre a été ajouté sur GitHub pour corriger le build.

2. **Mappage de Nom de Domaine** : Le nom de domaine personnalisé `karmicgochara.app` a été mappé vers le service `gochara-api` en `europe-west1`.

3. **Problèmes de Cache** : Résolution des problèmes de cache Cloudflare (purge) qui bloquaient le chargement de `style.css`.

4. **Intégration IA Locale** : L'intégration complète et réussie de l'IA locale (vLLM avec `mlx-community/phi-4-4bit`) a été réalisée. L'interface web envoie bien les requêtes au serveur local de l'utilisateur lorsque le fournisseur 'Serveur Local' est sélectionné, avec un indicateur 'œil' 👁️ pour afficher/masquer l'URL. Le modèle génère les réponses (environ 8 tokens/s) sans erreur CORS.

## Objectif

Ce fichier sert de "point de sauvegarde" pour permettre à une IA de reprendre le développement facilement. Le projet vise à fournir une solution d'intégration IA robuste et facilement déployable. L'accent sera mis sur l'amélioration de l'expérience utilisateur, l'optimisation des performances et l'expansion des fonctionnalités pour répondre aux besoins des utilisateurs finaux.