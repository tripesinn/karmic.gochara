# Skill: Gestion du Karmic Vault

Ce skill explique l'utilité et le fonctionnement du dossier `karmic_vault`.

## Utilité
Le dossier `karmic_vault` contient la source de vérité scripturale de la doctrine **@siderealAstro13**. Ces fichiers sont utilisés pour :
1. Alimenter le script `build_task_file.py` lors de l'assemblage des prompts.
2. Servir de référence pour l'IA (Claude ou Gemma) afin de maintenir une cohérence doctrinale parfaite.
3. Permettre une mise à jour facile des textes sans modifier le code Python.

## Structure des fichiers
- `00_MASTER_CONTEXT.md` : Identité de l'IA (Lecteur d'âme) et définitions des concepts ROM/RAM/Dharma/Doors.
- `01_output_rules.md` : Règles strictes de formatage et de ton (interdictions, formats obligatoires).
- `02_planet_keywords.md` : Significations karmiques des planètes.
- `07_nakshatra_keywords.md` : Significations karmiques détaillées des 27 nakshatras.

## Comment l'utiliser
Quand vous modifiez un concept doctrinal :
1. Mettez à jour le fichier Markdown correspondant dans `karmic_vault/`.
2. Reportez les changements dans les variables correspondantes de `build_task_file.py` (ou automatisez l'importation si le script le supporte).
3. Redémarrez le service pour que les nouveaux fichiers `.task` incluent la doctrine mise à jour.

> [!IMPORTANT]
> Ce dossier est CRITIQUE. Toute modification ici change l' "ADN" des interprétations fournies à l'utilisateur final.
