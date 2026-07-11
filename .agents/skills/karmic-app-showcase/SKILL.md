---
name: karmic-app-showcase
description: Procédure pour intégrer une capture vidéo (MP4) ou une image défilante de l'application mobile dans la maquette de téléphone CSS du site web Flask.
---

# Karmic App Showcase Integration

Cette compétence (skill) doit être utilisée lorsque l'application est prête et que l'utilisateur demande d'intégrer une démonstration vidéo dans la landing page du site web (`templates/index.html`). L'agent IA est responsable de réaliser lui-même la capture vidéo via ADB sur l'appareil connecté.

## Contexte
Le site web (projet Flask) possède une structure HTML/CSS reproduisant un téléphone (`.mockup-container`, `.mockup-screen`). L'objectif est de remplacer l'image statique actuelle par une vidéo MP4 fluide enregistrée directement depuis le Pixel de l'utilisateur.

## Procédure d'intégration

### Étape 1 : Réaliser la capture vidéo via ADB
1. Assurez-vous que l'application est lancée sur le téléphone Pixel de l'utilisateur.
2. Utilisez la commande `adb shell screenrecord --time-limit 15 /sdcard/demo_app.mp4` pour filmer l'écran pendant 15 secondes.
3. Pendant l'enregistrement, utilisez des commandes `adb shell input swipe` pour simuler un scroll fluide (ex: faire défiler la synthèse karmique).
4. Récupérez la vidéo avec `adb pull /sdcard/demo_app.mp4 static/img/demo_app.mp4` puis supprimez-la de l'appareil (`adb shell rm /sdcard/demo_app.mp4`).

### Étape 2 : Modification du template HTML (`templates/index.html`)

**Option A : Intégration d'une Vidéo (Recommandée)**
Localiser la balise `<img>` à l'intérieur du `.mockup-screen` et la remplacer par une balise `<video>`.
Il est **crucial** d'utiliser les attributs suivants pour que la vidéo se comporte comme un GIF :
```html
<video class="mockup-video" autoplay loop muted playsinline>
    <source src="{{ url_for('static', filename='img/demo_app_' ~ lang.code ~ '.mp4') }}" type="video/mp4">
    <!-- Fallback image si la vidéo ne charge pas -->
    <img src="{{ url_for('static', filename='img/screenshot_' ~ lang.code ~ '.png') }}" alt="Aperçu de l'application Karmic Gochara">
</video>
```

**Option B : Intégration d'une image avec défilement CSS**
Si l'utilisateur fournit une longue image au lieu d'une vidéo, modifier le CSS de `.mockup-screen` ou de l'image :
```css
.mockup-screen {
    overflow-y: auto; /* Permet le scroll manuel */
    /* Masquer la scrollbar pour un effet natif */
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.mockup-screen::-webkit-scrollbar {
    display: none;
}
```

### Étape 3 : Styles CSS additionnels (`static/css/index.css`)
S'assurer que la vidéo prend toute la place du conteneur sans déborder :
```css
.mockup-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border-radius: inherit; /* Pour hériter des coins arrondis de l'écran */
}
```

### Étape 4 : Validation
1. Déployer sur le serveur Flask local ou vérifier manuellement avec l'utilisateur.
2. Demander à l'utilisateur si la vidéo se lance bien toute seule (l'attribut `muted` est obligatoire pour l'autoplay sur la majorité des navigateurs).
3. Commiter avec le message : `feat: integrate dynamic video showcase in phone mockup`.
