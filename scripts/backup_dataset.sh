#!/usr/bin/env bash
# Sauvegarde incrémentale du dataset_finetuning.jsonl.
# 1) Copie locale SYSTEMATIQUE (toujours autorisée, protège les données).
# 2) Copie Google Drive BEST-EFFORT (peut être bloquée par TCC si /bin/bash
#    n'a pas Full Disk Access — voir message ci-dessous).
# Idempotent : ne réécrit pas si identique au dernier backup du jour.
set -uo pipefail

SRC="$HOME/karmic.gochara/dataset_finetuning.jsonl"
LOCAL_DIR="$HOME/karmic.gochara/backups"
DRIVE_DIR="$HOME/Library/CloudStorage/GoogleDrive-jerome@jeromemalige.fr/Mon Drive/KarmicGochara/backups"
TS="$(date +%Y%m%d)"

[ -f "$SRC" ] || { echo "$(date) [skip] source absente: $SRC"; exit 0; }

# --- 1) Copie locale (toujours OK) ---
mkdir -p "$LOCAL_DIR"
LOCAL="$LOCAL_DIR/dataset_finetuning_$TS.jsonl"
if [ -f "$LOCAL" ] && cmp -s "$SRC" "$LOCAL"; then
  echo "$(date) [local] inchangé ($LOCAL)"
else
  cp -p "$SRC" "$LOCAL"
  echo "$(date) [local] backup -> $LOCAL ($(wc -c < "$SRC") bytes)"
fi

# --- 2) Copie Drive (best-effort) ---
mkdir -p "$DRIVE_DIR" 2>/dev/null
DRIVE="$DRIVE_DIR/dataset_finetuning_$TS.jsonl"
if [ -f "$DRIVE" ] && cmp -s "$SRC" "$DRIVE"; then
  echo "$(date) [drive] déjà à jour ($DRIVE)"
  exit 0
fi
if cp -p "$SRC" "$DRIVE" 2>/dev/null; then
  echo "$(date) [drive] backup -> $DRIVE ($(wc -c < "$SRC") bytes)"
else
  echo "$(date) [drive] BLOQUÉ par TCC (Full Disk Access requis pour /bin/bash)."
  echo "        → Réglage : Réglages Système > Confidentialité > Accès disque complet > + /bin/bash"
  echo "        → La copie locale reste valide : $LOCAL"
fi
