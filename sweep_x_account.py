#!/usr/bin/env python3
"""Full X account sweep -> local DeepSeek offload.

Fetches every surface via xurl (raw JSON saved to files, never into agent
context), then offloads each to local DeepSeek (8889) for a concise summary.
Writes a single consolidated report. Run in background (DeepSeek is slow).
"""
import subprocess, os, sys, datetime

SKILL_SCRIPTS = "/Users/jero87/.hermes/profiles/karmic_gochara/skills/social-media/x-account-ingest-local/scripts"
sys.path.insert(0, SKILL_SCRIPTS)
from summarize_x import summarize  # DeepSeek offload

UID = "1604336612929839105"
OUT = "/Users/jero87/karmic.gochara"

surfaces = [
    ("tweets", f"xurl /2/users/{UID}/tweets",
     "Summarize the THEMES and TOPICS of my own tweets. List recurring motifs, "
     "any promotion of my app/site (karmicgochara.app), approximate count, and "
     "notable thread styles."),
    ("bookmarks", "xurl bookmarks",
     "Summarize what I bookmark — dominant themes, types of accounts, topics of "
     "interest. Approximate count."),
    ("likes", "xurl likes",
     "Summarize what I like — themes and accounts. Distinguish astrology vs other. "
     "Approximate count."),
    ("followers", "xurl followers",
     "Summarize my follower base — categories of accounts, any notable "
     "astrologers/influencers, approximate count."),
    ("following", "xurl following",
     "Summarize who I follow — categories (competitors, astro peers, tech), "
     "approximate count."),
    ("dms", "xurl dms",
     "Summarize my DMs if any are present."),
    ("mentions", "xurl mentions",
     "Summarize recent mentions of me — who, about what."),
    ("timeline", "xurl timeline",
     "Summarize my home timeline — what content circulates, dominant themes."),
]

report = [f"# X Account Sweep — {datetime.datetime.now():%Y-%m-%d %H:%M}\n"]
ok = 0
for name, cmd, q in surfaces:
    print(f"[fetch] {name} ...", flush=True)
    try:
        raw = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        report.append(f"## {name}\n⚠️ xurl timeout\n")
        continue
    path = os.path.join(OUT, f"x_account_{name}.json")
    with open(path, "w") as f:
        f.write(raw.stdout)
    if (not raw.stdout.strip()
            or '"data":[]' in raw.stdout
            or 'result_count":0' in raw.stdout):
        report.append(f"## {name}\n(empty / no data)\n")
        continue
    print(f"[summarize] {name} via DeepSeek ...", flush=True)
    try:
        s = summarize(path, q)
    except Exception as e:
        report.append(f"## {name}\n⚠️ summarize failed: {e}\n")
        continue
    report.append(f"## {name}\n{s}\n")
    ok += 1

with open(os.path.join(OUT, "x_account_report.md"), "w") as f:
    f.write("\n".join(report))
print(f"DONE: {ok}/{len(surfaces)} surfaces summarized. "
      f"Report -> x_account_report.md", flush=True)
