#!/usr/bin/env python3
"""E2E proof harness: read a Karmic Gochara mention, ask Grok, reply via xurl.
Mirrors the live bot (imports x_bot_xurl funcs — single source).
DRY_RUN=1 (default): computes + shows Grok reply but does NOT write to X.
DRY_RUN=0: also posts the xurl reply. Author: Hermes sub-agent (AGY profile).
"""
import os, sys, json
sys.path.insert(0, "/Users/jero87/karmic.gochara")
import x_bot_xurl as B

DRY = os.environ.get("DRY_RUN", "1") == "1"

if __name__ == "__main__":
    root_id = sys.argv[1] if len(sys.argv) > 1 else "2076465504215073140"
    # Read the target tweet (read-only xurl call)
    try:
        tweet = B.xurl_json("read", root_id)["data"]
    except Exception as e:
        print("READ_ERR", e); sys.exit(1)
    print(f"[target] {root_id}: {tweet['text']!r}")

    ud = B.parse_user_request(tweet["text"])
    if not ud:
        print("PARSE_FAIL — format non reconnu"); sys.exit(1)
    print(f"[parsed] {ud}")

    try:
        prompt, kdata = B.generate_karmic_data(ud)
    except Exception as e:
        print("KARMIC_ERR", e); sys.exit(1)
    print("[theme] calculé")

    ai = B.call_grok(prompt, kdata)
    if not ai:
        print("[RESULT] GUARD REJET -> aucun envoi (attendu, on n'écris pas)")
        sys.exit(0)
    print(f"[GROK] {ai}")

    if DRY:
        print("[DRY] write skipped (DRY_RUN=1)")
    else:
        B.xurl("reply", root_id, f"{ai}\n\nMP envoyé 🔑")
        print("[WRITE] reply posté via xurl")
