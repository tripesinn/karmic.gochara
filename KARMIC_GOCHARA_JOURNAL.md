# Journal de Projet : karmicgochara.app

## État Actuel

Le projet Karmic Gochara a franchi un cap majeur concernant l'équilibre de son modèle économique et la simplicité de son expérience utilisateur. L'application distingue désormais de manière étanche et automatique les profils **PRO** et **Freemium**, avec un routage IA adapté (Edge IA locale pour le Pro, Grok pour le Free) et un système robuste de quotas quotidiens géré par Google Sheets. Le suivi des modèles de l'API Grok est maintenant entièrement autonome pour éviter toute interruption de service lors des dépréciations de x.ai. De plus, la page Freemium a été allégée et calquée sur le visuel épuré et mystique de "KarmicAstro X-bot", tandis que la Carte Karmique interactive avec interprétation IA en un clic a été intégrée comme une exclusivité majeure de l'offre PRO.

## Hébergement

- **Google Cloud Run** : Déploiement réussi dans la région `europe-west1` (Belgique).
- **Mappage de nom de domaine** : `karmicgochara.app` mappé vers le service `gochara-api` in the region `europe-west1`.

## Stack Technique

- **Google Cloud Build** : Déploiement continu automatisé.
- **Docker** : Utilisation d'un Dockerfile optimisé pour corriger le build et assurer la légèreté de l'image.
- **Base de données Google Sheets** : Stockage persistant des profils utilisateurs, maintenant doté d'une colonne de suivi temporel (`last_signal_date`) pour les quotas.
- **Routage Multi-IA** :
  - **PRO** : Serveur local / Edge IA via vLLM (`mlx-community/phi-4-4bit`).
  - **Freemium** : API Grok (propulsée par la clé serveur du créateur de l'application) offrant un ton "X-bot" mystique et percutant.
- **Interface Web** : Clean-up complet éliminant les sélecteurs techniques complexes pour les utilisateurs gratuits afin de maximiser l'immersion.

## Ajouts Récents

1. **Étanchéité Économique Freemium vs PRO** :
   - Suppression de l'affichage et de la sélection manuelle des modèles pour les comptes gratuits. Le routage est 100% automatique en fonction du plan de l'utilisateur défini dans Google Sheets.
   - Les utilisateurs PRO bénéficient d'un accès illimité à l'IA locale (Edge IA).
   - Les utilisateurs Freemium sont cantonnés à l'IA Grok (X-bot style) sans avoir à fournir de clé d'API personnelle, celle-ci étant débitée directement sur l'API serveur globale.

2. **Limitation du Freemium (1 Signal/jour)** :
   - Mise en place d'un quota de **1 Daily Signal par jour** pour les comptes gratuits.
   - Le système stocke désormais la date du dernier signal généré au format `YYYY-MM-DD` dans la colonne `last_signal_date` de Google Sheets.
   - Toute tentative de génération de signal supplémentaire le même jour renvoie un avertissement clair et bloque la requête.

3. **Design Épuré Freemium (Style X-bot)** :
   - Masquage automatique de la barre d'onglets pour les utilisateurs Freemium (l'onglet "Carte Karmique" n'est plus visible ni accessible dans le DOM).
   - Suppression complète de la section "Outils supplémentaires" et des alertes par email ("🔔 Transit alerts by email") pour les utilisateurs gratuits afin d'alléger l'interface et d'éliminer les messages d'erreur.
   - Refonte visuelle de l'encart du Signal du Jour (`#hook-transit-box`) en une somptueuse carte noire en suspension (fond glassmorphic sombre, bordure supérieure dorée, typographie serif "Georgia" très premium), rappelant fidèlement l'esthétique mystique du bot original.

4. **Exclusivité PRO : Carte Karmique Interactive (Doctrine)** :
   - Ajout de la "Carte Karmique (Doctrine)" dans le tableau public "Access & Plans" (Gratuit : `—` / PRO : `✓`).
   - Pour les membres PRO, la Carte Karmique est désormais cliquable. Un clic sur l'image de la carte déclenche une route API dédiée `/chart/interpret` qui analyse les coordonnées natales de l'utilisateur (Ketu/Rahu, Porte Invisible, Chiron/Porte Visible, Jupiter, Saturne).
   - L'interprétation, rédigée par l'IA siderealAstro13 avec un ton noble, profond et oraculaire, est instantanément affichée sous la carte avec un formatage Markdown élégant.

5. **Exclusivité PRO : Mémoire Karmique Persistante (RAG - Edge IA local)** :
   - Intégration complète d'une mémoire vectorielle locale avec `ChromaDB` et `SentenceTransformers` (`all-MiniLM-L6-v2`) via `rag_memory.py`.
   - L'application sauvegarde de manière asynchrone (threads séparés) toutes les lectures passées de l'utilisateur (natal, transits, synthèses, chat).
   - Lors de chaque nouvelle génération pour un utilisateur PRO, le contexte est enrichi avec son historique de lectures pour éviter la répétition et garantir un accompagnement spirituel de long terme.
   - Le module est automatiquement désactivé sur Google Cloud Run (`IS_CLOUD = True`) pour préserver les performances en production et gérer l'absence de persistance disque.

6. **Suivi des Modèles Grok Auto-géré ("Self-Healing")** :
   - Implémentation d'une fonction d'auto-découverte dans `ai_interpret.py` : l'application interroge dynamiquement `https://api.x.ai/v1/models`.
   - Filtrage automatique des modèles indésirables (image-generation, build agents, et modèles de pur raisonnement trop lents/coûteux) pour ne garder que les modèles de texte rapides et qualitatifs.
   - Tri par versioning mathématique pour élire automatiquement le modèle le plus moderne et récent (ex: bascule automatique sur `grok-4.20-0309-non-reasoning` au lieu de `grok-4.3`).
   - Cache mémoire de 12 heures pour éliminer tout impact de latence réseau, et fallback automatique ultra-sécurisé sur `grok-4.3` en cas de coupure de l'API x.ai.

## Erreurs Connues et Résolutions

### Erreur : Crash API Grok 400 (dépréciation de `grok-beta`)
* **Description :** L'ancien modèle de génération freemium `grok-beta` a été définitivement supprimé par x.ai, ce qui provoquait une erreur 400 globale empêchant l'accueil de charger pour les utilisateurs gratuits.
* **Résolution :** Résolu définitivement grâce à la fonction de recherche dynamique auto-gérée (`_get_grok_model()`) et de fallback sécurisé.

### Erreur : Écran de chargement infini pour les nouveaux profils (Délai d'API Sheets)
* **Description :** Lors de la création d'un nouveau profil sur l'application, l'API Google Sheets met parfois quelques secondes à propager l'écriture d'une nouvelle ligne. L'appel immédiat de `/hook/transit` qui suivait ne retrouvait pas encore l'utilisateur dans l'onglet des profils et bloquait la génération sur une roue infinie.
* **Résolution :** Ajout d'une tolérance intelligente dans `check_and_consume_daily_signal`. Si l'utilisateur est introuvable mais vient manifestement de s'enregistrer, le système l'autorise gracieusement à obtenir son tout premier signal quotidien de bienvenue sans bloquer son parcours.

## Roadmap (Noël 2026)

- **Optimisation des performances et Multi-Profils** : Préparation de l'intégration de profils secondaires illimités pour les utilisateurs PRO et transition éventuelle de Google Sheets vers Supabase ou Firebase pour supporter la charge à grande échelle.

## Objectif

Ce fichier sert de "point de sauvegarde" pour permettre à une IA de reprendre le développement facilement. Le projet vise à fournir une solution d'intégration IA robuste et facilement déployable. L'accent sera mis sur l'amélioration de l'expérience utilisateur, l'optimisation des performances et l'expansion des fonctionnalités pour répondre aux besoins des utilisateurs finaux.