# Synthesix — Guide de collaboration (Palier 1)

Deux agents travaillent sur cette branche : **Claude** et **Codex**. Ce document
est la **source de vérité** pour ne pas se marcher dessus. Lis-le en entier avant
de coder. Complète `AGENTS.md` (règles générales) et `docs/UX_REDESIGN.md`
(design system).

## 1. But & décisions verrouillées

Palier 1 = migrer progressivement la couche UI vers
**TypeScript + Lit (Web Components) + tokens CSS + esbuild**, **bundle committé**,
sans casser le modèle `python main.py`.

- Backend **Python inchangé** (moteurs, Zendriver/CDP, enquêtes, evidence, exports).
- UI : **TS + Lit + tokens (`theme.css`) + esbuild**. Bundles committés dans `assets/`.
- **Overlay** : bundle isolé **IIFE + Shadow DOM**, injecté par `main.py`.
- **Pas** de React / Tailwind / serveur au Palier 1.
- **Palier 2** (FastAPI localhost + UI réactive) = décision séparée et ultérieure,
  déclenchée seulement si le workspace en Lit devient trop lourd. Ne pas l'amorcer
  sans accord explicite.
- Migration progressive, jamais d'un coup :
  **overlay → result cards → chips/tags/scores → inspecteur d'enquête → entités/propriétés**.

## 2. État de départ (cette branche, depuis `redesign/cockpit`)

Déjà en place et **testé (221 tests verts)** :
- Design system : tokens dans `theme.css`, helpers de rendu **`ui.py`**.
- Pages générées refondues : rapport (`utils.py`), historique (`utils.py`),
  archive (`investigations/search_view.py`), home (`index.html`), worklist
  d'enquête (`investigations/view.py`).
- Garde-fous i18n : `tests/test_i18n_coverage.py`.

Le Palier 1 **remplace progressivement** le JS inline (`index.html`, `main.py`) et
le markup généré par des composants Lit, en réutilisant **les mêmes tokens**.

> WIP Codex sur `ux-redesign` (overlay/`main.py`/`view.py`/`theme.css`) : à
> **committer sur `ux-redesign`** puis porter ici (cherry-pick ou réécrit en Lit).
> Ne pas le perdre.

## 3. Structure

```
frontend/
  package.json  tsconfig.json  build.mjs   # toolchain (Node, dev only)
  src/
    tokens.ts             # tokens CSS pour contextes injectés (overlay)
    components/           # composants partagés <sx-*>
      sx-chip.ts          # PATTERN DE RÉFÉRENCE — copie-le
    index.ts              # enregistre les composants d'app (bundle ESM)
    overlay/index.ts      # entrée overlay (bundle IIFE)
  demo/                   # pages de démo pour capture headless
  TASKS.md                # REGISTRE DE TÂCHES — à tenir à jour
assets/
  synthesix-ui.js         # bundle app (committé, généré)
  synthesix-overlay.js    # bundle overlay (committé, généré)
```

## 4. Build

```
cd frontend
npm install            # une fois (node_modules NON committé)
npm run build          # régénère assets/synthesix-ui.js + assets/synthesix-overlay.js
npm run watch          # dev
npm run typecheck      # tsc --noEmit
```

Les **bundles `assets/*.js` SONT committés** (pour que `python main.py` marche sans
Node). `node_modules/` ne l'est jamais.

## 5. Protocole anti-collision (LE point clé)

1. **Une tâche = une ligne dans `frontend/TASKS.md`.** Avant de coder, **réclame**-la :
   mets ton nom + `in progress`, **committe cette ligne seule et pousse tout de suite**.
2. **Un composant = un fichier** sous `src/components/` (ou `src/overlay/`).
   Deux agents sur deux fichiers ≠ conflit.
3. **`git pull --rebase` avant de commencer**, **commits petits**, **pousse souvent**.
4. **Ne touche jamais un fichier marqué `in progress` par l'autre.**
5. **Fichiers chauds partagés** — modif parcimonieuse + annonce dans `TASKS.md`,
   préfère l'additif aux réécritures : `theme.css`, `frontend/build.mjs`,
   `frontend/src/index.ts`, `frontend/package.json`, `frontend/tsconfig.json`,
   `main.py`, `i18n.js`, `index.html`.
6. **Régénère le bundle** après modif d'un composant et **committe source + bundle
   ensemble**.

## 6. Invariants — NE JAMAIS casser

- **Contrats CDP** : `window.synthesixHome` / `window.synthesixPage` (méthodes,
  `window.name = "synthesix-home"`), tous les **noms d'actions**, **payloads** et
  **IDs** consommés par `main.py`.
- Recherche en **phrase exacte**, **isolation des moteurs**, fermeture **propre de
  Zendriver** (`await asyncio.sleep`, jamais `time.sleep`).
- **i18n** : toute nouvelle chaîne ajoutée dans `i18n.js`, **dans les deux** dicos
  `multilingual` (fr/es/zh) et `additionalTranslations` (pt/de), **synchronisés**.
- Ne **jamais committer** : secrets, profils navigateur, données d'enquête,
  artefacts runtime (`history/`, `data/`, `*-profile/`, `node_modules/`,
  `tmp_ui_render/`).
- **`unittest` vert** à chaque commit ; **`git diff --check` propre**.

## 7. Conventions composants

- Préfixe **`sx-`**. **TypeScript strict**. `LitElement`.
- **Thème par tokens** : `var(--accent)`, `var(--surface)`, etc. (héritent dans le
  Shadow DOM). Pour l'**overlay** (DOM tiers, sans `theme.css`), injecter
  `tokens.ts`.
- **Pas de texte i18n en dur** dans un composant : exposer le texte via
  attribut/`slot` et laisser l'appelant fournir le libellé déjà traduit (ou passer
  par le mécanisme `i18n.js`).
- **Accessibilité** : rôles/ARIA utiles, focus visible, navigation clavier.

## 8. Definition of Done (par composant/tâche)

- [ ] Typé strict, compile (`npm run typecheck`).
- [ ] Shadow DOM + tokens, OK clair **et** sombre.
- [ ] Bundle régénéré **et committé** avec la source.
- [ ] **Vérifié visuellement** (capture Chrome headless, voir `frontend/README.md`).
- [ ] `unittest` vert, `git diff --check` propre.
- [ ] Ligne `TASKS.md` passée à `done`.

## 9. Vérification visuelle sans navigateur interactif

Chrome est installé. Capture headless d'une page (ou d'une démo de composant) :

```
"<chrome.exe>" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1440,1000 "--screenshot=F:/.../out.png" "file:///F:/.../page.html"
```

Pour un composant : crée `frontend/demo/<comp>.html` qui charge le bundle + le
composant, puis capture.

## 10. Workflow git résumé

```
git checkout feat/lit-frontend && git pull --rebase
# réclamer la tâche dans frontend/TASKS.md -> commit + push
# coder le composant (fichier dédié) -> npm run build
.venv/Scripts/python.exe -m unittest discover && git diff --check
git add <source> assets/<bundle> && git commit && git push   # souvent
# passer la tâche à "done" dans TASKS.md
```
