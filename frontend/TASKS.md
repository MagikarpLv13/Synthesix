# Registre de tâches — Palier 1 (`feat/lit-frontend`)

**Avant de coder** : réclame ta tâche (mets ton nom + `in progress`), committe
**cette ligne seule** et pousse immédiatement. **Après** : passe-la à `done`.
Détails dans `../COLLAB.md`.

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 0 | Scaffold toolchain (TS + Lit + esbuild) + pilote `sx-chip` | `frontend/*` | Claude | done |
| 1 | Overlay externe → Web Component(s) isolé(s) (depuis `main.py`) | `src/overlay/`, `main.py` (injection) | Claude (repris de Codex) | done |
| 2 | `sx-result-card` (titre, domaine, extrait, méta, actions, triage) | `src/components/sx-result-card.ts` | Codex | done |
| 3 | `sx-score` / `sx-tag` (affiner à partir de `sx-chip`) | `src/components/` | Claude | done |
| 4 | `sx-provenance` / `sx-evidence-badge` | `src/components/` | Claude | done |
| 5 | Inspecteur d'enquête (liste ↔ détail) | `src/components/` | Claude | done |
| 6 | Entités / propriétés | `src/components/` | Claude | done |

## Palier 1.5 — Intégration

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 7 | Intégrer `sx-result-card` dans les pages résultats + densifier la liste | `utils.py`, `ui.py`, `frontend/src/components/sx-result-card.ts`, `assets/synthesix-ui.js` | Claude | done |

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
- (Claude) **Reprise de la tâche 1 (overlay) à Codex**, sur accord explicite de
  l'utilisateur. État relevé : `sx-overlay-action` / `-capture-menu` /
  `-selection-trigger` existent et sont déjà câblés dans `main.py`
  (`_install_and_consume_save_overlay`). **Reste en inline dans `main.py`** : le
  host `#__synthesix-save-overlay` + toolbar (~427/438), la box de sélection
  (~666-696), le panneau d'entité (~809-942), et les callbacks de statut
  (`host.__synthesixSetButtonState` / `__synthesixSetCaptureState` /
  `__synthesixSetArchiveState`) lus par `_set_*_overlay_status`.
  ⚠️ **Garde-fou** : ce JS injecté n'est PAS couvert par `unittest` (221 tests
  restent verts quoi qu'il arrive). Toute migration du DOM inline de `main.py`
  doit donc être faite par petits pas + **smoke test CDP live** (`python main.py`
  contre une vraie page) — ne pas réécrire en aveugle.
  Incrément livré ce tour (sûr/vérifiable, sans toucher `main.py`) : correction
  i18n de `sx-overlay-capture-menu` — les chaînes (`placeholder`, label nom,
  « Visible area » / « Select area ») passent d'un texte EN codé en dur à des
  propriétés (`placeholder`/`name-label`/`viewport-label`/`region-label`, défauts
  EN → rétrocompatible), conformément à COLLAB §7. Démo dédiée + bundle overlay
  régénéré. Suite recommandée : câbler ces props depuis `i18n.js` via `main.py`,
  puis migrer host/toolbar/status en composant (`sx-overlay-root` ?) sous smoke
  test live.
- (Claude) Tâche 1 — **pas A.1** : la box de sélection région (inline
  `__synthesixStartRegionSelection`, ~120 lignes dans `main.py`) est extraite en
  `<sx-overlay-selection-box>`. Comportement préservé à l'identique (voile +
  crosshair, pill, rectangle cyan, Esc, seuil 8px, coords viewport+scroll).
  `main.py` ne fait plus que créer l'élément et écouter `synthesix-region-selected`
  / `synthesix-region-cancel` (toolbar masquée pendant la capture, restaurée à
  l'annulation). ⏳ **À smoke-tester live** : Capture → « Select area » → drag.
- (Claude) Tâche 1 — **pas A.2** : le panneau d'entité au surlignage (~500 lignes
  inline dans `main.py`) est extrait en `<sx-overlay-entity-menu>` (trigger +
  panneau créer/rattacher + détection de sélection + suggestions tags/propriétés).
  `main.py` ne fait plus que créer l'élément, lui passer les données
  (`baseTagsets`/`tagsetProperties` + shims `__synthesixSetEntityTagsets` /
  `__synthesixSetGraphEntities`) et reconstruire les **payloads CDP identiques**
  (`create_graph_entity_from_selection` / `attach_selection_to_graph_entity`) à
  partir des événements `synthesix-entity-create` / `-attach`. `test_main`
  (`test_external_page_overlay_returns_save_action`) mis à jour : il assertait des
  détails d'implémentation inline désormais dans le bundle minifié → recentré sur
  la création du composant + contrats CDP + données injectées. ⏳ **À smoke-tester
  live** : surligner du texte → trigger → créer entité (type) → rattacher à une
  entité existante (+ suggestions de propriétés).
- (Codex) Tâche 1 — **pas A.3** : le host `#__synthesix-save-overlay` devient
  `<sx-overlay-root>` ; la toolbar est portée par le Shadow DOM du root avec
  actions slottées, les setters historiques
  `__synthesixSetButtonState` / `__synthesixSetCaptureState` /
  `__synthesixSetArchiveState` délèguent aux méthodes du composant, et l'overlay
  peut être rétracté en petit bouton `SX` avec persistance
  `localStorage` (`synthesix:external-overlay-collapsed`). Validation :
  `npm run typecheck`, `npm run build`, `tests.test_main`, suite `unittest`
  complète et `git diff --check` OK. ⚠️ Smoke navigateur intégré non réalisé :
  la policy Browser a bloqué l'URL `file://` de la démo ; à refaire via CDP live
  sur une vraie page pilotée par `python main.py`.
- (Codex) Tâche 1 — ajustement UX post-validation : `<sx-overlay-root>` devient
  déplaçable par un grip visible en mode ouvert et collapsed. La position est
  bornée au viewport et persistée (`synthesix:external-overlay-position`) ; le
  menu de capture s'aligne automatiquement selon le bord gauche/droit et
  haut/bas pour ne pas sortir de l'écran.
- (Codex) Tâche 1 — ajustement placement : à l'ouverture depuis l'état collapsed,
  le root conserve son bord d'ancrage et recalcule sa position avec une marge de
  sécurité. La flèche de repli et la poignée suivent les bords gauche/droit et
  haut/bas pour éviter les contrôles hors écran. L'orientation du menu de
  capture est calculée séparément (`menu-edge` / `menu-vertical-edge`) selon
  l'espace réellement disponible avant ouverture.
- (Claude) Lot 7 livré : `result_card(component=True)` rend désormais
  `<sx-result-card>` ; le bundle `assets/synthesix-ui.js` est chargé par le shell
  partagé `ui.render_page` (module ESM) → branché sur les pages **rapport +
  historique** (utils.py). Slots `meta`/`actions` wrappés `display:contents` pour
  garder les gaps des chips/score/provenance ; `data-triage-item tabindex="0"`
  émis en HTML statique (compat triage au parse-time). Densité : padding carte
  12/16→8/12, marges head/snippet réduites (composant) → ~7 résultats visibles
  vs 2-3. `view.py`/`search_view.py` **intacts** (CSS, à migrer en Lot 8/archive)
  → zéro collision. Validé : typecheck, build, `unittest discover` (221),
  diff-check, capture rapport 12 résultats (clair/sombre OK). Tests `test_utils`
  mis à jour (`class="result-card"`→`<sx-result-card`, + assert bundle chargé).
  Nuance : la provenance « Trouvé via … » par carte montre les *variants* (pas
  juste la requête en tête) → conservée volontairement (signal OSINT utile).
- (Claude) Lot 7 — refonte SERP (retour utilisateur) : `sx-result-card` adopte le
  rendu moteur de recherche (Google/DDG) — ligne URL grise (breadcrumb
  `domaine › chemin`) + badge moteur + score, titre lien bleu 16px, extrait gris
  clampé 2 lignes ; flat (plus de boîte/bordure/accent), colonne ≤680px alignée à
  gauche (`:host max-width`, pas de modif `theme.css`), police plus petite.
  `utils.py` : suppression du bouton « Ouvrir » (lien explicite), « Trouvé via »
  seulement si >1 variante, breadcrumb d'URL via `_result_breadcrumb`. Badge
  moteur + score conservés. Capture 12 résultats : ~8 visibles, dark mode OK.
- (Claude) Lot 7 — affinage SERP (retour utilisateur) : ligne source en haut
  (avatar-lettre du domaine + nom de site + badge moteur/score à droite), titre
  lien **18px**, breadcrumb **10px sous le titre**, description **14px** clampée
  2 lignes, plus d'espace entre cartes (`:host` margin). Le terme recherché est
  **mis en gras** dans titre + description via `ui._highlight` (tokens ≥2 car.,
  insensible à la casse, échappé avant surlignage). `result_card` gagne le param
  `highlight` ; breadcrumb construit côté `ui.py` (urlsplit) → `_result_breadcrumb`
  retiré de `utils.py`. Validé : typecheck, build, `unittest discover` (221),
  diff-check, capture rapport (clair/sombre).
- (Claude) **Fix file:// crucial** : le bundle app `synthesix-ui.js` passe de
  **ESM → IIFE** (`build.mjs`) et `ui.render_page` le charge en `<script>`
  classique (plus `type="module"`). Les modules ES sont bloqués par CORS sur les
  pages `file://` (sans `--allow-file-access-from-files`), donc les `<sx-*>` ne
  s'upgradaient pas dans l'app réelle (rendu en vrac). La capture headless le
  masquait (j'avais le flag). Vérifié headless **sans** le flag → SERP OK.
  ⚠️ Tout futur bundle app destiné aux pages `file://` doit rester **IIFE +
  script classique** (comme l'overlay).
- (Claude) Lot 7 — affinages SERP (retour utilisateur) : breadcrumb des cartes
  passé **10px → 12px** (`sx-result-card.ts` `::slotted([slot="domain"])`, bundle
  régénéré). Puis le **détail du calcul du score** passe d'un `<details>`
  cliquable à une **infobulle au survol/focus** : `score_badge` (`ui.py`) rend
  désormais `<span class="score score--tip" tabindex="0">` + `<span
  class="score__tip" role="tooltip">` (breakdown + note toujours dans le DOM →
  lisible par lecteurs d'écran) ; styles tooltip dans `theme.css` (`--surface`,
  `--shadow-soft`, `--line`, révélé sur `:hover`/`:focus`/`:focus-within`,
  `--focus` au clavier). Chemin rendu = `score_badge` light-DOM (pas le composant
  `sx-score`, démo-only) → **pas de rebuild bundle**. Validé : `test_utils`,
  `unittest discover` (221), `git diff --check`.
