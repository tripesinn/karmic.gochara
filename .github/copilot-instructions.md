# Copilot Instructions — Karmic Gochara

> **Vedic Astrology AI Synthesis Engine** — Flask + Capacitor mobile web app combining Swiss Ephemeris calculations with Claude AI narrative synthesis using a custom karmic doctrine framework.

---

## **Project Overview**

**Karmic Gochara** generates personalized Vedic astrology (Jyotish) interpretations for natal charts and transits by:
1. Computing planetary positions, houses, and lunar mansions (nakshatras) via Swiss Ephemeris
2. Mapping astrological configurations to karmic doctrine (NAKSHATRA_KARMA in `doctrine.py`)
3. Synthesizing narrative interpretations via Anthropic Claude or local Gemma (Android, test only)
4. Displaying results in French-first UI with Unicode astrological symbols

**Tech Stack**: Flask 3.0 + Gunicorn | Vanilla JS + Capacitor 8.3 | Android (Gradle) | Swiss Ephemeris | Claude API + Gemma

**Key Uniqueness**: Non-standard Vedic choices — Djwhal Khul ayanamsa, Chandra Lagna (Moon-based ascendant), no database, French-language esoteric framing.

---

## **Architecture Overview**

```
USER (Browser / Android Capacitor WebView)
    ↓
FRONTEND: templates/index.html (Jinja2 → www/index.html)
    ├─ Form: Input birth date, location
    ├─ JS handlers: fetch /calculate → astro_calc → doctrine
    └─ GemmaSynthesis (Capacitor plugin, test only)
    ↓
BACKEND: Flask (app.py)
    ├─ /calculate: Compute planetary positions + doctrine mappings
    ├─ /send_synthesis: Claude API call with karmic_vault context
    ├─ /login, /register: Session-based auth (no JWT, no DB)
    └─ Multi-language routing (FR/EN templates)
    ↓
PYTHON MODULES
    ├─ astro_calc.py → Swiss Ephemeris wrapper (planets, houses, nakshatras)
    ├─ doctrine.py → Nakshatra karma mappings + pillar semantics (LLM source of truth)
    ├─ ai_interpret.py → Claude API synthesis + karmic_vault context injection
    ├─ calendar_calc.py, profiles.py, transit_alerts.py
    └─ swisseph_ctypes.py → Direct PySwisseph bindings
    ↓
EXTERNAL SERVICES
    ├─ Anthropic Claude (synthesis)
    ├─ Google Geocoding API (location search)
    └─ Google Sheets (credentials.json) → user profiles (optional)
    ↓
ANDROID (Capacitor)
    ├─ capacitor.config.json → plugin registry
    ├─ GemmaSynthesisPlugin.java → MediaPipe GenAI (local Gemma)
    └─ MainActivity.java → registerPlugin (GemmaSynthesisPlugin)
```

---

## **Key Files & Responsibilities**

| File | Purpose | Key Sections |
|------|---------|---|
| **app.py** | Flask backend, routes, auth | `/calculate` (line ~698), `/send_synthesis` (line ~804), session validation |
| **astro_calc.py** | Swiss Ephemeris calculations | `compute_chart()`, `get_nakshatra()`, `get_houses()` |
| **doctrine.py** | **Centralized source of truth for astrological meanings** | `NAKSHATRA_KARMA` dict, `PILLAR_MEANINGS` (must be edited for new doctrine) |
| **ai_interpret.py** | Claude API synthesis logic | `build_system_prompt()`, `fetch_synthesis()` (injects karmic_vault context) |
| **templates/index.html** | Jinja2 frontend (rendered to www/index.html) | Form handlers (line ~413), GemmaSynthesis integration (line ~629) |
| **render_static.py** | Build step: generates www/index.html from templates/ | Extracts LANGS, renders Jinja2 |
| **capacitor.config.json** | Mobile config: plugins, webDir, app ID | `webDir: www`, GemmaSynthesis plugin registration |
| **requirements.txt** | Python dependencies | Flask, Gunicorn, Anthropic, PySwisseph, Pytz, etc. |
| **render.yaml** | Render.com deployment spec | Build/run commands, env vars, Node/Python versions |
| **package.json** | Node dependencies | Capacitor packages only (no frontend framework) |

### **Doctrine Module (doctrine.py) — Extend Here for New Meanings**

```python
NAKSHATRA_KARMA = {
    "Ashwini (Mercury)": {
        "ROM_loop": "Running in circles...",
        "RAM_process": "Healing through speed...",
        "DHARMA_shift": "Breakthrough via consciousness..."
    },
    # ... 26 more nakshatras
}

HOUSE_MEANINGS = {
    "1": {"FR": "L'incarnation", "EN": "The Incarnation"},
    # ... 12 houses
}

PILLAR_MEANINGS = {
    "Pillar 1": {
        "Ketu": "Static memory (ROM), karmic past",
        "Rahu": "Future dharma, unconscious pull"
    },
    # ... 5 more pillars
}
```

**To add new astrological meanings**: Edit `doctrine.py`, add entries, test with `/calculate`.

---

## **Karmic Vault (Doctrine Context for LLM)**

Located: `karmic_vault/` (test version: `karmic.gochara.test/karmic.gochara/karmic_vault/`)

**Three files injected into Claude system prompt** (~2500 tokens total):
1. **00_MASTER_CONTEXT.md** — Meta-instructions: "You are a Vedic astrology oracle. Synthesize the chart using these 6 pillars. Output ONLY the oracle text—no technical labels, no degrees."
2. **01_output_rules.md** — Strict format constraints:
   - Each pillar: `**[BLOCAGE ACTIF]**` (2 sentences) + `**[ALTERNATIVE DE CONSCIENCE]**` (1 imperative)
   - No numbers, no technical symbols, oracular tone
3. **02_planet_keywords.md** — Planet + nakshatra keywords for semantic grounding

**To modify LLM output behavior**: Edit these files; do NOT hardcode in `ai_interpret.py`.

---

## **Build & Run Commands**

### **Local Web Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app (http://localhost:5000)
python app.py

# Generate static www/index.html for Capacitor (only after editing templates/index.html)
python render_static.py
```

### **Local Web Testing (with Gunicorn, like production)**
```bash
pip install gunicorn
gunicorn app:app --bind 127.0.0.1:5000 --workers 1 --reload
```

### **Android Development**
```bash
# Install Node dependencies
npm install

# Sync Capacitor plugins
npx cap sync

# Open Capacitor project in Android Studio
npx cap open android

# Run on device/emulator
npx cap run android

# After editing www/index.html: re-sync
npx cap sync
```

### **Deployment (Render.com)**
```bash
# Auto-triggered on push to GitHub (render.yaml)
# Build: npm install && pip install -r requirements.txt
# Run: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

---

## **Environment Variables**

**Required for production**:
- `ANTHROPIC_API_KEY` — Anthropic Claude API key
- `GOOGLE_SHEETS_API_KEY` (optional) — For user data persistence

**Development toggles** (test version only):
- `ENABLE_LOCAL_AI=1` → Use Gemma plugin (Android only)
- `ENABLE_LOCAL_AI=0` → Use Claude API (production safe)
- `ENABLE_FEATURES=1` → Enable calendar_calc, annual_report modules

---

## **Development Workflow**

### **Adding New Astrological Calculations**
1. **Add to `astro_calc.py`**: Extend `compute_chart()` with new Swift Ephemeris calls
2. **Add meanings to `doctrine.py`**: Map results to NAKSHATRA_KARMA, HOUSE_MEANINGS, or PILLAR_MEANINGS
3. **Test locally**: `python app.py`, POST to `/calculate` with test birth data
4. **Front-end integration**: Update `templates/index.html` to display new fields

### **Modifying LLM Output**
1. **Edit `karmic_vault/00_MASTER_CONTEXT.md`** — Meta-prompt changes
2. **Edit `karmic_vault/01_output_rules.md`** — Output format/tone changes
3. **Edit `karmic_vault/02_planet_keywords.md`** — Add semantic keywords
4. **Test in `/send_synthesis`** — Call Claude with new context

### **Updating Frontend**
1. **Edit `templates/index.html`** (Jinja2 template with Python variable injection)
2. **Run `python render_static.py`** → Generates `www/index.html`
3. **Test: `python app.py`** (local), then **`npx cap sync && npx cap run android`** (mobile)
4. **Commit both `templates/index.html` and `www/index.html`**

### **GemmaSynthesis Plugin (Local AI, Test Only)**
- **File**: `android/app/src/main/java/com/karmicgochara/app/GemmaSynthesisPlugin.java`
- **Method**: `generate(systemPrompt, userPrompt)` → Runs Gemma inference locally
- **JS API**: `Gemma.generate(systemPrompt, userPrompt)` in `www/index.html`
- **Prod**: Set `ENABLE_LOCAL_AI=0` to disable, fallback to Claude API

---

## **Design Principles**

1. **Stateless Backend** — No database; use Google Sheets or localStorage for persistence
2. **Doctrine as Config** — All astrological meanings live in `doctrine.py`, not hardcoded in templates
3. **Jinja2 for Multi-Language** — UI strings injected at render time (LANGS dict)
4. **Vanilla JS + Capacitor** — No frontend framework; full control over mobile integration
5. **Claude as Oracle Generator** — LLM synthesizes meanings, not generates calculations
6. **Karmic Vault as LLM Guide** — Context files (karmic_vault/) shape Claude's output, not code
7. **French-First Esoteric Framing** — All planetary labels, nakshatra names, UI copy in French with Unicode symbols

---

## **Common Tasks**

### **Q: How do I add a new planetary influence?**
**A:** 
1. Compute it in `astro_calc.py` (add to `compute_chart()` return dict)
2. Add karma meanings to `doctrine.py` (NAKSHATRA_KARMA or new dict)
3. Add display logic to `templates/index.html`
4. Run `python render_static.py`
5. Test: `python app.py → /calculate`

### **Q: How do I change astrological house system?**
**A:**
1. Edit `astro_calc.py` — modify `get_houses()` function (currently uses Chandra Lagna)
2. Update `doctrine.py` → HOUSE_MEANINGS if interpretations change
3. Test: `python app.py`, POST /calculate with test birth data

### **Q: How do I fix the LLM output format?**
**A:** Edit `karmic_vault/01_output_rules.md` — redefine output constraints; Claude will respect them. Do NOT change `ai_interpret.py`.

### **Q: How do I test on Android?**
**A:**
```bash
npx cap sync          # Copy www/ to Android
npx cap open android  # Open Android Studio
# Build & run from Android Studio, or:
npx cap run android
```

### **Q: How do I add a new user field?**
**A:**
1. Edit `templates/index.html` — add form field
2. Edit `app.py` — extract form data in /calculate or /register
3. Edit `doctrine.py` if it affects astrological interpretation
4. Run `python render_static.py` → sync Capacitor

### **Q: How do I deploy to Render?**
**A:** 
1. Push to GitHub
2. Render auto-deploys via `render.yaml` (build: pip install + npm install, run: gunicorn)
3. Check logs on Render dashboard

---

## **Gotchas & Pitfalls**

| Pitfall | Fix |
|---------|-----|
| **Edited `templates/index.html` but changes don't show** | Run `python render_static.py` to regenerate `www/index.html`; both files must be committed |
| **Gemma plugin fails on device** | Check `ENABLE_LOCAL_AI=1` env var; ensure MediaPipe GenAI model is downloaded on device |
| **Claude API returns wrong format** | Edit `karmic_vault/01_output_rules.md` to clarify constraints; test with `/send_synthesis` directly |
| **Render cold starts (~30sec after 15min inactivity)** | Expected on free tier; use paid plan or accept latency |
| **Swiss Ephemeris calculations differ from online tools** | Check: ayanamsa (Djwhal Khul 28.0°), house system (Chandra Lagna), node type (True) |
| **Mobile GemmaSynthesis not available** | Fallback to Claude API; ensure `Plugins.GemmaSynthesis` registered in Android |
| **Astrology looks "wrong" (degree positions off)** | Document exact date/time/location; could be:ayanamsa setting, timezone, Chandra Lagna, or Swiss Eph version |

---

## **File Organization—at a Glance**

```
karmic.gochara/
├─ app.py                          ← Flask backend (main entry point)
├─ astro_calc.py                  ← Astrology calculations
├─ doctrine.py                    ← Astrological meanings (EDIT THIS for doctrine)
├─ ai_interpret.py                ← Claude synthesis logic
├─ templates/
│  └─ index.html                  ← Jinja2 frontend (EDIT, then render_static.py)
├─ www/
│  └─ index.html                  ← Static web (generated from templates/)
├─ android/
│  └─ app/src/main/java/com/karmicgochara/app/
│     ├─ GemmaSynthesisPlugin.java ← Local AI (Gemma MediaPipe)
│     └─ MainActivity.java         ← Android entry point
├─ karmic_vault/
│  ├─ 00_MASTER_CONTEXT.md        ← LLM meta-prompt
│  ├─ 01_output_rules.md          ← LLM output constraints (EDIT for format changes)
│  └─ 02_planet_keywords.md       ← LLM semantic guide
├─ static/
│  ├─ manifest.json               ← PWA metadata
│  ├─ sw.js                       ← Service worker
│  └─ icons/                      ← App icons
├─ capacitor.config.json          ← Mobile config
├─ package.json                   ← Node dependencies
├─ requirements.txt               ← Python dependencies
├─ render.yaml                    ← Render deployment config
├─ DEPLOIEMENT.md                 ← Deployment guide (French)
├─ render_static.py               ← Build: templates → www/
└─ credentials.json               ← Google API credentials (gitignored)
```

---

## **Testing Checklist**

Before committing:
- [ ] **Python**: `pip install -r requirements.txt && python app.py` → http://localhost:5000 works
- [ ] **Astro calcs**: POST to `/calculate` with test birth data; numbers match doctrine.py expectations
- [ ] **Frontend**: `python render_static.py` completed; `www/index.html` updated
- [ ] **Claude API**: `ANTHROPIC_API_KEY` set; `/send_synthesis` returns oracle text in correct format
- [ ] **Android**: `npx cap sync && npx cap run android` builds & runs on device/emulator
- [ ] **Production template**: Check both `templates/index.html` and `www/index.html` committed
- [ ] **Karmic vault**: `karmic_vault/*.md` files in sync with expected LLM behavior

---

## **Related Documentation**

- **[DEPLOIEMENT.md](DEPLOIEMENT.md)** — Step-by-step Render.com deployment guide (French)
- **[CHANGES.md](CHANGES.md)** — Recent modifications & feature log
- **[render.yaml](render.yaml)** — Deployment config; edit for new env vars or build commands
- **[doctrine.py](doctrine.py)** — Complete astrological doctrine mappings; _modify here_ for new meanings
- **Anthropic Docs** — https://docs.anthropic.com (Claude API reference)
- **SwissEphemeris Docs** — https://pyswisseph.readthedocs.io/ (astro calculation reference)

---

## **Quick Start for Contributing**

```bash
# 1. Clone & setup
git clone https://github.com/tripesinn/karmic.gochara.git
cd karmic.gochara
pip install -r requirements.txt
npm install

# 2. Set env var
export ANTHROPIC_API_KEY="your-api-key-here"

# 3. Run locally
python app.py
# → http://localhost:5000

# 4. Edit code
# - Backend astro calcs: astro_calc.py
# - Astrological meanings: doctrine.py ← MAIN SOURCE OF TRUTH
# - Frontend: templates/index.html (then run render_static.py)
# - LLM output: karmic_vault/*.md

# 5. Generate static frontend
python render_static.py

# 6. Test Android (optional)
npx cap sync
npx cap run android

# 7. Deploy (automatic via GitHub push)
git push origin main
# → render.yaml triggers Render deployment
```

---

## **Questions?**

- **Astrological system**: Check `doctrine.py` for Djwhal Khul ayanamsa (28.0°) and Chandra Lagna house system
- **LLM output**: Edit `karmic_vault/01_output_rules.md`
- **Calculations**: Reference `astro_calc.py` and Swiss Ephemeris docs
- **Deployment**: See `render.yaml` and `DEPLOIEMENT.md`
