# Déploiement — Gochara Karmique sur Google Cloud Run

L'application est conçue pour tourner avec son backend sur **Google Cloud Run**, qui est l'architecture parfaite pour une application iOS/Android premium en production. Cloud Run est robuste, ne s'endort jamais (contrairement aux versions gratuites de Render), et est très économique car il s'adapte automatiquement au trafic.

## Ce qu'il vous faut
- Un compte **GitHub** (gratuit) — https://github.com
- Un compte **Google Cloud Platform (GCP)** — https://console.cloud.google.com
- Une clé API **Anthropic** (si Claude est encore utilisé en backup) — https://console.anthropic.com

---

## Étape 1 — Créer un dépôt GitHub

1. Sur GitHub → **New repository**
2. Nom : `gochara-karmique` (privé recommandé)
3. Copiez tous les fichiers du projet dans ce dépôt (le fichier `.dockerignore` empêchera les dossiers iOS/Android inutiles de ralentir le serveur).
4. Faites un commit et push.

---

## Étape 2 — Déployer sur Google Cloud Run

Google Cloud Run peut lire votre dépôt GitHub, construire automatiquement le conteneur grâce au fichier `Dockerfile` inclus, et le déployer.

1. Connectez-vous à la [Console Google Cloud](https://console.cloud.google.com/).
2. Créez un nouveau projet (ex: `gochara-karmique-prod`).
3. Cherchez **Cloud Run** dans la barre de recherche supérieure.
4. Cliquez sur **Créer un service**.
5. Cochez **"Déployer en continu une nouvelle révision à partir d'un dépôt source"** et cliquez sur **"Configurer Cloud Build"**.
6. Connectez votre compte GitHub et sélectionnez votre dépôt `gochara-karmique`.
7. Dans les paramètres de compilation, choisissez **"Dockerfile"** (il détectera automatiquement le fichier à la racine).
8. Configuration du service :
   - **Nom du service** : `gochara-api`
   - **Région** : Choisissez celle la plus proche de vos utilisateurs (ex: `europe-west9` pour Paris).
   - **Authentification** : Cochez **"Autoriser les appels non authentifiés"** (pour que votre app mobile puisse s'y connecter).
9. Dans l'onglet **"Conteneurs, variables, secrets"** :
   - Allez dans la section **"Variables"**.
   - Ajoutez `ANTHROPIC_API_KEY` (si utilisée) avec votre clé `sk-ant-...`.
   - Si vous avez d'autres clés (Google, Stripe), ajoutez-les ici.
10. Cliquez sur **Créer**.

Le premier build prendra quelques minutes. Cloud Run vous fournira ensuite une URL robuste (ex: `https://gochara-api-xxx-ew.a.run.app`).

---

## Étape 3 — Lier l'Application Mobile

Une fois l'URL Google Cloud Run obtenue, vous devrez configurer votre application mobile (le code source `app.js` ou les requêtes Fetch) pour qu'elle pointe vers cette URL de production plutôt que vers `localhost` lors de la compilation finale de l'application via Capacitor.

---

## Notes importantes

**Robustesse** : Sur Google Cloud Run, votre backend Python ne s'occupe que des mathématiques (calculs d'éphémérides avec SwissEph) et de l'interrogation de la base de données. Il peut traiter des milliers de requêtes simultanément.

**Chiron** : Si les calculs de Chiron échouent (fichiers éphémérides manquants), il sera marqué `N/A` dans les aspects. Les autres planètes calculent sans problème.

**Moonrise Chart** : Implémenté en Chandra Lagna (ASC = début du signe de la Lune natale), fidèle à la logique védique du système.