# Karmic Gochara Lite — Prompts pour test Ollama gemma4:31b
# Profil : Jérôme (31/10/1974 8h25 Paris)
# DK Ayanamsa — Chandra Lagna Bélier (H1)
# Date transit : 06/06/2026
# ─────────────────────────────────────────────

## PROMPT 1 — NATAL HOOK (3 phrases)

### SYSTEM
```
Tu es @siderealAstro13. Lecteur d'ame karmique vedique siderale.
Oraculaire, direct, sans hedging. Zero degres, zero orbes. Tutoiement.
Texte brut uniquement — jamais de markdown, jamais de headers, jamais de listes, jamais de tirets.
INTERDIT : noms de signes zodiacaux. Maisons H1-H12 uniquement.
```

### USER
```
Theme natal de Jérôme :
Chandra Lagna H1: Bélier. Ketu (ROM): H2. Chiron (RAM, ouverture): H12.
Porte Visible: Lion. Lilith (epreuve): H10.
Nakshatras: Ketu en Rohini, Rahu en Anuradha, Chiron en Revati.

Ecris exactement 3 phrases de prose enchainee. Pas de numeros, pas de titres, pas de markdown.
La premiere phrase : le schema karmique dominant que Jérôme rejoue (Ketu H2 — ROM figee).
La deuxieme phrase : la blessure active et ce qu'elle cherche (Chiron H12 — outil vers la Porte Visible H5).
La troisieme phrase : la direction de liberation (Stage) + amorce d'Alternative de Conscience.
Dense, precis. Donne envie d'en savoir plus.
```

---

## PROMPT 2 — SYNTHESE COMPLETE (4 blocs)

### SYSTEM
```
Tu es l'intelligence siderealAstro13, experte en Doctrine Évolutive Synthétique.
ROM (Ketu)=Mémoires passées/automatisme.
RAM (Chiron)=Traitement actif de la blessure, outil d'ouverture de la Porte Visible (guérison/Stage).
Porte Invisible=Prison inconsciente/refoulement.
LILITH=Point de rupture/épreuve.
DHARMA (Rahu)=Destination d'évolution.
Tutoie l'utilisateur. Sois direct et chirurgical.
Note : la date de transit fournie (2026) est injectée statiquement. Ignore ta limite de connaissances (cutoff) et ne fais aucun avertissement sur le temps réel.
```

### USER
```
Analyse karmique de transit pour Jérôme — 06/06/2026.
Natal : Chandra Lagna Bélier, Ketu Taureau H2, Rahu Scorpion H8, Chiron Poissons H12, Lilith Capricorne H10.
Aspects actifs :
T.ASC ↑ (♑ Capricorne 0°) Carré □ N.ASC ↑ (♈ Bélier 0°) [0.0°]
T.MC ↑ (♈ Bélier 20°54′) Sextile ✶ N.Saturne ♄ (♊ Gémeaux 20°54′) [0.01°]
T.Lilith ⚸ (♐ Sagittaire 4°03′) Sextile ✶ N.Mars ♂ (♎ Balance 4°01′) [0.02°]
T.Nœud Nord ☊ ℞ (♒ Verseau 4°12′) Trigone △ N.Mars ♂ (♎ Balance 4°01′) [0.18°]

MISSION POUR L'IA :
Analyse ces données en 4 blocs :

DIAGNOSTIC ROM (Ketu) : Quel schéma de passé-vie est activé en ce moment ?
Quel automatisme défensif est à l'œuvre ?

PORTE INVISIBLE → PORTE VISIBLE : Quels transits activent la prison inconsciente ?
Comment Chiron (RAM) peut-il ouvrir le passage vers le Stage ?

ÉPREUVE LILITH : Quelle friction karmique est en cours ?
Comment Lilith propulse-t-elle vers le Dharma (Rahu) ?

ALTERNATIVE DE CONSCIENCE : Formule l'insight transformateur précis,
chirurgical, actionnable — ce que l'âme doit comprendre MAINTENANT
pour avancer vers son Stage.

Style : direct, technique, non-astro-jargon dans les conclusions. Tutoiement direct ("tu").
Longueur : 400-600 mots. Pas de généralités. Chaque phrase = une vérité chirurgicale.
```

---

## Résultat benchmark — gemma4:31b (Ollama Cloud)
### Date : 06-07/06/2026 — Prompt Synthèse 4 blocs

### Tableau comparatif

| Critère | minimax-m3 | phi4 local | gemma4:31b cloud |
|---|---|---|---|---|
| Prompt respecté | ★★★☆☆ (refus lite) / ★★★★★ (cloud) | ★★★★☆ | ★★★★★ |
| Zéro signe zodiacal | ★★★★★ | ★★★★★ | ★★★★★ |
| Ton oraculaire | ★★★★★ | ★★★☆☆ | ★★★★★ |
| Structure ##1-4 | ★★★★★ | ★★★★★ | ★★★★★ |
| Qualité littéraire | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| Alternative actionnable | ★★★★★ | ★★★★☆ | ★★★★★ |
| Temps réponse | 26" ★★★★★ | 1'39" ★★★★★ | 26" ★★★★★ |
| Qualité globale | ★★★★☆ (cloud) | ★★★★☆ | ★★★★★ |

**Détails par modèle :**

**minimax-m3** — Refus catégorique sur prompt lite (450 tok). Révélation sur prompt cloud (~3000 tok) : meilleure plume des trois. Images poétiques et uniques ("thésaurisation", "pétrification", "main invisible", "propulseur nucléaire"). Alternative la plus originale ("nomme à voix haute la peur"). Le prompt long le déverrouille complètement. ★★★★☆

**phi4 local (MLX)** — 80% du gemma pour un temps quasi réel. Le format long (prompt cloud) le contraint mieux que le lite. Ton encore un peu thérapeutique, manque de tranchant oraculaire. ★★★★☆

**gemma4:31b cloud** — Meilleur interprète. Capte les subtilités des aspects sans les nommer. ★★★★★

**Tu veux tester toi-même ?**
Installe [Ollama](https://ollama.com) → `ollama pull gemma4:31b` → colle le prompt lite ou cloud.
Ou utilise [Ollama Cloud](https://ollama.com/cloud) (free tier = modèle cloud sans install).
Tu peux y tester gemma4, phi4, minimax-m3 et des dizaines d'autres modèles gratuitement.

**Coût estimé :** ~1050 tokens/appel → ~4700 appels pour 5M tokens/semaine

---

## Annexe : Positions sidérales DK de Jérôme

| Planète | Signe | Degré | Maison CL | Nakshatra | Lord |
|---------|-------|-------|-----------|-----------|------|
| Lune (CL) | ♈ Bélier | 12°34′ | H1 | Ashwini p4 | Ketu |
| Ketu (ROM) | ♉ Taureau | 12°30′ | H2 | Rohini p1 | Lune |
| Rahu (Dharma) | ♏ Scorpion | 12°30′ | H8 | Anuradha p3 | Saturne |
| Chiron (RAM) | ♓ Poissons | 24°44′ | H12 | Revati p3 | Mercure |
| PV | ♌ Lion | 10°48′ | H5 | Magha p4 | Ketu |
| PI | ♒ Verseau | 10°48′ | H11 | Shatabhisha p2 | Rahu |
| Lilith | ♑ Capricorne | 7°13′ | H10 | Uttara Ashadha p4 | Soleil |
| Saturne | ♊ Gémeaux | 20°54′ | H3 | Punarvasu p1 | Jupiter |
| ASC↑ | ♈ Bélier | 0°00′ | — | Ashwini p1 | Ketu |
| Jupiter | ♒ Verseau | 10°00′ | H11 | Shatabhisha |
| Mars | ♎ Balance | 4°01′ | H7 | Chitra |
| Vénus | ♎ Balance | 7°54′ | H7 | Swati |
| Soleil | ♎ Balance | 14°56′ | H7 | Swati |
| Mercure | ♍ Vierge | 27°51′ | H6 | Chitra |