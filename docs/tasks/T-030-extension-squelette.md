# T-030 — Squelette extension MV3 + build

- **Statut** : done
- **Priorité** : P1 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : aucune (peut démarrer en parallèle des phases 0-2)

## Objectif

Créer le répertoire `extension/` : manifest MV3, service worker, content
script « hello » minimal, build esbuild intégré à la chaîne frontend
existante. Aucune fonctionnalité produit encore — uniquement la structure qui
compile, se charge et journalise.

## Contexte

Décision DEC-PLAN-03 (`PROJECT_STATE.md`) : l'overlay des pages http(s)
migre de l'injection CDP vers une extension Chrome intégrée. Le build
frontend existe déjà (`frontend/build.mjs`, esbuild, bundles IIFE) et les
composants overlay Lit vivent dans `frontend/src/overlay/` — l'extension les
réutilisera (T-033). L'extension est un artefact du dépôt, chargé par
Synthesix (T-032), jamais publié sur un store.

Périmètre de l'extension (décisions à respecter, `PROJECT_STATE.md`) :
- pages `http/https` uniquement (DEC-PLAN-04) ; jamais `file://` ni pages
  internes Synthesix ;
- les captures restent côté Python/CDP (DEC-PLAN-05) ;
- pas de serveur, pas de dépendance réseau.

## Fichiers concernés

- Nouveaux : `extension/manifest.json`, `extension/src/background.ts`,
  `extension/src/content/bootstrap.ts`, `extension/src/content/focus-guard.ts`
  (vide pour l'instant), `extension/README.md`.
- `frontend/build.mjs` : cibles de build supplémentaires vers
  `extension/dist/` (même esbuild, mêmes conventions).
- `frontend/package.json` : script `build` inchangé, il produit aussi
  l'extension (un seul point d'entrée de build).

## Étapes

1. `manifest.json` (MV3) :
   - `content_scripts` : `matches: ["http://*/*", "https://*/*"]`,
     `js: ["dist/content.js"]`, `run_at: "document_idle"` ;
   - second content script `dist/focus-guard.js` avec `"world": "MAIN"`,
     `"run_at": "document_start"` (Chrome ≥ 111) — vide pour l'instant ;
   - `background.service_worker: "dist/background.js"` ;
   - `permissions: ["storage"]` (minimales ; étendre seulement quand une tâche
     le justifie) ;
   - `web_accessible_resources` : `dist/overlay-main.js` (préparé pour T-033) ;
   - `exclude_matches` à compléter en T-033 (Google Lens/Maps, cf. liste
     `_OVERLAY_BLOCKED_HOST_FRAGMENTS` de `main.py:356`).
2. `background.ts` : service worker qui journalise l'installation et relaie
   les messages `chrome.runtime.onMessage` vers une file interne (structure
   pour T-031/T-034).
3. `bootstrap.ts` : content script qui pose un marqueur
   `document.documentElement.dataset.synthesixExt = version` et écoute les
   messages du SW — rien d'autre.
4. Build : étendre `frontend/build.mjs` (esbuild, TS strict, cibles IIFE pour
   content scripts, ESM pour le SW). Sortie dans `extension/dist/`,
   commit comme les autres bundles (règle AGENTS.md §8).
5. `extension/README.md` : rôle, périmètre, comment charger à la main
   (chrome://extensions → mode développeur → « Charger l'extension non
   empaquetée ») en attendant T-032.
6. Vérification manuelle : charger dans Brave/Chrome, visiter une page http(s),
   vérifier le marqueur DOM et le log SW ; vérifier qu'aucun script ne tourne
   sur `file://`.

## Critères d'acceptation

- `cd frontend && npm run typecheck && npm run build` produit
  `extension/dist/*` sans erreur.
- Extension chargeable non empaquetée ; marqueur présent sur une page https ;
  absent sur les pages `file://` de Synthesix.
- Aucune permission au-delà de `storage`.

## Commandes de test

```powershell
cd frontend; npm run typecheck; npm run build; cd ..
git diff --check
```

Vérification manuelle de chargement (documentée dans `extension/README.md`).

## Risques

- Divergence de versions TS/esbuild entre `frontend/` et `extension/` :
  évitée en réutilisant le même `frontend/package.json` et le même build.
- Choisir trop de permissions « pour plus tard » : refusé — chaque permission
  arrive avec la tâche qui l'exige.

## Résultat 2026-07-07

- `extension/` créé avec manifest MV3, service worker, content script de
  bootstrap, focus-guard main-world vide et placeholder `overlay-main`.
- `frontend/build.mjs` produit `extension/dist/background.js`,
  `content.js`, `focus-guard.js` et `overlay-main.js`.
- `frontend/tsconfig.json` inclut les sources TypeScript de l'extension.
- `.gitignore` laisse `extension/dist/**` versionnable malgré la règle
  globale `dist/`.
- Vérification manuelle de chargement non exécutée dans cette passe ; elle
  reste à faire avant T-031/T-032 si une session Chrome interactive est
  disponible.
