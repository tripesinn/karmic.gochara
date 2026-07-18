#!/usr/bin/env python3
# finetune_kg.py — Pipeline fine-tune Karmic Gochara (doctrine @siderealAstro13)
#
# CONTEXTE ARCHI (décisif, vérifié 2026-07-18):
#   litertlm-android:latest.release (0.14.0) N'EXPOSE PAS d'API LoRA runtime
#   (issue LiteRT-LM #1188 : feature request, PR #2508 pas encore dans la release).
#   => On ne peut PAS charger un adapter .bin à l'inférence sur le Pixel.
#   => L'artefact valide est un .litertlm PRÉ-MERGÉ (LoRA fusionné dans le base
#      Gemma-4-E2B-it OFFLINE), qui REMPLACE le modèle de base sur le device.
#      Aucun changement de code de chargement côté app : le plugin charge le
#      merged .litertlm exactement comme le base actuel (backend CPU).
#   => Le nom LORA_ASSET_PATH="lora/doctrine_adapter.bin" du plugin est donc
#      OBSOLÈTE (il visait un runtime LoRA mort-né). Le merged model prend la
#      place du fichier gemma-4-E2B-it.litertlm.
#
# SOUS-COMMANDES:
#   filter   -> filtre dataset_finetuning.jsonl -> dataset_train_clean.jsonl
#               (garde uniquement les lignes {messages:[system,user,assistant]};
#                droppe les lignes {user_id,rating,soul_debug}). Pure stdlib,
#                exécutable partout (macOS 3.9.6 inclus).
#   train    -> (guardé) LoRA sur Gemma-4-E2B via PEFT/unsloth -> lora/doctrine_adapter/
#   merge    -> (guardé) bake LoRA -> .litertlm via google.ai.edge litert-model-cpp
#   deploy   -> (guardé) push le merged .litertlm sur le Pixel (adb) + note maj sha256
#
# Usage:
#   python3 finetune_kg.py filter
#   python3 finetune_kg.py train   --base HF_ID --out lora/doctrine_adapter
#   python3 finetune_kg.py merge   --base chemin/base.litertlm --adapter lora/doctrine_adapter --out doctrine_adapter_merged.litertlm
#   python3 finetune_kg.py deploy  --merged doctrine_adapter_merged.litertlm --serial 55161FDCH0004E

import sys, os, json, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(ROOT, "dataset_finetuning.jsonl")
CLEAN   = os.path.join(ROOT, "dataset_train_clean.jsonl")

ROLES = {"system", "user", "assistant"}


def is_valid_messages(obj):
    """Retourne True si obj = {messages:[{role,content}...]} avec system+user+assistant."""
    if not isinstance(obj, dict):
        return False
    msgs = obj.get("messages")
    if not isinstance(msgs, list) or not msgs:
        return False
    roles = set()
    for m in msgs:
        if not isinstance(m, dict):
            return False
        r = m.get("role"); c = m.get("content")
        if r not in ROLES or not isinstance(c, str):
            return False
        roles.add(r)
    return {"system", "user", "assistant"}.issubset(roles)


def cmd_filter():
    kept = 0
    dropped = 0
    with open(DATASET, "r", encoding="utf-8") as f, \
         open(CLEAN, "w", encoding="utf-8") as out:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                dropped += 1
                continue
            if is_valid_messages(obj):
                out.write(json.dumps(obj, ensure_ascii=False) + "\n")
                kept += 1
            else:
                dropped += 1
    print(f"[filter] {kept} lignes conservées (messages complets) -> {CLEAN}")
    print(f"[filter] {dropped} lignes ignorées (ratings / incomplets)")


def _require(module, hint):
    try:
        return __import__(module)
    except ImportError:
        sys.exit(f"[guard] module '{module}' requis. Installe: {hint}")


def cmd_train(args):
    _require("torch", "pip install torch")
    _require("transformers", "pip install transformers")
    _require("peft", "pip install peft")
    # Lancement PEFT LoRA sur base Gemma-4-E2B (HF_ID).
    # (Implémentation complète côté GPU box — voir doc export.)
    print("[train] base=", args.base, "out=", args.out)
    print("[train] NON EXÉCUTÉ ici (nécessite GPU + deps). Lancer sur la box d'entraînement.")
    print("[train] Exemple PEFT:")
    print("   from peft import LoraConfig, get_peft_model")
    print("   LoraConfig(r=16, lora_alpha=32, target_modules=['q_proj','v_proj'], task_type='CAUSAL_LM')")
    print("   trainer.train() -> adapter sauvegardé dans", args.out)


def cmd_merge(args):
    litert = _require("litert_model_cpp", "pip install litert-model-cpp  (Google AI Edge)")
    print(f"[merge] base={args.base} adapter={args.adapter} -> {args.out}")
    print("[merge] NON EXÉCUTÉ ici (nécessite litert-model-cpp + base .litertlm).")
    print("[merge] Commande cible (Google AI Edge LoRA bake):")
    print(f"   litert_model_cpp bake_lora --checkpoint {args.adapter} --base {args.base} --output {args.out}")
    print("[merge] Le .litertlm résultant REMPLACE gemma-4-E2B-it.litertlm sur le Pixel.")


def cmd_deploy(args):
    merged = args.merged
    if not os.path.exists(merged):
        sys.exit(f"[deploy] merged introuvable: {merged}")
    serial = args.serial
    # Push du merged model à la place du base (même chemin résolu par resolveModelPathSilently)
    remote = "/sdcard/Android/data/com.karmicgochara.app/files/Download/gemma-4-E2B-it.litertlm"
    print(f"[deploy] adb -s {serial} push {merged} {remote}")
    print("[deploy] ⚠️  MAJ OBLIGATOIRE dans GemmaSynthesisPlugin:")
    print("   EXPECTED_MODEL_SHA256 = sha256(<merged>)  (sinon isValidModel le rejette silencieusement)")
    print("   EXPECTED_MODEL_SIZE   = taille(<merged>)  (si différente de 2588147712)")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("filter")
    pt = sub.add_parser("train"); pt.add_argument("--base", required=True); pt.add_argument("--out", required=True)
    pm = sub.add_parser("merge"); pm.add_argument("--base", required=True); pm.add_argument("--adapter", required=True); pm.add_argument("--out", required=True)
    pd = sub.add_parser("deploy"); pd.add_argument("--merged", required=True); pd.add_argument("--serial", default="55161FDCH0004E")
    args = p.parse_args()
    {"filter": lambda a: cmd_filter(), "train": cmd_train, "merge": cmd_merge, "deploy": cmd_deploy}[args.cmd](args)


if __name__ == "__main__":
    main()
