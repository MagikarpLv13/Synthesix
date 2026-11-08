# Synthesix — Plan de travail Codex / Claude

Ce document sert de mode opératoire commun pour la suite de la refonte UI/UX.
Il complète `COLLAB.md`, `frontend/TASKS.md`, `AGENTS.md` et
`docs/UX_REDESIGN.md`.

Objectif : permettre à Codex et Claude de travailler en parallèle sans conflit,
avec des lots vérifiables, des responsabilités claires et une progression
réelle vers une interface plus dense, plus rapide et plus confortable pour un
usage OSINT/investigation.

## 1. État actuel

Branche de travail : `feat/lit-frontend`.

Socle livré :

- Toolchain TypeScript + Lit + esbuild.
- Bundles committés :
  - `assets/synthesix-ui.js` pour les pages internes.
  - `assets/synthesix-overlay.js` pour l'overlay injecté.
- Overlay externe migré en Web Components :
  - `sx-overlay-root`
  - `sx-overlay-action`
  - `sx-overlay-capture-menu`
  - `sx-overlay-selection-box`
  - `sx-overlay-entity-menu`
- Composants applicatifs disponibles :
  - `sx-result-card`
  - `sx-chip`
  - `sx-tag`
  - `sx-score`
  - `sx-provenance`
  - `sx-evidence-badge`
  - `sx-inspector`
  - `sx-entity`
  - `sx-property`

Le Palier 1 "bibliothèque de composants" est donc globalement posé. La suite
doit surtout intégrer ces composants dans les vues générées par Python, puis
refondre l'organisation des écrans.

## 2. Direction produit

Synthesix n'est pas une landing page. C'est un outil de travail pour analyste.
La refonte doit viser :

- densité utile : afficher plus de résultats et d'informations pertinentes ;
- rapidité d'action : sauvegarder, trier, inspecter, rattacher en peu de clics ;
- lisibilité : hiérarchie claire, titres compacts, métadonnées scannables ;
- workspace desktop assumé : peu de marges, panels rétractables, vues larges ;
- continuité `python main.py` : pas de serveur obligatoire au Palier 1 ;
- composants réutilisables : éviter les gros blocs HTML inline spécialisés.

Ce qu'il faut éviter :

- cartes trop grandes ;
- marges latérales inutiles ;
- duplication d'informations déjà affichées ailleurs ;
- boutons texte génériques quand une icône claire suffit ;
- champs vides visibles par défaut ;
- réécriture complète sans filet de tests.

## 3. Règle de coordination

Avant chaque lot :

1. `git checkout feat/lit-frontend`
2. `git pull --rebase`
3. Choisir un lot dans ce document ou dans `frontend/TASKS.md`.
4. Réclamer le lot dans `frontend/TASKS.md` :
   - agent ;
   - statut `in progress` ;
   - fichiers principaux touchés.
5. Committer et pousser la ligne de claim seule si le travail est simultané.

Pendant le lot :

- Un agent ne modifie pas un fichier marqué `in progress` par l'autre.
- Un composant Lit = un fichier dédié autant que possible.
- Les fichiers chauds nécessitent une annonce dans `frontend/TASKS.md` :
  - `main.py`
  - `ui.py`
  - `utils.py`
  - `investigations/view.py`
  - `investigations/search_view.py`
  - `index.html`
  - `i18n.js`
  - `theme.css`
  - `frontend/src/index.ts`
  - `frontend/build.mjs`
- Source TS et bundle généré doivent être committés ensemble.
- Ne jamais committer :
  - `exemple_zn.json`
  - `tmp_ui_render/`
  - profils navigateur ;
  - données d'enquête ;
  - secrets.

Après le lot :

1. `npm run typecheck`
2. `npm run build`
3. Tests ciblés Python.
4. Si surface large : `.venv\Scripts\python.exe -m unittest discover`
5. `git diff --check`
6. Smoke visuel ou navigateur si UI modifiée.
7. Passer la ligne `TASKS.md` à `done`.
8. Commit + push.

## 4. Découpage recommandé

### Lot A — Intégration de la page résultats

But : rendre la recherche plus orientée résultats.

Fichiers probables :

- `utils.py`
- `ui.py`
- `frontend/src/components/sx-result-card.ts`
- `frontend/src/index.ts`
- `assets/synthesix-ui.js`
- tests associés aux rendus HTML.

Travail attendu :

- Utiliser `sx-result-card` dans les rendus de résultats.
- Mettre source/domaine sur la même ligne que le titre.
- Retirer la requête exacte de chaque carte si elle est déjà en haut.
- Garder la requête accessible seulement dans un détail, une meta compacte ou
  un panneau si nécessaire.
- Réduire hauteur, padding et espacement vertical.
- Garder les actions de triage accessibles sans occuper toute la carte.
- Vérifier une page avec 10+ résultats : elle doit permettre de scanner vite.

Critères d'acceptation :

- Sur un écran classique, on voit nettement plus que 2 ou 3 résultats.
- Le titre, la source, l'extrait et les actions principales sont visibles sans
  lecture laborieuse.
- Les contrats JS existants de triage/sauvegarde restent fonctionnels.

### Lot B — Workspace investigation en deux zones

But : transformer l'espace rapport en zone de travail avec panel de droite.

Fichiers probables :

- `investigations/view.py`
- `ui.py`
- `theme.css`
- `frontend/src/components/sx-inspector.ts`
- `assets/synthesix-ui.js`
- tests de rendu investigation.

Travail attendu :

- Réduire les marges globales.
- Layout desktop :
  - contenu principal à gauche ;
  - panel dynamique à droite ;
  - largeur de panel bornée ;
  - panel rétractable ;
  - pas d'optimisation mobile prioritaire.
- Clic sur un élément = chargement de son détail dans le panel.
- Supprimer les boutons `Inspecter` si le clic suffit.
- Garder une navigation clavier minimale sur les listes.

Critères d'acceptation :

- La vue principale respire moins et montre plus de contenu utile.
- Le panel droit ne masque pas le travail principal.
- Le panel peut être réduit quand l'utilisateur veut reprendre de la place.

### Lot C — Entités et propriétés compactes

But : rendre les entités utiles au quotidien, pas décoratives.

Fichiers probables :

- `investigations/view.py`
- `investigations/service.py` si besoin uniquement ;
- `frontend/src/components/sx-entity.ts`
- `frontend/src/components/sx-property.ts`
- tests sur propriétés vides.

Travail attendu :

- Masquer les propriétés vides.
- Continuer à proposer les propriétés par défaut lors de l'ajout/édition.
- Remplacer les actions texte `Supprimer`, `Remove`, etc. par icônes explicites.
- Éviter les doublons de tags suggérés.
- Compacter les blocs longs :
  - pas de `Detection details` affiché par défaut ;
  - détails en disclosure si utile ;
  - labels courts ;
  - valeurs longues tronquées avec détail accessible.

Critères d'acceptation :

- Une entité avec beaucoup de champs vides reste courte.
- Une entité riche reste lisible.
- L'utilisateur comprend où ajouter une propriété sans subir tous les champs
  vides en lecture.

### Lot D — Panneaux et actions globales

But : uniformiser les interactions et réduire le bruit visuel.

Fichiers probables :

- `theme.css`
- `ui.py`
- composants `sx-*`
- `i18n.js` si nouveaux libellés.

Travail attendu :

- Standardiser icônes/actions :
  - supprimer = `×` ou icône poubelle selon contexte ;
  - valider = coche ;
  - éditer = crayon ;
  - ouvrir = flèche/lien ;
  - archiver = boîte/archive ;
  - capture = caméra.
- Ajouter `title` / `aria-label` aux icônes seules.
- Remplacer les boutons génériques quand le sens est évident.
- Harmoniser les états hover/focus/disabled.

Critères d'acceptation :

- Les actions prennent moins de place.
- Les icônes restent compréhensibles.
- Le clavier et les lecteurs d'écran gardent un libellé exploitable.

### Lot E — Nettoyage i18n et contrats JS

But : fiabiliser la migration progressive.

Fichiers probables :

- `i18n.js`
- `index.html`
- `main.py`
- tests i18n / tests JS string.

Travail attendu :

- Toute nouvelle chaîne utilisateur doit être traduisible.
- Pas de texte dur dans les composants si la vue Python peut le fournir.
- Documenter les contrats JS conservés :
  - actions `window.synthesixHome`
  - actions `window.synthesixPage`
  - actions overlay `window.__synthesixSavePageAction`
- Supprimer les anciens helpers inline uniquement quand le composant Lit couvre
  vraiment le comportement.

Critères d'acceptation :

- Tests i18n verts.
- Les noms d'actions CDP n'ont pas changé.
- Les payloads consommés par Python restent compatibles.

## 5. Répartition conseillée entre Codex et Claude

Pour limiter les conflits :

- Codex prend plutôt les intégrations Python + contrats CDP :
  - `main.py`
  - `utils.py`
  - `investigations/view.py`
  - tests `unittest`
  - smoke navigateur.
- Claude prend plutôt les composants Lit autonomes et raffinements visuels :
  - `frontend/src/components/`
  - `frontend/src/overlay/`
  - pages de démo ;
  - micro-interactions ;
  - documentation de design.

Exception : si un agent commence un lot, il peut toucher les deux côtés, mais il
doit l'annoncer clairement dans `TASKS.md`.

## 6. Format des lignes `TASKS.md`

Ajouter les lots d'intégration sous le tableau existant ou dans une nouvelle
section `Palier 1.5 — Intégration`.

Format recommandé :

```md
| 7 | Intégrer `sx-result-card` dans les pages résultats | `utils.py`, `ui.py`, `sx-result-card.ts` | Codex | in progress |
```

Journal recommandé :

```md
- (Codex) Lot 7 en cours : intégration de `sx-result-card` dans les résultats.
  Objectif : densifier les cartes, retirer la requête répétée, préserver triage
  et actions existantes. Fichiers chauds touchés : `utils.py`, `ui.py`.
```

## 7. Smoke tests visuels

Pour chaque écran modifié :

- générer ou ouvrir une page HTML réelle ;
- capturer un rendu desktop ;
- tester au moins :
  - état vide ;
  - état nominal ;
  - état avec contenu long ;
  - état avec beaucoup d'éléments.

Pour l'overlay :

- smoke CDP live obligatoire après changement fonctionnel ;
- vérifier :
  - sauvegarde page ;
  - archive HTML ;
  - capture visible ;
  - capture région ;
  - sélection texte ;
  - création entité ;
  - rattachement propriété ;
  - overlay collapsed + menu contextuel.

## 8. Tests minimums par type de changement

Composant Lit seul :

```powershell
cd frontend
npm run typecheck
npm run build
```

Rendu Python ciblé :

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main
git diff --check
```

Changement investigation :

```powershell
.venv\Scripts\python.exe -m unittest tests.test_investigations
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

Changement large ou avant push de batch :

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

## 9. Definition of Done d'un lot UX

Un lot est terminé seulement si :

- le comportement demandé est visible dans l'UI ;
- les fichiers générés nécessaires sont committés ;
- les champs vides inutiles ne polluent pas l'interface ;
- les actions principales sont accessibles au clavier ou ont un `aria-label` ;
- les tests minimums ont été exécutés ;
- `TASKS.md` documente ce qui a été fait et ce qui reste ;
- les fichiers temporaires ne sont pas staged.

## 10. Prochaine étape recommandée

Le prochain lot prioritaire est :

```md
| 7 | Intégrer `sx-result-card` dans les pages résultats et densifier la liste | `utils.py`, `ui.py`, `frontend/src/components/sx-result-card.ts`, `assets/synthesix-ui.js` | à prendre | pending |
```

Raison : c'est la surface la plus utilisée, et le besoin utilisateur est clair :
un moteur de recherche doit afficher beaucoup de résultats exploitables, pas de
grosses cartes décoratives.

Ensuite :

```md
| 8 | Workspace investigation deux zones + panel droit rétractable | `investigations/view.py`, `ui.py`, `theme.css`, `sx-inspector.ts` | à prendre | pending |
| 9 | Entités/propriétés compactes, champs vides masqués, actions icônes | `investigations/view.py`, `sx-entity.ts`, `sx-property.ts` | à prendre | pending |
```
