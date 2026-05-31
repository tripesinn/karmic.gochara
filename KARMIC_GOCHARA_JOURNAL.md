# Journal de Projet : Karmic Gochara (Gochara App)

## 1. Métadonnées du Projet

*   **Nom du Projet** : Karmic Gochara (Gochara App)
*   **Hébergement API** : Google Cloud Run (service `gochara-api`)
*   **Builds Mobiles** : iOS (Capacitor) & Android (Capacitor)
*   **Version / Date** : Mai 2026


## 2. Stack Technique du Projet

*   **Backend** : Python Flask (`app.py`), sqlite3 / structures locales
*   **Frontend** : HTML5, CSS Vanilla (Thème astrologique sombre et or)
*   **Mobile Framework** : Capacitor.js (Synchronisation du dossier `www`)
*   **Moteur d'IA** :
    *   **Cloud** : Google Gemini / Anthropic Claude / Groq
    *   **IA Locale** : Modèle `phi-4` s'exécutant sur le Mac de l'utilisateur via vLLM
    *   **Pont Cloud-Local** : URL de tunnel ngrok saisie par l'utilisateur


## 3. Changements Majeurs Récents

### Paramètres de l'IA Personnelle & de Routage
*   **Sauvegarde & Clés Personnelles** :
    - Restauration complète des champs d'édition d'IA (Serveur Local, Gemini, Claude, Groq, OpenRouter) dans le modal de paramètres.
    - Correction de la persistance locale (`KarmicStore`) pour les clés d'API et les modèles personnalisés.

*   **Routage Individuel & Isolation des Coûts** :
    - Mise à jour de la fonction de routage pour préserver à 100% les clés et modèles personnalisés des utilisateurs PRO.
    - Blocage du repli (fallback) invisible sur le compte payant du serveur. Si la clé personnelle de l'utilisateur ou sa connexion locale échoue, l'application renvoie un message explicatif clair au lieu d'impacter le budget cloud du serveur.

### Correctifs de la Version Mobile (Capacitor Build)
*   **Affichage Unconditionnel des Paramètres** :
    - Retrait complet des restrictions Jinja (`{% if session_profile %}`) autour de l'icône de paramètres `⚙️` et de l'option de téléchargement hors-ligne dans `templates/index.html`.
    - Les fonctionnalités sont désormais visibles et fonctionnelles pour les utilisateurs de l'application statique/mobile (qui n'ont pas de session serveur Jinja active).

*   **Intégration du Dossier Statique dans le Dossier de Build (`www/`)** :
    - Résolution d'un bug critique où le dossier `/static` (contenant `app.js` et `style.css`) n'était pas présent dans le dossier de build `www/`.
    - Mise à jour de `render_static.py` pour copier automatiquement et de manière robuste le dossier `/static` vers `www/static`.
    - Permet le chargement complet des scripts et styles indispensables dans les environnements mobiles et résout le dysfonctionnement silencieux d'actions comme `openSettings()`.


## 4. État des Livraisons (Git Commits & Push)

*   **Statut Local** : Propre.
*   **Dépôt Distant (Origin)** : Tous les commits locaux (incluant l'intégration `localV1`, les correctifs de modal de paramètres, et l'intégration mobile des assets statiques) ont été poussés sur la branche `main` avec succès.


## 5. Prochaines Étapes Planifiées

*   **Validation Mobile** :
    - Tester l'ouverture du modal de paramètres et le chargement des styles CSS sur un simulateur iOS/Android après compilation de Capacitor.

*   **Optimisation Hors-Ligne** :
    - Valider le bon fonctionnement du téléchargement des années de calcul astronomique locales (`Mode Hors-Ligne`) sur mobile sans connexion internet.