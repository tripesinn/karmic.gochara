---
name: karmic-build
description: >
  Build and deploy workflow for Karmic Gochara. Executes frontend build, Capacitor sync, and pushes changes to GitHub to trigger Google Cloud Build.
---

# Karmic Gochara Build & Deploy Workflow

## Overview
This skill automates the full deployment cycle for the Karmic Gochara application. It ensures that frontend changes are built and synced to the mobile project (Capacitor), and that backend changes are deployed to Google Cloud Run via a GitHub push.

## Workflow

### 1. Compile Astro and Sync Capacitor
Run the sync script in the `astro` directory. This builds the static site and copies the assets to `android` and `ios`.

```bash
cd astro && npm run sync:capacitor
```

### 2. Commit and Push to GitHub
Since the backend API is hosted on Google Cloud Run and connected to a Cloud Build trigger on the GitHub repository, any backend modifications (Python) or frontend changes must be committed and pushed to `main` to trigger the CI/CD pipeline.

```bash
git add .
git commit -m "feat/fix: <description of changes>"
git push origin main
```

### 3. Verification
Once pushed, inform the user that:
- The mobile assets have been updated locally (ready to run via Android Studio / Xcode).
- The Cloud Build pipeline has been triggered for the backend and will be live in a few minutes.
