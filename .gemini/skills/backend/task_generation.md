# Skill: Génération des fichiers .task

Ce skill décrit le processus de génération des fichiers `.task` utilisés pour l'inférence locale avec Gemma 3 sur Android.

## Rôle du fichier .task
Le fichier `.task` est un JSON exporté par le backend qui contient :
1. **gemma_system_prompt** : Le système prompt compressé (doctrine + contexte natal + transit).
2. **gemma_payload** : Les données factuelles de l'utilisateur.
3. **fingerprint** : Pour la gestion du cache.

## Script Principal : `build_task_file.py`
Ce script est le coeur de la transformation des données astrologiques brutes en instructions actionnables par l'IA.

### Fonctions clés
- `build_task_file(user, natal_data, transit_data)` : Assemble le JSON final.
- `build_gemma_system_prompt()` : Compile les briques doctrinales selon le transit actif.
- `extract_natal_for_task()` : Mappe les sorties de `astro_calc.py` vers le format attendu.
- `extract_dominant_transit()` : Priorise le transit le plus impactant (planètes lentes > orbe faible).

## Flux de données
1. L'utilisateur demande `/generate_task`.
2. Le backend calcule le thème natal et les transits via `astro_calc.py`.
3. `build_task_file.py` récupère ces données et injecte les fragments de doctrine correspondants (Nakshatras, Houses, Planet Keywords).
4. Un fichier JSON est envoyé au client Capacitor.

## Mise à jour de la doctrine
Toute modification des mots-clés ou des règles de sortie doit être faite dans `build_task_file.py` (variables `VAULT_CORE`, `VAULT_RULES`, `PLANET_KEYWORDS`, etc.) pour être répercutée sur Android.

> [!NOTE]
> Le budget de jetons (tokens) visé pour le system prompt est de **450-550 tokens** pour rester efficace sur Gemma 1B.
