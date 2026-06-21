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

## Palier 2 — Workspace investigation (Lot 9)

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 9 | Entités/propriétés gérables dans le rail (à la zeroneurone) : rail redimensionnable, clic→gestion, champs vides masqués, actions icônes | `investigations/view.py`, `theme.css` | Claude | done |
| 10 | Refonte entités **extraites** (par page) : compactes + gérées dans le rail, tags retirés, détection en infobulle, promote-to-entity | `investigations/view.py`, `theme.css` | Claude | done |
| 11 | Alignement propriétés sur zeroneurone (cible export) : suggestions de propriétés typées par catégorie (A) + type précis dérivé des tagsets à l'export (B) | `investigations/view.py`, `exports/zeroneurone.py`, `exports/zeroneurone_tagsets.py` | Claude | done |

- (Claude) Lot 9 — **pas 1 : rail redimensionnable + gouttières resserrées**.
  Le rail prend une largeur variable `--rail-w` (défaut 340px) ; une poignée
  `.workspace__resizer` (séparateur entre main et rail) permet de glisser pour
  élargir le rail au détriment du main (clamp 280–680px, persistance
  `synthesix:rail-width:<id>`, double-clic = reset). JS dans l'IIFE existant
  (pointer events). Conteneur élargi `app--workspace` 1480→1600px, gouttières
  24→16px, gap grille 24→16px. **Fix** (régression pas 3) : `.inspector-panel`
  forçait `display:flex` et écrasait `[hidden]` → tous les panels s'affichaient ;
  corrigé en `.inspector-panel:not([hidden])`. Validé : `unittest discover`
  (222), `git diff --check`, smoke headless (défaut / rail élargi 560px). ⏳
  Pas 2 : clic entité → gestion dans le rail. Pas 3 : cartes compactes, champs
  vides masqués, actions icônes.
- (Claude) Lot 9 — **pas 2 : clic entité → gestion dans le rail** (à la
  zeroneurone). Les `.graph-entity-card` (gestion complète : nom/tags/notes,
  propriétés +/−, sources, « Manage entity ») sont **déplacées dans le rail**
  (cachées, `hidden` + `data-inspector-entity`), et la colonne principale
  affiche une **liste compacte cliquable** (`_entity_rows_markup` : label + tags
  + « N prop · M src »). Clic sur une ligne → la carte de gestion correspondante
  s'affiche dans l'Inspector. **Astuce clé** : les bindings JS existants ciblent
  `.graph-entity-card` + `card.querySelector(...)` → ils fonctionnent quel que
  soit l'emplacement de la carte ⇒ **zéro contrat CDP touché** (update/delete/
  set/delete property intacts). Sélection unifiée pages+entités (mutuellement
  exclusives, `hideInspectorPanels` + `.is-inspected`). CSS : `.entity-row`
  (grille label/tags/meta), `.inspector-entity` sans bordure + colonnes
  empilées dans le rail. Test `test_entities_are_compact_rows_with_management_card_in_rail`.
  Validé : `unittest discover` (223), `git diff --check`, smoke headless (entité
  sélectionnée rail 520px : gestion complète OK ; page sélectionnée). ⏳ Pas 3 :
  champs vides masqués + actions en icônes.
- (Claude) Lot 9 — **pas 3 : icônes + champs vides masqués** → Lot 9 **terminé**.
  Helper `_icon` autonome (SVG inline, classe `.icon`, paths trash/plus/check).
  Actions des entités/propriétés en icônes : supprimer entité / supprimer
  propriété = **poubelle** (`.icon-action--danger`, `title`/`aria-label`),
  ajouter propriété = **＋ Add**, sauvegarder = **✓ Save**. Masquage des vides :
  notes (`<p class="graph-entity-notes">`) et tags (`.result-tags`) **non rendus
  si vides** (plus de `<p>`/`<div>` fantômes). CSS `.icon-action` (28px, hover
  surface-2, danger au survol). Tests : assertions icône sur la suppression +
  `test_entity_card_hides_empty_tags_and_notes`. Validé : `unittest discover`
  (224), `git diff --check`, smoke headless (icônes + manage déplié). **Lot 9
  complet** : rail redimensionnable + clic→gestion (pages & entités) + compact/
  icônes. Reste au plan : Lot D (icônes/actions globales), Lot E (i18n).
- (Claude) Lot 10 — **refonte des entités extraites** (`_entity_markup`, retour
  utilisateur : une entité prenait ~½ page, 2-3 formulaires). Chaque entité
  extraite devient une **ligne compacte cliquable** dans le corps de la page
  (`_extracted_entity_row` : type · valeur · confiance · statut), et sa gestion
  s'ouvre dans le **rail** (`_extracted_entity_panel`, panels cachés branchés sur
  l'Inspector unifié pages/entités/extraites). Nettoyages demandés : **tags
  supprimés** (le type prime ; `add_entity_tag` était client-only) ; **détection/
  suggested → infobulle ⓘ** (`title` natif via `_detection_title`, plus de bloc
  « Detection details ») ; **lien propriété sorti** du dropdown → contrôle propre
  (attach/detach) ; **« Promote to entity » = bouton + mini-formulaire de
  confirmation** (catégorie + nom de propriété) au lieu d'un `<details>`.
  Handlers CDP **déplacés du loop `resultCards` vers le scope global** (ils
  utilisaient déjà `closest("[data-entity-id]")`) car les panels vivent désormais
  dans le rail — `update_entity_status` / `update_entity_metadata` (sans tags) /
  `attach`/`detach_extracted_property` / `create_graph_entity_from_extracted` /
  `delete_entity` **intacts**. Icône `info` + classes `.entity-chip-row`,
  `.extracted-panel`, `.info-tip`, `.promote-entity`. **Code mort retiré** :
  `_entity_markup_legacy` (~240 l) + `_highlight_entity_source_text`. Tests MAJ
  (strings/tags retirés). 2 bugs `[hidden]` corrigés (`.extracted-panel` +
  `.promote-entity__form` → `:not([hidden])`). Validé : `unittest discover`
  (224), `git diff --check`, smoke headless (ligne compacte + panel rail + promote).
- (Claude) Lot 11 — **alignement propriétés ↔ zeroneurone** (cible de l'export ;
  modèle : `Property{{key,value,type}}`, types ∈ text|number|date|datetime|
  boolean|choice|geo|country|link). **A (UI)** : le formulaire « ajouter une
  propriété » d'une entité-graphe (rail) propose désormais les **propriétés
  canoniques typées** de la catégorie via `zeroneurone_tagset_suggested_properties`
  (ex. *Entreprise* → SIREN·text, Date de création·date, Capital social·number) ;
  choisir une suggestion remplit la clé (`data-graph-property-suggestion`, JS).
  **B (export)** : nouvel helper `zeroneurone_property_type(key)` (map
  clé→type depuis les tagsets) ; `_native_property_type` l'utilise **avant**
  l'heuristique → les clés canoniques exportent leur **type précis** (Capital
  social→number, Nationalité→country, Date…→date) au lieu de retomber sur text.
  Sans changement de schéma DB (type dérivé de la clé canonique). Tests :
  `test_property_type_lookup_uses_tagset_declared_type` +
  `test_entity_property_form_suggests_typed_zeroneurone_properties`. Validé :
  `unittest discover` (226), `git diff --check`, smoke headless (select de
  suggestions Entreprise). Suite possible : (C) confiance 0-100 par paliers ;
  étendre les suggestions au « promote-to-entity » des entités extraites.
- (Claude) Lot 12 — **panel inspecteur façon zeroneurone** (retour utilisateur +
  capture). (1) **« Next actions » disparaît à la sélection** : le rail bascule
  entre `#rail-next-actions` (par défaut) et `#inspector-detail` (caché par
  défaut, montré à la sélection) ; bouton **« ‹ Actions »** (`data-inspector-close`,
  icône `arrow-left`) pour revenir. `revealInspector` masque l'un / montre
  l'autre ; placeholder `data-inspector-empty` retiré. (2) **Lisibilité/espace** :
  `.workspace__rail-body` padding/gap ↑, `.analyst-fields` **en 1 colonne** dans
  le rail (labels Name/Tags ne se chevauchent plus), `.inspector-entity` flex
  column gap 14px, propriétés/sources aérées. ⚠️ **3e piège `[hidden]`** :
  `.inspector-entity { display:flex }` réaffichait la carte même masquée →
  `:not([hidden])`. Test `test_inspector_starts_hidden_with_a_back_control`.
  Validé : `unittest discover` (227), `git diff --check`, smoke headless (entité
  + extraite : Next actions masqué, panel isolé et lisible).
- (Claude) Lot 13 — **affinage propriétés + sauvegarde sans reload** (retour
  utilisateur). (1) **Formulaire d'ajout de propriété retiré** (`graph-property-form`
  + select de suggestions + handlers JS) : l'édition de propriétés est le rôle de
  zeroneurone ; Synthesix = preuve de l'info. Reste l'affichage des propriétés
  (+ suppression) et l'édition nom/tags/notes. (2) **Style propriétés minimaliste**
  (façon zeroneurone) : `.graph-property-list` en **12px**, **badge de type**
  `.prop-type` (`_property_type_badge` via `zeroneurone_property_type` → « Texte/
  Nombre/Date/Pays/Lien… »), en-têtes PROPERTIES/SOURCES en petit uppercase muted.
  (3) **Sauvegarde inline sans reload** : `main.py` — `update_graph_entity`,
  `update_entity_metadata`, `update_entity_status` **persistent sans
  `_generate_investigation_page` + `tab.reload()`** (statut « Saved. ») ;
  `update_graph_entity` extrait du bloc partagé. Frontend : mise à jour
  **optimiste** (titre h4 du rail + label/tags de la ligne compacte) au Save.
  Test `test_entity_properties_show_type_badges_without_add_form` (remplace le
  test de suggestions du Lot 11). Validé : `unittest discover` (227),
  `git diff --check`, smoke headless (panel sans formulaire d'ajout, badges
  « Texte »). ⚠️ **Smoke CDP live requis** pour (3) : changer un nom d'entité →
  Save → pas de reload, valeur persistée.
- (Claude) Lot 14 — **panneau entité façon zeroneurone IDENTITÉ + auto-save**
  (retour utilisateur). (1) **Édition en haut** : la carte entité du rail est
  restructurée en sections `.entity-section` — **IDENTITÉ** d'abord (Nom, Notes,
  Tags éditables + trash), puis PROPRIÉTÉS, puis SOURCES. Plus de `<details>`
  « Manage entity » ni de bouton Save. (2) **Auto-save sur blur** : Nom/Notes
  sauvegardent au `blur`, tags à l'ajout/retrait → `queueAction("update_graph_entity")`
  (no-reload du Lot 13) + maj optimiste de la ligne compacte. (3) **Éditeur de
  tags multi** type zeroneurone : chips `.tag-chip` avec `×` + input
  « Nouveau tag… » (`data-tag-input`, datalist `entity-tagsets` = `ZERONEURONE_TAGSETS`).
  Tests MAJ (`save-graph-entity` retiré → `data-graph-entity-label` ;
  `test_entity_tag_editor_renders_chips_and_an_add_input`). Validé : `unittest
  discover` (227), `git diff --check`, smoke headless (IDENTITÉ en haut, chips +
  add input, propriétés compactes). ⚠️ **Smoke CDP live** : éditer Nom → cliquer
  ailleurs (blur) → persiste sans reload ; ajouter/retirer un tag → persiste.
- (Claude) Lot 15 — finitions panneau entité (retour utilisateur). (1) **Indicateur
  de sauvegarde** : « ✓ Enregistré » (`[data-save-indicator]`) flashe dans
  l'en-tête de l'inspecteur à chaque save (`flashSaved`, 1,5 s). (2) **Suppression
  de propriété sans reload** : `delete_graph_entity_property` extrait du bloc
  partagé dans `main.py` (persiste + « Saved. », pas de reload) + retrait
  optimiste du `<li>` côté frontend. (3) **Styles d'inputs cohérents** : Nom/Notes/
  Tags reprennent le style standard (`padding/border/bg/radius` comme
  `.analyst-fields`), tag-editor en conteneur d'input (focus-within). (4)
  **Valeur de propriété sous la clé** : `<li>` en flex column (`graph-property-head`
  clé+badge+actions, puis `graph-property-value` en dessous), aligné à gauche.
  (5) **Lien vers la source par propriété** : icône `external` → la page d'où la
  propriété a été extraite (map `property_key`→url des entités extraites
  rattachées, résolue + brute pour robustesse). Test
  `test_property_links_back_to_its_extracted_source`. Validé : `unittest discover`
  (228), `git diff --check`, smoke headless (indicateur, valeur dessous, 🔗 source).
  ⚠️ **Smoke CDP live** : supprimer une propriété → pas de reload.

## Palier 1.5 — Intégration

| # | Tâche | Fichier(s) cible(s) | Agent | Statut |
|---|---|---|---|---|
| 7 | Intégrer `sx-result-card` dans les pages résultats + densifier la liste | `utils.py`, `ui.py`, `frontend/src/components/sx-result-card.ts`, `assets/synthesix-ui.js` | Claude | done |
| 8 | Workspace investigation 2 zones + panel droit rétractable + clic→détail | `investigations/view.py`, `theme.css` | Claude | done |

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
- (Claude) Lot 8 — **pas 1 : densification** (CSS only, sans risque contrat JS) :
  l'espacement de la vue investigation est resserré — `.investigation-topbar`
  margin 34→20px, `.investigation-nav` margin 28→16px / padding 8→6px,
  `.investigation-overview` gap 32→24px / padding-bottom 28→18px,
  `.investigation-section` padding 30→18px. But : « la vue principale respire
  moins » (critère d'acceptation Lot B). Validé : `test_investigation_view` (7),
  `unittest discover` (221), `git diff --check`, rendu réel via
  `workspace_payload`. ⏳ **Reste** (pas 2+) : coquille 2 zones (contenu gauche +
  rail droit borné), panel rétractable (collapse + persistance), clic sur un
  élément → détail dans le panel, nav clavier. Ces pas touchent le DOM/JS de
  `view.py` → smoke visuel requis (§7).
- (Claude) Lot 8 — **pas 2 : coquille 2 zones + rail rétractable**. `view.py`
  enveloppe les sections dans `.workspace` (grid `minmax(0,1fr) 340px`) :
  `.workspace__main` (gauche) + `<aside class="workspace__rail">` sticky borné
  (droite). Le rail héberge « Next actions » (focus-summary **déplacé** de
  l'overview vers le rail — meilleure place, toujours visible au scroll) + un
  emplacement « Inspector » placeholder (rempli au pas 3). Toggle de repli
  (`data-rail-toggle`) câblé **dans l'IIFE existant** (réutilise le pattern
  localStorage try/catch, clé `synthesix:rail-collapsed:<id>`, persistance) —
  **aucun contrat `queueAction`/`synthesixPage` touché**. Replié → bande 40px +
  bouton de réouverture, le main reprend toute la largeur. `app--workspace`
  (conteneur plus large 1480px). ⚠️ **Bug corrigé** : le grid `.workspace`
  ne se dimensionnait pas (parent `.app` en `min()/calc()` → largeur indéfinie,
  `1fr` repliait sur le contenu) → ajout `width: 100%`. Test focus-summary
  recentré sur le rail (`//aside[...workspace__rail]`). Validé : `unittest
  discover` (221), `git diff --check`, **smoke headless Chrome** (étendu +
  replié, clair). Smoke via `frontend/README.md` §Visual check (chrome
  `--headless --screenshot`). ⏳ Reste pas 3 (clic→détail) + pas 4 (clavier).
- (Claude) Lot 8 — **pas 3 : clic → détail dans l'Inspector**. Clic sur l'en-tête
  d'une page sauvegardée (`.result-heading`, hors liens/boutons/champs) affiche
  son **résumé** dans le panel Inspector du rail : titre (lien), URL, badges
  (statut / favori / surveillance), stats (score, observations, evidence,
  entités, analyses URL, dernière observation localisée) + bouton « Go to card »
  (scroll vers la carte). Helper `_inspector_panel` (panels pré-rendus cachés,
  un par résultat, dans le rail) ; sélection via JS **dans l'IIFE existant**
  (réutilise `resultCards`, toggle `hidden` + classe `.is-inspected` sur la carte,
  ré-ouvre le rail si replié) — **aucun contrat CDP touché**, panel en lecture
  seule. En-tête de carte cliquable (curseur + hover). Pas de bouton « Inspecter »
  (le clic suffit, cf. Lot B). Test `test_rail_inspector_panel_summarizes_each_saved_page`.
  Validé : `unittest discover` (222), `git diff --check`, smoke headless (état
  sélectionné : date localisée OK, XSS échappé). Nuance : seules les **pages**
  sont inspectables pour l'instant (entités = suivi possible). Pas 4 (clavier)
  **abandonné** sur demande utilisateur (hors priorité).
- (Claude) Lot 7 — peaufinage infobulle score (retour utilisateur) : (1) chaque
  point `+X.X` est désormais **coloré et en gras** selon son poids
  (`utils.py` → `<span class="score__pts score__pts--{strong≥4|good≥2|low}">`,
  inks `--success-ink`/`--accent-ink`/`--muted`) ; (2) **note par défaut
  supprimée** (« Multi-engine consensus… not factual accuracy ») — l'appel
  `score_badge` ne passe plus `note` ; (3) infobulle **élargie** (`width:
  max-content; max-width: 380px`) avec **un point par ligne** (`li white-space:
  nowrap`, puces retirées). `test_utils` mis à jour (assert points colorés +
  absence de la note). Validé : `unittest discover` (221), `git diff --check`,
  rendu réel 8 cartes (16 strong / 5 good / 15 low, 0 note).
