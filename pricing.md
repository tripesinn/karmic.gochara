# Karmic Gochara — Pricing Strategy

> Jyotish sidéral DK · Doctrine Évolutive Synthétique

---

## 1. Pricing Tiers

*   **Signal du Jour (Gratuit)**
    *   Plateforme : Web + App
    *   Contenu : Hook nakshatra quotidien généré par Gemini Flash
    *   Durée : Illimité

*   **Version Pro (9,99 € - Lifetime One-Time)**
    *   Plateforme : Web + App
    *   Contenu : Synthèse karmique complète (via Cloud) + Chatbot Pro (uniquement en Local)
    *   Durée : À vie (Achat unique)

---

## 2. Funnel d'acquisition

```
Signal du Jour gratuit  →  Version Pro (9,99 € Achat Unique)
```

### Étape 1 — Signal du Jour (Gratuit · Web + App)

**Why :** Créer l'habitude quotidienne. L'utilisateur découvre
la doctrine DK sans friction. Le hook est précis et donne envie
d'en savoir plus.

**How :** Nakshatra du jour + transit dominant + Alternative de
Conscience en 3 phrases, générés par Gemini Flash. Disponible
via TikTok (@siderealastro13) et sur le site/app.

---

### Étape 2 — Version Pro (9,99 € · Lifetime)

**Why :** Tarification simple et sans abonnement récurrent pour
lever tous les freins.

**How :** L'utilisateur entre ses coordonnées de naissance. Il
reçoit sa synthèse karmique complète + accès au chatbot Pro.

**Routage des coûts et protection API :**
*   L'IA locale (si disponible sur l'appareil) gère l'intégralité
    des conversations du chatbot.
*   Il n'y a **aucun fallback cloud** pour le chatbot afin de garantir
    que l'infrastructure ne génère aucune facture API récurrente.
    Si l'appareil n'a pas d'IA locale disponible, le bouton du chatbot
    Pro invite l'utilisateur à l'activer (Chrome Built-in AI sur web
    ou Google AICore sur Android).

---

## 3. Feature Comparison

*   **Gratuit (Signal du Jour)**
    *   Signal du Jour (nakshatra) : Oui
    *   Synthèse karmique complète : Non
    *   Questions chatbot : Non
    *   Alertes transit : Non
    *   Thème natal sauvegardé : Non
    *   Alternative de Conscience : Teaser uniquement

*   **Pro (9,99 € Lifetime)**
    *   Signal du Jour (nakshatra) : Oui
    *   Synthèse karmique complète : Oui (Générée via cloud)
    *   Questions chatbot : Illimité (uniquement si IA locale active)
    *   Alertes transit : Oui
    *   Thème natal sauvegardé : Oui
    *   Alternative de Conscience : Complète
    *   IA locale : Requise pour le chatbot (automatique sur appareils compatibles)

---

## 4. Architecture IA Cloud & Local

*   **Daily Reading & Synthèse initiale : Gemini Flash**
    *   Modèle par défaut sur serveur.
    *   Coût extrêmement bas (idéal pour le lifetime 9,99 €).
    *   Vitesse d'exécution optimale.

*   **Chatbot Pro : IA locale uniquement (oMLX, Gemma, Phi-4, AICore)**
    *   Exécution exclusive sur l'appareil.
    *   Réduit le coût cloud chatbot serveur à 0 € absolu.

---

## 5. Positioning — Value Proposition

> **Doctrine Jyotish DK. Propulsé par Gemini.**
> L'oracle karmique personnel.

Ce n'est pas une simple app d'horoscope. C'est Gemini
entraîné sur une doctrine karmique précise (Nœuds, Chiron,
Saturne, ayanamsa DK, tutoiement direct).

---

## 6. Roadmap 6 mois

*   **Jalon T0 — Launch (Avril 2026)**
    *   Web + APK. Gemini Flash par défaut pour le cloud. Stripe Achat Unique.
*   **Jalon T1 — Stabilisation (Juin 2026)**
    *   Alertes live transits. Optimisation des invites de prompts.
*   **Jalon T2 — IA locale native (Décembre 2026)**
    *   Gemma natif Android.

---

## 7. Metrics & KPIs

*   **Conversion Hook → Pro :** Cible 3% (3 mois) / 5% (6 mois).
*   **Alternative de Conscience hit rate :** > 90%.
*   **Taux d'utilisation IA locale (Pro) :** > 15%.

---

## 8. Notes stratégiques

*   **Ce qu'on ne fait pas :**
    *   Pas d'abonnements récurrents compliqués.
    *   Pas de version freemium avec publicité dégradante.
    *   Pas de modèle Grok (sidelined).
    *   Pas de requêtes chatbot Pro routées sur le cloud pour éliminer
        toute possibilité de dérive des coûts API à long terme.
