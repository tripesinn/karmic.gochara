# karmic-gochara Application Context

This document provides a high-level overview of the karmic-gochara application to help AI models understand its structure, purpose, and key components.

## 1. Project Overview

*   **Name:** karmic-gochara
*   **Purpose:** karmic-gochara appears to be a comprehensive application focused on astrological calculations, transit alerts, and potentially related services. It seems to integrate astrological data and calculations with user-facing applications, possibly including mobile and web interfaces.

## 2. Key Features & Components

*   **Astrological Calculations:** Modules for calculating astrological events, transits, and ephemerides (e.g., `astro_calc.py`, `calendar_calc.py`, `swisseph_ctypes.py`).
*   **Transit Alerts:** Functionality to generate and manage astrological transit alerts (`transit_alerts.py`, `transit-alert.agent.yaml`).
*   **Core Services/Vault:** Central logic or data storage for the application (`karmic_vault`, `karmic-gochara-agent.skill`, `karmic-master.agent.yaml`).
*   **Mobile Application:** Support for Android mobile development, including native components and Capacitor for cross-platform capabilities (`android/`, `capacitor.config.json`).
*   **Web Interface:** Components for a web landing page and application (`www/index.html`, `karmic-landing.html`).
*   **AI/Agent Integration:** Use of agents and potential integration with AI models (`.agent.yaml` files, `gemini_api.py`, `test-and-fix-agent.agent.yaml`).
*   **Python Backend/Scripts:** A significant portion of the application logic is written in Python.

## 3. Technologies Stack (Inferred)

*   **Language:** Python, JavaScript, QML, Java/Kotlin (for Android)
*   **Frameworks/Libraries:**
    *   Python: `swisseph` (for ephemeris data), likely others for web/API if any.
    *   Web: HTML, CSS, JavaScript, potentially a frontend framework (implied by `package.json`).
    *   Mobile: Capacitor, Android SDK.
*   **Build/Dependencies:** `requirements.txt` (Python), `package.json` (Node.js/Web), Gradle (Android).

## 4. Directory Structure Highlights

*   `android/`: Native Android project files.
*   `www/`: Web application assets.
*   `static/`: Static web assets.
*   `templates/`: HTML templates for web pages.
*   `.gemini/`: Configuration and skills for Gemini CLI.
*   `scripts/`: Utility scripts.
*   `karmic_vault/`: Potential core application logic or data.

## 5. Important Files

*   `README.md`: Project overview and setup instructions.
*   `requirements.txt`: Python project dependencies.
*   `package.json`: Node.js/Web project dependencies.
*   `app.py`: Likely a main entry point for a Python application or backend service.
*   `GEMINI.md`: Project-specific instructions for Gemini CLI.

This file aims to provide a comprehensive yet concise overview for understanding the karmic-gochara project.
