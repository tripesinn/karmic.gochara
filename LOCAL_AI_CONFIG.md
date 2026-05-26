# Documentation de l'Architecture Locale d'IA sur Mac

## Vue d'ensemble

Cette documentation détaille l'architecture locale d'IA mise en place sur un Mac, optimisée pour l'Apple Silicon. Elle inclut des informations sur le moteur d'inférence, le modèle utilisé, la configuration du serveur, l'exposition sur internet et l'intégration IDE.

## Moteur d'Inférence

- **Moteur** : `vllm-mlx`
- **Optimisé pour** : Apple Silicon

## Modèle Utilisé

- **Modèle** : `mlx-community/phi-4-4bit`

## Configuration du Serveur

- **Port d'écoute** : `8000`
- **Commande de lancement** :
  ```bash
  ~/.local/bin/vllm-mlx serve mlx-community/phi-4-4bit --prompt-cache-path ~/.cache/vllm-mlx-prompts.json
  ```

## Exposition sur Internet

- **Outil** : `ngrok`
- **Commande** :
  ```bash
  ngrok http 8000
  ```
- **Résultat** : Génère une URL publique, par exemple : `https://drinking-respect-research.ngrok-free.dev`

## Intégration IDE Antigravity

- **Création de la compétence** : `localV1`
- **Emplacement** : `~/.gemini/config/plugins/local-ai-plugin`
- **Script de pont** : `scripts/query_local_ai.py`

## Configuration Instantanée

Cette configuration permet à une IA d'assimiler toute la configuration instantanément au début d'un nouveau chat, éliminant le besoin de redondance ou de répétition dans les échanges.

```

Cette documentation fournit un aperçu clair et structuré de l'architecture locale d'IA, facilitant la compréhension et l'intégration rapide pour les utilisateurs et les développeurs.