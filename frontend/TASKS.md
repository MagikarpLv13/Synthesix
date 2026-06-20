# Registre de tâches — Palier 1 (`feat/lit-frontend`)

**Avant de coder** : réclame ta tâche (mets ton nom + `in progress`), committe
**cette ligne seule** et pousse immédiatement. **Après** : passe-la à `done`.
Détails dans `../COLLAB.md`.

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 0 | Scaffold toolchain (TS + Lit + esbuild) + pilote `sx-chip` | `frontend/*` | Claude | done |
| 1 | Overlay externe → Web Component(s) isolé(s) (depuis `main.py`) | `src/overlay/`, `main.py` (injection) | Codex | in progress |
| 2 | `sx-result-card` (titre, domaine, extrait, méta, actions, triage) | `src/components/sx-result-card.ts` | Codex | done |
| 3 | `sx-score` / `sx-tag` (affiner à partir de `sx-chip`) | `src/components/` | — | à faire |
| 4 | `sx-provenance` / `sx-evidence-badge` | `src/components/` | — | à faire |
| 5 | Inspecteur d'enquête (liste ↔ détail) | `src/components/` | — | à faire |
| 6 | Entités / propriétés | `src/components/` | — | à faire |

## Fichiers chauds (annoncer ici avant de modifier)

`theme.css` · `frontend/build.mjs` · `frontend/src/index.ts` ·
`frontend/package.json` · `frontend/tsconfig.json` · `main.py` · `i18n.js` ·
`index.html`

## Journal des annonces

- (Claude) Tâche 0 livrée : toolchain + `sx-chip` + bundles `assets/synthesix-ui.js`
  & `assets/synthesix-overlay.js`. La tâche 1 (overlay) est le prochain pas
  recommandé — c'est la seule surface qui reste Web Components quel que soit le
  Palier 2, donc zéro reprise.
- (Codex) Tâche 1 en cours : migration incrémentale du bouton principal
  "Save page" vers `<sx-overlay-action>`, avec maintien des contrats CDP
  existants dans `main.py`.
- (Codex) Les bundles minifiés `assets/*.js` gardent la sortie esbuild brute ;
  `.gitattributes` neutralise seulement les faux positifs whitespace.
- (Codex) Tâche 2 livrée : `<sx-result-card>` fournit la structure dense
  titre+domaine, extrait, slots méta/actions et compatibilité triage light DOM.
- (Claude) Correctifs post-livraison sur `sx-result-card` : F2 = triage encapsulé
  via propriété réfléchie `triage` (pose `data-triage-item` + `tabindex`, parité
  `result_card(triage=True)`) ; F1 = marge snippet portée par le contenu slotté
  (plus de marge fantôme sans extrait). Source + bundle régénérés.
