# HANDOFF → profil astro : validation export fine-tune Karmic Gochara

**De** : profil karmic_gochara (routing/déploiement/serveur)
**Date** : 2026-07-18
**Sujet** : valider l'archi d'export du fine-tune AVANT finalisation (livrable c du brief Pixel)
**Contexte technique déjà tranché** (côté karmic_gochara) : litertlm-android:latest.release (0.14.0)
n'expose PAS d'API LoRA runtime → l'artefact = un `.litertlm` **pré-mergé** (LoRA baké offline via
litert-model-cpp) qui remplace le base Gemma-4-E2B sur le Pixel, chargé comme le base actuel
(backend CPU). Le `LORA_ASSET_PATH` du plugin est mort-né.

Le serveur Pixel (a), la capture server-side (b) et le build APK (d) sont LIVRÉS ET PROUVÉS sur
device (2 générations captées, texte Gemma réel). Il reste à valider le (c) avec toi.

---

## PROMPT DE VALIDATION (à exécuter côté profil astro)

> **Rôle** : tu es le gardien de la VOIX et de la DOCTRINE Karmic Gochara (@siderealAstro13).
> Le pipeline de fine-tune côté infra (scripts/finetune_kg.py, format merged-`.litertlm`) est prêt
> mais son artefact doit respecter 3 garde-fous éditoriaux. Valide-les et réponds en français,
> concis, avec le WHY.
>
> **Fichiers de référence** :
> - `karmic.gochara/docs/finetune_export_plan.md` (archi + contraintes)
> - `karmic.gochara/dataset_finetuning.jsonl` (source : {messages:[system,user,assistant], type, engine, ts})
> - `karmic.gochara/scripts/finetune_kg.py` (mode `filter` déjà exécuté → dataset_train_clean.jsonl, 44 lignes)
> - `karmic.gochara/android/app/src/main/java/com/karmicgochara/app/DoctrinePromptBuilder.java` (prompt système live)
>
> **Points à valider (réponds point par point) :**
>
> 1. **Voix vs poids** — Le prompt système (DoctrinePromptBuilder) vit côté app, PAS dans les poids
>    du modèle. Le fine-tune (LoRA baké dans le `.litertlm`) ne fait que renforcer le style/la
>    structure. Est-ce que le merged model doit OU NON ré-encoder le prompt système dans les poids
>    (ex: injecter le system prompt dans chaque sample d'entraînement) ? Ou le laisser 100% côté app
>    comme filet éditorial unique (single-source) ? → Trance + explique le WHY.
>
> 2. **Format dataset** — `finetune_kg.py filter` ne garde QUE les lignes
>    `{messages:[system,user,assistant]}` complètes. Les lignes `{user_id, rating, soul_debug}`
>    (feedback utilisateur) sont EXCLUES du training supervisé. Cela te convient-il, ou veux-tu
>    que le rating conditionne le choix des samples (ex: ne garder que rating ≥ 4) ? → Dis oui/non
>    et si non, la règle exacte.
>
> 3. **Taille du merged model** — Si le `.litertlm` mergé dépasse 2.58 GB (taille du base actuel),
>    le checker `isValidModel` du plugin (taille + sha256) le REJETTERA silencieusement. Donne la
>    taille cible max acceptable pour le Pixel (contrainte stockage + RAM), ou valide le maintien
>    sous 2.58 GB (LoRA r=16 faible rank).
>
> **Livrable attendu de ta part** : un OK/NOK par point + (si NOK) la règle corrigée à appliquer
> dans `finetune_kg.py` (mode `merge`/`deploy`) et dans le prompt système. Sans ta validation,
> l'archi (c) reste en stand-by.

---

## Note de coordination
- Le profil karmic_gochara n'édite PAS le prompt système (domaine astro, single-source).
- Une fois ta validation reçue, karmic_gochara exécute `train`→`merge`→`deploy` sur GPU box et
  met à jour le sha256/size du plugin si besoin.
- Le corpus de capture ne s'évapore plus (capture server-side live) — les nouvelles générations
  alimenteront le dataset via `pixel_generations_pull.sh`.
