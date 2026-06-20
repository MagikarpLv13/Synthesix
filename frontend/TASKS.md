# Registre de tâches — Palier 1 (`feat/lit-frontend`)

**Avant de coder** : réclame ta tâche (mets ton nom + `in progress`), committe
**cette ligne seule** et pousse immédiatement. **Après** : passe-la à `done`.
Détails dans `../COLLAB.md`.

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 0 | Scaffold toolchain (TS + Lit + esbuild) + pilote `sx-chip` | `frontend/*` | Claude | done |
| 1 | Overlay externe → Web Component(s) isolé(s) (depuis `main.py`) | `src/overlay/`, `main.py` (injection) | Codex | in progress |
| 2 | `sx-result-card` (titre, domaine, extrait, méta, actions, triage) | `src/components/sx-result-card.ts` | Codex | done |
| 3 | `sx-score` / `sx-tag` (affiner à partir de `sx-chip`) | `src/components/` | Claude | done |
| 4 | `sx-provenance` / `sx-evidence-badge` | `src/components/` | Claude | done |
| 5 | Inspecteur d'enquête (liste ↔ détail) | `src/components/` | Claude | done |
| 6 | Entités / propriétés | `src/components/` | Claude | done |

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
- (Claude) Tâche 3 livrée : `<sx-score>` (port de `score_badge`, pill `level` +
  `expandable` → `<details>` breakdown/note) et `<sx-tag>` (refinement du chip,
  `tone` + `removable` émettant `sx-tag-remove`). Démos + bundle app régénéré.
- (Claude) Tâche 4 livrée : `<sx-provenance>` (port de `provenance()` : icône +
  label muted + detail, slots i18n) et `<sx-evidence-badge>` (port de
  `.evidence-verification` : `status` pending/verified/error, region `aria-live`).
  Primitives autonomes — le câblage au flux JS `verify_evidence_capture`
  (`data-evidence-verification` dans `view.py`) reste à faire à l'intégration.
- (Claude) Tâche 5 livrée : `<sx-inspector>` (liste↔détail). Layout deux-volets
  responsive (repli mono-volet + bouton retour <720px), état `selected` qui
  pilote `aria-current` sur la ligne et l'affichage du panneau, nav clavier
  (flèches/Home/End), événement `sx-inspector-select`. Peu opinioné : lignes
  `[data-inspector-item]` et panneaux `[data-inspector-panel]` fournis en slots.
  Câblage à `view.py` = étape d'intégration.
- (Claude) Tâche 6 livrée : `<sx-entity>` (port de `.graph-entity-card` :
  `kind`/`confidence`/`status` candidate-confirmed-rejected, valeur monospace,
  slots `actions`/`meta`/`properties` avec wrappers auto-masqués si vides) et
  `<sx-property>` (port de `.graph-property-list li` : label/valeur/actions). Tous
  les composants `<sx-*>` du Palier 1 sont livrés ; reste l'intégration côté
  `ui.py`/`view.py` et la tâche 1 (overlay, Codex).
