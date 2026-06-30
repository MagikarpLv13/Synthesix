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
