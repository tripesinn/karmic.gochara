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

## Erreurs Connues et Résolutions

### Erreur : Consciousness Alternative (aucun contenu)

**Description de l'Erreur**
L'erreur "Consciousness Alternative (aucun contenu)" se produit lorsque le projet `karmic.gochara` ne parvient pas à afficher ou à générer le contenu attendu. Cela est généralement dû à un fichier vide, à un chemin de fichier incorrect ou à un problème de configuration entraînant l'affichage de ce message d'erreur.

**Causes Potentielles**
- Fichier requis vide ou manquant
- Chemin de fichier incorrect dans la configuration
- Dépendances manquantes ou incompatibles
- Problème de génération de contenu

**Solutions**
1. **Vérification des Fichiers :** Assurez-vous que tous les fichiers requis sont présents et contiennent les données attendues. Vérifiez les chemins de fichier pour vous assurer qu'ils sont corrects.
2. **Vérification de la Configuration :** Examinez les fichiers de configuration pour vous assurer qu'ils sont correctement définis, y compris les chemins de fichier et les paramètres de liaison de données.
3. **Vérification des Dépendances :** Assurez-vous que toutes les dépendances requises sont installées et à jour en consultant la documentation du projet pour les versions spécifiques requises.
4. **Journalisation Détaillée :** Activez la journalisation détaillée pour obtenir plus de détails sur ce qui pourrait causer l'erreur.

### Erreur : Erreur de Routage API Local vers Gemini (404 Not Found)

**Description de l'Erreur**
Lors de l'utilisation du fournisseur local (phi-4 via ngrok), si l'API locale ne répond pas ou génère une erreur, l'application tentait de faire un "fallback" vers Gemini. Cependant, elle passait l'URL ngrok en tant que `api_key` et le modèle local (`mlx-community/phi-4-4bit`) à Gemini, provoquant une erreur `404 Not Found` sur l'URL `generativelanguage.googleapis.com`.

**Résolution**
Correction dans `ai_interpret.py` (fonction `generate_ai` et `stream_ai`) : lors du fallback vers Gemini après un échec du provider local, on efface désormais explicitement la variable `model` et `user_key` pour que Gemini utilise ses propres clés d'API serveur et son modèle par défaut. Nous avons également ajouté un `.strip()` pour nettoyer les espaces superflus dans l'URL ngrok saisie par l'utilisateur.

## Roadmap (Noël 2026)

- **Mémoire Karmique Persistante (RAG)** : Implémenter un système de mémoire à long terme (Retrieval-Augmented Generation) exclusif à Gochara Pro avec l'IA locale. L'application indexera toutes les lectures passées de l'utilisateur (hooks, synthèses, alternatives de conscience, conversations du chatbot). Lors d'une nouvelle génération, l'IA locale lira cet historique pour offrir une analyse évolutive et connectée aux événements passés, agissant comme un véritable accompagnateur spirituel de long terme.

## Objectif

Ce fichier sert de "point de sauvegarde" pour permettre à une IA de reprendre le développement facilement. Le projet vise à fournir une solution d'intégration IA robuste et facilement déployable. L'accent sera mis sur l'amélioration de l'expérience utilisateur, l'optimisation des performances et l'expansion des fonctionnalités pour répondre aux besoins des utilisateurs finaux.