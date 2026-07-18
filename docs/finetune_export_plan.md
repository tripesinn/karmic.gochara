# Karmic Gochara — Fine-tune : format d'artefact & archi (à valider avec @siderealAstro13 / profil astro)

**Date** : 2026-07-18 | **Profil** : karmic_gochara (routing/déploiement/serveur)
**Contexte** : le modèle de référence = Pixel (gemma-4-E2B-it.litertlm), pas le proxy MLX Mac.

## 1. DÉCISION ARCHI (contrainte technique dure)

`litertlm-android:latest.release` (= 0.14.0) **n'expose PAS d'API LoRA runtime**.
Preuve : issue LiteRT-LM #1188 (feature request) + PR #2508 (juin 2026) NON incluse dans la
release publique. Le plugin utilise `litertlm-android:latest.release` → **runtime LoRA impossible
aujourd'hui sur le Pixel**.

Conséquence sur le livrable (c) :
- ❌ LoRA adapter `.bin` chargé à l'inférence (LORA_ASSET_PATH du plugin = mort-né, `sLoraLoaded`
     reste `false` partout).
- ✅ **Artefact valide = `.litertlm` PRÉ-MERGÉ** (LoRA fusionné dans le base Gemma-4-E2B OFFLINE
     via l'outil Google AI Edge `litert-model-cpp`), qui **remplace le modèle de base** sur le
     device. Aucun changement de code de chargement : le plugin charge le merged `.litertlm`
     exactement comme le base actuel (backend CPU, `isValidModel` par taille+sha256).

## 2. PIPELINE (scripts/finetune_kg.py)

- `filter`  ✅ EXÉCUTÉ (macOS 3.9.6) → `dataset_train_clean.jsonl` : 44 lignes messages complets
  conservées, 1 ligne rating ignorée.
- `train`   ⏸ guardé (requiert GPU box + torch/peft/unsloth). LoRA PEFT r=16 sur Gemma-4-E2B.
- `merge`   ⏸ guardé (requiert litert-model-cpp). Bake LoRA -> `.litertlm`.
- `deploy`  ⏸ guardé : push merged `.litertlm` + **MAJ OBLIGATOIRE** EXPECTED_MODEL_SHA256/SIZE
  dans GemmaSynthesisPlugin (sinon isValidModel rejette silencieusement le merged model).

## 3. ACTION REQUISE profil astro

Valider l'export avant finalisation :
1. Le merged `.litertlm` garde-t-il la VOIX/DOCTRINE du prompt système actuel (qui vit côté app
   via DoctrinePromptBuilder, pas dans le poids) ? → Si oui, le fine-tune ne fait que renforcer
   le style ; le prompt système reste le filet éditorial (single-source astro).
2. Format dataset : `finetune_kg.py filter` ne garde QUE {messages:[system,user,assistant]} ;
   les lignes {user_id,rating,soul_debug} sont exclues (elles ne sont pas du training supervisé).
   OK pour astro ?
3. Taille cible du merged model : si > 2.58GB, le checker doit être mis à jour (voir §2 deploy).

## 4. ROUTING / ENDPOINT (livrés a+b+d)

- `LlmServer` (ServerSocket 127.0.0.1:8099 — 8088 évité : occupé par proxy pipelock Mac).
  Endpoints : POST /v1/generate, GET /capture, GET /healthz.
- Réutilise EXACTEMENT le moteur de `generate()` (CPU, timeout 180s).
- Capture server-side → `llm_server_capture.jsonl` (ExternalFilesDir), aligné dataset.
- Hook app `captureGeneration()` GARDÉ comme filet (déclenché par generate()).
- Script pull `pixel_generations_pull.sh` fusionne APP + SERVER (dédup ts).
- APK 1.9.44 build+installé, vérifié : /healthz running:true, 2 générations captées (preuve adb pull).

## 5. NOTE validateur (non bloquant)

Le serveur démarre via flag-file `llm_server.flag` (mécanisme non-humain, validé). En prod,
llmServer(start) sera déclenché par l'app (après login + prepareModel) — à câbler côté JS/TS
quand le mode "app en client HTTP" sera activé. Aujourd'hui le serveur tourne et capture même
sans UI (preuve de robustesse).
