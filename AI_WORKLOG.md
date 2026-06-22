# AI_WORKLOG.md — Coordination et suivi des agents IA

> Source de vérité opérationnelle pour Claude, Codex, Copilot et tout autre agent IA travaillant sur Synthesix.

## Règles d'utilisation

- Lire ce fichier avant toute modification non triviale.
- Utiliser un identifiant unique `AI-YYYYMMDD-NNN`.
- Inscrire une tâche dans **Travaux actifs** avant d'éditer le code.
- Déclarer tout fichier chaud dans **Verrous de fichiers**.
- Un fichier ne peut avoir qu'un seul propriétaire écrivain à la fois.
- Mettre à jour `Dernière MAJ` après une étape significative ou un blocage.
- À la fin, retirer la ligne active et les verrous, puis ajouter un compte rendu dans **Travaux terminés**.
- Les comptes rendus terminés et les décisions sont append-only : ne pas réécrire l'historique d'un autre agent.
- Faire `git pull --rebase` avant un claim et avant la clôture lorsque le distant est accessible.
- Si le distant est inaccessible, indiquer `offline` dans la colonne Branche/commit.
- `frontend/TASKS.md` peut conserver le backlog détaillé de la refonte frontend ; le présent fichier fait autorité pour les claims et verrous actifs.

Statuts autorisés : `claimed`, `in_progress`, `blocked`, `review`, `handoff`.

## Travaux actifs

| ID | Agent | Statut | Début UTC | Dernière MAJ UTC | Objectif | Périmètre / fichiers prévus | Tests prévus | Branche / commit |
|---|---|---|---|---|---|---|---|---|
| _Aucun travail actif_ |  |  |  |  |  |  |  |  |

> Reste basse priorité (hors lot) : durcir la regex téléphone
> (`analysis/entities.py`) — remonte des plages de dates en `téléphone`.

## Verrous de fichiers

| Fichier ou motif | Tâche | Agent | Pris UTC | Motif | Libération prévue |
|---|---|---|---|---|---|
| _Aucun verrou actif_ |  |  |  |  |  |

Un verrou doit être précis. Éviter les verrous globaux tels que `*.py` ou `frontend/**`. Pour un lot multi-fichiers, lister les fichiers chauds ; les fichiers dédiés à un nouveau composant peuvent rester couverts par la tâche sans verrou séparé.

## Blocages et relais

| Date UTC | Tâche | De | Vers | Blocage / contexte | État vérifié | Prochaine action exacte |
|---|---|---|---|---|---|---|
| _Aucun blocage ou relais_ |  |  |  |  |  |  |

## Décisions partagées

Les décisions doivent décrire un choix durable qui affecte plusieurs tâches. Ajouter une nouvelle entrée au lieu de modifier rétroactivement une décision. En cas de remplacement, référencer l'identifiant précédent.

| ID | Date UTC | Auteur | Décision | Motif | Fichiers / contrats concernés | Remplace |
|---|---|---|---|---|---|---|
| DEC-001 | 2026-06-21 | Initialisation | `AI_WORKLOG.md` est la source de vérité pour les claims et verrous IA actifs. | Éviter la dispersion entre plusieurs journaux. | `AGENTS.md`, `CLAUDE.md`, `frontend/TASKS.md` | — |

## Travaux terminés

Ajouter les nouveaux comptes rendus à la fin de cette section. Ne pas supprimer ni réécrire les anciens.

### AI-20260621-001 — Gouvernance et coordination des agents IA

- **Agent :** ChatGPT
- **Période UTC :** 2026-06-21
- **Branche / commits :** non appliqué au dépôt ; fichiers préparés hors repository
- **Objectif :** fournir des règles communes, des instructions Claude Code et un journal central de coordination.
- **Changements :**
  - création de `CLAUDE.md` avec import de `AGENTS.md` et règles spécifiques à Claude Code ;
  - refonte de `AGENTS.md` autour des invariants Synthesix, du workflow de validation et de la coordination multi-IA ;
  - création du présent journal avec claims, verrous, relais, décisions et comptes rendus.
- **Fichiers préparés :**
  - `CLAUDE.md`
  - `AGENTS.md`
  - `AI_WORKLOG.md`
- **Tests exécutés :**
  - relecture de structure Markdown et cohérence des références ;
  - aucun test du dépôt exécuté, les fichiers n'ayant pas été appliqués à une copie locale du repository.
- **Risques / reste à faire :**
  - copier les trois fichiers à la racine de la branche ;
  - décider si `COLLAB.md` et `frontend/TASKS.md` restent purement historiques ou sont simplifiés pour pointer vers ce journal.
- **Relais :** après intégration, créer un claim réel pour toute prochaine modification de code.

### AI-20260621-002 — Fonts locales et plan rattachement des preuves

- **Agent :** Codex
- **Période UTC :** 2026-06-21 15:14-15:18
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** intégrer les fonts Bevan, Exo 2 et Nunito en local et préparer le lot de rattachement des preuves/images.
- **Changements :**
  - ajout des fonts locales sous `assets/fonts/` ;
  - déclaration `@font-face` et tokens `--font-display`, `--font-ui`, `--font-body` ;
  - application de Bevan aux titres principaux, Nunito au texte courant et Exo 2 aux contrôles/UI ;
  - alignement de `sx-result-card` sur le token de font global ;
  - création du plan `docs/EVIDENCE_ATTACHMENT_PLAN.md`.
- **Fichiers modifiés :**
  - `theme.css`
  - `frontend/src/components/sx-result-card.ts`
  - `assets/synthesix-ui.js`
  - `assets/fonts/Bevan-Regular.ttf`
  - `assets/fonts/Exo2-VariableFont_wght.ttf`
  - `assets/fonts/Nunito-VariableFont_wght.ttf`
  - `docs/EVIDENCE_ATTACHMENT_PLAN.md`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - l'overlay injecté ne charge pas les fonts locales pour rester indépendant des pages tierces ;
  - `Photo de profil` est traité comme nom de propriété, pas comme `PropertyType`.
- **Tests exécutés :**
  - `npm run typecheck` — OK
  - `npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - tests Python non relancés, aucun code Python modifié dans ce lot ;
  - smoke visuel non exécuté dans ce lot.
- **Risques / reste à faire :**
  - vérifier visuellement que Bevan ne prend pas trop de place sur certaines pages denses ;
  - implémenter le lot 1 du plan preuves : bloc `attach` commun capture/archive.
- **Relais :** prochaine action exacte : implémenter le helper service de rattachement `EvidenceCapture` -> propriété sourcée, puis brancher capture et archive.

### AI-20260621-003 — Densification du panneau gauche investigation

- **Agent :** Codex
- **Période UTC :** 2026-06-21 15:31-15:35
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** réduire la place prise par les métriques, le formulaire de création et la liste d'entités dans la colonne principale.
- **Changements :**
  - remplacement du bloc de gros chiffres par des chips métriques avec symbole, valeur et infobulle ;
  - transformation du formulaire de création d'entité en bande compacte avec champs accessibles ;
  - compression des lignes d'entités : tags limités, compteurs propriétés/sources en micro-badges avec infobulles ;
  - ajustements CSS pour réduire les hauteurs et l'espacement.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP ou payload modifié ;
  - la liste d'entités reste une navigation, le détail complet reste dans le panneau de droite.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — échec initial sur un XPath de test trop large, corrigé, puis OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - suite Python complète non relancée, changement limité au rendu HTML/CSS et tests ciblés verts ;
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - vérifier visuellement la lisibilité des symboles métriques sur l'écran réel ;
  - si validé, appliquer la même logique de micro-compteurs aux autres listes denses.
- **Relais :** aucun

### AI-20260621-004 — Recherche fluide entités et filtres pages rétractables

- **Agent :** Codex
- **Période UTC :** 2026-06-21 15:50-15:55
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** simplifier les libellés entités et fluidifier la navigation sans vue graphe.
- **Changements :**
  - retrait des libellés visibles `Final graph`, `Investigation entities` et `Final graph node` ;
  - titre de section réduit à `Entités` ;
  - ajout d'un filtre instantané des entités par nom, tag, propriété ou valeur ;
  - ajout d'un compteur d'entités filtrées ;
  - déplacement des filtres de pages enregistrées derrière un bouton loupe, panneau caché par défaut ;
  - ajout d'un état visuel `aria-expanded` pour le bouton de filtres.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP ou payload modifié ;
  - navigation entités retenue : liste dense filtrable + panneau de détail, pas de graphe.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - suite Python complète non relancée, changement limité au rendu HTML/CSS/JS inline de la page investigation ;
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - valider visuellement la position du bouton loupe et du filtre entités ;
  - si la liste dépasse 30-40 entités, envisager groupes repliables par tag principal ou entités épinglées.
- **Relais :** aucun

### AI-20260621-005 — Correctifs filtres et création d'entité dans le rail

- **Agent :** Codex
- **Période UTC :** 2026-06-21 16:09-16:13
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** corriger les filtres visibles malgré `hidden`, ajouter un indicateur de filtre et déplacer le formulaire de création d'entité dans le panneau droit.
- **Changements :**
  - ajout de règles CSS explicites pour masquer `.investigation-filters[hidden]`, `.entity-row[hidden]` et `.graph-entity-create-panel[hidden]` ;
  - ajout d'une icône loupe dans le champ de filtre des entités ;
  - remplacement du formulaire inline par un bouton `+ Entité` près du compteur ;
  - déplacement du formulaire de création d'entité dans le rail workspace ;
  - branchement JS du bouton `+ Entité` sur le panneau droit, avec focus sur le champ nom.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP ou payload modifié ;
  - l'action `create_graph_entity` conserve le même formulaire et le même payload.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - suite Python complète non relancée, changement limité au rendu HTML/CSS/JS inline de la page investigation ;
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - valider visuellement l'ouverture du formulaire dans le rail ;
  - si souhaité, ajouter une transition courte à l'ouverture du rail/formulaire.
- **Relais :** aucun

### AI-20260621-006 — Tags multiples sur création d'entité

- **Agent :** Codex
- **Période UTC :** 2026-06-21 16:19-16:22
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** aligner la création d'entité sur la modification : tags multiples en chips et identité visuelle cohérente dans le rail.
- **Changements :**
  - remplacement du champ tags simple par le composant visuel `tag-editor` ;
  - ajout, suppression et déduplication de tags côté création ;
  - support de `Entrée`, virgule et blur pour transformer le texte en chip ;
  - collecte des tags en chaîne comma-separated avant `create_graph_entity` ;
  - ajustement CSS pour que le champ interne du tag-editor garde le style de l'édition.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP ou payload modifié ;
  - `create_graph_entity.entity.tags` reste une chaîne.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - suite Python complète non relancée, changement limité au rendu HTML/CSS/JS inline de la page investigation ;
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - valider visuellement que les chips de création correspondent bien aux chips de modification.
- **Relais :** aucun

### AI-20260621-007 — Clic sur suggestion de tag en création

- **Agent :** Codex
- **Période UTC :** 2026-06-21 22:49-22:50
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** ajouter le tag au clic/sélection d'une suggestion pendant la création d'entité et finir l'alignement visuel avec l'édition.
- **Changements :**
  - ajout du handler `change` sur le champ tag de création ;
  - conservation des handlers `Entrée`, virgule et blur ;
  - resserrage CSS pour que le panneau de création prenne toute la largeur du rail ;
  - retrait des bordures/surfaces spécifiques qui différenciaient visuellement la création de l'édition.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP ou payload modifié.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - suite Python complète non relancée, changement limité au rendu HTML/CSS/JS inline de la page investigation ;
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - vérifier visuellement dans le navigateur que la sélection native de datalist déclenche bien `change` selon Chrome.
- **Relais :** aucun

### AI-20260621-008 — Cartes pages enregistrées compactes

- **Agent :** Codex
- **Période UTC :** 2026-06-21 23:10-23:18
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** alléger les cartes de pages enregistrées et déplacer leurs détails secondaires dans le rail workspace.
- **Changements :**
  - remplacement des actions de carte par des boutons icônes avec `title`/`aria-label` ;
  - déplacement des entités liées, analyse URL, entités extraites et preuves dans le panneau droit de chaque page ;
  - liaison d'une source à une entité directement au `change` du sélecteur, sans bouton `Link source` ;
  - suppression du bloc `Créer une entité depuis ce site` et des contrôles visibles `Notes/tags analyste` sur la carte ;
  - compactage CSS des blocs déplacés dans le rail.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun payload CDP existant modifié ;
  - les notes/tags de résultat restent conservés en champs cachés pour préserver `update_investigation_result`.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - valider visuellement que les blocs déplacés dans le rail restent confortables avec plusieurs preuves ;
  - décider si les liens d'artefacts de preuve doivent aussi passer en icônes.
- **Relais :** aucun

### AI-20260621-009 — Cartes pages sans collapse ni score

- **Agent :** Codex
- **Période UTC :** 2026-06-21 23:32-23:37
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** simplifier les cartes de pages enregistrées et le rail en supprimant les contrôles/données redondants.
- **Changements :**
  - suppression du bouton collapse, de son stockage local et du JS associé ;
  - remplacement par une action icône vers Wayback Machine ;
  - retrait du score de la carte et du rail ;
  - retrait du bloc provenance/page référente sur les cartes ;
  - suppression des stats doublonnées du rail ;
  - uniformisation des tailles d'icônes dans la rangée d'actions et amélioration du select `Link source to...`.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun payload CDP existant modifié ;
  - le score reste disponible côté données, mais n'est plus rendu dans l'espace pages enregistrées.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - smoke visuel navigateur non exécuté dans ce lot.
- **Risques / reste à faire :**
  - valider visuellement que l'icône Wayback est assez explicite avec le tooltip ;
  - décider si `Go to card` doit aussi devenir une icône dans le rail.
- **Relais :** aucun

### AI-20260622-001 — Zone cliquable des pages enregistrées

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend`
- **Objectif :** ouvrir le détail dans le rail en cliquant la carte, et n'ouvrir
  la page que via le lien titre.
- **Changements :**
  - clic sur toute la carte `.investigation-result` → `selectInspectorPage`
    (sauf `a/button/input/select/textarea/label`) ;
  - `.result-title` passe en `display: inline` pour que le lien ne couvre que
    son texte ;
  - `.investigation-result` : `cursor: pointer` + survol accent.
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP/payload modifié.
- **Tests exécutés :** `unittest discover` (232) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** smoke visuel du comportement de clic (statique
  uniquement) ; à confirmer en live.
- **Relais :** aucun. Reste demandé : refonte affichage des entités proposées
  (triage inline) et durcissement regex téléphone.

### AI-20260622-002 — Refonte triage des entités extraites (liste actionnable)

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend` — `8b493b8` (backend) + lot frontend
  (rows/CSS/JS).
- **Objectif :** rendre chaque entité extraite triable directement dans la liste
  (toutes les actions de l'ancien panneau détail), et garder les candidats en
  « proposée » jusqu'au triage analyste.
- **Changements :**
  - **Backend (`8b493b8`)** : suppression des deux appels
    `_auto_attach_result_properties` (`extract_entities` +
    `link_result_to_graph_entity`) → plus d'auto-rattachement/validation ;
    méthode morte et helpers retirés ; test
    `test_extracts_entities_from_saved_archive_text` adapté.
  - **Frontend (`investigations/view.py`)** : `_extracted_entity_row` réécrite en
    ligne auto-suffisante — L1 : badge type (masqué si `other`) + **valeur** en
    avant + ⓘ source + ✓ valider + 🗑 rejeter (masque la ligne) + ↗ promouvoir ;
    L2 : input **nom de propriété** (onChange → `update_entity_metadata`) ;
    L3 : select **« Lier à une entité… »** (onChange → attach/detach) ;
    mini-formulaire de promotion (toggle). `data-entity-type` /
    `data-property-type` portés sur la ligne pour les payloads.
  - Suppression du panneau `_extracted_entity_panel`, de son injection et du drill
    (`selectInspectorExtracted`, `inspectorExtractedPanels`).
  - Plus d'étiquette analyste, plus de sélecteur de type, plus de `%` affiché.
  - **CSS (`theme.css`)** : `.entity-chip-row` en colonne flex
    (`__head/__value/__name/__actions/__link/__promote`).
- **Fichiers modifiés :** `investigations/service.py`, `investigations/view.py`,
  `theme.css`, `tests/test_investigations.py`, `tests/test_investigation_view.py`,
  `AI_WORKLOG.md`
- **Contrats ou décisions :** actions CDP inchangées (`update_entity_status`,
  `update_entity_metadata`, `attach_extracted_property`,
  `detach_extracted_property`, `create_graph_entity_from_extracted`) ;
  `delete_entity` n'est plus émis par l'UI (rejet =
  `update_entity_status('rejected')`).
- **Tests exécutés :** `unittest discover` (232) OK ; `git diff --check` OK (CRLF) ;
  smoke headless des lignes (`tmp_ui_render`, capturé).
- **Vérifications non exécutées :** smoke CDP live des actions inline
  (attach/detach, validate/reject, rename, promote) — à confirmer en live.
- **Relais :** aucun. Reste basse priorité : durcir la regex téléphone
  (`analysis/entities.py`).

### AI-20260622-003 — Détail page : URL analysis, overflow, rejet, batch

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend` — `d723309` (1-3) + lot batch.
- **Objectif :** retours live — retirer la section URL analysis, corriger
  l'overflow du rail, faire que rejeter supprime vraiment, et ajouter des
  actions groupées.
- **Changements :**
  - Section « Technical URL analysis » retirée du détail page (fonction
    `_url_analysis_markup` et action `analyze_result_url` conservées pour
    réactivation).
  - Overflow horizontal du rail corrigé : item evidence en 2 colonnes
    (vignette + texte) avec liens artefacts en `flex-wrap` sur leur propre
    ligne ; la longue ligne SHA-256 d'URL analysis disparaît avec la section.
  - **Rejet d'une entité = `delete_entity`** (suppression réelle) au lieu de
    `update_entity_status('rejected')` → ne réapparaît plus au refresh.
  - **Actions groupées** : case à cocher par ligne + barre d'actions (« N
    sélectionnée(s) », « Lier la sélection à… », rejeter). Deux nouvelles
    actions CDP `delete_entities` (liste d'IDs) et `attach_extracted_properties`
    (`graphEntityId` + `items[]`), traitées en boucle dans le handler partagé de
    `main.py` avec **un seul reload** (le reload vide la file in-page, donc
    boucler `queueAction` côté client était impossible). Erreurs isolées par
    item.
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`, `main.py`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** ajout des actions CDP `delete_entities` et
  `attach_extracted_properties` (réutilisent `delete_entity` /
  `attach_extracted_property` côté service).
- **Tests exécutés :** `unittest discover` (232) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (rail sans overflow, batch bar capturée).
- **Vérifications non exécutées :** smoke CDP live des deux actions batch
  (`delete_entities`, `attach_extracted_properties`) — à confirmer en live.
- **Relais :** aucun. Reste basse priorité : durcir la regex téléphone
  (`analysis/entities.py`).

### AI-20260622-004 — Fix overflow valeur longue (URL) dans le rail

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend`.
- **Objectif :** une valeur d'entité très longue (URL) ne se tronquait pas et
  élargissait le rail (scroll horizontal).
- **Changements :** `.inspector-panel__details` passe en
  `grid-template-columns: minmax(0, 1fr)` ; la colonne se contraint à la largeur
  du rail, donc le `min-width: 0` + ellipsis de `.entity-chip-row__value`
  s'applique enfin.
- **Fichiers modifiés :** `theme.css`, `AI_WORKLOG.md`
- **Tests exécutés :** `tests.test_investigation_view` (15) OK ; `git diff --check`
  OK ; smoke headless (URL longue tronquée, plus d'overflow).
- **Vérifications non exécutées :** —
- **Relais :** aucun.

### AI-20260622-005 — Entités : suggestions, état validé, header allégé

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend`.
- **Objectif :** retours live sur le triage et le header du rail.
- **Changements :**
  - Input nom de propriété : `list="property-suggestions"` — nouvelle datalist
    `#property-suggestions` (union dédupliquée des clés de
    `ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES`) ; saisie libre conservée ;
    sauvegarde au blur via l'event `change` (déjà en place).
  - Bouton ✓ « Valider » masqué quand l'entité est `validated` (rendu
    conditionnel + masquage immédiat côté JS après validation no-reload). Lier à
    une entité valide côté serveur → re-render sans ✓.
  - Boutons retirés : « Go to card » (panneau page) et « ← Actions » (header
    inspecteur) ; l'indicateur « Enregistré » reste.
  - Hover « bizarre » de la carte page corrigé : suppression du
    `.result-heading:hover` (et de son `cursor`) résiduel qui doublait le hover
    `.investigation-result:hover` depuis que toute la carte est cliquable.
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP modifié.
- **Tests exécutés :** `unittest discover` (233) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (datalist présente, ✓ masqué sur entité validée).
- **Vérifications non exécutées :** rendu live du datalist au focus (statique).
- **Relais :** aucun. Reste basse priorité : durcir la regex téléphone.

### AI-20260622-006 — No-reload suppression/liaison + icône extraction

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend`.
- **Objectif :** fluidifier le triage (pas de reload sur suppression/liaison) et
  lever l'ambiguïté de l'icône d'extraction (lue comme une recherche).
- **Changements :**
  - `main.py` : `delete_entity` devient no-reload (service + « Saved », plus de
    régénération) ; dans le dispatch partagé, `attach_extracted_property`,
    `detach_extracted_property`, `delete_entities` et `attach_extracted_properties`
    sont exclus du reload (statut « Saved »).
  - `view.py` JS optimiste : rejet/suppression masque déjà la ligne ; la liaison
    (simple et batch) passe la ligne en `entity-item--validated` et masque le ✓ ;
    le détachement repasse en `proposed`.
  - Icône du bouton « Extraire » : nouvelle icône `scan` (viewfinder) au lieu de
    la loupe + libellé « Extraire les entités de la page ».
- **Fichiers modifiés :** `main.py`, `investigations/view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucune nouvelle action CDP ; seul le reload
  (effet de bord) est retiré pour ces actions.
- **Tests exécutés :** `unittest discover` (233) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (icône scan rendue).
- **Vérifications non exécutées :** smoke CDP live du comportement no-reload
  (suppression/liaison simple et batch) — à confirmer en live.
- **Relais :** aucun. Reste demandé : éditeur propriétés classiques (option 1),
  mémoire des noms saisis, filtre des entités extraites.

### AI-20260622-007 — Filtre entités, mémoire des noms, propriétés classiques

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Branche / commits :** `feat/lit-frontend` — `054aa9b` (lots A+B) + lot C.
- **Objectif :** trois retours utilisateur sur le triage et l'édition d'entités.
- **Changements :**
  - **Lot A — filtre (`054aa9b`)** : sur la liste des entités extraites, champ
    « Filtrer les propriétés… » + select de statut (toutes / en attente /
    validées). Filtre les `.entity-chip-row` côté JS (valeur + nom de propriété) ;
    les lignes rejetées/supprimées portent `data-removed` pour rester masquées.
  - **Lot B — mémoire des noms (`054aa9b`)** : `#property-suggestions` agrège
    désormais les clés classiques ET les noms déjà utilisés dans l'enquête
    (`custom_label` / `property_key` des entités + clés des propriétés du graphe)
    via `_property_suggestion_keys`. Aucun stockage ajouté.
  - **Lot C — propriétés classiques** : l'inspecteur d'une entité du graphe
    affiche une section « Propriétés classiques » listant les propriétés suggérées
    de son/ses tagset(s) comme champs de valeur éditables (pré-remplis si déjà
    présents), sauvegarde au blur via `set_graph_entity_property` (passé en
    no-reload).
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`, `main.py`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** `set_graph_entity_property` rejoint les actions
  no-reload ; aucune nouvelle action CDP.
- **Tests exécutés :** `unittest discover` (234) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (filtre, datalist, éditeur de propriétés classiques).
- **Vérifications non exécutées :** smoke CDP live de la saisie au blur des
  propriétés classiques et du filtre — à confirmer en live.
- **Relais :** aucun. Reste basse priorité : durcir la regex téléphone.

## Modèle de compte rendu terminé

```markdown
### AI-YYYYMMDD-NNN — Titre court

- **Agent :**
- **Période UTC :**
- **Branche / commits :**
- **Objectif :**
- **Changements :**
  - ...
- **Fichiers modifiés :**
  - `...`
- **Contrats ou décisions :**
  - ...
- **Tests exécutés :**
  - `commande` — résultat
- **Vérifications non exécutées :**
  - raison
- **Risques / reste à faire :**
  - ...
- **Relais :**
  - prochaine action exacte, ou `aucun`
```

## Modèle de claim

Copier les informations suivantes dans une nouvelle ligne de **Travaux actifs** :

```text
ID: AI-YYYYMMDD-NNN
Agent: Claude | Codex | Copilot | autre
Statut: claimed
Début UTC: YYYY-MM-DD HH:MM
Dernière MAJ UTC: YYYY-MM-DD HH:MM
Objectif: résultat observable en une phrase
Périmètre: fichiers prévus et fichiers explicitement exclus
Tests prévus: commandes ou scénarios
Branche / commit: branche, SHA ou offline
```

Puis ajouter les verrous strictement nécessaires.

## Modèle de point d'étape

```markdown
### Checkpoint — AI-YYYYMMDD-NNN — YYYY-MM-DD HH:MM UTC

- Réalisé :
- Fichiers touchés :
- Tests exécutés :
- Décision ou difficulté :
- Écart de périmètre :
- Prochaine action :
```

Les checkpoints ordinaires peuvent rester dans la PR ou le commit. Les ajouter ici seulement lorsqu'ils sont utiles à un autre agent ou à un relais.

## Résolution de conflit

1. Ne pas écraser l'entrée d'un autre agent.
2. Rebaser et conserver les deux historiques.
3. Le claim le plus ancien conserve le verrou, sauf abandon explicite.
4. Un claim sans mise à jour depuis 24 heures n'est pas supprimé automatiquement :
   - vérifier branche ou commits ;
   - ajouter un relais ou demander arbitrage ;
   - ne reprendre qu'après libération explicite ou décision humaine.
5. Si deux agents ont modifié le même contrat, arrêter l'intégration et consigner le conflit.
6. Les résultats de tests restent factuels ; ne pas fusionner deux exécutions comme si elles n'en formaient qu'une.

## Checklist de clôture

- [ ] Objectif réalisé.
- [ ] Diff relu.
- [ ] Tests ciblés exécutés.
- [ ] Suite large exécutée si nécessaire.
- [ ] `git diff --check` propre.
- [ ] Bundle régénéré si source frontend modifiée.
- [ ] Smoke visuel/CDP réalisé si requis.
- [ ] Documentation mise à jour.
- [ ] Aucun secret, profil, donnée d'enquête ou artefact runtime staged.
- [ ] Verrous retirés.
- [ ] Tâche retirée de **Travaux actifs**.
- [ ] Compte rendu ajouté à **Travaux terminés**.
