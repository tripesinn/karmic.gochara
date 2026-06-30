# Karmic Gochara — État Orchestrateur

> Fichier de persistance inter-sessions.
> Mis à jour par la skill `karmic-orchestrator` à chaque session.
> TOUJOURS lire ce fichier en premier.

---

## État Actuel

**Dernière mise à jour** : 2026-06-30T09:35 (session orchestrateur)

**Build Astro** : ⚠️ STALE — `www/` est un ancien build, `dist/` absent
**Deploy Cloud Run** : ✅ Dernier push connu (build.log confirme push Docker)
**Pixel 10** : ❌ Assets Capacitor pas synchronisés (www/ stale)
**IA Locale (port 8888)** : ❌ DOWN — 507 Insufficient Storage

---

## Bugs Actifs

| ID | Priorité | Description | Cause Racine | Fichier |
|----|----------|-------------|--------------|---------|
| BUG-001 | **P1** | `Unable to open asset URL: /app/chat/index.html` | Page `chat.astro` inexistante dans `src/pages/app/` | À créer |
| BUG-002 | **P2** | LoginCard interceptait `/register` | Guard ajouté ligne 35 (`_path.includes('/register')`) | `LoginCard.astro` ✅ patché |
| BUG-003 | **P2** | `www/` stale — pas rebuild depuis dernières modifs | `LoginCard.astro` modifié mais Astro non rebuild | `npm run build` requis |
| BUG-004 | **P3** | `lecture.astro` ne déclenche pas Gemma | À investiguer (hors scope session courante) | `lecture.astro` |

---

## Architecture Confirmée

```
capacitor.config.json → webDir: "www"   ✅
astro/src/pages/app/ → index, lecture, miroir (chat ABSENT)
www/app/             → index.html, lecture/, miroir/ (chat ABSENT)
```

---

## Séquence de Correction Validée

1. [x] Phase 0 — Diagnostic complet (FAIT)
2. [ ] BUG-001 — Créer `astro/src/pages/app/chat.astro`
3. [ ] Phase 2 — `npm run build` → vérifier dist/app/chat/
4. [ ] Phase 2 — `npm run sync:capacitor` → www/ mis à jour
5. [ ] Phase 4 — Vérifier sur Pixel 10 via adb
6. [ ] Phase 3 — `git add . && git commit && git push`

---

## Historique

### 2026-06-30 — Session orchestrateur
- Skill `karmic-orchestrator` créée
- Fichier d'état créé
- Phase 0 exécutée (IA locale DOWN, diagnostic manuel)
- Bugs P1/P2/P3 identifiés et priorisés
- BUG-002 : LoginCard patché (ligne 35 guard /register)
