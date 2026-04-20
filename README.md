# ☸️ Gochara Karmique — Edge AI Astrology

![Edge AI](https://img.shields.io/badge/AI-Gemma_3_1B_Local-orange)
![License](https://img.shields.io/badge/License-Dual_MIT_CC-blue)
![Platform](https://img.shields.io/badge/Platform-Android_Capacitor-green)
![Version](https://img.shields.io/badge/Version-1.2.0-purple)

**Gochara Karmique** est un moteur expert d'astrologie védique fonctionnant en "Edge AI" (intelligence artificielle locale). Il combine les calculs de précision du Jyotish sidéral avec une synthèse doctrinale originale pour transformer des transits astronomiques en conseils oraculaires profonds.

---

## 🚀 Le Concept : "Open Engine, Hidden Recipe"

Ce projet suit un modèle de développement hybride :
1. **L'Engine (Open Source)** : Tout le code permettant de calculer les transits, de gérer le pont Capacitor et d'injecter les prompts dans l'IA est ouvert.
2. **La Recette (Propriétaire)** : La doctrine évolutive, les synthèses de Nakshatras et l'architecture de mélange (le "Vault") appartiennent à l'auteur (**@siderealAstro13**). Ces fichiers sont ignorés par Git pour protéger le savoir-faire.

---

## 🛠 Architecture Technique : "Astro AI Edge"

L'innovation majeure de ce chatbot réside dans sa capacité à fonctionner **100% hors-ligne** sur mobile :
- **Inférence Locale** : Utilise **Gemma 3 1B** (int4) via le plugin Capacitor Gemma.
- **Injection Dynamique** : Des fichiers `.task` JSON sont générés par le backend Flask pour injecter précisément les fragments de doctrine pertinents au transit de l'utilisateur.
- **Précision Astronomique** : Intégration de la **Swiss Ephemeris** (sidéral DK) pour des calculs dignes des meilleurs logiciels professionnels.
- **Performance Optimisée** : Temps de réponse < 3 secondes sur appareils Android récents.

---

## 🪐 Principes de la Doctrine

La synthèse repose sur le mélange inédit de plusieurs concepts :
- **ROM (Read-Only Memory)** : Le pôle Ketu, mémoires automatiques.
- **RAM (Wound Processing)** : Le pôle Chiron, clé de transmutation.
- **DHARMA (Direction)** : Le pôle Rahu, appel évolutif.
- **Les Portes (Castanier)** : Porte Visible (Résolution) et Porte Invisible (Enfermement).

Pour plus de détails sur l'implémentation, consultez le fichier [doctrine.example.py](doctrine.example.py).

---

## 📜 Licences et Propriété

- **Code Source** : [MIT License](LICENSE.md) — Libre d'utilisation technique.
- **Synthèse Doctrinale & Textes** : **Copyright © @siderealAstro13**. Tous droits réservés sur la "Recette" (fichiers `karmic_vault/` et `doctrine.py`).
- **Architecture de Synthèse** : L'agencement spécifique de ces concepts pour un usage en Edge AI doit être crédité à l'auteur original.

---

## 📡 Installation Express

```bash
# Clone
git clone https://github.com/siderealAstro13/karmic.gochara.git

# Backend
pip install -r requirements.txt
python app.py

# Frontend
npm install
npx cap sync android
```

*Note : L'application nécessite un fichier `doctrine.py` (ou `doctrine.example.py`) à la racine pour fonctionner.*

## 🔧 Prérequis Techniques

- Python 3.9+
- Node.js 16+
- **Java 17** (important : le projet est optimisé pour Java 17)
- Android Studio (pour le build Android)
- 2 Go d'espace disque (modèle Gemma inclus)

---

## 📱 Build Android

Le projet est configuré pour générer un fichier AAB (Android App Bundle) prêt pour le Google Play Store :

```bash
# Synchroniser les assets
npx cap sync android

# Ouvrir dans Android Studio
npx cap open android

# Ou générer directement un AAB
cd android
./gradlew bundleRelease
```

Le fichier AAB sera généré dans `android/app/build/outputs/bundle/release/app-release.aab`

### Compatibilité Java

Le projet utilise Java 17 pour la compilation. Si vous rencontrez des problèmes de version Java :

1. Vérifiez que Java 17 est installé sur votre système
2. Exécutez le script de correction inclus : `scripts/fix_java_version.ps1`

---

## 📊 Fonctionnalités

- **Transits Planétaires** : Calcul précis des transits en temps réel
- **Analyse Nakshatra** : Interprétation basée sur les 27 nakshatras védiques
- **Synthèse Personnalisée** : Adaptation du conseil selon le thème natal
- **Mode Hors-ligne** : Fonctionnement complet sans connexion internet
- **Multi-langues** : Français et Anglais supportés
- **Performance Optimisée** : Utilisation de MediaPipe tasks-genai v0.10.14 pour stabilité

---

## 🤝 Contribuer

Les contributions sont bienvenues sur la partie technique (engine). Pour proposer des améliorations :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout: nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

*Note: Les contributions à la partie doctrinale ne sont pas acceptées.*
