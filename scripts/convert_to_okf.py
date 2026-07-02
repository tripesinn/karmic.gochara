import os
import re
from datetime import datetime

VAULT_DIR = "/Users/jero87/karmic.gochara/karmic_vault"
OKF_DIR = os.path.join(VAULT_DIR, "okf")

os.makedirs(OKF_DIR, exist_ok=True)
os.makedirs(os.path.join(OKF_DIR, "planets"), exist_ok=True)
os.makedirs(os.path.join(OKF_DIR, "aspects"), exist_ok=True)
os.makedirs(os.path.join(OKF_DIR, "nakshatras"), exist_ok=True)

def clean_key(name):
    # Convert name to safe lowercase filename key
    name = name.lower()
    name = re.sub(r"[\s\(\)☋☊⚷⚸♄♃♅℞]+", "_", name)
    name = name.strip("_")
    return name

def parse_planet_keywords():
    filepath = os.path.join(VAULT_DIR, "02_planet_keywords.md")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    content = open(filepath, "r", encoding="utf-8").read()
    
    # Split content into lines and group by planet/aspect block
    lines = content.split("\n")
    
    current_concept = None
    concept_lines = []
    
    # We will match lines like "**Pluton**" or "**Ketu (Nœud Sud ☋)**" or "**Conjonction**"
    # Note that planets/aspects are under different sections: PLANÈTES, NŒUDS, ASPECTS
    current_section = "planets"
    
    for line in lines:
        if line.startswith("## PLANÈTES") or line.startswith("## NŒUDS"):
            if current_concept:
                save_concept(current_concept, current_section, concept_lines)
                current_concept = None
            current_section = "planets"
        elif line.startswith("## ASPECTS"):
            if current_concept:
                save_concept(current_concept, current_section, concept_lines)
                current_concept = None
            current_section = "aspects"
        
        # Check for planet/aspect header like "**Pluton**" or "**Ketu ...**"
        match = re.match(r"^\*\*(.*?)\*\*(?:\s*:\s*(.*))?$", line.strip())
        if match:
            # Save previous concept if exists
            if current_concept:
                save_concept(current_concept, current_section, concept_lines)
            
            name = match.group(1).strip()
            desc = match.group(2).strip() if match.group(2) else ""
            current_concept = name
            concept_lines = []
            if desc:
                concept_lines.append(desc)
        elif current_concept is not None:
            # If empty line and we just started, ignore
            if not line.strip() and not concept_lines:
                continue
            # Accumulate lines
            concept_lines.append(line)
            
    # Save last concept
    if current_concept:
        save_concept(current_concept, current_section, concept_lines)

def save_concept(name, section, body_lines):
    key = clean_key(name)
    title = name.split("(")[0].strip() # Clean name for title, e.g., "Ketu" from "Ketu (Nœud Sud ☋)"
    
    body = "\n".join(body_lines).strip()
    # Extract first sentence or line as description if not empty
    desc = body.split("\n")[0] if body else ""
    desc = re.sub(r"\*\*|__", "", desc).strip()
    if len(desc) > 100:
        desc = desc[:97] + "..."
        
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    type_name = "Astrological Planet" if section == "planets" else "Astrological Aspect"
    tags = [section, key]
    
    okf_content = f"""---
type: {type_name}
title: {title}
description: {desc}
tags: {tags}
timestamp: {timestamp}
---

# {title}

{body}
"""
    
    out_path = os.path.join(OKF_DIR, section, f"{key}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(okf_content)
    print(f"Saved {type_name} OKF: {out_path}")

def parse_nakshatra_keywords():
    filepath = os.path.join(VAULT_DIR, "07_nakshatra_keywords.md")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    content = open(filepath, "r", encoding="utf-8").read()
    
    # Split by the horizontal line separator
    blocks = content.split("---")
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Look for headers like "### 1. Ashwini | Ketu | ROM_oppression"
        match = re.search(r"^###\s*(\d+)\.\s*([a-zA-Z\s]+)\s*\|", block)
        if match:
            num = match.group(1)
            name = match.group(2).strip()
            key = clean_key(name)
            
            # Find description
            desc_match = re.search(r"-\s*\*\*Essence\*\*\s*:\s*(.*)", block)
            desc = desc_match.group(1).strip() if desc_match else f"Nakshatra {name}"
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            okf_content = f"""---
type: Astrological Nakshatra
title: {name}
number: {num}
description: {desc}
tags: [nakshatra, {key}]
timestamp: {timestamp}
---

{block}
"""
            out_path = os.path.join(OKF_DIR, "nakshatras", f"{key}.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(okf_content)
            print(f"Saved Nakshatra OKF: {out_path}")

if __name__ == "__main__":
    parse_planet_keywords()
    parse_nakshatra_keywords()
    print("OKF Conversion Complete!")
