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

## Travaux planifiés (à reprendre)

Les lots #1 (archive auto + archive protégée), #2 (provenance vers le snapshot
archivé + surlignage text-fragment), #4 (export ZeroNeurone des propriétés
`page`) et le no-reload restant ont été réalisés (comptes rendus AI-20260622-013
à 016) et **le smoke CDP live a été validé par l'utilisateur le 2026-06-23**
(aucune anomalie). Reste :

- **Basse priorité** : durcir la regex téléphone (`analysis/entities.py`) — elle
  remonte des plages de dates en `téléphone`.
- **Cosmétique** : recalculer côté client les compteurs focus/next-actions après
  les suppressions optimistes (seuls les compteurs de section le sont).
- **Par conception** : `extract_result_entities` (scan), `analyze_result_url`,
  `create_graph_entity*`, `link/unlink` rechargent la page (nouvelles données
  serveur) ; un no-reload exigerait un rendu partiel renvoyé par l'action.

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
  - **Lot C — propriétés classiques (annulé)** : un bloc « Propriétés classiques »
    avait été ajouté sur l'inspecteur d'entité du graphe (commit `efcac6a`) puis
    **retiré** (commit suivant) — l'utilisateur n'en voulait pas. Le besoin réel
    était autre (voir AI-20260622-008).
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md` (lots A+B) ; `main.py` +
  `theme.css` pour le lot C puis son annulation.
- **Contrats ou décisions :** aucune nouvelle action CDP. Lot C annulé.
- **Tests exécutés :** `unittest discover` (233) OK ; `git diff --check` OK (CRLF) ;
  smoke headless (filtre, datalist).
- **Vérifications non exécutées :** smoke CDP live du filtre — à confirmer en live.
- **Relais :** clarifier le découpage propriétés source/page vs entité
  (AI-20260622-008) avant de re-livrer.

### AI-20260622-008 — Découpage propriétés extraites, lots 2 et 3

- **Agent :** Claude puis Codex pour les lots 2/3
- **Période UTC :** 2026-06-22 ; reprise Codex 16:09-16:11
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** terminer la bascule manuelle persistée page/entité et les suggestions de propriétés scopées par tagset lié.
- **Changements :**
  - ajout de l'action CDP no-reload `set_entity_property_scope` ;
  - persistance dédiée de `attributes.property_scope` via service/repository, sans passer par `update_entity_metadata` ;
  - bouton-icône par `.entity-chip-row` pour basculer entre « À rattacher à une entité » et « Propriétés de la page » ;
  - déplacement optimiste de la ligne entre groupes côté client, avec ajustement des contrôles visibles ;
  - datalists `property-suggestions-{result_id}` fondées sur les tagsets des entités du graphe liées à la page, avec mémoire des noms déjà saisis ;
  - fallback conservé vers `#property-suggestions` quand aucune entité liée ne donne de tagset exploitable.
- **Fichiers modifiés :**
  - `main.py`
  - `investigations/view.py`
  - `investigations/service.py`
  - `investigations/repository.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `tests/test_investigations.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - `scope` accepté : `page` ou `entity` uniquement ;
  - aucun bundle Lit à reconstruire, la page reste rendue par Python + JS inline ;
  - le Lot 4 export ZeroNeurone reste à faire séparément.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_investigations` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 237 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome — OK, captures `tmp_ui_render/property_scope_lots_2_3.png` et `tmp_ui_render/property_scope_lots_2_3_rail.png`
- **Vérifications non exécutées :**
  - smoke CDP live de l'action `set_entity_property_scope` non exécuté dans une vraie session navigateur.
- **Risques / reste à faire :**
  - Lot 4 : adapter `exports/zeroneurone.py` pour rattacher les propriétés scope `page` au nœud source/page plutôt qu'à l'entité ;
  - confirmer en live que la bascule no-reload garde bien la position et le statut « Saved. ».
- **Relais :** prochain lot exact : export ZeroNeurone des propriétés `property_scope="page"`.

### AI-20260622-009 — Nettoyage du workspace page

- **Agent :** Codex
- **Période UTC :** 2026-06-22 16:18-16:44
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** alléger le rail des pages enregistrées et renforcer la cohérence entre propriétés de page, propriétés d'entité et preuves.
- **Changements :**
  - suppression du bloc manuel « Linked entities / Link source to... » et des actions `link/unlink` du workspace page ;
  - datalist dédiée `property-suggestions-site-web` pour les propriétés de page/site web, fondée sur le tagset « Site web » et les noms source déjà utilisés ;
  - groupes repliables « À rattacher à une entité », « Propriétés de la page » et `Evidence`, avec sélection multiple et filtre commun sur les propriétés extraites ;
  - compteur `Entities (n)` mis à jour côté client après suppression simple ou groupée ;
  - suppression d'evidence en no-reload : la ligne est retirée côté client et le handler CDP se contente d'enregistrer ;
  - suppression d'une propriété du rail entité avec confirmation explicite et suppression des propriétés extraites liées au même couple entité/propriété ;
  - indication dans le rail que le scan de propriétés s'appuie sur les archives HTML/texte enregistrées.
- **Fichiers modifiés :**
  - `main.py`
  - `investigations/view.py`
  - `investigations/service.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `tests/test_investigations.py`
  - `AI_WORKLOG.md`
  - `investigations/repository.py` : verrou pris mais aucun changement nouveau pour ce lot.
- **Contrats ou décisions :**
  - `delete_evidence_capture` devient no-reload dans la page d'enquête ;
  - `delete_graph_entity_property` supprime aussi les propriétés extraites liées pour éviter les résidus dans les pages enregistrées.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_investigations` — OK, 55 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 238 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome — OK, captures `tmp_ui_render/cases/page_workspace_cleanup.png` et `tmp_ui_render/cases/page_workspace_cleanup_rail.png`
- **Vérifications non exécutées :**
  - smoke CDP live de suppression evidence/propriété non exécuté dans une vraie session navigateur.
- **Risques / reste à faire :**
  - Lot 4 : adapter l'export ZeroNeurone des propriétés `property_scope="page"` vers le nœud source/page ;
  - confirmer en live que les handlers no-reload conservent bien l'état du rail pendant une session CDP réelle.
- **Relais :** aucun blocage ; prochain lot recommandé : export ZeroNeurone des propriétés de page.

### AI-20260622-010 — Ajustements rail page après retour visuel

- **Agent :** Codex
- **Période UTC :** 2026-06-22 17:19-17:24
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** conserver la lecture des entités utilisant une page, clarifier les groupes repliables et conditionner le scan aux archives HTML/texte.
- **Changements :**
  - ajout d'un bloc lecture seule « Entités utilisant cette page » dans le rail page, construit depuis les liens explicites et les propriétés extraites déjà rattachées ;
  - les entrées de ce bloc ouvrent directement le détail de l'entité dans le workspace ;
  - ajout d'un chevron CSS visible sur les groupes repliables d'entités/propriétés de page ;
  - désactivation du bouton de scan quand la page n'a aucune archive exploitable (`html`, `mhtml`, `text`/`txt` ou mime texte/html) ;
  - warning orange dans ce cas pour expliquer l'action attendue ;
  - tests de rendu pour la liste liée et le scan désactivé.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - la datalist de propriétés reste une combinaison du tagset global applicable et des noms déjà présents dans l'enquête courante uniquement ;
  - `extract_result_entities` conserve son reload : l'action produit de nouvelles lignes calculées côté Python.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 20 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 239 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome — OK, captures `tmp_ui_render/cases/page_workspace_archive_ready_rail.png` et `tmp_ui_render/cases/page_workspace_no_archive_rail.png`
- **Vérifications non exécutées :**
  - smoke CDP live non exécuté.
- **Risques / reste à faire :**
  - le scan reste volontairement avec reload ; une version no-reload demanderait un rendu partiel ou un contrat CDP de retour de lignes.
- **Relais :** aucun.

### AI-20260622-011 — Extraction depuis les archives Evidence

- **Agent :** Codex
- **Période UTC :** 2026-06-22 17:33-17:37
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** replacer l'action d'extraction automatique au niveau de l'archive source et alléger le rail `Entities`.
- **Changements :**
  - suppression du message warning inline dans `Entities` ;
  - conservation d'une icône désactivée avec tooltip dans `Entities` uniquement quand aucune archive HTML/texte exploitable n'existe ;
  - ajout d'un bouton d'extraction sur chaque evidence disposant d'un artefact exploitable (`html`, `mhtml`, `text`/`txt` ou mime texte/html) ;
  - espacement vertical renforcé dans le bloc `Entities` ;
  - tests adaptés au nouveau placement du scan.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - l'action reste `extract_result_entities` au niveau page/résultat ; le bouton est déplacé visuellement sur l'archive exploitable.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 20 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 239 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome — OK, captures `tmp_ui_render/cases/page_workspace_archive_ready_rail.png` et `tmp_ui_render/cases/page_workspace_no_archive_rail.png`
- **Vérifications non exécutées :**
  - smoke CDP live non exécuté.
- **Risques / reste à faire :**
  - si l'on veut scanner une archive précise parmi plusieurs, il faudra faire évoluer le contrat CDP pour accepter un `captureId`.
- **Relais :** aucun.

### AI-20260622-010 — Fix overflow rail + persistance file d'actions

- **Agent :** Claude
- **Période UTC :** 2026-06-22 (par-dessus le travail non committé de Codex,
  lots 2/3 et 009).
- **Objectif :** deux bugs signalés en live : rail qui déborde horizontalement
  sur valeur longue, et éléments supprimés (entités/preuves) qui réapparaissent
  au refresh.
- **Changements :**
  - `theme.css` : `min-width: 0` ajouté sur `.result-entities` (& voisins de la
    grille `.inspector-panel__details`), `.entity-group` et `.entity-chip-list`,
    pour que l'ellipsis de `.entity-chip-row__value` s'applique enfin malgré les
    nouveaux conteneurs (groupes `<details>` de Codex) → plus d'overflow.
  - `investigations/view.py` (JS) : la file d'actions (`actionQueue`) est
    persistée en `localStorage` (clé `synthesix:action-queue:{id}`), relue au
    chargement, et réécrite à chaque `queueAction`/`consumeAction`. Une action
    no-reload encore en attente (ex. une suppression) survit donc à un refresh
    manuel au lieu d'être perdue → l'élément ne réapparaît plus.
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP modifié ; comportement no-reload
  conservé mais rendu sûr au refresh.
- **Tests exécutés :** `unittest discover` (239) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (URL longue tronquée, rail sans overflow).
- **Vérifications non exécutées :** smoke CDP live (rejouer une suppression après
  refresh) — à confirmer en live.
- **Risques / reste à faire :** après refresh, un élément supprimé mais pas encore
  consommé peut se réafficher brièvement le temps que l'action rejouée passe (puis
  disparaît) ; acceptable vs perte définitive. Lot 4 export reste à faire.

### AI-20260622-011 — Masquer propriétés vides + ajout manuel de propriété

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Objectif :** deux retours : ne plus afficher les propriétés d'entité vides,
  et permettre l'ajout manuel d'une propriété sourcée à une entité.
- **Changements :**
  - `investigations/view.py` : la liste `PROPRIÉTÉS` d'une entité ignore les
    propriétés à valeur vide (`if str(value or "").strip()`).
  - `investigations/view.py` : formulaire d'ajout manuel `data-add-property`
    (champ Propriété avec `list="property-suggestions"` + champ Valeur + bouton
    Ajouter) dans la section Propriétés ; au submit, `set_graph_entity_property`
    (action existante, avec reload → la nouvelle propriété apparaît).
  - `theme.css` : style `.graph-property-add*`.
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun nouveau contrat CDP (réutilise
  `set_graph_entity_property`). Revient sur la décision « pas d'ajout manuel »
  (cas d'usage : sourcer des personnes connues d'avance).
- **Tests exécutés :** `unittest discover` (240) OK ; `git diff --check` OK
  (CRLF) ; smoke headless (propriétés vides masquées, formulaire d'ajout rendu).
- **Vérifications non exécutées :** smoke CDP live de l'ajout manuel.
- **Risques / reste à faire :** demandes overlay (#1 archive auto à la création
  depuis page + #2 indicateur visuel de provenance) non traitées — à cadrer.

### AI-20260622-012 — Audit no-reload + conversions (favori, suppression page)

- **Agent :** Claude
- **Période UTC :** 2026-06-22
- **Objectif :** recenser les actions qui reloadent la page d'investigation et
  passer en no-reload celles qui le peuvent (demande utilisateur).
- **Audit :**
  - **Déjà no-reload** : `update_entity_status`, `update_entity_metadata`,
    `delete_entity`, `attach`/`detach_extracted_property`, `delete_entities`,
    `attach_extracted_properties`, `set_entity_property_scope`,
    `delete_evidence_capture`, `delete_graph_entity_property`.
  - **Converties ce lot** : `update_investigation_result` (favori/statut/tags/
    notes) et `remove_saved_page` (suppression de page).
  - **Convertibles plus tard** (petit JS optimiste) : `set_graph_entity_property`
    (ajout manuel), `delete_zeroneurone_export`, `delete_page_monitor`.
  - **Doivent reloader** (nouvelles données serveur) : `extract_result_entities`
    (scan), `analyze_result_url`, `create_graph_entity*`, `link/unlink`,
    `create_page_monitor`, `archive_page_to_investigation`,
    `capture_evidence_to_investigation`, `verify_evidence_capture`,
    `export_zeroneurone`. Un vrai no-reload pour le scan/analyse exigerait que
    l'action renvoie les nouvelles lignes pour insertion côté page (refonte du
    protocole d'action) = lot séparé.
- **Changements :**
  - `main.py` : `update_investigation_result` et `remove_saved_page` ne
    régénèrent plus la page (service + « Saved. »).
  - `investigations/view.py` (JS) : le retrait d'une page enlève la carte **et**
    son panneau de rail ; `saveResult` met à jour `data-favorite` (filtre/métrique
    favoris cohérents sans reload).
- **Fichiers modifiés :** `main.py`, `investigations/view.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP modifié.
- **Tests exécutés :** `unittest discover` (240) OK ; `git diff --check` OK
  (CRLF).
- **Vérifications non exécutées :** smoke CDP live (favori + suppression de page
  sans reload).
- **Relais :** reste no-reload + #1/#2 + lot 4 consignés en « Travaux planifiés ».

### AI-20260622-013 — Archive de provenance et export page-scope

- **Agent :** Codex
- **Période UTC :** 2026-06-22 22:02-22:22
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** archiver automatiquement la page lors des créations/rattachements depuis l'overlay, protéger les archives de provenance, pointer les badges source vers le snapshot archivé et exporter les propriétés `page` sur le nœud source ZeroNeurone.
- **Changements :**
  - ajout d'une réutilisation d'archive `page_archive` récente lors de `create_graph_entity_from_selection` et `attach_selection_to_graph_entity` ;
  - persistance de `attributes.source_capture_id` sur l'entité extraite attachée ;
  - garde service + helper main pour refuser la suppression d'une archive référencée comme provenance ;
  - `remove_saved_page` supprime désormais les captures liées à la page en base, et le handler retire aussi leurs dossiers locaux ;
  - rendu des badges de provenance vers l'artefact HTML/texte archivé avec fragment `#:~:text=...` et bouton suppression désactivé pour les captures protégées ;
  - export ZeroNeurone : les propriétés `attributes.property_scope == "page"` enrichissent le nœud source/page au lieu de devenir des nœuds de fait ou des propriétés d'entité.
- **Fichiers modifiés :**
  - `main.py`
  - `investigations/service.py`
  - `investigations/repository.py`
  - `investigations/view.py`
  - `exports/zeroneurone.py`
  - `tests/test_main.py`
  - `tests/test_investigations.py`
  - `tests/test_investigation_view.py`
  - `tests/test_zeroneurone_export.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - pas de modification du bundle overlay Lit ; le CDP existant déclenche toujours les mêmes actions, le comportement serveur archive ensuite la page ;
  - le surlignage utilise le text fragment navigateur plutôt qu'une mutation du HTML archivé.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_main tests.test_investigations tests.test_investigation_view tests.test_zeroneurone_export` — OK, 100 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 243 tests
  - `.venv\Scripts\python.exe -m py_compile main.py investigations\service.py investigations\repository.py investigations\view.py exports\zeroneurone.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - `npm run typecheck` / `npm run build` non exécutés car aucun fichier `frontend/src/overlay/*` ni bundle `assets/synthesix-overlay.js` n'a été modifié ;
  - smoke CDP live non exécuté dans cette session : à faire sur une vraie page externe pour confirmer archive créée, badge vers snapshot surligné et suppression archive bloquée.
- **Risques / reste à faire :**
  - vérifier en live le rendu du text-fragment selon le navigateur/artefact (HTML préféré, texte en fallback).
- **Relais :** smoke CDP live overlay, puis décider si les actions no-reload restantes méritent un lot séparé.

### AI-20260622-014 — No-reload restant et restauration du workspace

- **Agent :** Codex
- **Période UTC :** 2026-06-22 22:28-22:45
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** convertir les actions simples restantes en no-reload et restaurer le contexte du rail après les actions serveur qui doivent rafraîchir.
- **Changements :**
  - `set_graph_entity_property` passe en no-reload côté `main.py` ;
  - ajout manuel de propriété : insertion/mise à jour optimiste de la ligne dans le panneau entité, avec suppression réutilisable sur la nouvelle ligne ;
  - `delete_zeroneurone_export` passe en no-reload avec suppression optimiste de la carte export et mise à jour du compteur ;
  - `delete_page_monitor` passe en no-reload avec retrait optimiste des cartes/boutons monitoring et mise à jour du compteur ;
  - ajout d'un `localStorage` de contexte par enquête (`synthesix:view-state:*`) pour restaurer rail page/entité/création et position de scroll après `extract_result_entities`, `analyze_result_url`, `create_page_monitor` et créations d'entité.
- **Fichiers modifiés :**
  - `main.py`
  - `investigations/view.py`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucune modification du bundle Lit/overlay ;
  - scan/analyse/create continuent à recharger la page, mais restaurent le workspace pertinent.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_main tests.test_investigation_view` — OK, 47 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 243 tests
  - `.venv\Scripts\python.exe -m py_compile main.py investigations\view.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - smoke navigateur live non exécuté dans cette session ;
  - `npm run typecheck` / `npm run build` non exécutés car aucun fichier frontend Lit ni bundle `assets/synthesix-overlay.js` n'a été modifié.
- **Risques / reste à faire :**
  - vérifier en UI réelle que le scroll restauré place bien le rail au bon endroit après un scan long ;
  - les compteurs de focus/next-actions ne sont pas recalculés côté client pour ces suppressions optimistes, uniquement les compteurs de section.
- **Relais :** aucun.

### AI-20260622-015 — Correctif parsing JS inline no-reload

- **Agent :** Codex
- **Période UTC :** 2026-06-22 22:50-22:55
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** réparer les boutons/workspace inertes causés par un script inline invalide.
- **Changements :**
  - correction de l'injection dynamique des icônes SVG dans le JS inline via `json.dumps(...)`, afin d'échapper correctement les guillemets du SVG ;
  - ajout d'un test qui génère une page d'investigation et lance `node --check` sur le script inline quand Node est disponible.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `tests/test_investigation_view.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucun contrat CDP modifié.
- **Tests exécutés :**
  - génération temporaire d'une page + `node --check` sur le script inline — OK
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 22 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 244 tests
  - `.venv\Scripts\python.exe -m py_compile investigations\view.py tests\test_investigation_view.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - smoke navigateur manuel non exécuté dans cette session.
- **Risques / reste à faire :**
  - recharger la page d'enquête ouverte dans Chrome pour récupérer le HTML régénéré.
- **Relais :** aucun.

### AI-20260622-016 — Lisibilité propriétés extraites et doublons de rattachement

- **Agent :** Codex
- **Période UTC :** 2026-06-22 23:00-23:09
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** rendre les lignes de propriétés extraites plus logiques et demander une décision avant de rattacher un doublon.
- **Changements :**
  - en-tête des lignes extraites réordonné : nom de propriété, badge de type de donnée, valeur détectée ;
  - inférence de type affichée même sans type explicite (`Nombre`, `Texte`, etc.) ;
  - options de rattachement enrichies avec les propriétés existantes de l'entité cible ;
  - warning JS au rattachement si une propriété du même nom existe déjà : `A` ajoute/concatène avec `;`, `R` remplace, annuler ne fait rien ;
  - `attach_extracted_property` accepte `duplicate_strategy=append|replace` et applique la stratégie côté service ;
  - le rattachement multiple propage aussi la stratégie choisie par ligne.
- **Fichiers modifiés :**
  - `investigations/view.py`
  - `investigations/service.py`
  - `main.py`
  - `theme.css`
  - `tests/test_investigation_view.py`
  - `tests/test_investigations.py`
  - `AI_WORKLOG.md`
- **Contrats ou décisions :**
  - aucune modification du bundle Lit/overlay ;
  - `append` reste le comportement par défaut côté service pour compatibilité.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_investigations` — OK, 60 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 245 tests
  - `.venv\Scripts\python.exe -m py_compile investigations\view.py investigations\service.py main.py tests\test_investigation_view.py tests\test_investigations.py` — OK
  - génération temporaire d'une page + `node --check` sur le script inline — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Vérifications non exécutées :**
  - smoke navigateur manuel non exécuté dans cette session.
- **Risques / reste à faire :**
  - vérifier visuellement le wording du prompt natif ; si besoin, remplacer plus tard par une modale Synthesix custom.
- **Relais :** aucun.

### AI-20260623-001 — Durcir l'extraction (faux positifs téléphone/domaine)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** réduire les faux positifs d'extraction (l'utilisateur voyait
  trop de bruit, surtout des plages de dates remontées en téléphone).
- **Changements (`analysis/entities.py`) :**
  - `YEAR_RANGE_PATTERN` (« 2008-2010 », « 2012 à 2015 », « 1998/2004 ») ajouté
    aux `protected_number_spans` → plus jamais pris pour un téléphone.
  - `_looks_like_phone(value)` : un candidat n'est retenu comme téléphone que s'il
    a un préfixe `+`, un `0` initial (national), ou ≥2 séparateurs de groupage.
    Les runs bruts (« 20082010 ») sont rejetés.
  - `FILE_EXTENSIONS` : les « domaines » dont le TLD est une extension de fichier
    (`rapport.pdf`, `logo.png`, …) sont ignorés.
- **Fichiers modifiés :** `analysis/entities.py`, `tests/test_entities.py`,
  `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP ; comportement d'extraction plus
  strict (peut produire quelques faux négatifs assumés sur des runs ambigus).
- **Tests exécutés :** `unittest tests.test_entities` (11) OK ; `unittest discover`
  (247) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** validation sur corpus réel (pages variées) —
  à confirmer à l'usage.
- **Risques / reste à faire :** **gap pré-existant** (non causé par ce lot) — un
  téléphone FR pointé « 01.40.24.18.39 » contient « 01.40.24 » que
  `NUMERIC_DATE_PATTERN` capture comme une date (mois invalide non vérifié) et
  dont le span protège la zone → le téléphone pointé n'est pas auto-extrait.
  Correctif possible : ne protéger/émettre une date numérique que si mois/jour
  sont plausibles (1-12 / 1-31). À traiter séparément (touche la logique date).

### AI-20260623-002 — Moteurs/overlay : Bing redirects, overlay Maps/Lens, attente DDG

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** trois correctifs moteurs/overlay signalés par l'utilisateur.
- **Changements :**
  - **Bing (`bing.py`)** : `resolve_bing_redirect()` décode les liens
    `bing.com/ck/a?...&u=a1<base64url>` vers l'URL réelle, appliqué dans
    `parse_results`. Les résultats Bing fusionnent désormais avec les autres
    moteurs (le merge se fait sur `link`).
  - **Overlay (`main.py`)** : `_overlay_injection_blocked()` empêche l'injection
    de l'overlay sur Lens (`lens.google.*`) et Maps (`maps.google.*`,
    `*.google.*/maps`) ; `_install_and_consume_save_overlay` retourne `None` sur
    ces hôtes. Évite le crash navigateur (notamment la reconnaissance d'image
    intégrée de Chrome = Lens).
  - **DuckDuckGo (`duckduckgo.py`)** : `looks_like_duckduckgo_no_results()` +
    court-circuit dans `_wait_for_result_content` → on arrête d'attendre dès que
    la page indique « no results » au lieu de poller les 10 s complètes.
- **Fichiers modifiés :** `bing.py`, `main.py`, `duckduckgo.py`,
  `tests/test_engines.py`, `tests/test_main.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucune action CDP modifiée ; comportement moteurs
  inchangé hormis le décodage Bing et le court-circuit DDG ; pas de bundle
  overlay touché (la garde est côté serveur).
- **Tests exécutés :** `unittest tests.test_engines tests.test_main` (57) OK ;
  `unittest discover` (255) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** smoke live (utilisateur) — fusion réelle des
  résultats Bing, absence de crash overlay sur Lens/Maps, et attente DDG réduite
  sur une requête sans résultats.
- **Risques / reste à faire :** la détection « no results » DDG s'appuie sur le
  texte visible (post-rendu) ; à confirmer sur le rendu réel (JS + endpoint
  HTML). Le gap téléphone pointé FR (date vs téléphone) reste ouvert.

### AI-20260623-003 — Overlay : ne plus renvoyer le bundle à chaque poll

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** corriger le gel du rendu de la page hôte quand Lens est actif et
  Synthesix tourne (confirmé par l'utilisateur : gel uniquement avec Synthesix).
- **Diagnostic :** `_install_and_consume_save_overlay` ré-évaluait à **chaque
  cycle de poll** un `tab.evaluate` contenant le bundle overlay complet (~100 KB)
  intégré dans la chaîne JS. Même si l'exécution est gardée (`if (!host)` /
  `!window.SynthesixOverlay`), le moteur JS de la page **re-parse** cette grosse
  chaîne sur le thread principal à chaque cycle. Sur un rendu déjà chargé (Lens
  en panneau latéral, URL = page hôte), ce parse répété fige la page.
- **Changements (`main.py`) :** pré-check léger `await tab.evaluate("!!window.
  SynthesixOverlay")` ; si le bundle est déjà chargé, on envoie
  `overlayBundle = ""` dans l'eval principal au lieu de re-transférer/re-parser
  le bundle. Bénéfice général sur toutes les pages, pas seulement Lens.
- **Fichiers modifiés :** `main.py`, `tests/test_main.py`, `AI_WORKLOG.md`
- **Contrats ou décisions :** aucun contrat CDP modifié ; bundle overlay
  inchangé (toujours injecté à la première fois, plus re-transféré ensuite).
- **Tests exécutés :** `unittest tests.test_main` (31) OK ; `unittest discover`
  (257) OK ; `git diff --check` OK (CRLF). Mock `test_external_page_overlay_
  returns_save_action` adapté au pré-check.
- **Vérifications non exécutées :** smoke live (utilisateur) — confirmer que Lens
  sur une page (ex. `pappers.fr`) ne gèle plus avec Synthesix lancé.
- **Risques / reste à faire :** si le gel persiste, c'est que la cause n'est pas
  (que) le parse du bundle → activer le mode verbose pour capturer une éventuelle
  erreur CDP, et envisager un timeout sur les `evaluate` d'onglets externes.

### AI-20260623-004 — Refonte export ZeroNeurone (graphe curé)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** 4 retours utilisateur sur l'export du graphe curé.
- **Décisions utilisateur :** libellé lien source = « Trouvé sur » ; nœud projet
  « RV » retiré du graphe.
- **Changements (`exports/zeroneurone.py`, fonction `_build_curated_graph` + natif) :**
  1. **ID/Manifeste masqués** : `HIDDEN_NATIVE_PROPERTIES = {synthesix_id,
     manifest_path}` exclus du rendu dans `_native_properties` et
     `_serializable_properties` (gardés en interne pour le rattachement fichiers).
  2. **Evidences → fichiers d'entités** : plus de nœuds `evidence-*` dans le
     graphe curé ; `_copy_native_assets` re-mappe les artefacts vers les entités
     liées (via `linked_result_ids`) ; `_write_native_dossier` pose les `assetIds`
     sur ces entités. Fallback conservé sur le nœud preuve pour le chemin
     « résultats seuls » (sans entités curées).
  3. **Nœud « RV » retiré** : plus de nœud projet ni d'arêtes `CONTAINS` dans le
     graphe curé (l'enquête reste dans les métadonnées du dossier).
  4. **URLs source = entités** : chaque page source devient un nœud « Site web »
     relié à l'entité par une arête **« Trouvé sur »** ; la propriété « Sources »
     est supprimée.
- **Périmètre :** changements sur le **graphe curé** (cas réel de l'utilisateur).
  Le chemin « résultats seuls » (sans `graph_entities`) garde son comportement
  (nœud investigation + nœuds preuve).
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest tests.test_zeroneurone_export` (17) OK ;
  `unittest discover` (258) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** smoke live dans ZeroNeurone (import du bundle,
  fichiers visibles sur les entités, liens « Trouvé sur ») — à confirmer par
  l'utilisateur.

### AI-20260623-005 — Mise en page de l'export curé (lisibilité)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** l'export curé s'affichait en une seule ligne verticale (peu
  lisible) car entités (`curated_entity`, x≈650) et URLs source (`result`,
  x=700) tombaient quasiment dans la même colonne.
- **Changements (`exports/zeroneurone.py`) :** `_native_positions` prend
  désormais les arêtes ; nouvelle `_curated_positions` place les entités en
  colonne (x=0) et les URLs source **alignées à droite sur la même ligne** que
  l'entité (via les arêtes « Trouvé sur »). Le chemin « résultats seuls » garde
  la mise en page en colonnes par type.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest tests.test_zeroneurone_export` (18) OK ;
  `unittest discover` (259) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** rendu réel dans ZeroNeurone — à confirmer.
- **Risques / reste à faire :** pour beaucoup d'entités, une disposition en
  grille (plutôt qu'une colonne) serait plus compacte — itération possible si
  besoin.

### AI-20260623-006 — Export ZeroNeurone : dates, taille nœud, mise en page

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** retours utilisateur : dates qui disparaissent (date de naissance
  absente), nœuds qui ne s'adaptent pas au contenu, cascade peu lisible.
- **Changements (`exports/zeroneurone.py`) :**
  1. **Dates** : un fait `date` ne devient un événement que s'il parse
     (`_entity_events`) ; sinon il reste une **propriété** (ne disparaît plus).
     Libellé d'événement = `custom_label` → `property_key` → « Événement détecté ».
  2. **Taille nœud** : `_content_size(label)` (small/medium/large selon longueur)
     posée comme taille de base dans `_native_visual` ; les URLs longues ne sont
     plus tassées (les tagsets ne forçant pas de taille, le contenu prime).
  3. **Mise en page** : `_curated_positions` donne à chaque entité un **bloc
     vertical** dimensionné sur son éventail de sources (pas de chevauchement),
     entités à gauche, sources à droite, écarts élargis.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (260) OK ; `git diff --check` OK (CRLF).
- **Vérifications non exécutées :** rendu réel ZeroNeurone — à confirmer.
- **Risques / reste à faire :** date de naissance absente peut aussi venir d'un
  fait non rattaché à l'entité (triage) — hors export. Disposition grille possible
  si beaucoup d'entités.


### AI-20260623-007 — Export ZeroNeurone : valeurs date en ISO

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** propriété date (ex. « Date de naissance » = `19/10/2003`)
  s'exportait avec type `date` mais valeur non-ISO → champ date vide dans
  ZeroNeurone.
- **Changements (`exports/zeroneurone.py`) :** `_iso_property_date()` normalise
  les valeurs de propriétés de type `date` vers `YYYY-MM-DD` (parse `DD/MM/YYYY`,
  `DD-MM-YYYY`, ISO…) dans `_native_properties`. Inchangé si non parsable.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (261) OK.
- **Vérifications non exécutées :** rendu réel ZeroNeurone — à confirmer.

### AI-20260623-008 — Relations entité↔entité (mot-clé)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** lier deux entités par un mot-clé/phrase (ex. « PDG de »),
  no-reload + save au blur.
- **Changements :**
  - Migration 15 : table `investigation_entity_relations` (source, target,
    label).
  - `repository.py` : `add_entity_relation` (id client accepté),
    `update_entity_relation`, `delete_entity_relation`,
    `list_entity_relations_by_source`.
  - `service.py` : `add/update/delete_graph_entity_relation` ; workspace_payload
    injecte `relations` par entité (avec `target_label`).
  - `main.py` : actions CDP `add/update/delete_graph_entity_relation`
    (no-reload).
  - `view.py` : section « Relations » sur la carte entité (liste éditable +
    formulaire « mot-clé » + select entité) ; JS optimiste (id relation généré
    client via `crypto.randomUUID`), save au blur, suppression.
  - `theme.css` : styles relations.
  - `exports/zeroneurone.py` : relations → arêtes étiquetées (label = mot-clé,
    sinon « Lié à ») entre entités.
- **Fichiers modifiés :** `investigations/migrations.py`,
  `investigations/repository.py`, `investigations/service.py`, `main.py`,
  `investigations/view.py`, `theme.css`, `exports/zeroneurone.py`,
  `tests/test_investigations.py`, `tests/test_zeroneurone_export.py`,
  `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (264) OK ; `git diff --check` OK ;
  smoke headless (section Relations rendue).
- **Vérifications non exécutées :** smoke CDP live (ajout/édition/suppression
  relation no-reload) — à confirmer.

### AI-20260623-010 — Relations visibles aussi sur l'entité cible (inverse)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** une relation A→B doit aussi apparaître sur B (en inverse).
  Revert de l'affichage en phrase (AI-20260623-009, commit revert `2c0582c`).
- **Changements :**
  - `repository.py` : `list_entity_relations_by_target` (relations entrantes
    avec `source_label`).
  - `service.py` : workspace_payload ajoute `incoming_relations` par entité.
  - `view.py` : sur la carte entité, lignes entrantes en lecture seule
    « ← {source} : {mot-clé} » + suppression (réutilise `delete-relation`).
  - `theme.css` : style ligne entrante (italique).
- **Fichiers modifiés :** `investigations/repository.py`,
  `investigations/service.py`, `investigations/view.py`, `theme.css`,
  `tests/test_investigations.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (264) OK ; smoke headless (ligne
  entrante sur la cible).
- **Vérifications non exécutées :** smoke CDP live.

### AI-20260623-011 — Relations cliquables (aller à l'entité)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** rendre la cible (sortante) et la source (entrante) d'une
  relation cliquables pour ouvrir l'entité liée.
- **Changements (`investigations/view.py`, `theme.css`) :** la cible/source
  devient un bouton `entity-relation__goto` avec `data-relation-goto={entité}` ;
  clic → `selectInspectorEntity(id)` (handler délégué sur la carte). Append
  optimiste produit aussi le bouton. CSS lien (hover accent + souligné).
- **Fichiers modifiés :** `investigations/view.py`, `theme.css`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (264) OK (inclut `node --check` du JS
  inline) ; smoke headless.
- **Vérifications non exécutées :** smoke CDP live.

### AI-20260623-012 — Scan : pas de popup doublon sur propriété vide + mémoire = validées

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** (1) le scan d'une archive sur une entité neuve affichait la
  popup ajouter/remplacer pour les propriétés de base (SIREN/SIRET) pourtant
  vides ; (2) les noms gardés en mémoire (datalists) incluaient les propriétés
  proposées → beaucoup de déchet.
- **Changements (`investigations/view.py`) :**
  - `duplicateStrategyForAttach` : si la valeur existante est vide (placeholder
    de tagset), on remplit sans demander (strategy `replace`, pas de prompt).
  - `_property_suggestion_keys`, `_used_property_suggestion_keys` (scoped),
    `_source_property_suggestion_keys` : n'ajoutent les noms d'entités extraites
    que si `status == "validated"`.
- **Fichiers modifiés :** `investigations/view.py`,
  `tests/test_investigation_view.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (265) OK (asserts datalist adaptés +
  nouveau test mémoire-validées).
- **Vérifications non exécutées :** smoke CDP live.

### AI-20260623-013 — Import de fichiers locaux (preuves/sources)

- **Agent :** Claude
- **Période UTC :** 2026-06-23
- **Objectif :** glisser/déposer (ou choisir) un fichier local (PDF…) dans
  Synthesix comme preuve/source, avec URL source optionnelle (vide si externe).
- **Changements :**
  - Migration 16 : reconstruit `evidence_captures` pour autoriser
    `capture_kind = 'imported'`.
  - `main.py` : `_import_evidence_file` (décode base64, écrit le fichier sous
    `evidence_dir/<inv>/<capture>/`, sha256, manifeste, `record_evidence_capture`
    kind `imported`). Si URL → `save_page(url)` ; sinon page synthétique
    `https://files.synthesix.local/<id>` (source_url vide). Action CDP
    `import_evidence_file` (reload pour afficher la preuve).
  - `view.py` : section « Importer un fichier » avec zone de drop + input URL
    optionnel ; JS `FileReader`→base64→`queueAction`.
  - `theme.css` : style dropzone.
- **Fichiers modifiés :** `investigations/migrations.py`, `main.py`,
  `investigations/view.py`, `theme.css`, `tests/test_investigations.py`,
  `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (265) OK (migration + JS inline check) ;
  schema_version=16.
- **Vérifications non exécutées :** smoke live (drag-drop réel d'un PDF, fichier
  rattaché à l'entité via la page source).
- **Risques / reste à faire :** fichiers externes créent une page source
  synthétique (`files.synthesix.local`) ; à terme, regrouper sous une source
  « Fichiers importés » unique serait plus propre.

### AI-20260630-001 — Import de fichiers : déblocage, ouverture, badge + filtre

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Objectif :** rendre l'import de fichiers locaux réellement fonctionnel
  (tous types), ouvrable, et distinguable des pages web dans la liste.
- **Changements :**
  - `investigations/repository.py` : `record_evidence_capture` rejetait
    `capture_kind='imported'` (allowlist Python `{screenshot, page_archive}`
    non synchronisée avec la migration 16) → tout import levait
    `InvestigationValidationError`. Ajout de `imported` à l'allowlist.
  - `investigations/view.py` : helper `_imported_artifact_view` (href local
    relatif + détection image). Le titre du résultat et l'inspector panel
    pointent vers le fichier local (au lieu de l'URL synthétique injoignable)
    et affichent « Imported document ». `_evidence_markup` : lien « Ouvrir »
    pour tout import, miniature image inline ou vignette « FICHIER » générique.
    Carte résultat : badge « Imported document » + `data-imported`. Filtre
    « Type » (Tous / Pages web / Documents importés) intégré au JS de filtrage
    existant (recherche et autres filtres préservés). Indication dropzone
    élargie (PDF, image, audio, vidéo, document…).
  - `i18n.js` : 5 clés (`Type`, `All types`, `Web pages`,
    `Imported documents`, `Imported document`) ajoutées dans `multilingual`
    (fr/es/zh) et `additionalTranslations` (pt/de).
  - `theme.css` : styles `.result-type-badge` et `.evidence-thumbnail--file`.
- **Fichiers modifiés :** `investigations/repository.py`,
  `investigations/view.py`, `i18n.js`, `theme.css`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (265) OK ; `test_i18n_coverage` OK ;
  repros de rendu hors-ligne (href local résolvant vers fichier existant,
  badge, `data-imported`, filtre Type) OK ; `git diff --check` propre.
- **Vérifications non exécutées :** néant de bloquant — smoke UI réel
  (upload tous types, ouverture, badge, filtre, thèmes clair/sombre) **validé
  par l'utilisateur le 2026-06-30**.
- **Risques / reste à faire :** l'URL synthétique reste dans l'index de
  recherche (`data-search`, invisible) ; regroupement « Fichiers importés »
  comme source unique toujours possible plus tard.

### AI-20260630-002 — No-reload : régénérer le fichier page après sauvegarde

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Objectif :** corriger le bug où une action no-reload (suppression, etc.)
  s'enlève visuellement mais réapparaît au F5 jusqu'au prochain redémarrage.
- **Cause racine :** les handlers no-reload de `main.py` persistaient bien en
  base via le service mais ne régénéraient jamais le HTML statique sur disque
  (`generate_investigation_page`). Un F5 rechargeait donc le fichier périmé ;
  seul un redémarrage régénérait la page depuis la base.
- **Changements (`main.py`) :**
  - `_refresh_investigation_page_file` : régénère le fichier page sur disque
    sans recharger l'onglet (try/except → log debug si échec).
  - `_save_in_place` : régénère le fichier puis pose le statut « Saved. ».
  - les 11 sites no-reload (`update_investigation_result`, `update_graph_entity`,
    `delete_graph_entity_property`, dispatch partagé `set_graph_entity_property`
    /relations/attach/detach/scope/batch, `update_entity_status`,
    `update_entity_metadata`, `delete_entity`, `delete_zeroneurone_export`,
    `remove_saved_page`, `delete_evidence_capture`, `delete_page_monitor`)
    appellent désormais `_save_in_place`. L'onglet ouvert n'est pas rechargé.
- **Fichiers modifiés :** `main.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `py_compile main.py` OK ;
  `unittest tests.test_investigations tests.test_investigation_view` (63) OK ;
  `git diff --check` propre.
- **Vérifications non exécutées :** smoke CDP live (action no-reload puis F5
  réel reflétant l'état) — à confirmer en session navigateur.

### AI-20260630-003 — Perte d'artefacts en migration 16 : fix runner + récupération

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Objectif :** comprendre la disparition du bouton scan / miniatures sur les
  anciennes captures, corriger la cause, restaurer les données.
- **Cause racine :** la migration 16 reconstruit `evidence_captures`
  (`DROP TABLE` + recreate). Le runner ouvre chaque migration avec
  `PRAGMA foreign_keys = ON` ; or `evidence_artifacts.capture_id` a
  `ON DELETE CASCADE` → le DROP a cascade-supprimé **toutes** les lignes
  `evidence_artifacts` des captures antérieures (8 lignes restantes pour 40
  captures ; 36 captures sans artefact → `_has_extractable_archive` faux →
  pas de bouton scan ni miniature).
- **Changements (code) :** `investigations/repository.py` — le runner exécute
  désormais chaque migration avec `PRAGMA foreign_keys = OFF` autour du
  `BEGIN/COMMIT` (le PRAGMA est inopérant dans une transaction) puis
  `PRAGMA foreign_key_check` après pour détecter une vraie violation
  d'intégrité (lève `IntegrityError` le cas échéant).
- **Récupération données (hors dépôt) :** script ponctuel relisant chaque
  `manifest.json` (intact sur disque) pour réinsérer les lignes
  `evidence_artifacts` manquantes. Backup `data/synthesix.db.bak-<ts>` créé
  avant écriture. Résultat : 80 lignes réinsérées (8 → 88), 36 → 0 captures
  sans artefact, 0 fichier manquant. Régénération de la page d'enquête :
  boutons scan 2 → 14, miniatures images restaurées.
- **Fichiers modifiés :** `investigations/repository.py`, `AI_WORKLOG.md`
- **Tests exécutés :** `unittest discover` (265) OK (les 16 migrations
  s'appliquent proprement avec FK OFF + `foreign_key_check`).
- **Vérifications non exécutées :** aucun test unitaire dédié au runner ajouté
  (le tester exige un refacto : la fin de `initialize()` lit des tables réelles,
  donc patcher `MIGRATIONS` casse). À ajouter si souhaité.
- **Risques / reste à faire :** récupération appliquée à la base locale de
  l'utilisateur uniquement ; toute autre base déjà migrée garde la perte tant
  que le script de récupération n'est pas rejoué (manifests requis).

### AI-20260630-005 — Graphe de relations des entités (composant Lit) + toggle Liste/Graphe

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** présenter les entités d'une enquête sous forme de graphe de
  relations (retour utilisateur : préférence pour un graphe type link-analysis
  plutôt qu'une liste dense ou des infos en ligne). Une première piste de
  densification + preview de propriétés inline (ex-AI-20260630-004) a été
  **annulée** sur retour utilisateur et n'a jamais été committée.
- **Changements :**
  - nouveau composant Lit `frontend/src/components/sx-entity-graph.ts` (enregistré
    dans `frontend/src/index.ts`) : graphe force-directed rendu en SVG, mises à
    jour de position impératives pour la fluidité. Nœuds colorés par catégorie
    (1er tag) et dimensionnés par degré, liens dirigés avec libellé, toolbar
    zoom/ajuster, légende, drag des nœuds, pan, zoom molette, survol = mise en
    avant du voisinage, clic/Entrée = `CustomEvent('sx-entity-select')`. Aucune
    dépendance ajoutée (uniquement `lit`).
  - `investigations/view.py` : la page charge désormais le bundle
    `assets/synthesix-ui.js` (script classique, file://-safe) ; section « Entités »
    dotée d'un toggle **Liste ⇄ Graphe** (persisté en `localStorage`,
    `list` par défaut) ; nouveau helper `_entity_graph_payload` qui sérialise
    nœuds+liens en JSON (self-loops, liens vers nœud inconnu et doublons écartés ;
    `<` échappé pour l'îlot JSON). Le clic d'un nœud appelle le
    `selectInspectorEntity(id)` existant → entité ouverte dans le rail. Icônes
    `list` et `graph` ajoutées au registre.
  - `theme.css` : styles `.view-toggle` / `.entity-view` + dimension du conteneur
    `sx-entity-graph` (les tokens CSS traversent le Shadow DOM → thème hérité).
  - `tests/test_investigation_view.py` : tests des deux vues + îlot JSON, et du
    helper `_entity_graph_payload` (nœuds/liens, filtrage, échappement). Les deux
    tests qui scannent les `<script>` inline excluent désormais les
    `type="application/json"`.
- **Contrats ou décisions :**
  - aucun contrat Python/CDP/payload existant modifié ; aucune nouvelle action CDP.
  - nouveau contrat front : élément `sx-entity-graph` + îlot
    `<script type="application/json" data-graph-data>` ({nodes, edges}) + événement
    `sx-entity-select` ({ detail: { id } }).
  - la page d'investigation devient la première vue applicative à charger
    `assets/synthesix-ui.js` (jusqu'ici : pages history/démos).
- **Tests exécutés :**
  - `cd frontend && npm run typecheck` — OK
  - `cd frontend && npm run build` — OK (bundle `assets/synthesix-ui.js` régénéré ;
    `synthesix-overlay.js` inchangé)
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 26 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 268 tests
  - `git diff --check` — OK (avertissements CRLF uniquement)
  - smoke headless Chrome (payload 10 entités + relations, vue graphe forcée,
    `--virtual-time-budget`) — OK : layout organique, nœuds colorés, liens
    fléchés, légende, toolbar.
- **Vérifications non exécutées :**
  - smoke live navigateur réel non exécuté : interactions (drag/zoom/pan, survol,
    clic → rail) validées seulement en capture statique ;
  - rendu thème clair non capturé (tokens hérités, attendu OK mais non vérifié).
- **Risques / reste à faire :**
  - chevauchement de libellés possible dans les clusters denses (inhérent au
    node-link ; le drag permet de désencombrer) ; à valider sur un vrai jeu
    d'entités ;
  - layout O(n²) (répulsion toutes paires) : convient à des dizaines d'entités,
    à surveiller au-delà de ~150 nœuds.
- **Relais :** aucun. Bundle + sources committés ensemble si validé en live.

### AI-20260630-006 — Ajustements graphe (layout figé, libellés, hauteur)

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend`, non committé (suite de AI-20260630-005)
- **Objectif :** trois retours utilisateur sur `sx-entity-graph`.
- **Changements (`frontend/src/components/sx-entity-graph.ts` + `theme.css`) :**
  - layout calculé **en une passe synchrone** puis figé (suppression de la boucle
    `requestAnimationFrame`/`_reheat`) : le graphe ne bouge plus tout seul ; un
    drag déplace uniquement le nœud saisi, sans re-simulation globale ;
  - libellés de relation **affichés par défaut** (`opacity` 0 → 0.92 ; au survol,
    seuls les libellés du voisinage restent pleins, les autres s'atténuent) ;
  - hauteur du conteneur passée à `--graph-height: 55vh`.
- **Contrats ou décisions :** aucun contrat modifié.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck` — OK
  - `cd frontend && npm run build` — OK (bundle régénéré)
  - `git diff --check` — OK
  - smoke headless Chrome — OK : graphe statique, libellés de relation visibles,
    hauteur réduite.
- **Vérifications non exécutées :** smoke live navigateur réel (drag/zoom/survol).
- **Relais :** aucun.

### AI-20260630-007 — Cartes « Pages enregistrées » en composant Lit + page élargie

- **Agent :** Claude
- **Période UTC :** 2026-06-30 12:46-15:10
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** refonte des cartes de pages enregistrées pour gagner de la place
  et migrer leur présentation en Lit (demande utilisateur : moins de JS inline,
  rendu propre). Bordures noires réduites, observations minifiées, actions
  secondaires regroupées dans un menu extensible.
- **Changements :**
  - **Nouveau composant `frontend/src/components/sx-saved-page-card.ts`** : shell
    Shadow DOM (favicon-lettre, pills observations `œil`/`horloge` formatées en
    locale, menu `⋯` avec état open/close + click-outside + Escape). Les éléments
    porteurs de mots ou bindés par le JS de page restent en **slots light-DOM**
    (titre, domaine, favori, statut, items de menu, tags, champs cachés) → i18n et
    dispatch CDP inchangés. Convention repo suivie (libellés composant en FR, comme
    `sx-entity-graph`).
  - `frontend/src/index.ts` : enregistrement du composant ; bundle
    `assets/synthesix-ui.js` régénéré.
  - `investigations/view.py` (`_result_cards`) : chaque carte ré-émise en
    `<sx-saved-page-card>` (attributs `observations`/`first-seen`/`last-seen`/
    `initial`/`imported` + slots). Wayback, Monitor et Remove deviennent des items
    de menu libellés (`saved-card__menu-item`). Description tronquée 1 ligne.
    Suppression de l'`<article>`/`result-heading`/`result-metadata`/`result-body`
    et du pill « Monitoring » d'en-tête. `type_badge` retiré (→ `badge_markup` slot).
  - `theme.css` : `.app--workspace` 1600→1920px ; box de carte neutralisée (dessinée
    par le composant) ; styles compacts des slots (`saved-card__actions`,
    `saved-card__menu-item`, `saved-card__desc`, titre/url/tags) ; retrait du
    `.investigation-result.is-inspected` externe (géré par `:host(.is-inspected)`).
  - `i18n.js` : clés « Open Wayback Machine » et « Remove from investigation »
    (multilingual + additionalTranslations).
  - `tests/test_investigation_view.py` : assertions adaptées à
    `<sx-saved-page-card>` (sélecteurs `article`→tag, `.result-url` div→span,
    libellés menu, ancien `result-body` → slot `title`).
- **Contrats ou décisions :** aucun contrat/payload CDP modifié ; les `data-*`
  (filtre/favori/statut), `data-result-favorite`, `data-result-status`,
  `.remove-saved-page`, `.start/stop-page-monitor`, champs cachés notes/tags
  conservés à l'identique en light DOM. Le menu `⋯` est extensible (ajouter un
  `slot="menu"`). Présentation seule migrée ; le JS global de page (file d'actions,
  no-reload, filtres) reste inline = lots ultérieurs.
- **Tests exécutés :**
  - `npm run typecheck` — OK
  - `npm run build` — OK (bundle 55.5kb régénéré)
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_i18n_coverage` — OK, 29 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 268 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome — OK : carte compacte (favicon, pills, statut, kebab,
    description 1 ligne) + menu `⋯` ouvert (Wayback/Monitor/Remove) capturés.
- **Vérifications non exécutées :**
  - smoke CDP live dans une vraie session navigateur (clic-carte→inspecteur,
    favori/statut/remove/monitor via le menu, click-outside) — à confirmer en live.
- **Risques / reste à faire :**
  - en-tête de carte ne montre plus le pill « Monitoring » (l'item « Stop
    monitoring » du menu l'implique) ; rajouter un indicateur discret si souhaité ;
  - règles CSS `.result-heading`/`.result-metadata`/`.result-body`/`.result-description`
    désormais inutilisées pour ces cartes — laissées en place (nettoyage hors
    périmètre) ;
  - étendre la même approche Lit aux autres blocs denses (rail workspace) en lot
    séparé.
- **Relais :** aucun.

### AI-20260630-008 — Cartes pages : grille multi-colonnes + carte épurée

- **Agent :** Claude
- **Période UTC :** 2026-06-30 15:10-15:35
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** retours utilisateur — liste pleine largeur trop étirée + carte
  trop chargée provoquant un débordement horizontal. Passer en grille et épurer la
  carte (autorisation explicite de retirer des éléments).
- **Changements :**
  - `theme.css` : `.investigation-results` en
    `grid-template-columns: repeat(auto-fill, minmax(380px, 1fr))` + `align-items:
    start` (responsive ~3 colonnes, cartes courtes non étirées).
  - `sx-saved-page-card.ts` : carte réécrite en **2 lignes** — (1) favicon coloré +
    titre + favori + menu `⋯`, (2) statut + domaine + pills observations/dates.
    **Description retirée** de la carte (cause du débordement : `white-space:nowrap`
    gonflait la largeur min) ; statut déplacé en ligne 2 ; favicon coloré
    déterministe par domaine (attribut `site`) ; `:host([menu-open])` → `z-index:20`
    (+ attribut reflété) pour que le pop `⋯` passe au-dessus de la carte voisine.
  - `view.py` (`_result_cards`) : favori/statut séparés en slots `star`/`status` ;
    attribut `site` = domaine seul (`netloc`) ; suppression de l'émission
    description + badge importé (l'icône doc du favicon suffit).
  - `theme.css` : titre `display:block` + ellipsis (tronque enfin) ; select statut
    borné (`max-width:116px`) ; favori/statut compacts ; retrait des styles
    `.saved-card__actions`/`.saved-card__desc` obsolètes. Bundle régénéré.
- **Tests exécutés :** `npm run typecheck` — OK ; `npm run build` — OK ;
  `unittest tests.test_investigation_view` (26) + `tests.test_i18n_coverage` — OK ;
  smoke headless (grille 3×2 sans débordement, favicons colorés, titres tronqués,
  menu ouvert par-dessus la carte du dessous) — OK.
- **Vérifications non exécutées :** smoke live navigateur réel.
- **Risques / reste à faire :** description et tags ne sont plus sur la face de
  carte (tags conservés en DOM, masqués si vides) ; si besoin, les afficher dans
  l'inspecteur du rail au clic.
- **Relais :** aucun.

### AI-20260630-009 — Cartes pages : favicons de marque + URL/description repensées

- **Agent :** Claude
- **Période UTC :** 2026-06-30 16:05-16:35
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** retours utilisateur — remplacer le nom de domaine par l'icône de
  la plateforme, déplacer la description dans le rail, rendre le lien titre
  cliquable sur le texte seul.
- **Changements :**
  - `sx-saved-page-card.ts` : favicon = **glyphe de marque** (Simple Icons CC0,
    embarqués) pour tiktok/instagram/x/facebook/youtube/googlemaps/telegram/
    snapchat/pinterest/reddit/whatsapp ; fallback lettre colorée pour les domaines
    inconnus ; X en `currentColor` (s'adapte clair/sombre). Slot `domain` retiré.
    Titre en `flex: 0 1 auto` + `star` en `margin-left:auto` → la zone cliquable du
    lien = le texte seul (plus toute la ligne). Map de marques extensible (ajouter
    une entrée `BRANDS`).
  - `view.py` : span `result-url` retiré de la carte ; `title` du lien = titre
    complet + URL (tooltip au survol) ; attribut `site` = domaine (`netloc`) ;
    `_inspector_panel` ajoute `<p class="inspector-panel__desc">` (description dans
    le rail au clic).
  - `theme.css` : style `.inspector-panel__desc` ; retrait du style `.result-url`
    de carte. Bundle régénéré.
  - `tests/test_investigation_view.py` : `test_compacts_long_urls` retargeté sur
    l'URL du rail (`inspector-panel__url`) + le tooltip du titre.
- **Contrats ou décisions :** aucun contrat CDP/payload modifié ; data-* et
  contrôles JS-bindés conservés. Marques = Simple Icons (licence CC0).
- **Tests exécutés :** `npm run typecheck` — OK ; `npm run build` — OK ;
  `unittest tests.test_investigation_view tests.test_i18n_coverage` (29) — OK ;
  `unittest discover` (268) — OK ; smoke headless **clair + sombre** (9 cartes,
  glyphes de marque + fallback lettre, menu par-dessus la carte voisine) — OK.
- **Vérifications non exécutées :** smoke live navigateur réel.
- **Risques / reste à faire :** domaines inconnus (ex. pappers) affichent une
  lettre, sans texte de site — ajouter d'autres marques ou un libellé site pour les
  inconnus si souhaité ; brand map facile à étendre.
- **Relais :** aucun.

### AI-20260630-010 — Persistance des positions du graphe par enquête

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend` (suite de AI-20260630-005/006)
- **Objectif :** conserver l'agencement manuel du graphe entre deux visites d'une
  enquête (retour utilisateur).
- **Changements :**
  - `frontend/src/components/sx-entity-graph.ts` : attribut `storage-key` ;
    `_loadLayout`/`_saveLayout` (localStorage). Au build, les nœuds avec position
    sauvegardée sont restaurés et épinglés pendant le settle (seuls les nouveaux
    nœuds se replacent autour), puis la position résolue est persistée ; un drag
    sauvegarde la nouvelle position ; bouton toolbar `↻ Réorganiser` qui efface la
    sauvegarde et relance l'auto-layout.
  - `investigations/view.py` : `storage-key="synthesix:graph-layout:{id}"` sur
    `<sx-entity-graph>`.
  - `tests/test_investigation_view.py` : assertion de présence du `storage-key`.
- **Contrats ou décisions :** persistance **client (localStorage)**, cohérente
  avec l'état de vue existant (rail, toggle, scroll, file d'actions) ; local au
  navigateur, non exporté avec le dossier d'enquête (pas de DB pour ce besoin).
- **Tests exécutés :**
  - `cd frontend && npm run typecheck` — OK
  - `cd frontend && npm run build` — OK (bundle régénéré)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 268 tests
  - `git diff --check` — OK
  - smoke headless Chrome : layout pré-injecté en localStorage (grille 2×5)
    restitué à l'identique → chemin de restauration validé.
- **Vérifications non exécutées :** aller-retour live (drag → reload) en
  navigateur réel ; sauvegarde au drag validée par lecture de code uniquement.
- **Relais :** aucun.

### AI-20260630-011 — Export nommé + renommage et rattachement direct des preuves

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** (1) nommer le dossier d'export ZeroNeurone avec le titre de
  l'enquête plutôt que le littéral `zeroneurone` ; (2) permettre de renommer
  une preuve (capture, archive, fichier importé) après coup, en plus du nom
  choisi à la capture qui existait déjà ; (3) rattacher une preuve existante
  directement à une entité, comme une propriété sourcée (couvre aussi les
  fichiers importés manuellement, à la demande de l'utilisateur).
- **Changements :**
  - `main.py` : helper `_slugify()` (accents repliés, ponctuation → `-`) ;
    le dossier d'export devient `{slug-du-titre}_{timestamp}` ; deux nouveaux
    handlers d'action `rename_evidence_capture` et
    `attach_evidence_capture_to_entity` (reload complet, comme les autres
    actions qui créent une entité/propriété).
  - `investigations/repository.py` : `rename_evidence_capture()` (UPDATE
    ciblé sur `evidence_captures.name`, même garde « enquête active » que
    `delete_evidence_capture`).
  - `investigations/service.py` : `rename_evidence_capture()` (validation
    nom non vide, `MAX_EVIDENCE_NAME_LENGTH` déjà existant) ;
    `attach_evidence_capture_to_entity()` — réutilise le pipeline existant
    `record_selection_entity` → `set_extracted_entity_source_capture` →
    `attach_extracted_property` (même mécanisme que le rattachement de texte
    sélectionné depuis l'overlay), avec une clé de propriété par défaut selon
    `capture_kind` (`Capture écran` / `Archive HTML` / `Pièce jointe`).
  - `investigations/view.py` : helper partagé `_graph_entity_attach_options()`
    (extrait de `_extracted_entity_row`, réutilisé) ; icône `edit` ; chaque
    `evidence-item` reçoit un bouton « Renommer » (`prompt()`) et un
    `<select data-evidence-attach>` réutilisant le style
    `entity-chip-row__link` (pas de modification de `theme.css`) ; JS de
    rattachement demande le nom de propriété via `prompt()` avant
    `queueAction`.
  - Tests : `tests/test_main.py` (`_slugify`), `tests/test_investigations.py`
    (renommage, rattachement + erreurs de validation),
    `tests/test_investigation_view.py` (présence bouton/`select` et
    `data-default-key`).
- **Contrats ou décisions :** aucune nouvelle table — le rattachement preuve↔
  entité réutilise le mécanisme `extracted_entity` + `source_capture_id` déjà
  en place (cf. `docs/EVIDENCE_ATTACHMENT_PLAN.md`, jamais branché jusqu'ici) ;
  les deux nouvelles actions rechargent la page (comme
  `create_graph_entity_from_result`), pas de rendu no-reload pour ce lot.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_main tests.test_investigations tests.test_investigation_view tests.test_zeroneurone_export`
    — OK, 122 tests
  - `git diff --check` — OK (avertissements CRLF uniquement)
  - Aucune modification TypeScript/overlay : `npm run typecheck`/`build` non
    requis.
- **Vérifications non exécutées :** smoke visuel/CDP réel en navigateur
  (pas de navigateur disponible dans cette session) — renommage et
  rattachement vérifiés uniquement par tests Python (lxml) + relecture du
  diff JS généré.
- **Risques / reste à faire :** pas de détachement direct depuis la liste de
  preuves (seul `detach_extracted_property` existe, via la ligne d'entité
  extraite) ; le rattachement n'a pas de no-reload (cohérent avec le reste du
  lot création d'entité).
- **Relais :** smoke CDP live recommandé avant de considérer le lot
  définitivement validé.

### AI-20260630-012 — Correctifs du lot preuves (delegation JS, nom de téléchargement) + rattachement à la capture

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend`, non committé (suite de AI-20260630-011)
- **Objectif :** corriger deux régressions remontées par l'utilisateur après
  smoke réel sur AI-20260630-011, et combler un manque identifié à cette
  occasion : pouvoir choisir le nom du fichier **et** l'entité de
  rattachement directement au moment de la capture, pas seulement après
  coup.
- **Bugs corrigés :**
  - **Bouton « Renommer » inactif :** le JS du lot précédent avait été câblé
    sur `resultCards.forEach((card) => ...)` (`.investigation-result`), mais
    les items de preuve vivent dans le rail `.inspector-panel`, un sous-arbre
    DOM différent — le listener ne s'attachait donc jamais. Les blocs
    `delete-evidence`/`verify-evidence` du même `resultCards.forEach` étaient
    déjà du code mort pour la même raison (seul le listener délégué sur
    `document` + `.closest(".inspector-panel")` fonctionne réellement) ;
    déplacé `rename-evidence` dans ce listener délégué et ajouté un listener
    `change` délégué dédié pour `[data-evidence-attach]` (`investigations/view.py`).
  - **Nom de fichier téléchargé toujours `zeroneurone.zip` :** seul le
    *dossier* d'export avait été renommé (AI-20260630-011) ; le navigateur
    nomme le téléchargement d'après le dernier segment de l'URL, donc le
    fichier zip lui-même restait `zeroneurone.zip`. Ajout d'un attribut
    `download="{slug-du-titre}.{ext}"` sur chaque lien d'export
    (`_export_cards` dans `investigations/view.py`, avec un `_slugify()`
    local — pas d'import croisé avec `main.py`).
- **Nouvelle fonctionnalité — rattachement dès la capture :**
  - `frontend/src/overlay/sx-overlay-capture-menu.ts` : nouvelle section
    optionnelle (affichée seulement si l'enquête a des entités) avec un
    `<select>` d'entités + un champ nom de propriété, mêmes
    principes que `sx-overlay-entity-menu` (réutilisé `graphEntities`
    déjà poussé par `main.py`). Le choix est inclus dans le détail de
    l'événement `synthesix-capture-choice` (`attach: {entityId, propertyKey, propertyType} | null`).
  - `main.py` : `host.__synthesixSetGraphEntities` alimente maintenant aussi
    `captureMenu.graphEntities` (en plus de `entityMenu`) ; `attach` est
    propagé à travers `__synthesixQueueCapture`/`__synthesixStartRegionSelection`
    jusqu'au payload `capture_evidence_to_investigation` ; `_capture_evidence()`
    appelle `service.attach_evidence_capture_to_entity(...)` après
    l'enregistrement de la capture — en best-effort (une erreur d'attache
    n'annule pas la capture, juste un `logger.warning`).
  - Bundle overlay reconstruit (`npm run typecheck && npm run build`).
- **Tests :**
  - `tests/test_main.py` : `test_capture_evidence_attaches_to_entity_when_requested`,
    `test_capture_evidence_ignores_attach_failure`.
  - `tests/test_investigation_view.py` : `test_generates_filterable_analyst_workspace`
    étendu avec l'assertion `download="case-alpha-test.zip"`.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck` — OK
  - `cd frontend && npm run build` — OK (seul `assets/synthesix-overlay.js`
    a changé)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 274 tests
  - `git diff --check` — OK (avertissements CRLF uniquement)
- **Vérifications non exécutées :** smoke CDP live (navigateur réel) toujours
  pas exécuté dans cette session — c'est précisément ce qui aurait attrapé
  le bug de délégation JS plus tôt. **À faire avant de considérer ce lot
  validé : ouvrir une vraie page, capturer un screenshot avec rattachement,
  vérifier le bouton Renommer, et vérifier le nom du fichier téléchargé.**
- **Risques / reste à faire :** les libellés de la nouvelle section
  « rattacher à une entité » du menu de capture ne sont pas encore reliés à
  `i18n.js` (ils suivent la convention déjà en place pour ce composant —
  défauts anglais en dur, aucun composant de ce menu n'était traduit avant
  ce lot non plus) ; pas de détachement direct depuis la liste de preuves.
- **Relais :** smoke CDP live obligatoire avant de clore définitivement ce
  lot — c'est le deuxième tour où un bug n'a été détecté que par
  l'utilisateur en usage réel.

### AI-20260630-013 — Sources : lien vers la sélection de l'analyste + fix href fichier importé + badge type de doc

- **Agent :** Claude
- **Période UTC :** 2026-06-30
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** suite à retour utilisateur sur capture d'écran du panneau
  entité : (1) la liste « Sources » en bas de carte entité doit pouvoir
  renvoyer vers la capture/sélection de l'analyste correspondante (pas le
  chiffre inline, qui pointe déjà vers la copie archivée avec
  surlignage text-fragment) ; (2) pour un fichier importé manuellement, le
  lien « Open source » pointait vers l'URL synthétique
  `https://files.synthesix.local/...` au lieu du fichier réel ; (3) ajouter
  un badge de type de document (Image/PDF/Document/Audio/Vidéo/Fichier)
  quand la source d'une propriété est un import.
- **Changements (`investigations/view.py`) :**
  - nouvelle fonction `_capture_open_href()` : résout le href d'ouverture
    d'une capture — fichier local réel (`_imported_artifact_view`) pour les
    imports, archive HTML (+ text-fragment) sinon. Remplace les appels
    directs à `_archive_href()` dans la construction des sources de
    propriété et des sources liées par résultat (boucle
    `linked_result_ids`, qui ne considérait auparavant que `page_archive` —
    un résultat purement importé retombait aussi sur l'URL synthétique).
  - nouvelle fonction `_imported_doc_kind()` (+ `_DOC_KIND_LABELS`,
    `_doc_kind_badge()`) : déduit image/pdf/audio/video/document/file
    depuis le mime/extension de l'artefact importé ; badge rendu à côté du
    type de propriété (`_property_type_badge`) et dans chaque ligne de la
    liste Sources.
  - `source_entries` (tuple 4 → 7 champs : + `result_id`, `capture_id`,
    `doc_kind`) ; `_source_row()` ajoute un bouton « Voir la sélection de
    l'analyste » (`data-inspector-goto` + `data-evidence-goto`, icône
    `archive`).
  - `_evidence_markup()` : ajout d'un `id="evidence-{capture_id}"` sur
    chaque `<li class="evidence-item">` pour permettre le ciblage direct.
  - listener JS délégué existant sur `data-inspector-goto` (jusqu'ici mort
    code — l'attribut n'était jamais posé dans le markup) réutilisé et
    étendu : scroll vers la carte `#result-{id}`, puis vers
    `#evidence-{capture_id}` avec un flash visuel temporaire
    (`.evidence-item--flash`, `theme.css`).
- **Bug additionnel trouvé en écrivant le test :** la liste fusionnée
  « Sources » dédoublonnait par URL en donnant priorité à l'entrée issue de
  `linked_result_ids` (capture résolue uniquement via `page_archive`), donc
  une capture `screenshot`/`region` (= la sélection réelle de l'analyste,
  qui embarque pourtant un artefact HTML exploitable) perdait son
  `capture_id`/href corrects au profit d'une entrée vide dès qu'elle était
  aussi le résultat lié de l'entité. Corrigé en (1) traitant
  `property_sources` avant `linked_result_ids` dans la fusion, et (2) en
  élargissant le fallback de résolution de capture à tout capture du
  résultat possédant un artefact archive exploitable
  (`_has_archive_artifact`), pas seulement `page_archive`/`imported`.
- **Tests ajoutés (`tests/test_investigation_view.py`) :**
  - `test_property_links_back_to_its_extracted_source` étendu : vérifie
    `id="evidence-capture-123"` et le bouton `.source-goto-evidence`
    (`data-inspector-goto`/`data-evidence-goto`).
  - `test_imported_source_links_to_the_local_file_with_a_doc_badge` (nouveau) :
    capture `capture_kind="imported"` (artefact PDF) référencée par une
    propriété → vérifie que le lien `graph-property-source` pointe sur le
    fichier local réel (pas `files.synthesix.local`) et que le badge
    `prop-type--doc` affiche « PDF » à la fois sur la propriété et sur la
    ligne Sources correspondante.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m py_compile investigations/view.py` — OK
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` —
    OK, 28 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 275 tests
  - `git diff --check` — propre
- **Vérifications non exécutées :** pas de smoke CDP live / capture
  d'écran réelle dans cette session. À valider en usage réel : clic sur le
  bouton « Voir la sélection » scrolle bien jusqu'à la bonne carte de
  preuve, et l'ouverture d'une source importée (PDF/image) pointe bien sur
  le fichier et plus sur `files.synthesix.local`.
- **Risques / reste à faire :** aucun.
- **Ajustement (même session, retour utilisateur) :** le bouton dédié
  « Voir la sélection » faisait doublon avec le lien externe déjà présent
  par pastille. Remplacé par une carte cliquable : le `<li>` de la liste
  Sources porte lui-même `data-inspector-goto`/`data-evidence-goto`
  (classe `.entity-source-card`, `theme.css`) ; le listener JS ignore les
  clics sur `<a>` pour laisser le lien externe s'ouvrir normalement sans
  déclencher le scroll. Test `test_property_links_back_to_its_extracted_source`
  ajusté (cible `li.entity-source-card` au lieu de
  `button.source-goto-evidence`). `unittest tests.test_investigation_view`
  (28) et `unittest discover` (275) — OK ; `git diff --check` propre.
- **Correction (même session, retour utilisateur) :** le clic devait ouvrir
  le panneau de la page dans le rail de droite (`#inspector-detail` →
  `[data-inspector-panel="{result_id}"]`), pas juste scroller la carte dans
  la grille principale. Bug latent découvert au passage : les items de
  preuve (`#evidence-{capture_id}`) vivent *dans* ce panneau de page
  (`_evidence_markup` fait partie de `details_markup` de `_inspector_panel`),
  donc tant que le panneau restait masqué (`hidden`), le flash/scroll vers
  l'evidence ne pouvait jamais être visible. Remplacé le `scrollIntoView`
  de la carte de résultat par un appel à la fonction déjà existante
  `selectInspectorPage(resultId)` (même mécanisme que le clic sur une
  `sx-saved-page-card` ou sur `data-relation-goto` → `selectInspectorEntity`),
  qui affiche le panneau, puis le scroll/flash de l'évidence s'exécute une
  fois le panneau visible. `unittest tests.test_investigation_view` (28) et
  `unittest discover` (275) — OK ; `git diff --check` propre.
- **Nettoyage (même session, retour utilisateur) :** ouvrir le panneau
  suffit, mécanisme de scroll/flash vers l'item de preuve superflu.
  Supprimé : bloc JS `evidenceId` (le clic n'appelle plus que
  `selectInspectorPage`), attribut `data-evidence-goto` et champ
  `capture_id` du tuple `source_entries` (7 → 6 champs), `id="evidence-…"`
  sur `<li class="evidence-item">` (`_evidence_markup`), règle CSS
  `.evidence-item--flash` (`theme.css`). Tests ajustés en conséquence.
  `unittest tests.test_investigation_view` (28) et `unittest discover`
  (275) — OK ; `git diff --check` propre.
- **Suite (même session, retour utilisateur) sur les blocs Evidence
  (`_evidence_markup`) :**
  1. Le `<select>` « Rattacher à une entité… » ne présélectionnait jamais
     l'entité déjà rattachée. `_evidence_markup` reçoit maintenant
     `result_entities` (les entités extraites du même résultat, déjà
     disponibles à l'appel) ; une entrée dont `attributes.source_capture_id`
     correspond à la capture (et `status != rejected`) fixe
     `selected_id` sur `_graph_entity_attach_options` (ce paramètre
     existait déjà, jamais branché ici).
  2. Le select prenait toute la largeur de sa colonne, au-dessus de la
     ligne Manifeste/vérifier/renommer/supprimer. Déplacé dans
     `.evidence-links` (même conteneur flex que ces boutons) avec une
     classe dédiée `.evidence-attach-select` (`flex: 1 1 180px; max-width:
     260px`, `theme.css`) ; le retour à la ligne sur écran étroit reste géré
     par la règle `.inspector-panel__details .evidence-links {{
     flex-wrap: wrap }}` déjà existante.
  - **Test ajouté :** `test_evidence_attach_select_preselects_the_already_attached_entity`.
  - **Tests exécutés :** `unittest tests.test_investigation_view` (29) et
    `unittest discover` (276) — OK ; `git diff --check` propre.
  - **Non exécuté :** smoke visuel réel (mise en page finale du partage de
    ligne à confirmer dans le navigateur, notamment à largeur de rail
    intermédiaire).
- **Suite (même session, retour utilisateur) — refonte layout bloc Evidence :**
  1. Passage de `.evidence-item` (et son override
     `.inspector-panel__details .evidence-item`, seul contexte d'usage réel
     — la règle grid de base 3 colonnes était morte) d'une grille à un flex
     `flex-wrap: wrap` : nom, date, select et boutons tiennent sur une
     seule ligne quand le rail est assez large, et l'ensemble
     select+Manifeste+boutons (`.evidence-links`) retombe sur sa propre
     ligne sinon — sans media query dédiée, le wrap gère nativement le cas
     étroit.
  2. Vignette agrandie : 56×42px (taille réellement appliquée via l'override
     scoped, supprimé) → 64×64px unifié (`.evidence-thumbnail`, `theme.css`).
  3. Ligne « Zone sélectionnée »/« Zone visible » supprimée
     (`scope_detail` retiré de `_evidence_markup`) — jugée sans valeur
     ajoutée.
  4. Date compactée façon `sx-saved-page-card` (jour + mois court, ex.
     « 22 juin », date complète en tooltip au survol) : nouvelle fonction
     `_local_date_compact()` + attribut `data-local-date-compact`, JS
     `formatLocalDatetimes()` étendu avec une branche dédiée (parsing
     factorisé dans `parseLocalTimestamp()` partagé avec le format complet
     existant).
  - **CSS nettoyé :** overrides grid devenus morts supprimés
    (`.inspector-panel__details .evidence-item/.evidence-thumbnail`,
    `.evidence-verification { grid-column }`, bloc `@media (max-width:
    720px)` pour evidence-item/thumbnail/links/verification).
  - **Test ajusté :** `test_generates_filterable_analyst_workspace` —
    assertion `assertIn("Selected area", …)` devenue `assertNotIn`
    (suppression volontaire du libellé de zone).
  - **Tests exécutés :** `unittest tests.test_investigation_view` (29) et
    `unittest discover` (276) — OK ; `git diff --check` propre.
  - **Non exécuté :** smoke visuel réel (rendu à largeur de rail variable,
    apparence de la vignette agrandie sur les captures existantes).
- **Suite (même session, spécification détaillée de l'utilisateur) — bloc
  Evidence, itération 2 :**
  1. Nom de la capture retiré de l'affichage, déplacé en `title="{nom}"`
     sur le `<li class="evidence-item">` (tooltip natif au survol). La
     classe `.evidence-name` disparaît donc de la sortie ; **piège
     détecté et corrigé** : le JS de renommage lisait le nom courant via
     `item.querySelector(".evidence-name").textContent` pour préremplir le
     prompt — sans ce fix il serait devenu silencieusement vide. Remplacé
     par `item.getAttribute("title")`.
  2. Bloc restructuré en 3 lignes (`.evidence-body` > 3×`.evidence-row`) :
     (1) statut + date compacte, (2) select de rattachement seul (largeur
     libre, `.evidence-attach-select` recalé en `flex:1 1 auto` — n'a plus
     à partager sa ligne avec les boutons), (3) Manifeste/extraire/
     vérifier/renommer.
  3. Bouton supprimer sorti du groupe de boutons, enfant direct de `.evidence-item`
     avec `margin-left: auto` pour rester seul, collé à droite, aligné
     avec la vignette et le bloc de contenu.
  - **Nettoyage :** `view_href` (variable devenue inutile), classes/règles
    CSS `.evidence-name`, `.evidence-links`/`.inspector-panel__details
    .evidence-links` (remplacées par `.evidence-row`, plus aucun
    consommateur JS/test ne dépendait de `.evidence-links`).
  - **Tests :** `test_generates_filterable_analyst_workspace` ajusté
    (`title="Registry header"` au lieu de `class="evidence-name"`) ;
    `test_evidence_item_offers_rename_and_attach_to_entity` étendu (title,
    3 lignes, select en ligne 2, bouton supprimer en enfant direct).
  - **Tests exécutés :** `unittest tests.test_investigation_view` (29) et
    `unittest discover` (276) — OK ; `git diff --check` propre.
  - **Non exécuté :** smoke visuel réel (rendu final des 3 lignes + tooltip
    de nom au survol, alignement du bouton supprimer sur les différentes
    tailles de vignette/placeholder).
- **Suite (même session, retour utilisateur) — ajustements fins :**
  1. Bouton supprimer replacé dans le groupe de boutons (ligne 3 :
     Manifeste/extraire/vérifier/renommer/supprimer) — la règle
     `.evidence-item > .delete-evidence { margin-left: auto }` retirée.
  2. Select de rattachement recalé en largeur fixe compacte
     (`flex: 0 1 200px` au lieu de `1 1 auto`) : ne prend plus toute la
     largeur de sa ligne.
  3. Vignette étirée à 100% de la hauteur du bloc : `.evidence-item`
     passe de `align-items: center` à `align-items: stretch`,
     `.evidence-thumbnail` perd sa `height: 64px` fixe au profit de
     `min-height: 64px` (l'étirement flex fait le reste, plus d'espace
     mort au-dessus/en dessous de l'image).
  - **Test ajusté :** `test_evidence_item_offers_rename_and_attach_to_entity`
    — le bouton supprimer est cherché dans la 3ᵉ `evidence-row` au lieu
    d'être un enfant direct de `.evidence-item`.
  - **Tests exécutés :** `unittest tests.test_investigation_view` (29) et
    `unittest discover` (276) — OK ; `git diff --check` propre.
  - **Non exécuté :** smoke visuel réel.

### AI-20260701-001 — Export ZeroNeurone : carte Lit + noms de fichiers repris de l'enquête

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** retour utilisateur sur capture d'écran du bloc « Export
  ZeroNeurone » (`investigations/view.py`) : (1) rendre la carte plus belle,
  cohérente avec les autres blocs déjà migrés (`sx-saved-page-card`,
  `sx-entity-graph`) ; (2) la passer en composant Lit ; (3) faire reprendre
  le nom de l'enquête par les fichiers générés sur disque, pas seulement par
  l'attribut `download` du HTML.
- **Changements :**
  - **`frontend/src/components/sx-export-card.ts` (nouveau)** : composant
    Lit `sx-export-card`, même pattern shell + slots light-DOM que
    `sx-saved-page-card` — titre, timestamp, 3 pastilles de compte
    (nœuds/liens/assets), description, liens de téléchargement et bouton
    supprimer restent des enfants light-DOM slottés (texte traduisible par
    `i18n.js`, qui ne parcourt pas les Shadow DOM ; classe `.delete-export`
    conservée pour le JS délégué existant). Le composant n'ajoute que le
    chrome : avatar icône, pastilles arrondies pour les stats, liens en
    forme de puce avec icône, bouton supprimer en puce rouge alignée à
    droite (`margin-left: auto`, wrap correct en largeur étroite — vérifié
    à 600px).
  - **`frontend/src/index.ts`** : enregistrement du composant.
  - **`investigations/view.py`** : `_export_cards()` émet désormais
    `<sx-export-card>` (les classes `investigation-export-card`,
    `secondary-link`, `danger-link` disparaissent — plus aucun
    consommateur CSS/JS après migration, cascade évitée en ne les
    dupliquant pas dans le light-DOM slotté). Ajout de l'icône `file`
    (`_ACTION_ICON_PATHS`) pour le lien Dossier JSON ; chaque lien
    artefact a maintenant une icône dédiée (archive/file/graph/list/swap/
    info) + le bouton supprimer une icône `trash`.
  - **`theme.css`** : suppression des règles devenues mortes
    (`.investigation-export-card`, `.export-summary`, `.export-links`,
    `.danger-link`, y compris leurs variantes en media query) — la mise en
    page est désormais entièrement portée par le Shadow DOM du composant.
  - **`exports/zeroneurone.py`** : les artefacts générés sur disque
    reprennent le titre de l'enquête (nouvelle fonction privée
    `_filename_stem()`, slug ASCII, même logique que `_slugify()` déjà
    dupliquée entre `main.py`/`investigations/view.py`) — `{stem}.zip`,
    `{stem}-dossier.json`, `{stem}.graphml`, `{stem}.csv`,
    `{stem}-nodes.csv`, `{stem}-edges.csv`, `{stem}-manifest.json`. Le nom
    d'entrée interne au zip (`dossier.json`) est inchangé — c'est un
    contrat avec le format d'import ZeroNeurone, indépendant du nom du
    fichier zip lui-même. `_write_csv_files()` et `_write_native_dossier()`
    prennent un paramètre `stem` ; `export_zeroneurone_bundle()` le calcule
    une fois depuis `workspace["investigation"]`.
  - **`investigations/view.py`** : l'attribut `download` des liens est
    aligné sur cette même convention (`{report_slug}-nodes.csv`, etc. au
    lieu de `{report_slug}.nodes.csv`).
- **Contrats vérifiés avant modification :** `main.py` et
  `investigations/repository.py`/`models.py` ne lisent jamais ces noms de
  fichiers en dur (uniquement via les chemins stockés en base) ; les tests
  réels (`tests/test_zeroneurone_export.py`) référencent les artefacts via
  `exported.xxx_path`, jamais par nom littéral (sauf l'entrée interne
  `dossier.json` du zip, non touchée) — renommage sans risque de
  régression.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK, bundle
    `assets/synthesix-ui.js` régénéré (overlay inchangé)
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 21 tests
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` —
    OK, 29 tests (2 assertions adaptées au nouveau markup : les libellés de
    lien/bouton sont maintenant dans un `<span>` enfant plutôt que texte
    direct du `<a>`/`<button>`)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre
- **Vérifications effectuées :** smoke visuel réel via Chrome headless
  (rendu de la fixture `workspace_payload()` dans `tmp_ui_render/`,
  gabarits 1440×1600 et 600×2500) — carte conforme au goût visuel du
  projet (icônes, pastilles arrondies, wrap propre en largeur étroite).
  Thème sombre confirmé visuellement ; le thème clair n'a pas pu être forcé
  dans ce rendu headless isolé (le script de theme applique probablement
  une préférence système/stockée avant peinture), mais le composant ne
  code aucune couleur en dur — tout passe par les tokens CSS déjà
  partagés (`--accent`, `--line`, `--surface`, `--surface-2`, `--muted`,
  `--danger`), donc pas de risque de régression spécifique au thème clair.
- **Risques / reste à faire :** aucun bloquant. À confirmer en usage réel :
  téléchargement effectif d'un export et lecture du nom de fichier obtenu
  (le comportement de l'attribut `download` sur `file://` reste
  dépendant du navigateur, mais les fichiers sur disque portent
  maintenant le bon nom dans tous les cas).

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

### AI-20260701-002 — Lot 17 : primitives Lit orphelines + retrait sx-inspector

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** suite à une demande utilisateur sur l'état de la migration
  Lit, inventaire complet (2 agents Explore en parallèle) puis traitement du
  lot à faible risque identifié.
- **Constat de l'inventaire :** la moitié du catalogue `sx-*` livré au
  Palier 1 (`sx-chip`, `sx-score`, `sx-tag`, `sx-provenance`,
  `sx-evidence-badge`, `sx-inspector`, `sx-entity`, `sx-property`) n'était
  jamais instanciée côté Python — composants construits tôt, avant que
  l'UI réelle n'évolue via les retours utilisateur itératifs (Lots 7-16).
- **Changements :**
  - `ui.py` : `chip()` émet `<sx-chip tone="...">` (au lieu de
    `<span class="chip chip--...">`) ; `provenance()` émet
    `<sx-provenance>` avec icône/label slottés (au lieu de
    `<span class="provenance">`). Signatures Python inchangées.
  - `investigations/search_view.py` : la pastille provenance
    "Investigation" (dupliquée en HTML brut avec un lien conditionnel dans
    le détail — donc pas remplaçable par un simple appel à
    `ui.provenance()`, qui échappe son paramètre `detail`) est réécrite
    directement en `<sx-provenance>` avec le même contenu (lien préservé).
  - `theme.css` : suppression des règles mortes `.chip`, `.chip--*`,
    `.provenance`, `.provenance__detail` (vérifié : plus aucun émetteur
    brut de ces classes dans le dépôt ; `.provenance-label`, classe
    distincte utilisée ailleurs dans `view.py`, non touchée). `.score*`
    conservé (inchangé).
  - **Retrait de `sx-inspector`** : `frontend/src/components/sx-inspector.ts`
    et sa démo `frontend/demo/sx-inspector.html` supprimés, import retiré
    de `frontend/src/index.ts`. Composant orphelin dont le modèle (1 liste
    + 1 détail, sélection unique, gestion clavier interne) ne correspond
    pas au rail investigation réel : 3 sources sélectionnables (pages,
    entités-graphe, entités extraites), orchestration manuelle
    `hideInspectorPanels`/`revealInspector` dans l'IIFE, rail
    redimensionnable, navigation clavier volontairement abandonnée sur
    demande utilisateur, et plus de 30 actions CDP branchées dessus.
    Aucune perte fonctionnelle : le composant n'était référencé par aucun
    code Python ni test.
- **Hors périmètre, volontairement non traité (documenté en backlog
  `frontend/TASKS.md`)** :
  - `sx-score` est stale : conçu en mode `<details>` cliquable (Tâche 3),
    alors que `score_badge()` est passé au Lot 7 à une infobulle
    hover/focus toujours présente dans le DOM. Le brancher demanderait de
    réécrire le composant.
  - `sx-entity`/`sx-property` sont des composants d'affichage seul : pas de
    slot pour éditeur de tags, notes, relations, formulaires, indicateur de
    sauvegarde. Le panneau entité-graphe réel (`view.py` ~l.1370-1483) est
    bien plus riche ; les adapter est un lot à part (conception de nouveaux
    slots/propriétés).
  - Lots 18-23 listés dans `frontend/TASKS.md` (réécriture `sx-score`,
    extension `sx-entity`/`sx-property` + migration panneau entité-graphe,
    entités extraites, preuves/analyse URL, `search_view.py`, `index.html`).
- **Contrats vérifiés avant modification :** `ui.chip()`/`ui.provenance()`
  sont bien les seuls émetteurs des classes CSS retirées côté `ui.py`
  (grep sur tout le dépôt hors `.venv`/`node_modules`/`data/`) ; les
  valeurs de `tone` passées à `chip()` (neutral/info/success/engine/muted)
  correspondent toutes à l'enum `SxChip.tone` ; aucune assertion de test
  existante ne dépend de `class="chip"`/`class="provenance"` bruts.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK, bundles
    `assets/synthesix-ui.js`/`synthesix-overlay.js` régénérés (overlay
    inchangé en contenu, juste rebuild)
  - `.venv\Scripts\python.exe -m unittest tests.test_utils tests.test_investigation_view tests.test_investigations` —
    OK, 87 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre (seuls avertissements LF/CRLF attendus sur
    les bundles, neutralisés par `.gitattributes`)
- **Vérifications effectuées :** smoke visuel réel via Chrome headless —
  page investigation (fixture `workspace_payload()`) : chip "priority" et
  tag "registry" bien rendus ; page rapport de recherche (fixture ad hoc
  avec `query_variants` multiples) : chips moteurs, score badge, et
  pastille "Trouvé via" (provenance) imbriqués dans `<sx-result-card>`
  correctement affichés, thème sombre. Thème clair non vérifié
  spécifiquement (même limite déjà notée dans le compte-rendu précédent —
  script de thème applique une préférence avant peinture en rendu headless
  isolé), mais les composants ne codent aucune couleur en dur (tokens CSS
  partagés uniquement) donc pas de risque spécifique identifié.
- **Risques / reste à faire :** aucun bloquant. Backlog Lots 18-23 consigné
  dans `frontend/TASKS.md` pour ne pas reperdre l'inventaire lors d'une
  future reprise de la migration Lit.
- **Relais :** prochaine action possible = Lot 18 (réécriture `sx-score`
  en mode infobulle) ou Lot 19 (extension `sx-entity`/`sx-property`) selon
  priorité utilisateur — aucun n'est urgent, `aucun` verrou/blocage restant.

### AI-20260701-003 — Lot 18 : sx-score réécrit en infobulle + branché

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** suite du backlog de migration Lit consigné au Lot 17.
  `sx-score` était stale (mode `<details>` cliquable, Tâche 3) alors que
  `score_badge()` (`ui.py`) était passé au Lot 7 à une infobulle
  hover/focus toujours présente dans le DOM. Réécrire le composant pour
  qu'il corresponde au comportement réel, puis le brancher.
- **Changements :**
  - **`frontend/src/components/sx-score.ts`** : remplacement de la
    propriété `expandable`/rendu `<details>` par une propriété `tip`
    (booléenne, réfléchie) qui bascule le composant en mode infobulle —
    `:host([tip])` devient focusable (`tabIndex` géré dans `updated()`),
    positionné en `relative`, `cursor: help` ; un `.tooltip` (`role="tooltip"`,
    `position: absolute`) est révélé via `:host([tip]:hover/:focus/
    :focus-within)`. Slots `breakdown`/`note` inchangés dans leur nom mais
    attendent désormais un **conteneur unique** slotté (le `<ul>`/`<small>`
    complet avec sa classe), pas des `<li>` individuels — aligné sur la
    façon dont `ui.py` construit déjà ce HTML.
  - **`ui.py`** : `score_badge()` émet `<sx-score level="..." tip>` avec le
    `<ul class="score__list" slot="breakdown">` et le
    `<small class="score-note" slot="note">` existants inchangés en light-DOM
    (mêmes classes, donc `.score__list`/`.score__list li`/`.score__pts*`/
    `.score-note` restent valides sans modification). Signature Python
    inchangée.
  - **`theme.css`** : retrait des règles devenues mortes `.score`,
    `.score--tip`, `.score__value`, `.score--strong/good/moderate
    .score__value`, `.score--tip:focus-visible .score__value`, `.score__tip`,
    `.score--tip:hover/:focus/:focus-within .score__tip` (le chrome de la
    pastille est désormais dans le Shadow DOM du composant). Les règles
    encore consommées par le contenu slotté (`.score__list*`, `.score__pts*`,
    `.score-note`) sont conservées à l'identique.
  - **`frontend/demo/sx-score.html`** : démo mise à jour sur la nouvelle API
    (`tip` au lieu de `expandable`, `<ul slot="breakdown">` au lieu de `<li
    slot="breakdown">` isolés).
- **Contrats vérifiés avant modification :** un seul appelant de
  `score_badge()` dans tout le dépôt (`utils.py`) ; un seul test dépendant
  du markup (`class="score__pts score__pts--strong"`, non touché) ; aucun
  autre émetteur brut de `.score`/`.score--*`/`.score__value`/`.score__tip`
  trouvé par grep.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `.venv\Scripts\python.exe -m unittest tests.test_utils tests.test_investigation_view tests.test_investigations` —
    OK, 87 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre (avertissements LF/CRLF attendus)
- **Vérifications effectuées :** smoke visuel headless (fixture
  `generate_html_report` avec breakdown) — pastille de score colorée
  (vert/bleu selon niveau) rendue correctement, markup `<sx-score tip>`
  avec `<ul slot="breakdown">`/`<li><span class="score__pts...">` conforme
  à ce qu'émet `score_badge()`.
- **Vérifications non exécutées :** l'apparition réelle de l'infobulle au
  survol/focus n'a **pas** été capturée visuellement — une capture d'écran
  headless statique ne déclenche pas `:hover`/`:focus`. Le mécanisme CSS
  (`:host([tip]:hover/:focus/:focus-within) .tooltip`) reproduit à
  l'identique la règle précédente (`.score--tip:hover .score__tip`, etc.),
  donc risque jugé faible, mais non vérifié en interaction réelle.
- **Risques / reste à faire :** aucun bloquant. Vérification recommandée
  avant de considérer le lot pleinement clos : ouvrir
  `frontend/demo/sx-score.html` dans un navigateur interactif et confirmer
  au survol/focus clavier que l'infobulle s'affiche et reste lisible.
- **Relais :** Lot 19 suivant (extension `sx-entity`/`sx-property` +
  migration du panneau entité-graphe) reste le plus gros morceau du
  backlog — non démarré, `aucun` blocage.

### AI-20260701-004 — Lot 19 : panneau entité-graphe en composant Lit `sx-entity-panel`

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** suite du backlog de migration Lit (Lots 17-18). Migrer le
  plus gros bloc de HTML brut restant dans la vue investigation — le
  panneau de gestion d'une entité-graphe (`investigations/view.py`,
  `_graph_entities_markup`) — vers un composant Lit, en préservant à
  l'identique tout le JS et les contrats CDP existants.
- **Changements :**
  - **`frontend/src/components/sx-entity-panel.ts` (nouveau)** : composant
    Lit shell + slots (`identity`/`properties`/`relations`/`sources`), même
    méthode que `sx-saved-page-card`/`sx-export-card`. `:host` est
    `display:none` par défaut, seul `:host(:not([hidden]))` bascule en
    `display:flex` — garde-fou explicite contre le piège `[hidden]` déjà
    rencontré 3 fois dans ce projet (Lots 9/12).
  - **`frontend/src/index.ts`** : enregistrement du composant.
  - **`investigations/view.py`** : le tag racine
    `<article class="graph-entity-card inspector-entity" data-graph-entity-id="..." data-inspector-entity="..." hidden>`
    devient `<sx-entity-panel>` avec **exactement les mêmes classes et
    attributs**. Les 4 `<div class="entity-section...">` qui enveloppaient
    chaque section sont retirés ; leurs enfants (identiques à avant :
    champs identité, liste+formulaire propriétés, liste+formulaire
    relations, liste sources) reçoivent chacun l'attribut `slot`
    correspondant. Aucun autre changement de markup (mêmes `data-*`, mêmes
    classes, mêmes textes) — donc **aucun changement JS nécessaire**.
  - **`frontend/demo/sx-entity-panel.html` (nouveau)** : démo statique
    (identité, 1 propriété, 1 relation, 1 source).
  - **`tests/test_investigation_view.py`** : 6 assertions XPath codant en
    dur `//article[@data-inspector-entity=...]`/`//article[@data-graph-entity-id=...]`
    renommées en `//sx-entity-panel[...]`.
- **Écart au plan approuvé :** le plan prévoyait de retirer deux règles
  CSS `.entity-section`/`.entity-section:not(.entity-identity)` devenues
  soi-disant mortes. Vérification avant modification (grep direct) : la
  classe `.entity-section` est **aussi utilisée** par le formulaire de
  création rapide d'entité (`investigations/view.py` ~l.3201,
  `#graph-entity-create-form`), hors périmètre de ce lot. **`theme.css`
  n'a donc pas été modifié** — aucune règle retirée, tout reste valide
  pour les deux consommateurs.
- **Contrats vérifiés avant modification :** un agent Explore a confirmé
  que tous les sélecteurs JS du panneau (`querySelectorAll(".graph-entity-card")`,
  `card.querySelector("[data-...]")`, `closest("[data-relation-id]")`,
  `querySelectorAll("[data-inspector-entity]")`, etc.) visent des classes
  ou attributs `data-*`, jamais le tag `article` — donc aucun impact sur
  les actions CDP (`update_graph_entity`, `set_graph_entity_property`,
  `delete_graph_entity_property`, add/update/delete relation,
  `delete_graph_entity`) ni sur `hideInspectorPanels`/`revealInspector`.
  `.graph-entity-card`/`.inspector-entity` confirmées non réutilisées
  ailleurs dans le dépôt.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK, bundle
    `assets/synthesix-ui.js` régénéré
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` —
    OK, 29 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre (avertissements LF/CRLF attendus)
- **Vérifications effectuées :** smoke visuel headless réel (fixture
  `workspace_payload()`) : (1) état par défaut — capture identique en
  taille/contenu à celle du Lot 17, confirmant le panneau reste bien caché
  par défaut ; (2) état sélectionné (clic simulé sur la ligne d'entité via
  script injecté dans une copie de la fixture) — le panneau
  `sx-entity-panel` s'affiche correctement dans le rail : identité
  (nom/notes/tags éditables + bouton supprimer), propriétés (SIREN, Forme
  juridique avec badges de type + suppression + formulaire d'ajout),
  relations (formulaire vide + bouton Lier), sources (lien numéroté vers
  la page). Séparateurs entre sections corrects. Confirme que le JS
  existant (`selectInspectorEntity`/`hideInspectorPanels`/`revealInspector`)
  fonctionne sans modification avec le nouveau tag.
- **Vérifications non exécutées :** pas de smoke CDP live (édition réelle
  nom/tags/propriété/relation via `python main.py` contre une page réelle)
  dans cette session — comportement JS non modifié (mêmes sélecteurs),
  risque jugé faible mais non confirmé en interaction serveur réelle.
- **Risques / reste à faire :** aucun bloquant.
- **Relais :** backlog restant inchangé — Lot 20 (entités extraites,
  `_extracted_entity_row` ~l.759-927), Lot 21 (preuves/analyse URL/
  page-monitor-card), Lot 22 (`search_view.py`), Lot 23 (`index.html`).

### AI-20260701-005 — Lot 20 : tags Lit minimaux (couverture complète, sans gain fonctionnel)

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** suite du backlog Lots 17-19. Avant de coder, j'ai vérifié
  les 4 blocs restants prévus aux Lots 20/21 (`_extracted_entity_row`,
  `_evidence_markup`, `_page_monitor_cards`, `_url_analysis_markup`,
  `investigations/view.py`) et constaté qu'ils sont **déjà plats** (un seul
  élément racine, classes déjà bien factorisées, aucun wrapper générique à
  absorber en Shadow DOM comme au Lot 19) — un composant Lit ici n'ajoute
  ni chrome, ni réduction de CSS/JS/duplication. Signalé explicitement à
  l'utilisateur ; décision : **migrer quand même**, pour une couverture Lit
  complète plutôt que de s'arrêter à la valeur fonctionnelle.
- **Changements :** 4 nouveaux composants Lit minimaux (un seul
  `<slot></slot>` par défaut, aucun style propre — la classe déjà présente
  sur l'hôte porte tout le layout, comme `.graph-entity-card` au Lot 19) :
  - **`frontend/src/components/sx-extracted-entity-row.ts`** —
    `investigations/view.py` (`_extracted_entity_row`) :
    `<div class="entity-chip-row entity-item--{status}">` →
    `<sx-extracted-entity-row class="entity-chip-row entity-item--{status}">`.
  - **`frontend/src/components/sx-evidence-item.ts`** —
    `_evidence_markup` : `<li class="evidence-item">` →
    `<sx-evidence-item class="evidence-item">` (reste enfant de
    `<ul class="evidence-list">`, `list-style:none` déjà sur le parent).
  - **`frontend/src/components/sx-page-monitor-card.ts`** —
    `_page_monitor_cards` : `<article class="page-monitor-card">` →
    `<sx-page-monitor-card class="page-monitor-card">`.
  - **`frontend/src/components/sx-url-analysis.ts`** —
    `_url_analysis_markup` (2 branches : état vide + analyse complète) :
    `<div class="result-url-analysis">` →
    `<sx-url-analysis class="result-url-analysis">` dans les deux cas.
  - **`frontend/src/index.ts`** : 4 nouveaux imports.
  - **4 démos** (`frontend/demo/sx-extracted-entity-row.html`,
    `sx-evidence-item.html`, `sx-page-monitor-card.html`,
    `sx-url-analysis.html`).
  - Aucun changement CSS (rien de mort à retirer — les classes restent
    portées par l'hôte, exactement comme au Lot 19).
- **Contrats vérifiés avant modification :** tous les sélecteurs JS
  concernés (`.stop-page-monitor`, `[data-page-monitor-id]`,
  `[data-entity-id]`, `data-evidence-id`, `.analyze-result-url`, etc.)
  visent des classes/`data-*`, jamais le tag racine. `tests/test_investigation_view.py`
  n'a aucune assertion codant le nom de balise en dur pour ces 4 blocs
  (soit XPath `//*[contains(@class, ...)]` déjà insensible au tag, soit
  aucune assertion du tout) → **zéro modification de test nécessaire**.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK, bundle
    `assets/synthesix-ui.js` régénéré
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` —
    OK, 29 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre (avertissements LF/CRLF attendus)
- **Vérifications effectuées :** smoke visuel headless — capture de l'état
  par défaut de la fixture `workspace_payload()` : **taille en octets
  identique** à celle des Lots 17/19 (238770 octets), confirmant une
  absence totale de régression visuelle (carte de monitoring `Example
  page` rendue correctement via `sx-page-monitor-card`). Présence
  confirmée par grep des tags `sx-extracted-entity-row` (×1),
  `sx-evidence-item` (×1) et `sx-page-monitor-card` (×1) dans le HTML
  généré ; `sx-url-analysis` absent de cette fixture (aucune analyse URL
  dans les données de test — comportement attendu, pas un défaut). Les
  tests XPath passants confirment la structure DOM correcte pour
  `entity-chip-row`.
- **Vérifications non exécutées :** pas de capture interactive (clic pour
  révéler le panneau contenant `sx-evidence-item`/`sx-url-analysis` dans le
  rail) cette fois — jugé redondant : composants encore plus simples que
  `sx-entity-panel` (aucune logique interne, aucun style propre), et le
  mécanisme d'affichage (`hidden` natif + sélecteurs JS par classe/`data-*`)
  déjà prouvé au Lot 19 avec un composant plus complexe.
- **Risques / reste à faire :** aucun bloquant.
- **Relais :** reste au backlog — Lot 22 (`investigations/search_view.py`,
  0% Lit, incohérence `result_card(component=True)` à corriger), Lot 23
  (`index.html`, jamais investigué).

### AI-20260701-006 — Lot 22 : `search_view.py` sur `sx-result-card` + retrait du fallback mort

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** corriger l'incohérence trouvée au Lot 17 —
  `investigations/search_view.py` était le seul appelant de
  `ui.result_card()` sans `component=True`, retombant sur un fallback HTML
  brut au lieu de `<sx-result-card>`.
- **Changements :**
  - **`ui.py`** (`result_card`) : retrait du paramètre `component: bool =
    False` et de la branche `else` (HTML brut `<article class="result-card">`,
    ~90 lignes) — la fonction ne fait plus que construire
    `<sx-result-card>` (c'était déjà le seul chemin utilisé par les 2
    appelants restants). Docstring mise à jour.
  - **`investigations/search_view.py`** (`_result_card`) : l'appel à
    `ui.result_card(...)` reste inchangé (n'avait jamais besoin de l'
    argument `component`, retiré de la signature elle-même) — bascule
    automatiquement sur `<sx-result-card>`.
  - **`utils.py`** (2 sites, l.~281 et l.~613) : retrait de l'argument
    `component=True`, devenu redondant.
  - **`theme.css`** : suppression des règles mortes `.result-card`,
    `.result-card:hover`, `.result-card:focus-visible`, `.result-card:focus`,
    `.result-card--strong/good/moderate/weak`, `.result-card__body`,
    `.result-card__head`, `.result-card__title`, `.result-card__title:hover`,
    `.result-card__domain`, `.result-card__snippet`, `.result-card__meta`,
    `.result-card__actions`. Conservées (contenu slotté toujours utilisé) :
    `.result-card__notes`, `.result-card__notes strong`,
    `.result-card__tags`.
- **Contrats vérifiés avant modification :** grep exhaustif — seuls 2
  appelants de `ui.result_card()` dans tout le dépôt (`utils.py` ×2,
  `investigations/search_view.py` ×1), tous passaient déjà ou passent
  désormais par le chemin composant ; aucun test n'appelle
  `ui.result_card()` directement ni n'asserte sur les classes retirées
  (0 résultat grep dans `tests/`).
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK (aucun
    changement TS, bundle régénéré à l'identique)
  - `.venv\Scripts\python.exe -m unittest tests.test_utils tests.test_investigations tests.test_investigation_view` —
    OK, 87 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 276 tests
  - `git diff --check` — propre (avertissements LF/CRLF attendus)
- **Vérifications effectuées :** smoke visuel headless — page d'archive
  locale générée (fixture ad hoc avec notes/tags/sources/enquête liée) :
  `<sx-result-card>` confirmé par grep (1 occurrence, 0 fallback brut),
  rendu correct (chips, provenance "Enquête → Case Alpha" cliquable,
  "Première/Dernière observation", notes en gras, tags en chips mutées) —
  identique au style SERP déjà validé au Lot 7/17.
- **Risques / reste à faire :** aucun bloquant.
- **Relais :** reste au backlog — Lot 23 (`index.html`, cockpit principal,
  jamais investigué pour la migration Lit).

### AI-20260701-007 — Smoke CDP live du Lot 19 (rattrapage)

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Contexte :** l'utilisateur avait `python main.py` déjà lancé avec une
  vraie enquête ouverte (« OSINTOPIA », playground personnel — autorisation
  explicite de tester dedans). Ferme le ⚠️ laissé ouvert au Lot 19
  (AI-20260701-004) : « smoke CDP live non exécuté ».
- **Méthode :** connexion directe au websocket CDP de l'onglet ouvert
  (`ws://127.0.0.1:52999/devtools/page/...`, port trouvé via la ligne de
  commande Chrome lancée par Zendriver) et pilotage via `Runtime.evaluate`
  — clic réel sur une ligne d'entité, édition réelle du champ nom,
  déclenchement de l'auto-save au `blur` (comportement du Lot 13/14),
  restauration de la valeur d'origine ensuite (aucune donnée laissée
  modifiée).
- **Résultat :** confirmé sur l'application réelle (pas une fixture) —
  (1) `<sx-entity-panel>` bien présent dans la page réellement servie ;
  (2) clic sur la ligne d'entité → panneau révélé (`hidden` retiré) ;
  (3) édition du nom → `blur` → indicateur « Enregistré » affiché ;
  (4) **aucun rechargement de page** pendant toute l'opération (marqueur
  JS injecté avant le test resté intact après) ; (5) la ligne compacte
  dans le corps de page reflète le changement sans reload (mise à jour
  optimiste) ; (6) valeur restaurée à l'original avec succès, toujours
  sans reload.
- **Conclusion :** le renommage du tag racine (`article` → `sx-entity-panel`,
  Lot 19) et les composants tag-only du Lot 20 ne cassent aucun contrat
  CDP/JS en usage réel — confirmé au-delà des tests structurels
  (`unittest`) et du smoke visuel headless déjà faits.
- **Limites :** seul le flux « édition nom + auto-save » a été vérifié en
  live (le plus représentatif du risque signalé). Propriétés/tags/relations
  n'ont pas été testés individuellement en live cette fois — mais partagent
  le même mécanisme (`card.querySelector` + `data-*`, non affecté par le
  renommage de tag), donc risque résiduel jugé négligeable.
- **Fichiers modifiés :** aucun (vérification pure, aucun fichier du dépôt
  touché).

### AI-20260701-001 — Regroupement des pages enregistrées d'un même compte (entité partagée)

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** grouper visuellement, dans « Pages enregistrées », plusieurs
  URLs distinctes d'un même compte (ex. profil + vidéos TikTok du même
  `@handle`) qui créaient une carte chacune, sans perdre les pages
  individuelles (statut, dates, preuves).
- **Décision :** regroupement par entité partagée (`investigation_entity_sources`),
  pas par heuristique plateforme/URL — aucune extraction de plateforme
  n'existe dans le code, et le lien entité↔page est déjà posé par un geste
  analyste explicite (rattachement d'une propriété extraite), donc fiable
  sans faux positif automatique.
- **Changements :**
  - `investigations/repository.py` : nouvelle méthode
    `get_shared_entity_result_groups()` (jointure `investigation_entity_sources`
    → `investigation_entities` → `investigation_results`, `HAVING COUNT >= 2`,
    filtre `is_saved = 1`) + helper pur `_merge_transitive_result_groups()`
    (union-find, fusionne deux entités qui partagent un résultat en un seul
    groupe affiché — comportement documenté en commentaire, pas un bug) ;
  - `investigations/service.py` : wrapper fin `get_shared_entity_result_groups`
    + ajout de `shared_entity_groups` dans `workspace_payload()` ;
  - `investigations/view.py` : `_result_cards()` factorisé en
    `_single_result_card()` (réutilisable) + orchestration groupe
    (carte représentative + pages secondaires repliées dans un
    `slot="group-items"`, attributs `group-count`/`group-entity-labels`,
    nouveau bouton « Retirer du groupe » sur les cartes secondaires
    uniquement, relié à l'action existante `unlink_result_from_graph_entity`
    qui n'avait plus aucun point d'appel côté client depuis le lot
    AI-20260622-009 — réintroduit ici de façon minimale, pas le bloc
    manuel générique retiré à l'époque) ;
  - `frontend/src/components/sx-saved-page-card.ts` : props `groupCount`/
    `groupEntityLabels`, état `_groupOpen`, bouton pastille « +N autres
    pages », nouveau slot nommé `group-items` ;
  - `i18n.js` : clé `"Remove from group"` ajoutée dans les mêmes blocs que
    sa sœur `"Remove from investigation"` (fr/es/zh + pt/de).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigations` — OK, 46 tests
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 32 tests
  - `.venv\Scripts\python.exe -m unittest tests.test_i18n_coverage` — OK, 3 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 283 tests
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome (`chrome.exe --headless --screenshot`) sur une
    page d'enquête à 3 pages liées à la même entité (`RAYLOC`) : carte
    représentative + pastille « +2 autres pages » conformes au design visé.
- **Limites / non exécuté :** le clic réel d'expansion/repli de la pastille
  et le clic du bouton « Retirer du groupe » n'ont pas été testés en
  interaction live (pas de navigateur pilotable interactif dans cette
  session) — uniquement vérifiés structurellement via les tests `lxml`
  (présence des attributs, du slot, du bouton et de son
  `data-unlink-entity-id`) et via le typecheck/build TypeScript. Vérification
  du thème clair non faite séparément (le smoke a capturé le rendu par
  défaut de l'app, qui correspond à ce que l'utilisateur voit réellement).
- **Fichiers modifiés :** `investigations/repository.py`,
  `investigations/service.py`, `investigations/view.py`,
  `frontend/src/components/sx-saved-page-card.ts`, `i18n.js`,
  `tests/test_investigations.py`, `tests/test_investigation_view.py`.

### AI-20260701-002 — Remplacement du regroupement par entité par des règles de domaine/URL

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** après retour utilisateur sur AI-20260701-001 (« je regrouperais
  plutôt par URL, avec mes propres règles par site »), remplacer entièrement le
  regroupement par entité par un moteur de règles domaine + segments de chemin,
  éditable par l'utilisateur, avec défauts sûrs (aucun regroupement hors liste
  explicite).
- **Constat d'exploration :** aucune infrastructure de configuration persistée
  n'existait dans le dépôt (le dialogue « Paramètres » est purement client,
  `i18n.js`, langue/thème en `localStorage` uniquement). Réutilisation de la
  table `app_metadata` (clé/valeur, jusque-là un seul indicateur legacy) comme
  support de stockage global (pas par enquête) des règles.
- **Changements :**
  - `investigations/repository.py` : suppression de
    `get_shared_entity_result_groups`/`_merge_transitive_result_groups` ;
    ajout de `DEFAULT_URL_GROUPING_RULES` (tiktok.com, instagram.com,
    facebook.com, x.com, twitter.com — 1 segment, activées ; pappers.fr et
    tout domaine non listé restent hors regroupement par défaut),
    `get_url_grouping_rules()`, `set_url_grouping_rule()` (fusion
    défauts + overrides stockés dans `app_metadata`), et
    `get_url_based_result_groups()` (groupe par `domaine + N premiers
    segments de chemin`, sans union-find — un résultat ne produit qu'une
    seule clé, contrairement au cas entité) ;
  - `investigations/service.py` : wrappers fins + `workspace_payload()`
    expose `url_grouping_groups` et `url_grouping_rules` (remplace
    `shared_entity_groups`) ;
  - `investigations/view.py` : `_single_result_card`/`_result_cards`
    adaptés (paramètre `group_label` au lieu de `group_entity_labels`,
    suppression du bouton « Retirer du groupe » et de son câblage JS à
    `unlink_result_from_graph_entity` — action laissée intacte, seul ce
    point d'appel disparaît) ; nouveau panneau repliable « Règles de
    regroupement » (section `#url-grouping-rules`, aperçu
    `_url_grouping_rules_panel()`) avec liste des règles effectives
    (domaine, segments, activé/désactivé, retirer) et formulaire d'ajout,
    câblés en `queueAction("set_url_grouping_rule", …)` ;
  - `main.py` : nouvelle action `set_url_grouping_rule` dans la chaîne de
    dispatch (règles globales, `investigation_id` ignoré côté service mais
    toujours résolu par la boucle pour régénérer la page courante) ;
  - `frontend/src/components/sx-saved-page-card.ts` : renommage
    `groupEntityLabels`/`group-entity-labels` → `groupLabel`/`group-label` ;
    mécanisme `groupCount`/`_groupOpen`/pastille/`group-items` réutilisé tel
    quel (seule la source de la donnée change) ;
  - `i18n.js` : retrait de la clé `"Remove from group"` (plus utilisée) ;
    ajout de 9 clés courtes pour le panneau de règles (fr/es/zh +
    pt/de) — le paragraphe explicatif reste non traduit, cohérent avec le
    précédent existant (ex. le texte de la section surveillance) ;
  - `theme.css` : styles minimaux `.url-grouping-rule-row`/
    `.url-grouping-rule-form` (les lignes de règles étaient illisibles sans
    CSS dédié — vérifié visuellement avant/après).
- **Compromis assumé :** pas de dérogation par page individuelle — pour
  sortir une page d'un groupe, l'utilisateur désactive/modifie la règle du
  domaine (affecte toutes les pages de ce domaine). Cohérent avec le modèle
  « règles par site » demandé par l'utilisateur.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigations` — OK, 50 tests
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 32 tests
  - `.venv\Scripts\python.exe -m unittest tests.test_i18n_coverage` — OK, 3 tests
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 287 tests
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke headless Chrome (`chrome.exe --headless --screenshot`) : 3 pages
    TikTok même compte → groupées (carte + « +2 autres pages ») ; 2 pages
    pappers.fr de personnes différentes → non groupées malgré URLs de forme
    similaire ; panneau de règles affiche les 5 défauts avec cases à cocher,
    champs segments et formulaire d'ajout lisibles.
- **Limites / non exécuté :** interactions live (clic réel toggle/checkbox/
  formulaire) non testées dans un navigateur piloté interactif — seulement
  vérifiées via lxml (tests) et capture d'écran statique. Thème clair non
  vérifié séparément (capture = rendu par défaut réel de l'app).
- **Fichiers modifiés :** `investigations/repository.py`,
  `investigations/service.py`, `investigations/view.py`, `main.py`,
  `frontend/src/components/sx-saved-page-card.ts`, `i18n.js`, `theme.css`,
  `tests/test_investigations.py`, `tests/test_investigation_view.py`.

### AI-20260701-003 — Retours utilisateur sur le regroupement (représentative, clic, superposition, panneau Lit)

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** après usage réel de AI-20260701-002, corriger quatre points
  remontés par l'utilisateur : carte représentative = URL la plus courte,
  clic cassé sur les pages repliées, décalage visuel de la grille au dépli,
  panneau de règles pas en Lit et 1 règle par ligne.
- **Changements :**
  - `investigations/view.py` `_result_cards()` : la carte représentative
    d'un groupe est désormais celle dont l'URL est la plus courte
    (`min(..., key=len)`), plus le premier résultat rencontré dans l'ordre
    de la liste ;
  - `investigations/view.py` (script inline, wiring `resultCards`) : ajout
    d'une garde `event.target.closest("sx-saved-page-card") !== card` avant
    le `selectInspectorPage` du clic sur toute la carte — corrige un bug où
    le clic sur une page repliée (imbriquée dans le `slot="group-items"` de
    la représentative) remontait et rouvrait à tort le panneau de la
    représentative (les deux cartes ont chacune leur propre listener, le
    clic bullait vers l'ancêtre) ;
  - `frontend/src/components/sx-saved-page-card.ts` : le panneau des pages
    repliées (`slot="group-items"`) passe en superposition
    (`position: absolute`, même technique que le menu « ⋯ » existant,
    `z-index` juste en dessous) au lieu d'un bloc en flux normal — déplier
    ne pousse plus plus les cartes voisines de la grille ;
  - nouveau composant `frontend/src/components/sx-grouping-rules.ts` :
    remplace le HTML brut de `_url_grouping_rules_panel()` (supprimée).
    Payload JSON via `<script type="application/json" data-rules>` (même
    pattern que `sx-entity-graph`), un seul `CustomEvent("sx-rule-change",
    {bubbles, composed, detail:{domain, pathSegments, enabled}})` pour
    toute édition/retrait/ajout, grille interne `repeat(auto-fill,
    minmax(200px,1fr))` (4-5 règles par ligne selon largeur), texte en dur
    en français (cohérent avec `sx-saved-page-card.ts`, hors d'atteinte du
    balayage DOM de `i18n.js` une fois en Shadow DOM) ;
  - **bug de timing découvert et corrigé** : `synthesix-ui.js` est chargé en
    `<script>` classique dans `<head>` (pas de `type=module`, contrainte
    `file://`), donc tous les `sx-*` sont définis avant que le parseur
    n'atteigne leur contenu — `connectedCallback()` peut s'exécuter avant
    que le `<script data-rules>` enfant ne soit encore parsé. Même
    problème et même correctif déjà présents dans `sx-entity-graph.ts`
    (commentaire similaire) : relecture différée via
    `requestAnimationFrame` dans `firstUpdated()`. Découvert et vérifié en
    conditions réelles via le serveur de prévisualisation (le composant
    isolé fonctionnait, la page complète non, jusqu'au fix) ;
  - `investigations/view.py` : remplacement du wiring JS par règle
    individuelle par un seul `document.addEventListener("sx-rule-change",
    ...)` ; suppression de `_url_grouping_rules_panel()` ;
  - `theme.css` : retrait des règles `.url-grouping-rule-row`/
    `.url-grouping-rule-form` (remplacées par le Shadow DOM du composant) ;
  - `i18n.js` : retrait de 7 clés devenues mortes (déplacées en dur dans le
    composant) — a aussi corrigé une collision de clé dupliquée `"Domain"`
    que ces clés avaient introduite par erreur dans `multilingual`/
    `additionalTranslations` (silencieusement écrasée par JS, invisible
    sans relecture attentive) ; conservé « Grouping rules »/« Group saved
    pages by domain » (toujours light DOM, encore traduits).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 33 tests (dont 1 nouveau test représentative=URL courte réécrit, 1 nouveau test régression clic, 1 test panneau règles réécrit pour `<sx-grouping-rules>`)
  - `.venv\Scripts\python.exe -m unittest tests.test_i18n_coverage` — OK, 3 tests (confirme la collision de clé résolue)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
  - Vérification **interactive réelle** (pas seulement statique) via le
    serveur de prévisualisation MCP : (1) rendu du panneau de règles avec
    les 5 défauts en grille multi-colonnes ; (2) clic programmatique sur le
    bouton « +N autres pages » → panneau déplié sans décaler la section
    suivante (« Règles de regroupement » reste à la même position) ; (3)
    clic programmatique sur une carte imbriquée → ouvre bien son propre
    panneau d'inspection (`selectedPanel === nestedId`, pas
    `representative.id`) — confirme le fix du bug de clic en conditions
    réelles, pas seulement via l'assertion de présence du code.
- **Limites / non exécuté :** thème clair non vérifié séparément (rendu par
  défaut de l'app resté dark dans tous les smokes de cette session).
- **Fichiers modifiés :** `investigations/view.py`,
  `frontend/src/components/sx-saved-page-card.ts`,
  `frontend/src/components/sx-grouping-rules.ts` (nouveau),
  `frontend/src/index.ts`, `theme.css`, `i18n.js`,
  `tests/test_investigation_view.py`.

### AI-20260701-004 — Hauteur uniforme des cartes « Pages enregistrées »

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** retour utilisateur — dans une même ligne de la grille, les
  cartes de hauteurs différentes (ex. carte avec « +N autres pages » plus
  haute que ses voisines) rendaient l'ensemble visuellement inégal.
- **Changement :** `theme.css`, `.investigation-results` :
  `align-items: start` → `align-items: stretch`. Les cartes (grid items)
  s'étirent désormais à la hauteur de la ligne la plus haute ; le panneau
  replié (`slot="group-items"`, en superposition depuis AI-20260701-003)
  reste hors flux donc aucun conflit avec l'étirement.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_home_ui` — OK, 44 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - Smoke headless Chrome : capture avant/après confirmant les 3 cartes
    d'une même ligne (2 pappers.fr + 1 tiktok groupée) alignées à hauteur
    égale.
- **Fichiers modifiés :** `theme.css`.

### AI-20260701-005 — Pastille « +N » sur la ligne statut/date (au lieu d'une ligne à part)

- **Agent :** Claude
- **Période UTC :** 2026-07-01
- **Branche / commits :** `feat/lit-frontend`, non committé
- **Objectif :** le `align-items: stretch` du lot précédent rendait les
  cartes de même hauteur mais avec du vide visible en bas des cartes sans
  groupe — pas franchement propre. Retour utilisateur : mettre « +N pages »
  sur la même ligne que le statut/la date au lieu d'une ligne dédiée sous
  les tags, pour que le contenu réel des cartes ait la même hauteur, pas
  seulement leur boîte étirée.
- **Changement :** `frontend/src/components/sx-saved-page-card.ts` — le
  bouton `.group-toggle` déplacé dans la ligne `.sub` (après la pastille de
  date), `margin-left: auto` pour rester collé à droite comme les autres
  pastilles ; libellé raccourci en « +N » (le détail complet reste dans le
  `title` au survol) ; `align-self: flex-start` retiré (plus pertinent hors
  flex row dédiée).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` — OK, 33 tests
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
  - Smoke headless Chrome : capture confirmant les 3 cartes d'une même
    ligne à hauteur identique, pastille « +2 » bien alignée avec la date.
- **Fichiers modifiés :** `frontend/src/components/sx-saved-page-card.ts`.

### AI-20260702-001 — Fix overlay : saisie clavier volée par la page hôte (TikTok)

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** l'utilisateur ne pouvait plus écrire dans les champs de
  l'overlay (menu de capture) sur une page vidéo TikTok. Cause identifiée :
  les `<input>` de l'overlay vivent dans un Shadow DOM ; TikTok a un
  gestionnaire clavier global (raccourcis lecture/pause, seek…) qui décide
  d'intercepter la touche en inspectant `document.activeElement` — cette
  API s'arrête à la frontière du Shadow DOM et ne voit que l'hôte du
  custom element, jamais l'`<input>` réellement focus. TikTok croit donc
  qu'aucun champ n'est actif et appelle `preventDefault()` sur les touches
  destinées à l'overlay.
- **Changement :** `frontend/src/overlay/index.ts` — ajout d'écouteurs
  `keydown`/`keypress`/`keyup` sur `window` en phase de capture (le point
  le plus tôt possible dans la propagation, avant `document`) ; si
  l'événement provient d'un `input`/`textarea`/`select` situé dans un
  élément `sx-overlay-*` (détecté via `composedPath()`), `stopPropagation()`
  empêche l'événement d'atteindre les gestionnaires de la page hôte.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement (fin de ligne)
- **Non exécuté :** smoke réel sur une page TikTok via CDP live (nécessite
  une session Zendriver + navigation manuelle) — à valider par l'utilisateur
  en conditions réelles.
- **Fichiers modifiés :** `frontend/src/overlay/index.ts`,
  `assets/synthesix-overlay.js` (bundle régénéré).

### AI-20260702-002 — Fix racine du vol de focus overlay (TikTok) : injection CDP précoce

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** AI-20260702-001 (fix `stopPropagation` sur `keydown` dans le
  bundle overlay) n'a pas suffi — diagnostic live (utilisateur, console
  DevTools sur TikTok) a montré que le vol de focus n'est pas dû à un
  `preventDefault()` sur les touches mais à un appel JS direct
  `element.focus()` du SDK TikTok (`webmssdk.js`, chaîne d'appel minifiée
  `nf→nA→nY→nz`) qui reprend le focus sur son propre conteneur juste après
  que l'input de l'overlay l'ait obtenu. Blocage par `stopPropagation` sur
  `focus`/`focusin`/`blur`/`focusout` en capture sur `window` : inefficace
  (testé en live, confirmé par l'utilisateur). Patch direct de
  `playerRoot.focus` en no-op (instance) : inefficace aussi — l'appel est
  bien tracé mais le focus part quand même ailleurs, signe que
  l'interception doit se faire **avant** que le SDK tiers ne s'exécute, pas
  après.
- **Cause racine :** l'overlay Synthesix est injecté tard, via
  `tab.evaluate()` après chargement complet de la page (`main.py`,
  `_install_and_consume_save_overlay`) — toujours après les scripts de la
  page hôte, donc toujours perdant sur l'ordre d'exécution/enregistrement
  des écouteurs et sur toute référence native que le SDK tiers aurait déjà
  capturée.
- **Changement :** `main.py` — nouvelle fonction `_overlay_focus_guard_script()`
  (JS autonome, sans dépendance au bundle Lit) qui : (1) patche
  `HTMLElement.prototype.focus` pour bloquer tout `.focus()` externe tant que
  `document.activeElement` est dans un élément `sx-overlay-*` et que la
  cible ne l'est pas ; (2) garde en défense-en-profondeur le
  `stopPropagation` sur `keydown/keypress/keyup` pour les champs overlay
  (même logique que AI-20260702-001, dupliquée ici pour ne pas dépendre du
  bundle). Nouvelle fonction `_arm_overlay_focus_guard(tab)` qui enregistre
  ce script via CDP `Page.addScriptToEvaluateOnNewDocument`
  (`uc.cdp.page.add_script_to_evaluate_on_new_document`, exécuté **avant**
  tout script de la page sur chaque future navigation de l'onglet) — appelée
  au début de `_install_and_consume_save_overlay`, idempotente par onglet via
  un set `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` keyé sur `tab.target_id`
  (évite d'empiler le script à chaque tick de poll).
- **Limite connue :** comme Synthesix découvre les onglets par polling (pas
  d'écoute `Target.targetCreated`), ce script ne protège que les
  **navigations futures** de l'onglet (rechargement, nouvelle URL), jamais
  la page déjà chargée au moment où on l'arme. Sur une TikTok déjà ouverte,
  l'utilisateur doit recharger une fois la page pour que le guard s'arme ;
  ensuite il reste actif pour toute la session SPA (le patch de prototype
  survit à la navigation client-side, seule une vraie navigation/reload
  réexécute les scripts JS).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m py_compile main.py` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
  - `git diff --check` — OK, avertissements CRLF uniquement (fichiers déjà
    modifiés par AI-20260702-001)
- **Fichiers modifiés :** `main.py`.

### AI-20260702-004 — `stopImmediatePropagation` sur le guard clavier

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** smoke live utilisateur sur AI-20260702-003 : `guard armed:
  true`, focus/clic/sélection dans les champs texte fonctionnent enfin, mais
  taper au clavier (lettres, espace, effacer) ne fait toujours rien. Le vol
  de focus est résolu ; reste l'insertion de caractère bloquée — signe d'un
  `preventDefault()` sur `keydown`, probablement par un handler TikTok
  également enregistré sur `window`.
- **Cause :** `event.stopPropagation()` empêche l'événement d'atteindre
  d'AUTRES nœuds du DOM, mais pas les autres écouteurs sur le **même** nœud
  enregistrés après le nôtre. Comme le guard s'arme avant tout script de la
  page (AI-20260702-002/003), tout handler clavier que TikTok enregistre
  aussi sur `window` s'enregistre forcément après le nôtre — `stopPropagation`
  seul ne l'empêche pas de tourner et d'appeler `preventDefault()`. Il fallait
  `stopImmediatePropagation()`.
- **Changement :** `main.py` (`_overlay_focus_guard_script`) et
  `frontend/src/overlay/index.ts` — `event.stopImmediatePropagation()` ajouté
  avant `stopPropagation()` dans les écouteurs `keydown/keypress/keyup`
  ciblant les champs overlay.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `.venv\Scripts\python.exe -m py_compile main.py` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel sur TikTok — à revalider par l'utilisateur
  (redémarrer l'app, laisser Synthesix redécouvrir l'onglet, recharger la
  page TikTok, tester la frappe clavier dans les champs).
- **Fichiers modifiés :** `main.py`, `frontend/src/overlay/index.ts`,
  `assets/synthesix-overlay.js` (bundle régénéré).

### AI-20260702-005 — Suggestions de propriété manquantes + capture "Visible area" qui fait avancer la vidéo hôte

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** deux régressions signalées après validation du vol de focus :
  (1) le champ « Property name » du menu de capture n'affiche plus de
  suggestions (liste déroulante des propriétés de l'entité sélectionnée),
  contrairement au menu « Ajouter à l'enquête » qui l'a toujours ; (2) une
  capture « Visible area » (pas « Select area ») fait avancer le
  media (vidéo/photo suivante) sur TikTok/Instagram juste après la capture.
- **Cause (1) :** lors de la migration Lit, `sx-overlay-capture-menu.ts` n'a
  jamais reçu la logique de suggestions que `sx-overlay-entity-menu.ts`
  possède (datalist + `tagsetProperties` dérivées des tags de l'entité
  sélectionnée) — `main.py` ne passait `tagsetProperties` qu'à `entityMenu`,
  pas à `captureMenu`.
- **Cause (2) :** diagnostic confirmé par l'utilisateur — le changement de
  media survient *après* la capture, sans focus préalable dans un champ
  texte, donc pas un souci de focus/clic. Seul `capture_png` avec
  `capture_beyond_viewport=True` (CDP `Page.captureScreenshot`) diffère
  entre « Visible area » (clip = viewport exact) et « Select area » (clip =
  sous-région plus petite, qui ne reproduit pas le bug) ; ce flag pousse
  Chrome à ajuster le rendu au-delà du viewport visible, ce qui semble
  déclencher la logique « snap vers le media suivant » de ces sites
  (souvent basée sur la visibilité/scroll).
- **Changement :**
  - `frontend/src/overlay/sx-overlay-capture-menu.ts` — nouvelle propriété
    `tagsetProperties`, `GraphEntity` étendue (`tags`, `propertyKeys`),
    getter `_propertySuggestions` (même logique que l'entity-menu, sans la
    complexité du type de propriété qui n'existe pas ici), `<datalist>`
    branché sur `.prop-input` via `list=`.
  - `main.py` — `captureMenu.tagsetProperties = tagsetProperties;` ajouté à
    la création du menu (à côté de l'affectation identique sur
    `entityMenu`).
  - `evidence/capture.py`, `capture_png(...)` — nouveau paramètre
    `capture_beyond_viewport: bool = True` (défaut inchangé, rétrocompatible
    avec le test existant).
  - `main.py`, `_capture_evidence` — `capture_beyond_viewport=(capture_scope
    != "viewport")` : `False` uniquement pour le scope viewport, `True`
    conservé pour `region` (comportement déjà validé, non modifié).
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `.venv\Scripts\python.exe -m py_compile main.py evidence/capture.py` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel sur TikTok pour les deux points — à
  revalider par l'utilisateur (redémarrer l'app, recharger la page,
  vérifier les suggestions de propriété puis une capture « Visible area »).
- **Fichiers modifiés :** `frontend/src/overlay/sx-overlay-capture-menu.ts`,
  `main.py`, `evidence/capture.py`,
  `assets/synthesix-overlay.js` (bundle régénéré).

### AI-20260702-006 — `reset()` du menu de capture n'effaçait pas le `<select>` d'entité

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** après AI-20260702-005, une deuxième capture affichait
  l'entité de la capture précédente sélectionnée dans le `<select>` (visuel
  uniquement), sans accès aux suggestions de propriété, et l'attachement
  échouait silencieusement à l'enregistrement.
- **Cause :** `sx-overlay-capture-menu.ts::reset()` remet `_selectedEntityId`
  (état interne Lit) à `""`, mais le template ne lie pas `.value` sur le
  `<select class="entity-select">` — l'élément DOM garde donc sa valeur
  précédente après reset. Résultat : `_propertySuggestions` (basé sur
  `_selectedEntityId`, vide) ne trouve plus l'entité malgré le select qui
  l'affiche encore, et `_attach` (`if (!this._selectedEntityId) return
  null`) n'attache plus rien. `sx-overlay-entity-menu.ts::_close()` fait
  déjà `select.value = ""` explicitement — l'équivalent manquait côté
  capture-menu.
- **Changement :** `frontend/src/overlay/sx-overlay-capture-menu.ts` —
  nouvel accesseur privé `entitySelect()` (même pattern que `input()` /
  `propertyInput()`), `reset()` remet aussi `select.value = ""`.
- **Tests exécutés :**
  - `cd frontend && npm run typecheck && npm run build` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel — à revalider par l'utilisateur (deux
  captures successives avec attachement à une entité différente/aucune,
  vérifier que le select et les suggestions repartent bien à vide entre
  les deux).
- **Fichiers modifiés :** `frontend/src/overlay/sx-overlay-capture-menu.ts`,
  `assets/synthesix-overlay.js` (bundle régénéré).

### AI-20260702-003 — Correction du guard CDP : `Page.enable()` manquant

- **Agent :** Claude
- **Période UTC :** 2026-07-02
- **Branche / commits :** feat/lit-frontend
- **Objectif :** smoke live utilisateur sur AI-20260702-002 négatif — après
  redémarrage de l'app et double reload de la page TikTok,
  `window.__synthesixFocusGuardInstalled` restait `undefined`. Reproduit en
  isolation avec un script zendriver autonome (hors app, hors TikTok) : même
  un script minimal (`window.__minimalFlag = 'hello'`) enregistré via
  `Page.addScriptToEvaluateOnNewDocument` ne s'exécutait jamais après une
  vraie navigation suivante — la commande CDP est acceptée (renvoie un
  `ScriptIdentifier` valide) mais reste un no-op silencieux.
- **Cause :** `Page.addScriptToEvaluateOnNewDocument` exige que le domaine
  `Page` soit activé (`Page.enable`) sur la session CDP pour prendre effet
  réellement ; zendriver n'active ce domaine nulle part automatiquement et
  `_arm_overlay_focus_guard` ne l'envoyait pas non plus.
- **Changement :** `main.py`, `_arm_overlay_focus_guard` — ajout de
  `await tab.send(uc.cdp.page.enable())` avant l'appel à
  `add_script_to_evaluate_on_new_document`.
- **Tests exécutés :**
  - Script zendriver isolé (hors suite, `scratchpad`) : sans `page.enable()`
    → flag jamais posé après navigation réelle (`example.com`) ; avec →
    `True`. Puis re-testé avec la vraie fonction `_arm_overlay_focus_guard`
    du projet (pas une réimplémentation) : `installed after navigation: True`.
  - `.venv\Scripts\python.exe -m py_compile main.py` — OK
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 288 tests
- **Non exécuté :** smoke réel sur TikTok — à revalider par l'utilisateur
  (redémarrer l'app une nouvelle fois, laisser Synthesix découvrir l'onglet
  une fois, recharger la page TikTok, vérifier
  `window.__synthesixFocusGuardInstalled === true` puis tester la saisie).
- **Fichiers modifiés :** `main.py`.

### AI-20260703-001 — Refonte du layout et des propriétés de l'export ZeroNeurone

- **Agent :** Claude
- **Période UTC :** 2026-07-03 08:37-09:20
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** retour utilisateur sur le graphe curaté exporté vers
  ZeroNeurone : layout illisible (une colonne unique, les relations
  entité-entité traversaient tout le graphe), propriété `Type Synthesix`
  incompréhensible côté ZeroNeurone, `Sources liées` fausse/peu pertinente,
  propriété de page (ex. « Première publication ») explicitement rattachée à
  une entité mais absente de cette entité à l'export, et fichiers HTML/MHTML/
  Texte trop volumineux embarqués par défaut dans l'archive.
- **Changements (`exports/zeroneurone.py`) :**
  - `_curated_positions` réécrit : les entités curatées sont regroupées par
    composantes connexes (relations entité-entité, hors « Trouvé sur ») via
    BFS puis disposées en grille (jusqu'à 4 colonnes) au lieu d'une colonne
    unique ; les sources de chaque entité restent proches d'elle plutôt que
    dans une colonne globale partagée.
  - `HIDDEN_NATIVE_PROPERTIES` inclut désormais `synthesix_type` (n'était
    affiché nulle part ailleurs, cassait la lecture côté ZeroNeurone).
  - Propriété `linked_source_count` / « Sources liées » supprimée de l'export
    (comptage jugé non fiable et peu pertinent par l'utilisateur).
  - `facts_by_entity` (graphe curaté) n'exclut plus les faits de portée page
    (`property_scope: page`) qui ont explicitement été rattachés à une entité
    via `investigation_entity_id` (contrôle « rattacher à une entité » de
    `investigations/view.py`) : ces propriétés (ex. « Première publication »)
    apparaissent maintenant sur l'entité en plus de la page source. Les faits
    de page non rattachés restent uniquement sur le nœud « Site web » (test
    `test_curated_graph_keeps_page_scoped_properties_on_source_node`
    préservé).
  - Nouveau paramètre `include_page_archives` (défaut `False`) sur
    `export_zeroneurone_bundle` / `_write_native_dossier` /
    `_copy_native_assets` : les artefacts `html`/`mhtml`/`text`
    (`DOCUMENT_ARCHIVE_ARTIFACT_TYPES`) sont exclus des assets copiés par
    défaut ; seuls les captures d'écran (`png`) suivent `include_evidence`
    par défaut. Option tracée dans `manifest.json` (`options.
    include_page_archives`).
- **Changements (persistance / UI) :**
  - `investigations/migrations.py` — migration 17 : `ALTER TABLE
    investigation_exports ADD COLUMN include_page_archives INTEGER NOT NULL
    DEFAULT 0` (même style que la migration 10 pour `asset_count`).
  - `investigations/models.py`, `investigations/repository.py`,
    `investigations/service.py` (passthrough `**kwargs`, inchangé) —
    `InvestigationExport.include_page_archives` propagé de l'insert à
    `to_payload()`.
  - `investigations/view.py` — case à cocher « Also include full page
    archives (HTML/MHTML/Text) — large files » dans le formulaire d'export ;
    `includePageArchives` ajouté au payload JS `queueAction`;
    `_export_cards` distingue « evidence assets (screenshots only) » vs
    « (with page archives) » dans la description de l'export.
  - `main.py` (handler `export_zeroneurone`) — lit `includePageArchives`,
    le transmet à `export_zeroneurone_bundle` et à `record_export`.
- **Non retenu / vérifié faux par les tests existants :** copier
  automatiquement TOUTES les propriétés de page sur TOUTES les entités liées
  à cette page (essayé, puis abandonné) : le test
  `test_curated_graph_keeps_page_scoped_properties_on_source_node` encode
  volontairement que des métadonnées de page (ex. `Domaine`) ne doivent pas
  fuiter sur chaque entité trouvée sur la page. Seules les propriétés
  **explicitement rattachées** à une entité précise en sont remontées.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 25 tests (4 nouveaux : layout en grille, propriété de page rattachée
    à l'entité, propriétés internes/`Sources liées` absentes, filtrage des
    archives de page)
  - `.venv\Scripts\python.exe -m unittest tests.test_investigations
    tests.test_investigation_view tests.test_main
    tests.test_zeroneurone_export tests.test_zeroneurone_tags` — OK, 148
    tests (versions de schéma `16` → `17` mises à jour dans
    `tests/test_investigations.py`)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 292 tests
  - `.venv\Scripts\python.exe -m py_compile exports/zeroneurone.py
    investigations/view.py investigations/migrations.py
    investigations/models.py investigations/repository.py main.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel d'un export ouvert dans ZeroNeurone (nécessite
  l'application tierce) — à valider par l'utilisateur ; capture Chrome
  headless du graphe non pertinente ici (rendu fait côté ZeroNeurone, pas
  Synthesix).
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `investigations/migrations.py`, `investigations/models.py`,
  `investigations/repository.py`, `investigations/view.py`, `main.py`,
  `tests/test_zeroneurone_export.py`, `tests/test_investigations.py`.
- **Relais :** aucun blocage. Prochaine action si l'utilisateur constate
  encore des soucis : importer un export réel dans ZeroNeurone pour
  confirmer visuellement le nouveau layout en grille et la disparition de
  `Type Synthesix`/`Sources liées`.

### AI-20260703-002 — Les captures d'écran deviennent des nœuds visuels du graphe curaté

- **Agent :** Claude
- **Période UTC :** 2026-07-03 09:30-10:05
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** suite à AI-20260703-001, retour utilisateur : les propriétés
  remontent bien sur le graphe curaté, mais les captures d'écran (ex. 7-8
  captures liées à une entité « Rayloc ») restaient invisibles (fichiers
  attachés en silence sur l'entité, sans nœud propre). Demande : quand une
  preuve est de type image/capture d'écran, la faire apparaître comme nœud
  sur le graphe (plus visuel), avec la source de l'info ; sinon en evidence
  classique.
- **Changements (`exports/zeroneurone.py`) :**
  - `_build_curated_graph` crée désormais un nœud `evidence-{capture_id}`
    pour chaque capture liée à une entité curatée dont au moins un artefact a
    un `mime_type` commençant par `image/` (couvre les captures `screenshot`
    et les imports `imported` de type image, pas seulement `capture_kind ==
    "screenshot"`). Relié à l'entité par une arête « Illustré par » ; le nœud
    porte `source` = l'URL de la page capturée (la « source de l'info »
    demandée) et la date de capture. Gardé derrière `include_evidence`
    (paramètre déjà présent mais jusqu'ici inutilisé dans cette fonction).
    Les preuves non image (archives HTML/MHTML/Texte) restent de simples
    fichiers attachés à l'entité, comportement inchangé.
  - `_copy_native_assets` route désormais chaque artefact image vers le
    nouveau nœud evidence (`capture_id`) plutôt que vers l'entité, pour
    éviter un doublon (fichier visible à la fois sur le nœud image et dans
    les FICHIERS de l'entité).
  - `_native_visual` : les nœuds `evidence` récupèrent une forme carrée et
    une icône `Image` (au lieu d'une simple couleur) pour se distinguer sur
    le canevas.
  - `_curated_positions` généralisé : le mécanisme d'éventail qui plaçait
    uniquement les sources « Trouvé sur » à côté de leur entité couvre
    maintenant tout satellite (source de page **et** image de preuve), donc
    plusieurs captures sur une même entité restent groupées près d'elle au
    lieu de tomber dans la colonne « leftover » éloignée.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 26 tests (`test_curated_evidence_attaches_as_entity_files` réécrit en
    `test_curated_image_evidence_becomes_its_own_node` pour refléter le
    nouveau comportement voulu ; 2 tests ajoutés : nœud image + éventail de
    plusieurs captures autour d'une entité)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 293 tests
  - `.venv\Scripts\python.exe -m py_compile exports/zeroneurone.py
    tests/test_zeroneurone_export.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel dans l'application ZeroNeurone (rendu visuel
  de l'icône `Image` et de la forme carrée non vérifiable depuis Synthesix)
  — à valider par l'utilisateur sur le prochain export du cas Rayloc.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`.

### AI-20260703-003 — Captures citées par une propriété (`source_capture_id`) surfacées sur le graphe

- **Agent :** Claude
- **Période UTC :** 2026-07-03 10:15-10:50
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** retour utilisateur (cas « Rayloc ») : seules 3 captures sur 8+
  apparaissaient comme nœuds « Illustré par » (AI-20260703-002). La propriété
  « Capture voiture » de l'entité montre 8 valeurs (plaques) sourcées chacune
  par une capture différente (badges de citation numérotés dans Synthesix),
  mais ces captures n'étaient pas rattachées via `linked_result_ids` de
  l'entité (mécanisme page-level utilisé par AI-20260703-002), donc
  invisibles côté export. Demande explicite : ne pas se baser sur le mot
  « capture », utiliser le mécanisme rationnel déjà présent dans Synthesix ;
  le lien de l'image doit porter le nom de la propriété dont elle est la
  preuve.
- **Cause identifiée :** le flux « attacher une preuve à une propriété »
  (`InvestigationService.attach_evidence_capture_to_entity`, menu de capture
  overlay) crée un fait (`extracted entity`) dont `attributes.
  source_capture_id` pointe vers la capture source — c'est ce champ, pas
  `linked_result_ids`, que l'UI Synthesix utilise déjà pour numéroter les
  badges de citation (`investigations/view.py`, `sources_by_parent`). Le
  graphe curaté ignorait totalement ce champ.
- **Changements (`exports/zeroneurone.py`) :**
  - Nouveaux helpers `_capture_has_image(capture)` et
    `_evidence_node(capture, capture_id)` (factorisés hors de
    `_build_curated_graph`, réutilisés par les deux mécanismes).
  - Dans la boucle des faits de `_build_curated_graph` : pour chaque fait
    dont `attributes.source_capture_id` référence une capture avec un
    artefact `image/*`, un nœud preuve est créé et relié à l'entité par une
    arête **nommée d'après la clé de propriété du fait** (ex. « Capture
    voiture », « Capture Tiktok ») au lieu d'un « Illustré par » générique.
    La propriété texte existante (ex. « Capture voiture: WW-246-FA; ... »)
    est conservée telle quelle — le nœud image s'ajoute, ne la remplace pas.
  - Le passage générique « Illustré par » (page-level, via
    `linked_result_ids`) reste en filet de sécurité pour les captures sans
    citation de propriété, mais saute désormais les captures déjà rattachées
    par citation (`cited_capture_ids`) pour éviter une arête redondante vers
    le même nœud.
  - `_copy_native_assets` inchangé dans son principe (route déjà tout
    artefact image vers `capture_id`), fonctionne sans modification
    supplémentaire car le nœud existe désormais quel que soit le mécanisme
    qui l'a créé.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 27 tests (1 nouveau :
    `test_fact_cited_screenshot_surfaces_as_property_labelled_node`, capture
    rattachée uniquement via `source_capture_id`, page absente de
    `linked_result_ids`, vérifie le libellé d'arête = clé de propriété et la
    conservation de la propriété texte)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 294 tests
  - `.venv\Scripts\python.exe -m py_compile exports/zeroneurone.py
    tests/test_zeroneurone_export.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** smoke réel avec le vrai cas Rayloc dans ZeroNeurone (les
  8 captures « Capture voiture » doivent maintenant apparaître) — à valider
  par l'utilisateur sur son prochain export.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`.

### AI-20260703-004 — Notes analyste éditables sur les pages enregistrées

- **Agent :** Claude
- **Période UTC :** 2026-07-03
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** demande utilisateur (cas « Rayloc ») : pouvoir noter ce que
  l'analyste voit/pense sur une page enregistrée, avec un bloc visuel inspiré
  du champ Notes des entités, et que ces notes ressortent dans l'export
  ZeroNeurone.
- **Constat :** `InvestigationResult.notes` existait déjà de bout en bout
  (modèle, `repository.py`, validation `service.py`
  `MAX_RESULT_NOTES_LENGTH`, export `exports/zeroneurone.py:668,834` qui
  mappe déjà `result.notes` vers `Element.notes`). Le contrôle éditable avait
  été volontairement retiré de la carte compacte lors d'un lot antérieur
  (AI-20260621-008 : « suppression des contrôles visibles Notes/tags
  analyste sur la carte »), les notes restant en `<textarea data-result-notes
  hidden>` pour préserver le payload `update_investigation_result`. Il
  manquait uniquement un contrôle visible.
- **Changements (`investigations/view.py`) :**
  - `_inspector_panel` : nouveau paramètre `read_only`, nouveau bloc
    `<label class="entity-field"><span class="entity-field__label">Notes</span>
    <textarea data-result-notes-edit>...` inséré dans le panneau du rail
    (juste après les badges statut/favori/surveillance, avant la description
    auto-extraite), réutilisant tel quel les classes CSS déjà utilisées par
    le panneau d'entité (`sx-entity-panel`) — aucun CSS ajouté.
  - Site d'appel de `_inspector_panel` : passe `read_only=read_only`
    (désactive le textarea en investigation archivée, cohérent avec le
    reste du panneau).
  - JS : dans `resultCards.forEach`, écoute `blur` sur
    `[data-result-notes-edit]` du panneau correspondant, recopie la valeur
    dans le `<textarea data-result-notes hidden>` de la carte puis appelle
    `saveResult(card)` (réutilise le payload/action `update_investigation_result`
    existant, no-reload).
- **Contrats ou décisions :** aucun nouveau contrat CDP ; réutilise
  `update_investigation_result` (favori/statut/tags/notes) déjà no-reload.
  Pas d'éditeur de tags ajouté (hors périmètre de la demande).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_investigation_view` —
    OK, 33 tests (2 assertions ajoutées : présence/valeur/non-disabled du
    textarea dans `test_rail_inspector_panel_summarizes_each_saved_page`,
    `disabled` en investigation archivée dans
    `test_archived_workspace_disables_analyst_mutations`)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 294 tests
  - `git diff --check` — OK, avertissements CRLF uniquement
  - smoke visuel headless (rendu isolé du panneau rail via fixture
    `workspace_payload`) : le textarea affiche bien la valeur échappée
    (`Needs <verification>`) avec le style `entity-field` (label + zone de
    texte bordée), cohérent avec le bloc Notes des entités.
- **Non exécuté :** smoke CDP live dans l'application réelle (clic sur une
  page enregistrée, saisie de note, vérification de la persistance et de
  l'export ZeroNeurone du cas Rayloc) — à valider par l'utilisateur.
- **Fichiers modifiés :** `investigations/view.py`,
  `tests/test_investigation_view.py`.
- **Retour utilisateur immédiat (même lot) :** capture réelle de l'app →
  1) badge de statut sur la même ligne que le titre (était sur sa propre
  ligne sous l'URL) ; 2) couleurs par statut sur les badges (gris uniforme
  avant) ; 3) description de la page juste après l'URL (avant : après le
  bloc Notes) ; 4) placeholder du textarea Notes simplifié en « Notes… »
  (au lieu de « Ce que l'analyste voit, pense… »).
  - `investigations/view.py` : nouveau dict `STATUS_BADGE_TONES` (statut →
    warning/accent/danger/success) ; badge statut = `inspector-badge--
    {tone}` au lieu de `inspector-badge--status` ; nouveau wrapper
    `<div class="inspector-panel__head">` regroupant titre + badges ;
    nouvel ordre du panneau : head, url, description, notes, details.
  - `theme.css` : `.inspector-panel__head` (flex, titre flexible + badges
    figés), 4 nouvelles classes `inspector-badge--{accent,success,warning,
    danger}` réutilisant les tokens `--*-soft`/`--*-ink` déjà présents
    (mêmes valeurs que `--fav`/`--mon`, pas de nouvelle couleur inventée).
  - Tests : assertions ajoutées (placeholder, badge de statut coloré dans
    le head avec le titre, ordre description-avant-notes via position des
    enfants directs du panneau).
  - Tests exécutés : `unittest tests.test_investigation_view` (33 OK),
    `unittest discover` (294 OK), `git diff --check` OK.

### AI-20260703-005 — Notes de page absentes de l'export ZeroNeurone quand le lien passe par un fait

- **Agent :** Claude
- **Période UTC :** 2026-07-03
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** retour utilisateur (cas « Rayloc », suite d'AI-20260703-004) :
  la note saisie sur la page TikTok (« Voiture disponible à la location,
  plaque KTT-RW98 ») restait invisible dans ZeroNeurone — le nœud inspecté
  (« KTT-RW98 ») était en fait le nœud preuve/capture citant cette plaque, un
  nœud distinct du nœud « page ».
- **Cause racine :** `_build_curated_graph` (`exports/zeroneurone.py`) ne
  crée un nœud « Site web » pour une page que si elle apparaît dans
  `source_result_ids = linked_entities_by_result ∪ page_properties_by_result`.
  `linked_entities_by_result` n'était alimenté que par
  `entity.linked_result_ids` (lien explicite). Or le rail Synthesix
  (`_page_linked_entities_markup`, `investigations/view.py`) affiche déjà une
  page sous « Entités utilisant cette page » via **deux** mécanismes : ce
  même `linked_result_ids`, **ou** un fait extrait rattaché à l'entité
  (`investigation_entity_id` + `result_id` du fait). RAYLOC n'était lié à
  cette page TikTok que via des faits extraits (plaque, etc.), pas via
  `linked_result_ids` — donc côté export, la page n'obtenait jamais de nœud,
  et sa note (`result.notes`) n'avait nulle part où atterrir. Même classe de
  bug que AI-20260703-002/003 (mécanisme de citation non reconnu par
  l'export), appliquée cette fois au nœud page lui-même plutôt qu'aux
  preuves.
- **Correctif (`exports/zeroneurone.py`, `_build_curated_graph`) :**
  `linked_result_ids` (utilisé pour peupler `linked_entities_by_result` et le
  `source` du nœud entité) fusionne désormais l'ancien
  `entity.linked_result_ids` **et** les `result_id` des faits de l'entité
  (`facts_by_entity`), dédupliqués. Aucun changement de comportement pour les
  investigations où le lien était déjà explicite ; les pages liées
  uniquement par fait obtiennent maintenant leur nœud « Site web » (tags,
  notes, propriétés page-scope, arête « Trouvé sur »), comme le laissait
  déjà attendre le rail Synthesix.
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 28 tests (1 nouveau :
    `test_page_surfaces_with_its_notes_when_only_linked_through_a_fact` —
    `linked_result_ids: []`, entité liée uniquement par un fait ; vérifie que
    le nœud `result-result-1` existe, porte `notes == "Reviewed profile."`,
    le tag « Site web » et l'arête « Trouvé sur » vers l'entité)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 295 tests
  - `.venv\Scripts\python.exe -m py_compile exports/zeroneurone.py
    tests/test_zeroneurone_export.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** ré-export réel du cas Rayloc dans ZeroNeurone pour
  confirmer que le nœud page TikTok apparaît désormais avec sa note — à
  valider par l'utilisateur sur son prochain export.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`.

### AI-20260703-006 — Fusion du nœud « page » et du nœud « preuve » sur le graphe curaté

- **Agent :** Claude
- **Période UTC :** 2026-07-03
- **Branche / commits :** feat/lit-frontend, non committé
- **Objectif :** retour utilisateur (cas « Rayloc », confirmation
  d'AI-20260703-005) : le nœud page TikTok apparaît bien avec sa note, mais
  à côté un second nœud (la capture d'écran nommée « DW-47W88 ») fait
  doublon — même page, deux nœuds. Demande explicite : fusionner les deux ;
  le choix du libellé (nom de la preuve vs URL) est volontairement laissé
  ouvert pour plus tard.
- **Décision de périmètre :** revient sur une partie du comportement
  volontairement introduit par AI-20260703-002/003 (donner aux captures
  d'écran leur propre nœud visuel). Gardé pour l'instant : le libellé du
  nœud page reste l'URL (stable, unique par page — une preuve n'a pas
  toujours de nom unique quand plusieurs captures citent des propriétés
  différentes sur la même page), sujet à revoir plus tard comme demandé.
- **Changements (`exports/zeroneurone.py`, graphe curaté uniquement —
  `_build_curated_graph` / `_copy_native_assets` ; le graphe par défaut, sans
  entités, garde ses nœuds preuve dédiés, contrat inchangé) :**
  - `_build_curated_graph` : les captures citées par une propriété
    (`attributes.source_capture_id`) ne créent plus de nœud `evidence-*` ;
    elles sont mises en attente (`pending_property_citations`) puis, une
    fois les nœuds page construits, relient l'entité citante **directement**
    au nœud page avec le libellé de la propriété (ex. « Capture voiture »)
    au lieu de créer une arête vers un nœud preuve séparé.
  - Le nœud page se construit aussi désormais pour toute page dont une
    capture est ainsi citée (`cited_result_ids` ajouté à
    `source_result_ids`), pas seulement les pages liées par entité ou
    propriété page-scope.
  - L'arête générique « Trouvé sur » est sautée pour une paire
    (entité, page) qui a déjà une arête de citation spécifique (évite deux
    arêtes parallèles redondantes vers le même nœud).
  - La passe de secours « captures non citées deviennent un nœud Illustré
    par » est supprimée : ces images s'attachent maintenant directement au
    nœud page comme fichier joint (`assetIds`), sans arête dédiée — le lien
    entité↔page existe déjà via « Trouvé sur ».
  - `_evidence_node` (devenu mort) supprimé.
  - `_copy_native_assets` : les artefacts image d'une capture s'attachent
    désormais à `capture.result_id` (le nœud page) quand l'investigation a
    des `graph_entities` (graphe curaté) ; comportement inchangé (attache à
    son propre nœud preuve `capture_id`) pour le graphe par défaut, qui
    garde des nœuds preuve dédiés.
  - `_curated_positions` : commentaire mis à jour (ne mentionne plus
    « Illustré par », le fan-out beside-entity ne change pas de mécanisme —
    il continue de fonctionner tel quel puisqu'il s'appuie sur *toute* cible
    non-entité reliée par une arête, page ou non).
- **Tests exécutés :**
  - `.venv\Scripts\python.exe -m unittest tests.test_zeroneurone_export` —
    OK, 28 tests. Trois tests réécrits pour refléter la fusion (renommés
    pour rester descriptifs) :
    - `test_curated_image_evidence_becomes_its_own_node` →
      `test_curated_image_evidence_merges_onto_its_page_node`
    - `test_fact_cited_screenshot_surfaces_as_property_labelled_node` →
      `test_fact_cited_screenshot_surfaces_on_the_page_node`
    - `test_curated_layout_fans_out_several_screenshots_beside_entity` →
      `test_curated_layout_merges_several_screenshots_onto_one_page_node`
      (8→1 nœud, 6 `assetIds` sur le nœud page, position toujours à côté de
      l'entité)
  - `.venv\Scripts\python.exe -m unittest discover` — OK, 295 tests
  - `.venv\Scripts\python.exe -m py_compile exports/zeroneurone.py
    tests/test_zeroneurone_export.py` — OK
  - `git diff --check` — OK, avertissements CRLF uniquement
- **Non exécuté :** ré-export réel du cas Rayloc pour confirmer visuellement
  la fusion (un seul nœud par page, images en pièces jointes) — à valider
  par l'utilisateur sur son prochain export.
- **Reste ouvert (signalé par l'utilisateur, volontairement pas traité) :**
  choix définitif du libellé du nœud page quand plusieurs preuves nommées
  différemment y sont attachées (garder l'URL, basculer sur le nom de la
  preuve la plus récente, ou autre) — décision à prendre plus tard.
- **Fichiers modifiés :** `exports/zeroneurone.py`,
  `tests/test_zeroneurone_export.py`.

### AI-20260706-001 — Plan d'action robustesse + migration overlay vers extension Chrome

- **Agent :** Claude
- **Branche :** feat/lit-frontend
- **Résultat :** plan d'action complet issu de la review technique du
  2026-07-06, sous forme de fichiers de tâches autonomes.
  - `PROJECT_STATE.md` (nouveau) : état court, décisions structurantes
    DEC-PLAN-01 à 06 (Zendriver conservé ; transport push
    `Runtime.addBinding` ; overlay CDP remplacé progressivement par une
    extension Chrome MV3 intégrée, périmètre http/https uniquement ;
    captures restent CDP ; second navigateur de recherche à profil dédié).
  - `docs/tasks/README.md` + 24 tâches `T-0xx` réparties en 6 phases :
    Phase 0 quick wins (T-001..T-006), Phase 1 recherche robuste
    (T-010..T-015), Phase 2 BrowserService + push local (T-020..T-022),
    Phase 3 extension Chrome (T-030..T-036, spike transport T-031 bloquant),
    Phase 4 isolation/données (T-040..T-043), QA (T-050, T-051).
  - `AGENTS.md` : ajout de `PROJECT_STATE.md` et `docs/tasks/` aux documents
    de référence.
- **Tests exécutés :** aucun (documentation uniquement, aucun code modifié).
- **Prochaine action :** démarrer T-001 (Codex) puis T-006 (Claude, mesure de
  référence avant optimisations). T-030 peut démarrer en parallèle.

### AI-20260706-002 — Phase 0 du plan : quick wins stabilité (T-001..T-006)

- **Agent :** Claude
- **Branche :** feat/lit-frontend
- **Résultat :** les 6 tâches de la phase 0 sont livrées, une par commit :
  - T-001 (6bba4dc) : actions UI en files FIFO (overlay `window.__synthesixActions`,
    home `state.pendingActions`) — plus de clics perdus entre deux ticks.
  - T-006 (072723c) : `observability.py` + instrumentation CDP
    (main.py, search_engine, duckduckgo, brave) + `tests/test_cdp_budget.py`
    qui verrouille la baseline : 1 inventaire targets + 6 evaluates par tick
    idle (topologie 1 home + 1 externe + 1 page enquête).
  - T-003 (20ce8fb) : probe home léger + push des payloads
    history/investigations uniquement sur divergence de version —
    0 octet transféré en régime stable (verrouillé par test).
  - T-005 : quit propre après 10 s de navigateur injoignable, purge du set
    focus-guard ; dédoublonnage targets documenté non-réalisable sur
    zendriver 0.15.3 (update_targets ne retire jamais les targets fermés),
    sera supprimé par T-022.
  - T-004 : captcha Google détecté par `query_selector("#captcha-form")` +
    URL `/sorry/`, `RobotChallengeError` si non résolu (couverture
    `challenge`), garde anti-récursion des attentes.
  - T-002 : cache `AppSettings` par signature d'environnement
    (SYNTHESIX_* + cwd) + `reload_settings()` — compatible avec tous les
    tests `patch.dict`/chdir sans modification.
- **Tests exécutés :** suites ciblées par tâche (voir fichiers T-0xx) +
  `unittest discover` complet après T-002 : **307 tests OK**.
- **Non exécuté :** smoke navigateur réel (mesure 60 s à vide, kill Chrome,
  captcha Google réel) — à faire au premier run interactif ; les
  comportements sont couverts par tests unitaires.
- **Fichiers modifiés :** `main.py`, `index.html`, `settings.py`,
  `google.py`, `search_engine.py`, `duckduckgo.py`, `brave.py`,
  `observability.py` (nouveau), `tests/test_main.py`,
  `tests/test_engines.py`, `tests/test_settings.py`,
  `tests/test_cdp_budget.py` (nouveau), `docs/tasks/*`.
- **Prochaine action :** Phase 1 — T-010 (deadline globale de recherche,
  Claude) et T-013/T-015 (Brave fallback + golden files, Codex) sont
  indépendants et peuvent démarrer en parallèle. T-050 (harness FakeTab)
  utile avant T-010 pour mutualiser les fakes.

### AI-20260706-003 — Phase 1 : T-050 (harness FakeTab) + T-010 (budget global de recherche)

- **Agent :** Claude
- **Branche :** feat/lit-frontend
- **Résultat :**
  - **T-050** : nouveau `tests/fakes.py` — `FakeTab` (méthodes réellement
    utilisées par le code, référence zendriver 0.15.3), `FakeBrowser`,
    `FakeElement`, `CallJournal` (`count`, `scripts_evaluated_bytes`) et
    `fake_clock(*modules)` (proxy `time.monotonic`/`asyncio.sleep` sans effet
    global — un timeout de 30 s se teste sans temps réel). Réponses
    programmables : file `program()` → handler `on()` → défaut. 6 tests
    d'exemple dans `tests/test_fakes.py` (attente moteur succès/timeout,
    boucle home action, capture PNG). `tests/test_cdp_budget.py` migré sur le
    harness (fabrique `make_tab`), baseline T-006 inchangée.
  - **T-010** : réglage `search_total_budget`
    (`SYNTHESIX_SEARCH_TOTAL_BUDGET`, défaut 120 s, 0 = désactivé, relation
    aux timeouts de challenge documentée dans `settings.py`). Dans
    `_run_engines` : `asyncio.wait(tasks, timeout=budget)` au lieu de
    `gather` ; à l'échéance les tâches restantes sont annulées et attendues,
    erreur moteur `TimeoutError("search budget exceeded")`, couverture
    `{"status": "timeout"}`, log WARNING (budget + moteurs interrompus). Les
    moteurs terminés gardent leurs résultats (retour partiel) ; « tous en
    échec ⇒ exception » inchangé. Annulation vérifiée : pas de
    `except BaseException`/`except:` nu dans le dépôt, tab fermé par le
    `finally` de `SearchEngine.search` (assert `FakeTab.closed`).
- **Tests exécutés :** `tests.test_fakes` (6), `tests.test_cdp_budget` (4),
  `tests.test_search_orchestrator` (+4 tests budget),
  `tests.test_search_engine_errors`, `py_compile` des fichiers touchés,
  `unittest discover` — **317 tests OK** ; `git diff --check` OK (CRLF).
- **Non exécuté :** smoke navigateur réel d'une recherche coupée par le
  budget (comportement couvert par tests unitaires avec moteur suspendu) ;
  à observer au premier run interactif long.
- **Fichiers modifiés :** `tests/fakes.py` (nouveau), `tests/test_fakes.py`
  (nouveau), `tests/test_cdp_budget.py`, `search_orchestrator.py`,
  `settings.py`, `tests/test_search_orchestrator.py`,
  `docs/tasks/T-050-harness-faketab.md`,
  `docs/tasks/T-010-deadline-globale-recherche.md`, `docs/tasks/README.md`,
  `PROJECT_STATE.md`.
- **Prochaine action :** T-011 (recherche non bloquante + annulation,
  Claude) ; T-013/T-015 restent disponibles pour Codex en parallèle.

### AI-20260706-004 — T-011 : recherche non bloquante + annulation

- **Agent :** Claude
- **Branche :** feat/lit-frontend
- **Résultat :**
  - `main.py` : les actions `search` et `retry_search_combination` partent
    en tâche de fond (`_start_search_task`, done callback anti-exception
    silencieuse ; wrappers `_run_search_action` / `_run_retry_search_action`
    qui possèdent les statuts de fin). Une seule recherche à la fois
    (`_search_task_running`) ; nouvelle action home **`cancel_search`**
    (cancel + await + « Search cancelled. ») ; garde d'arrêt : la tâche
    active est annulée et attendue dans le `finally` de `main()` avant
    `browser_manager.stop()`. Nouveau push `_set_home_search_running` →
    contrat home `window.synthesixHome.setSearchRunning(bool)`.
  - `search_engine.py` : registre `ACTIVE_ENGINE_TAB_TARGETS` (add au
    `navigate`, discard au `close_tab`) ; `wait_for_home_action` saute ces
    tabs — pas d'injection overlay ni de focus-guard sur un tab moteur
    pendant un scrape concurrent.
  - `index.html` : bouton « Cancel search » (danger, caché par défaut,
    affiché via `setSearchRunning`) → `queueAction("cancel_search")` ;
    `theme.css` : `.search-row` en `1fr auto auto` + `.search-cancel-button`.
  - `i18n.js` : 5 clés (fr/es/zh + pt/de).
  - Concurrence : `record_search` (SQLite) pendant d'autres actions couvert
    par WAL + `busy_timeout` 5 s — documenté, pas de changement.
- **Tests exécutés :** `tests.test_main` (42, dont +7 T-011),
  `tests.test_i18n_coverage`, `tests.test_cdp_budget`,
  `py_compile`, `unittest discover` — **324 tests OK** ;
  `git diff --check` OK (CRLF). Smoke visuel headless : bouton
  visible/caché, thème sombre + clair
  (`tmp_ui_render/cancel_button_*.png`).
- **Non exécuté :** smoke live obligatoire (recherche réelle + save page
  pendant recherche + annulation ≤ 2 s + quit pendant recherche) — session
  navigateur réelle requise ; T-011 reste en `review` jusque-là.
- **Fichiers modifiés :** `main.py`, `search_engine.py`, `index.html`,
  `theme.css`, `i18n.js`, `tests/test_main.py`,
  `docs/tasks/T-011-recherche-non-bloquante.md`, `docs/tasks/README.md`,
  `PROJECT_STATE.md`.
- **Prochaine action :** smoke live T-011 au prochain run interactif ;
  ensuite T-012 (Claude) ; T-013/T-015 (Codex) toujours disponibles.
