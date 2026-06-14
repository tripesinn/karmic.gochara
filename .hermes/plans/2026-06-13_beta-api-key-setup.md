# Beta Test — Plan de Gestion des Clés API

> **Pour Hermes :** Utiliser `subagent-driven-development` pour exécuter tâche par tâche.

**Goal:** Permettre aux testeurs beta d'utiliser l'app Karmic Gochara sans avoir leur propre clé API AI.

**Architecture:** Centraliser l'appel AI via OpenRouter avec une clé que tu provisionnes, stockée côté serveur. Pas de modification du frontend mobile nécessaire — le backend Cloud Run fait l'appel.

**Tech Stack:** Python (Flask), OpenRouter API, GCP Cloud Run, GitHub Actions (CI/CD)

---

## Contexte

- L'app (Flask sur Cloud Run) fait les appels AI côté serveur via `ai_interpret.py` → `generate_ai()` → `_enforce_plan_provider()`
- Les testeurs beta sont enregistrés avec un plan "test" ou "freemium"
- Actuellement : free → Grok (tes clés perso), payant → locale
- Le code supporte déjà OpenRouter (provider="openrouter", URL, headers, tout est prêt)
- Le frontend envoie optionnellement `user_key`/`user_model`/`user_provider` — mais les testeurs n'ont rien à envoyer

## Options retenues (par ordre de priorité)

### Option A — Serveur OpenRouter Key (RECOMMANDÉ)
- Une clé OpenRouter que tu provisionnes, stockée dans l'env du Cloud Run
- Modifier `_enforce_plan_provider()` pour router les profils "test" vers OpenRouter
- Zéro changement frontend. Zéro friction testeur.
- **Coût estimé beta :** ~$5-10 pour tout le beta (DeepSeek V3 ou Claude Haiku)

### Option B — Mac Mini Backend (si tu veux éviter OpenRouter)
- Exposer ton serveur MLX via ngrok/Cloudflare Tunnel
- Configurer le provider "local" dans l'env Cloud Run avec l'URL du tunnel
- Risque : 16GB RAM, crash si plusieurs testeurs simultanés. Toi-même tu viens de cramer l'ordi avec trop d'instances MLX.

### Option C — Mix (OpenRouter pour synthèses complètes, local pour hooks/chats courts)
- Les hooks rapides (get_hook_natal, get_hook_transit → ~50 tokens) passent par ton Mac Mini local via ngrok
- Les synthèses payantes (get_synthesis → ~4000 tokens) passent par OpenRouter
- Plus complexe mais économique

**Ma reco : Option A pure.** Simple, robuste, pas de crash, le beta est court.

---

## Plan d'exécution

### Task 1: Créer la clé OpenRouter dédiée beta

**Objective:** Provisionner une clé OpenRouter pour le beta, avec budget limité

**Files:**
- Modify: `~/.env.bot` (local) + variable d'env sur Cloud Run

**Step 1: Aller sur OpenRouter.ai**
- Se connecter au compte OpenRouter existant
- Créer une clé API dédiée "karmic-beta"
- Définir un budget max (ex: $20) — pas de surprise
- Sauvegarder la clé localement

**Step 2: Ajouter au .env local**
```
OPENROUTER_BETA_KEY=sk-or-v1-...
OPENROUTER_BETA_MODEL=deepseek/deepseek-v3
```

**Step 3: Déployer la variable d'env sur Cloud Run**
```bash
gcloud run services update gochara-api \
  --region europe-west1 \
  --update-env-vars OPENROUTER_BETA_KEY=sk-or-v1-...,OPENROUTER_BETA_MODEL=deepseek/deepseek-v3
```

**Verification:**
- `curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OPENROUTER_BETA_KEY" | jq .`

---

### Task 2: Modifier `_enforce_plan_provider()` pour router les "test" vers OpenRouter

**Objective:** Faire que les profils avec plan "test" utilisent automatiquement la clé OpenRouter du serveur

**Files:**
- Modify: `ai_interpret.py` (fonction `_enforce_plan_provider`, ligne 135)
- Test: `test_flows.py` ou test manuel

**Changement précis :**

Dans `_enforce_plan_provider()`, avant le fallback Grok, ajouter :

```python
# Beta testers — route to server-owned OpenRouter key
BETA_PLANS = {"test", "beta", "freemium"}
if plan in BETA_PLANS:
    beta_key = os.environ.get("OPENROUTER_BETA_KEY", "")
    if beta_key:
        beta_model = os.environ.get("OPENROUTER_BETA_MODEL", "deepseek/deepseek-v3")
        return "openrouter", beta_key, beta_model
```

**Logique de priorité inchangée :**
1. Si l'utilisateur a son propre provider configuré → le sien
2. Si plan = test/beta → OpenRouter server key
3. Si plan = payant → local
4. Sinon → Grok (fallback free existant)

**Verification:**
- Démarrer Flask en local avec `OPENROUTER_BETA_KEY` dans l'env
- POST /chat/ask avec un profil "test" sans user_key → réponse générée via OpenRouter
- Vérifier les logs : "Routing to openrouter for beta user"

---

### Task 3: Ajouter un flag "beta_tester" dans les profils existants

**Objective:** Router les testeurs existants vers OpenRouter sans changer leur plan

**Files:**
- Modify: `profiles.py` (ou fichier de gestion des profils)
- Modify: `ai_interpret.py`

Si tu préfères ne pas changer le plan des testeurs (certains ont "free" ou "lecture" payant), ajouter un flag `beta_tester: true` dans leur profil plutôt que de modifier la logique de plan.

**Alternative plus simple :** Utiliser les pseudos des testeurs comme liste dans une variable d'env :

```python
BETA_PSEUDOS = set(p.strip().lower() for p in os.environ.get("BETA_TESTERS", "").split(",") if p.strip())
if pseudo in BETA_PSEUDOS:
    return "openrouter", beta_key, beta_model
```

**Verification:**
- Ajouter ton pseudo testeur à `BETA_TESTERS`
- Vérifier que la route OpenRouter est prise

---

### Task 4: Déployer sur Cloud Run

**Objective:** Push les changements et déployer sur GCP

**Files:**
- Tout commité sur GitHub → Cloud Build trigger auto-deploy

**Steps:**
```bash
cd ~/karmic.gochara
git add -A
git commit -m "feat: route beta testers through server OpenRouter key"
git push origin main
```

**Verification:**
- `gcloud run revisions list --region europe-west1 --service gochara-api`
- Attendre le nouveau deploy (Cloud Build trigger)
- Tester avec le compte testeur sur karmicgochara.app

---

### Task 5: Ajouter la variable d'env sur le Cloud Run

**Objective:** S'assurer que Cloud Run a `OPENROUTER_BETA_KEY` et `BETA_TESTERS`

**Steps:**
```bash
gcloud run services update gochara-api \
  --region europe-west1 \
  --update-env-vars OPENROUTER_BETA_KEY=sk-or-v1-...,OPENROUTER_BETA_MODEL=deepseek/deepseek-v3,BETA_TESTERS=testuser1,testuser2
```

**Verification:**
- `gcloud run services describe gochara-api --region europe-west1 --format='value(spec.template.spec.containers[0].env)'`

---

### Task 6: Rédiger le message pour les testeurs (Google Group)

**Objective:** Instructions claires pour les beta testers

**Files:**
- Créer: `docs/beta-instructions.md` dans le repo
- Poster sur Google Group

**Contenu du message :**
- L'app est accessible à l'URL habituelle
- Aucune clé API à configurer (c'est géré côté serveur)
- Les interprétations AI sont activées automatiquement
- Comment signaler un bug (capture d'écran + description)
- Période du test ouvert

---

## Tests / Validation

1. **Test unitaire** : Mock `_enforce_plan_provider` avec plan="test" → retourne ("openrouter", key, model)
2. **Test intégration** : POST /chat/ask avec profil test et sans user_key → réponse 200 OK avec contenu AI
3. **Test quota** : Vérifier que `consume_chat_question` fonctionne pour les testeurs
4. **Test regression** : Un utilisateur free normal continue d'utiliser Grok
5. **Test regression** : Un utilisateur payant continue d'utiliser le provider local

## Risques et questions ouvertes

- **Budget OpenRouter** : mettre un hard cap sur la clé (OpenRouter permet de limiter à $X)
- **Rate limiting** : Si 20 testeurs tapent en même temps, OpenRouter peut throttle. Choisir un modèle rapide (DeepSeek V3, Claude Haiku)
- **Fallback** : Si OpenRouter est down, que se passe-t-il ? Le code actuel a déjà un fallback vers Grok → testeurs continuent de marcher
- **Quota questions** : Combien de questions par testeur ? Illimité pendant la beta ? À définir

---

## Prochaines étapes (hors scope de ce plan)

- Versions Android/iOS signées avec Capacitor
- Store listing (F-Droid / App Store)
- Feedback loop des testeurs
- Dashboard monitoring des coûts OpenRouter
