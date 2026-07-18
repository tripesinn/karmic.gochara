# HANDOFF → profil astro : validation export fine-tune Karmic Gochara

**De** : profil karmic_gochara (routing/déploiement/serveur)
**Date création** : 2026-07-18
**Date validation astro** : 2026-07-18
**Sujet** : valider l'archi d'export du fine-tune AVANT finalisation (livrable c du brief Pixel)

**Contexte technique déjà tranché** (côté karmic_gochara) : `litertlm-android:latest.release`
(0.14.0) n'expose PAS d'API LoRA runtime → l'artefact = un `.litertlm` **pré-mergé** (LoRA baké
offline via `litert-model-cpp`) qui remplace le base Gemma-4-E2B sur le Pixel, chargé comme le base
actuel (backend CPU). Le `LORA_ASSET_PATH` du plugin est mort-né.

Le serveur Pixel (a), la capture server-side (b) et le build APK (d) sont LIVRÉS ET PROUVÉS sur
device. Voir `finetune_export_plan.md` §4 pour preuves (APK 1.9.44, /healthz running:true, 2 générations
captées).

---

## VALIDATION PROFIL ASTRO — RÉSULTAT (2026-07-18)

### Point 1 — Voix vs poids  ✅ OK
Le prompt système RESTE 100% côté app (`DoctrinePromptBuilder.buildSystemPrompt()`, assets
`system_prompt_mobile.json` + `nakshatra_karma.json`). Le fine-tune (LoRA baké) ne renforce que
style/structure. WHY : garder la single-source éditoriale astro ; correction doctrine sans re-fine-tune.

### Point 2 — Format dataset  ✅ OK (vérifié sur dataset réel)
Fichier `dataset_train_clean.jsonl` (branche `finetune/dataset-audit`, 28 lignes, 123 KB) :
- 28/28 triplets complets `{system,user,assistant}`, 0 incomplet, 0 assistant vide, 0 JSON invalide
- 2 profils system : 17× "miroir psychologique X/Twitter" (Soul Debug) + 11× "intelligence
  siderealAstro13 / Doctrine Évolutive Synthétique" (DES 5-piliers)
- Lignes `{user_id,rating,soul_debug}` bien exclues du training supervisé

⚠️ **Réserve éditoriale (non-bloquante)** : le dataset mélange 2 registres très différents
(Soul Debug X-Bot vs DES 5-piliers). Le fine-tune apprendra les deux. Si voix DES pure recherchée
sur Pixel → séparer les 11 lignes DES en sous-ensemble, OU accepter le mélange. Choix laissé à
karmic_gochara pour le `merge`.

### Point 3 — Taille merged model  ✅ OK
Cible max = sous 2.58 GB (taille du base actuel). LoRA PEFT r=16 (low rank) tient sous ce plafond.
AU `deploy` : `karmic_gochara` DOIT MAJ `EXPECTED_MODEL_SHA256`/`EXPECTED_MODEL_SIZE` dans
`GemmaSynthesisPlugin` (sinon `isValidModel` rejette le merged model silencieusement).

---

## SYNTHÈSE
| Point | État |
|---|---|
| 1. Voix vs poids | ✅ OK |
| 2. Format dataset | ✅ OK (28 lignes auditées) |
| 3. Taille merged | ✅ OK (< 2.58 GB, r=16) |

→ **Archi (c) VALIDÉE par le profil astro.** karmic_gochara peut exécuter `train`→`merge`→`deploy`.

## Note de coordination
- Le profil karmic_gochara n'édite PAS le prompt système (domaine astro, single-source).
- Une fois le merged `.litertlm` déployé, karmic_gochara met à jour le sha256/size du plugin.
- Le corpus de capture ne s'évapore plus (capture server-side live via `LlmServer` :8099 →
  `llm_server_capture.jsonl`) ; nouvelles générations alimentent le dataset via
  `pixel_generations_pull.sh`.
- Le serveur Pixel répond (`/healthz` OK, `modelReady:true`) ; test de génération `/v1/generate`
  en inférence CPU = lent (timeout > 200s observé) — à rejouer côté device ou avec timeout plus large.
