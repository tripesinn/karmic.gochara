# Skill: Calculs Astrologiques (Astro Engine)

Ce skill détaille les spécifications techniques des calculs effectués par `astro_calc.py`.

## Paramètres Fondamentaux
- **Ayanamsa** : Centre Galactique DK (Djwhal Khul).
- **Zodiaque** : Sidéral.
- **Système de Maisons** : **Chandra Lagna** (Moonrise Chart).
  - L'Ascendant (ASC) est fixé au début (0°) du signe de la Lune natale.
- **Nœuds Lunaires** : Nœuds Vrais (True Nodes).
- **Lilith** : Lilith vraie (Apogée osculatrice).
- **Orbe** : Maximum 3° pour tous les aspects.

## Objets Calculés
- **10 Planètes classiques** + Chiron.
- **Nœud Nord & Nœud Sud**.
- **Portes de Castanier** :
  - **Porte Visible (PV)** : Mi-point du petit arc Saturne→Uranus.
  - **Porte Invisible (PI)** : PV + 180°.
- **Nakshatras** : Calcul du Nakshatra (1-27), du Pada (1-4) et du régent planétaire.

## Divisionnaires (Amsas)
Le moteur calcule automatiquement les positions dans les thèmes divisionnaires suivants :
- **D9 (Navamsha)** : État de l'âme et du Dharma.
- **D10 (Dashamsha)** : Vocation et action publique.
- **D60 (Shashtyamsha)** : Archive karmique profonde (utilisé pour les seigneurs de D60).

## Utilisation Technique
Les calculs s'appuient sur la bibliothèque **Swiss Ephemeris** (`pyswisseph` ou `swisseph_ctypes`). Le fichier `swedll64.dll` est requis sous Windows.
