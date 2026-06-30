# Règles Spécifiques au Projet Karmic Gochara

<RULE[capacitor_sync]>
## Déploiement et Synchronisation Automatique Capacitor

L'utilisateur teste l'application de façon continue via Android Studio avec un Google Pixel branché.

**Règle absolue :** 
À chaque fois que vous modifiez un fichier frontend dans le dossier `astro` (composants `.astro`, styles, scripts, pages), vous **DEVEZ IMPÉRATIVEMENT** exécuter la commande de build et de synchronisation Capacitor **avant de terminer votre tour**, sans attendre que l'utilisateur le demande.

Commande à exécuter :
```bash
cd astro && npm run sync:capacitor
```
</RULE[capacitor_sync]>
