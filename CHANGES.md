# Changes to index.html for Task Data Integration

## Overview

This document describes the changes made to `index.html` to silently fetch `/generate_task` after login success, store the JSON response in a JavaScript variable `taskData`, and call `GemmaSynthesis.initializeTask()` with the payload.

## Changes Made

### 1. Global Storage for Task Data

Added global variable to store task data:
```javascript
window.taskData = null; // sera rempli après login
```

### 2. Modified Login Function

Updated the login function to:
- Store the task data globally in `window.taskData`
- Store the task data in `localStorage` for persistence across page reloads
- Call `GemmaSynthesis.initializeTask()` with the payload
- Call the natal and transit hooks with the task data
- Use `showLoggedInUI()` instead of reloading the page

### 3. Modified Register Function

Updated the register function to:
- Make it async to support await operations
- Fetch task data after registration
- Store the task data globally and in localStorage
- Call `GemmaSynthesis.initializeTask()` with the payload
- Call the natal and transit hooks with the task data
- Use `showLoggedInUI()` instead of reloading the page

### 4. Added showLoggedInUI Function

Created a new function to handle UI transitions after login:
```javascript
function showLoggedInUI() {
    const heroSection = document.getElementById('hero-section');
    const appSection = document.getElementById('app-section');
    
    if (heroSection) heroSection.style.display = 'none';
    if (appSection) appSection.style.display = 'block';
    
    // Populate user name if available
    const nameEl = document.getElementById('user-name-display');
    const savedProfile = localStorage.getItem('gochara_profile');
    if (nameEl && savedProfile) {
        const profile = JSON.parse(savedProfile);
        nameEl.textContent = profile.pseudo || profile.name;
    }
}
```

### 5. Added Natal and Transit Hooks

Created two new functions to process natal and transit data:
```javascript
function natalHook(data) {
    if (!data || !data.gemma_payload || !data.gemma_payload.natal) {
        console.log("No natal data available");
        return;
    }
    
    const natal = data.gemma_payload.natal;
    console.log("Natal hook processing data", natal);
    
    // Update hero-hook with natal insights if available
    const hookEl = document.querySelector('.hero-hook');
    if (hookEl) {
        // Keep the existing structure but potentially update content based on natal data
        const ketuHouse = natal.ketu_house;
        const chironHouse = natal.chiron_house;
        const ketuNak = natal.nakshatra_ketu;
        const chironNak = natal.nakshatra_chiron;
        
        console.log(`Natal data: Ketu in H${ketuHouse} (${ketuNak}), Chiron in H${chironHouse} (${chironNak})`);
    }
}

function transitHook(data) {
    if (!data || !data.gemma_payload || !data.gemma_payload.transit_actif) {
        console.log("No transit data available");
        return;
    }
    
    const transit = data.gemma_payload.transit_actif;
    console.log("Transit hook processing data", transit);
    
    // Update transit-related UI elements
    const planet = transit.planet;
    const house = transit.house;
    const aspect = transit.aspect;
    const target = transit.target;
    
    console.log(`Active transit: ${planet} in H${house} ${aspect} ${target}`);
}
```

### 6. Updated DOMContentLoaded Event Handler

Modified the event handler to restore task data from localStorage:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // Existing code...
    
    // Restore taskData if available
    const savedTaskData = localStorage.getItem('gochara_taskData');
    if (savedTaskData) {
        try {
            window.taskData = JSON.parse(savedTaskData);
            // Call hooks with restored data
            natalHook(window.taskData);
            transitHook(window.taskData);
        } catch (e) {
            console.error("Error restoring taskData", e);
        }
    }
});
```

## Benefits

1. **Silent Operation**: No visible spinner during the fetch process
2. **Data Persistence**: Task data is stored and available across page reloads
3. **Efficiency**: Data is fetched once and reused for both natal and transit hooks
4. **Modularity**: Separate hook functions make the code more maintainable

## Future Enhancements

1. Enhance the natal and transit hooks to update the UI with more specific data
2. Add error handling for cases where the task data is incomplete or malformed
3. Implement caching strategies to reduce server load
4. Add visual indicators when hooks are successfully processed
## Beta Release & Freemium Adjustments (May 2026)

### 1. Freemium vs Pro Access
- Renamed "Signal du Jour" (Daily Signal) to **"Daily Reading"**.
- Locked the **Natal Reading** exclusively to the Pro plan. Freemium users only see the Daily Reading.
- In the current closed beta phase, all new users are automatically granted the `pro` plan in `profiles.py` to allow full testing without manual upgrades.

### 2. Terminology Updates
- Replaced "Dharma" with **"The Stage"** (La Scène) as the third pillar of the doctrine to avoid confusion. The three pillars are now: Karmic Memory, Core Wound, and The Stage.

### 3. Translation & Caching Fixes
- Fixed a bug where the cached `hook_natal` and `hook_transit` were not language-aware. The cache keys in `app.py` now include the `lang` parameter (e.g., `hook_natal_{pseudo}_{lang}`).
- Added missing translations in `app.py` and `index.html` for `hero_eyebrow` (e.g., `@siderealAstro13 · Karmic Astrology`), `doctrine_pro` (The Doctrine), and `return_app`.

### 4. Deployment
- The app is currently deployed and running on Google Cloud Run (`gochara-api`).

## Beta Release & Freemium Adjustments (May 2026)
*(Continuing previous section)*

### 5. AI Assistant Ecosystem (karmic-gochara-plugin)
- Set up a customized **karmic-gochara-plugin** for the local LLM/Agentic ecosystem.
- Integrated various agentic skills specific to this codebase including `api-design-principles`, `architecture`, `backend-dev-guidelines`, `frontend-developer`, `python-fastapi-development`, and `typescript-expert` to structure our development workflows effectively.
