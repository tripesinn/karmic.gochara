---
name: karmic-app-showcase
description: Procédure pour intégrer une capture vidéo (MP4) ou une image défilante de l'application mobile dans la maquette de téléphone CSS du site web Flask.
---

# Karmic App Showcase Integration

Cette compétence (skill) doit être utilisée lorsque l'utilisateur indique qu'il a pris les captures d'écran vidéo (MP4) ou les longues images de son application finale, et qu'il souhaite les intégrer dans la landing page du site web (`templates/index.html`).

## Contexte
Le site web (projet Flask) possède une structure HTML/CSS reproduisant un téléphone (`.mockup-container`, `.mockup-screen`). L'objectif est de remplacer l'image statique actuelle par une vidéo MP4 ou une longue image défilante pour montrer le fonctionnement de l'application (le moment "Aha!").

## Procédure d'intégration

### Étape 1 : Vérifier et optimiser les médias fournis
1. Vérifier la présence du fichier vidéo (ex: `demo_app_fr.mp4`) ou de l'image longue dans le dossier de travail.
2. S'assurer que le fichier est copié dans le dossier `static/img/` du projet Flask.

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
